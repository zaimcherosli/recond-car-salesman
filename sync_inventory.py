#!/usr/bin/env python3
"""
Smarter Inventory & Pricing Sync Pipeline
- Parses dealer 'CAR PRICELIST.pdf'
- Performs incremental sync using stable composite key (stock_no + chassis)
- Preserves market research & manual overrides
- Runs centralized pricing engine to compute estimated OTR, market spread, commissions, and ad scores
- Generates 'admin_inventory.json' (Admin/Internal full commercial data)
- Generates 'cars_data.json' (Sanitized Public catalog with NO body price or margin leak)
- Optionally commits & pushes to GitHub for Cloudflare auto-deploy
"""

import os
import re
import sys
import json
import time
import argparse
import urllib.parse
import subprocess
import pdfplumber

from pricing_engine import (
    load_settings,
    calculate_car_pricing,
    sanitize_for_public,
    get_unique_key,
    SETTINGS_FILE,
    MARKET_FILE,
    ADMIN_INVENTORY_FILE,
    PUBLIC_DATA_FILE
)

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

PDF_FILENAME = "CAR PRICELIST.pdf"
CARS_DIR = os.path.join("public", "cars")

def clean_text(val):
    if val is None:
        return ""
    return re.sub(r'\s+', ' ', str(val)).strip()

def sanitize_code(stock_no):
    s = clean_text(stock_no).replace("/", "_").replace("\\", "_")
    return re.sub(r'[^a-zA-Z0-9_-]', '_', s)

def generate_seo_slug(brand, model, stock_no):
    raw = f"{brand} {model} {stock_no}".lower()
    slug = re.sub(r'[^a-z0-9]+', '-', raw).strip('-')
    return slug

def parse_price(price_str):
    if not price_str:
        return 0, "Harga Bincang"
    price_clean = clean_text(price_str).upper()
    
    promo_match = re.search(r'RM\s*([\d\.]+)\s*[KM]?\s*@\s*RM\s*([\d\.]+)\s*([KM]?)', price_clean)
    if promo_match:
        val_str = promo_match.group(2)
        unit = promo_match.group(3) or "K"
        val = float(val_str)
        num = int(val * 1000000) if unit == "M" else int(val * 1000)
        disp = f"RM {num:,} (Tawaran Istimewa)"
    else:
        m = re.search(r'RM\s*([\d\.]+)\s*([KM]?)', price_clean)
        if m:
            val = float(m.group(1))
            unit = m.group(2)
            if unit == "M" or val < 100:
                num = int(val * 1000000) if (unit == "M" or val < 10) else int(val * 1000)
            else:
                num = int(val * 1000)
            disp = f"RM {num:,}"
        else:
            return 0, price_str
            
    return num, disp

def extract_grade_and_mileage(spec_text):
    text = clean_text(spec_text)
    grade = "4.5A"
    mileage = "Perbatuan Rendah"
    
    g_match = re.search(r'GRADE\s*[:\s]*([0-9\.]+\s*[A-CS]*)', text, re.IGNORECASE)
    if g_match:
        grade = g_match.group(1).strip().upper()
        
    m_match = re.search(r'([\d,\.]+\s*KM)', text, re.IGNORECASE)
    if m_match:
        mileage = m_match.group(1).strip().upper()
    elif 'MILES' in text.upper():
        mi_match = re.search(r'([\d,\.]+\s*MILES)', text, re.IGNORECASE)
        if mi_match:
            mileage = mi_match.group(1).strip().upper()
            
    return grade, mileage

