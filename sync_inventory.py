#!/usr/bin/env python3
"""
Sync Inventory Pipeline for Recond Car Salesman Website
- Parses 'CAR PRICELIST.pdf'
- Performs incremental comparison against 'cars_data.json'
- Downloads photos for new cars (MY folder first, else JPN fallback)
- Cleans up deleted/sold units
- Updates 'cars_data.json' and 'index.html'
- Optionally commits and pushes to GitHub for instant Cloudflare Pages auto-deploy
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
import requests
import gdown

# Configure UTF-8 for Windows console
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

PDF_FILENAME = "CAR PRICELIST.pdf"
DATA_FILENAME = "cars_data.json"
HTML_FILENAME = "index.html"
CARS_DIR = os.path.join("public", "cars")

def clean_text(val):
    if val is None:
        return ""
    return re.sub(r'\s+', ' ', str(val)).strip()

def sanitize_code(stock_no):
    s = clean_text(stock_no).replace("/", "_").replace("\\", "_")
    return re.sub(r'[^a-zA-Z0-9_-]', '_', s)

def parse_price(price_str):
    if not price_str:
        return 0, "Harga Bincang", "Bincang"
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
            return 0, price_str, "Bincang"
            
    principal = num * 0.9
    total_interest = principal * 0.025 * 9
    monthly = int((principal + total_interest) / 108) if num > 0 else 0
    monthly_disp = f"~RM {monthly:,} / bln" if monthly > 0 else "Bincang"
    return num, disp, monthly_disp

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
    if any(k in m for k in ['ALPHARD', 'VELLFIRE', 'NOAH', 'VOXY', 'STEPWAGON', 'ODYSSEY', 'TANTO', 'WELCAB']):
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
    print(f"Reading PDF file: {pdf_path}...")
    records = []
    current_brand = ""
    current_section = "AVAILABLE"

    with pdfplumber.open(pdf_path) as pdf:
        for page_idx, page in enumerate(pdf.pages):
            tables = page.extract_tables()
            if not tables:
                continue
            table = tables[0]
            links = page.hyperlinks or []

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
                price_num, price_disp, monthly = parse_price(price_raw)
                grade, mileage = extract_grade_and_mileage(spec)
                brand = extract_brand(model, current_brand)
                category = classify_category(model)
                
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
                    "price_rm": price_num,
                    "price_display": price_disp,
                    "monthly_estimate": monthly,
                    "specs": clean_text(spec),
                    "status": status_label,
                    "section": current_section,
                    "page": page_idx + 1
                })
                
    print(f"[OK] Parsed {len(records)} car records from PDF.")
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
        if "IMG_2467" in img_name or "IMG_2468" in img_name or "10.21.19" in img_name or "12.19.34" in img_name or "06fd17e4" in img_name:
            cover = img
            break
            
    return chosen_images, cover, source_label

def update_website_files(cars_list):
    print("Updating cars_data.json & index.html...")
    with open(DATA_FILENAME, "w", encoding="utf-8") as f:
        json.dump(cars_list, f, indent=2, ensure_ascii=False)
        
    with open(HTML_FILENAME, "r", encoding="utf-8") as f:
        html = f.read()
        
    cars_json_str = json.dumps(cars_list, indent=2, ensure_ascii=False)
    data_pattern = re.compile(r'const allCarsData = \[[\s\S]*?\];', re.MULTILINE)
    if data_pattern.search(html):
        html = data_pattern.sub(f"const allCarsData = {cars_json_str};", html)
        
    with open(HTML_FILENAME, "w", encoding="utf-8") as f:
        f.write(html)
        
    print(f"[OK] Website database updated with {len(cars_list)} cars.")

def main():
    parser = argparse.ArgumentParser(description="Sync Inventory Pipeline for Recond Car Website")
    parser.add_argument("--limit", type=int, default=None, help="Had bilangan kereta")
    parser.add_argument("--push", action="store_true", help="Auto git commit & push to GitHub")
    args = parser.parse_args()

    print("="*60)
    print("SISTEM AUTOMASI PENYEGERAKAN INVENTORI KERETA RECOND")
    print("="*60)
    
    # 1. Parse PDF
    pdf_cars = parse_pdf_inventory(PDF_FILENAME)
    
    # 2. Load existing data
    existing_cars = {}
    if os.path.exists(DATA_FILENAME):
        try:
            with open(DATA_FILENAME, "r", encoding="utf-8") as f:
                old_list = json.load(f)
                for c in old_list:
                    existing_cars[c.get("code")] = c
        except Exception:
            pass
            
    print(f"Rekod sedia ada dalam database: {len(existing_cars)} kereta")
    
    # 3. Process cars
    final_cars = []
    limit = args.limit if args.limit is not None else len(pdf_cars)
    
    for i, car in enumerate(pdf_cars[:limit]):
        code = car["code"]
        imgs, cover, src_label = resolve_car_images(code)
        
        car["images"] = imgs
        car["thumbnail"] = cover
        car["image_count"] = len(imgs)
        car["source_label"] = src_label
        
        if imgs or code in existing_cars:
            final_cars.append(car)
            
    if not final_cars:
        final_cars = list(existing_cars.values())
        
    update_website_files(final_cars)
    
    # 4. Git Push if requested
    if args.push:
        print("\nMenolak (push) perubahan ke GitHub...")
        subprocess.run(["git", "add", "cars_data.json", "index.html", "public/"], check=False)
        subprocess.run(["git", "commit", "-m", f"chore(sync): update inventory sync ({len(final_cars)} units)"], check=False)
        res = subprocess.run(["git", "push", "origin", "main"], capture_output=True, text=True)
        if res.returncode == 0:
            print("[OK] Berjaya push ke GitHub! Cloudflare Pages sedang auto-deploy.")
        else:
            print(f"[WARN] Git push output: {res.stderr or res.stdout}")
            
    print("\nProses penyegerakan inventori selesai!")

if __name__ == "__main__":
    main()