def classify_category(model_str):
    m = model_str.upper()
    if any(k in m for k in ['ALPHARD', 'VELLFIRE', 'NOAH', 'VOXY', 'STEPWAGON', 'STEPWGN', 'ODYSSEY', 'TANTO', 'WELCAB']):
        return 'mpv'
    if any(k in m for k in ['HARRIER', 'RX300', 'RX350', 'NX250', 'NX350', 'LAND CRUISER', 'LANDCRUISER', 'DEFENDER', 'JIMNY', 'TAFT', 'MACAN', 'WRANGLER', 'GLC', 'GLA', 'GLB', 'GLE', 'URBAN']):
        return 'suv'
    if any(k in m for k in ['TYPE R', 'FL5', 'FK8', 'GT3', 'GT3 RS', 'M4', 'M2', '812 GTS', 'GTR', 'GR YARIS', 'GRMN', 'GR86', 'ROADSTER', 'ROADSTAR', 'BRZ', 'SWIFT SPORT']):
        return 'performance'
    if any(k in m for k in ['SEDAN', 'C200', 'E200', 'E300', 'IS300', 'LM500H']):
        return 'sedan'
    return 'hatchback'

def extract_brand(model_str, brand_hint=""):
    m = (model_str + " " + brand_hint).upper()
    for b in ['TOYOTA', 'HONDA', 'MERCEDES BENZ', 'MERCEDES', 'BMW', 'LEXUS', 'PORSCHE', 'PORSHCE', 'NISSAN', 'MAZDA', 'MINI', 'SUBARU', 'SUZUKI', 'DAIHATSU', 'FERRARI', 'LAND ROVER', 'JEEP']:
        if b in m:
            if b in ['MERCEDES', 'MERCEDES BENZ']:
                return 'Mercedes-Benz'
            if b == 'PORSHCE':
                return 'Porsche'
            return b.title()
    return 'Recond'

def parse_pdf_inventory(pdf_path=PDF_FILENAME):
    print(f"Reading Dealer PDF: {pdf_path}...")
    records = []
    current_brand = ""
    current_section = "AVAILABLE"

    with pdfplumber.open(pdf_path) as pdf:
        for page_idx, page in enumerate(pdf.pages):
            tables = page.extract_tables()
            if not tables:
                continue
            table = tables[0]

            for row in table:
                if not row or len(row) < 5:
                    continue
                col0 = str(row[0] or "").strip()
                col1 = str(row[1] or "").strip()
                col4 = str(row[4] or "").strip()
                
                joined_row = " ".join([str(c or "") for c in row]).upper()
                if "BOOKING" in joined_row and ("LOU" not in joined_row and "STOCK" not in joined_row):
                    current_section = "BOOKING"
                elif "LOU" in joined_row or "CASH BUYER" in joined_row:
                    current_section = "LOU/CASH"
                elif "INCOMING" in joined_row or "DUTY TO BE PAID" in joined_row:
                    current_section = "INCOMING"
                
                if col0 in ['BMW', 'DAIHATSU', 'FERRARI', 'HONDA', 'LAND ROVER', 'LEXUS', 'MAZDA', 'MERCEDES BENZ', 'MINI', 'NISSAN', 'PORSHCE', 'PORSCHE', 'SUBARU', 'SUZUKI', 'TOYOTA', 'JEEP']:
                    current_brand = col0
                    continue
                if col0 in ['NO', '', 'CAR PRICELIST AS AT']:
                    continue
                    
                if not col1 and not col4:
                    continue
                if col1 in ['STOCK NO', 'None']:
                    continue
                    
                stock_no = col1 if col1 else col0
                model = col4 if col4 else str(row[3] or "")
                if not model or model == "MODEL":
                    continue
                    
                spec = str(row[5] or "").strip() if len(row) > 5 else ""
                color = str(row[6] or "").strip() if len(row) > 6 else ""
                chassis = str(row[7] or "").strip() if len(row) > 7 else ""
                price_raw = str(row[10] or "").strip() if len(row) > 10 else ""
                status_raw = str(row[11] or "").strip() if len(row) > 11 else ""
                
                code = sanitize_code(stock_no)
                body_num, body_disp = parse_price(price_raw)
                grade, mileage = extract_grade_and_mileage(spec)
                brand = extract_brand(model, current_brand)
                category = classify_category(model)
                slug = generate_seo_slug(brand, clean_text(model), stock_no)
                
                status_label = "Ready Stock"
                if "INCOMING" in current_section or "INCOMING" in status_raw.upper():
                    status_label = "Incoming Stock"
                elif "BOOKING" in current_section or "BOOKING" in status_raw.upper() or "LOU" in current_section:
                    status_label = "Booking / Reserved"
                
                records.append({
                    "stock_no": stock_no,
                    "code": code,
                    "brand": brand,
                    "model": clean_text(model),
                    "category": category,
                    "year": clean_text(str(row[2] or "")),
                    "color": clean_text(color).title(),
                    "chassis": clean_text(chassis),
                    "mileage": mileage,
                    "grade": grade,
                    "body_price": body_num,
                    "price_rm": body_num,
                    "specs": clean_text(spec),
                    "status": status_label,
                    "section": current_section,
                    "page": page_idx + 1,
                    "slug": slug,
                    "detail_url": f"stok/{slug}.html"
                })
                
    print(f"[OK] Parsed {len(records)} vehicle records from PDF.")
    return records

def resolve_car_images(code):
    base_folder = os.path.join(CARS_DIR, code)
    if not os.path.exists(base_folder):
        return [], "", "No Photos"
        
    subdirs = [d for d in os.listdir(base_folder) if os.path.isdir(os.path.join(base_folder, d))]
    malay_folders = [d for d in subdirs if "malay" in d.lower() or "my" in d.lower()]
    japan_folders = [d for d in subdirs if "japan" in d.lower() or "jp" in d.lower()]
    
    chosen_images = []
    source_label = "Local Photos"
    
    if malay_folders:
        source_label = "Malaysia Stock"
        target_dir = os.path.join(base_folder, malay_folders[0])
        for f in sorted(os.listdir(target_dir)):
            if f.lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
                chosen_images.append(os.path.join(target_dir, f).replace("\\", "/"))
    elif japan_folders:
        source_label = "Japan Auction Stock"
        target_dir = os.path.join(base_folder, japan_folders[0])
        for f in sorted(os.listdir(target_dir)):
            if f.lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
                chosen_images.append(os.path.join(target_dir, f).replace("\\", "/"))
    else:
        for root, dirs, files in os.walk(base_folder):
            for f in sorted(files):
                if f.lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
                    chosen_images.append(os.path.join(root, f).replace("\\", "/"))
                    
    cover = chosen_images[0] if chosen_images else ""
    for img in chosen_images:
        img_name = os.path.basename(img)
        if any(k in img_name for k in ["IMG_2467", "IMG_2468", "10.21.19", "12.19.34", "06fd17e4", "4.40.14"]):
            cover = img
            break
            
    return chosen_images, cover, source_label

def main():
    parser = argparse.ArgumentParser(description="Smart Inventory & Pricing Sync Engine")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of cars")
    parser.add_argument("--push", action="store_true", help="Auto git commit & push to GitHub")
    args = parser.parse_args()

    print("="*75)
    print("SISTEM PENGURUSAN INVENTORI & PENETAPAN HARGA OTR KERETA RECOND")
    print("="*75)
    
    settings = load_settings()
    
    # 1. Load Market Research Database
    market_research = {}
    if os.path.exists(MARKET_FILE):
        try:
            with open(MARKET_FILE, "r", encoding="utf-8") as f:
                market_research = json.load(f)
        except Exception as e:
            print(f"[WARN] Failed to load {MARKET_FILE}: {e}")
            
    print(f"Pangkalan Data Market Research: {len(market_research)} rekod sedia ada.")
    
    # 2. Parse PDF Inventory
    pdf_cars = parse_pdf_inventory(PDF_FILENAME)
    
    # 3. Incremental Processing & Pricing Engine Execution
    admin_inventory = []
    public_inventory = []
    
    limit = args.limit if args.limit is not None else len(pdf_cars)
    
    unresearched_count = 0
    high_priority_ads = []
    
    for car in pdf_cars[:limit]:
        code = car["code"]
        key = get_unique_key(car)
        
        imgs, cover, src_label = resolve_car_images(code)
        car["images"] = imgs
        car["thumbnail"] = cover
        car["image_count"] = len(imgs)
        car["source_label"] = src_label
        
        # Pull matching market intelligence
        car_mkt = market_research.get(key) or market_research.get(car["stock_no"].replace(" ", "_").upper()) or {}
        
        # Calculate full commercial metrics
        admin_data = calculate_car_pricing(car, car_mkt, settings)
        admin_inventory.append(admin_data)
        
        # Sanitize for public catalog
        public_data = sanitize_for_public(admin_data)
        
        # Filter: only publish cars that have photos or were previously published
        if imgs or car.get("price_rm", 0) > 0:
            public_inventory.append(public_data)
            
        if admin_data["pricing_status"] == "UNRESEARCHED":
            unresearched_count += 1
        elif admin_data["ad_score"] >= 8.5 and admin_data["available_market_spread"] >= 3000:
            high_priority_ads.append(admin_data)

    # 4. Save Internal Admin Dataset
    with open(ADMIN_INVENTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(admin_inventory, f, indent=2, ensure_ascii=False)
    print(f"[OK] Fail dalaman {ADMIN_INVENTORY_FILE} disimpan ({len(admin_inventory)} unit lengkap maklumat Body Price & Margin).")
    
    # 5. Save Public Sanitized Dataset
    with open(PUBLIC_DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(public_inventory, f, indent=2, ensure_ascii=False)
    print(f"[OK] Fail awam {PUBLIC_DATA_FILE} dikemaskini ({len(public_inventory)} unit selamat diterbitkan - NO body price leak).")

    # 6. Summary Report
    print("\n" + "="*75)
    print("RINGKASAN STATUS INVENTORI & IKLAN PILIHAN (TOP ADS TO RUN)")
    print("="*75)
    print(f"Jumlah Stok Dalam PDF: {len(admin_inventory)} unit")
    print(f"Stok Sedia Ada Foto / Diterbitkan: {len(public_inventory)} unit")
    print(f"Unit Memerlukan Survey Pasaran (Unresearched): {unresearched_count} unit")
    print(f"Unit Berpotensi Iklan Tinggi (Ad Score >= 8.5): {len(high_priority_ads)} unit\n")
    
    # Sort top ads
    high_priority_ads.sort(key=lambda x: x["ad_score"], reverse=True)
    for idx, top in enumerate(high_priority_ads[:6]):
        print(f"🔥 #{idx+1} [{top['stock_no']}] {top['brand']} {top['model']} ({top['year']})")
        print(f"   Ad Score: {top['ad_score']}/10 | Market Spread: RM {top['available_market_spread']:,}")
        print(f"   Body Price: RM {top['body_price']:,} | Est OTR: RM {top['advertised_price_ncd55']:,} (Market: RM {top['market_median']:,})")
        print(f"   Cadangan Komisen: RM {top['suggested_commission']:,} | Buffer: RM {top['negotiation_buffer']:,}\n")

    print("="*75)
    
    # 7. Git Push if requested
    if args.push:
        print("\nMenolak (push) perubahan ke GitHub...")
        subprocess.run(["git", "add", "cars_data.json", "admin_inventory.json", "market_research.json", "pricing_settings.json"], check=False)
        subprocess.run(["git", "commit", "-m", f"chore(sync): update inventory & smart pricing engine ({len(public_inventory)} units)"], check=False)
        res = subprocess.run(["git", "push", "origin", "main"], capture_output=True, text=True)
        if res.returncode == 0:
            print("[OK] Berjaya push ke GitHub! Cloudflare Pages sedang auto-deploy.")
        else:
            print(f"[WARN] Git push output: {res.stderr or res.stdout}")

if __name__ == "__main__":
    main()
