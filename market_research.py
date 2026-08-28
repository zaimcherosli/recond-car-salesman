import os
import sys
import json
import csv
import argparse
import datetime
from typing import Dict, Any, List
from pricing_engine import load_settings, calculate_car_pricing, get_unique_key, MARKET_FILE, ADMIN_INVENTORY_FILE

def load_market_research(path: str = MARKET_FILE) -> Dict[str, Any]:
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"[WARN] Error loading {path}: {e}")
    return {}

def save_market_research(data: Dict[str, Any], path: str = MARKET_FILE) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"[OK] Saved {len(data)} market research records to {path}")

def export_market_research_csv(output_csv_path: str = "market_research_export.csv") -> None:
    market_data = load_market_research()
    fieldnames = [
        "stock_no", "chassis", "model",
        "market_low", "market_median", "market_high",
        "market_sample_size", "market_checked_at", "market_sources",
        "demand_score", "is_override", "suggested_commission",
        "negotiation_buffer", "advertised_price_ncd55", "advertised_price_ncd0",
        "minimum_sell_price", "market_notes"
    ]
    
    rows = []
    for key, item in market_data.items():
        overrides = item.get("manual_overrides", {})
        rows.append({
            "stock_no": item.get("stock_no", ""),
            "chassis": item.get("chassis", ""),
            "model": item.get("model", ""),
            "market_low": item.get("market_low", 0),
            "market_median": item.get("market_median", 0),
            "market_high": item.get("market_high", 0),
            "market_sample_size": item.get("market_sample_size", 0),
            "market_checked_at": item.get("market_checked_at", ""),
            "market_sources": item.get("market_sources", ""),
            "demand_score": item.get("demand_score", 8.5),
            "is_override": overrides.get("is_override", False),
            "suggested_commission": overrides.get("suggested_commission", ""),
            "negotiation_buffer": overrides.get("negotiation_buffer", ""),
            "advertised_price_ncd55": overrides.get("advertised_price_ncd55", ""),
            "advertised_price_ncd0": overrides.get("advertised_price_ncd0", ""),
            "minimum_sell_price": overrides.get("minimum_sell_price", ""),
            "market_notes": item.get("market_notes", "")
        })
        
    with open(output_csv_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
        
    print(f"[OK] Exported {len(rows)} records to {output_csv_path}")

def import_market_research_csv(csv_path: str, apply_changes: bool = False) -> Dict[str, Any]:
    if not os.path.exists(csv_path):
        print(f"[ERROR] File {csv_path} not found!")
        return {}
        
    current_data = load_market_research()
    updated_data = current_data.copy()
    
    diff_report = []
    
    with open(csv_path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            stock = str(row.get("stock_no", "")).strip()
            chassis = str(row.get("chassis", "")).strip()
            if not stock:
                continue
                
            key = f"{stock.replace(' ', '_').upper()}_{chassis.upper()}" if chassis and chassis != "-" else stock.replace(" ", "_").upper()
            
            try:
                m_low = int(float(row.get("market_low") or 0))
                m_median = int(float(row.get("market_median") or 0))
                m_high = int(float(row.get("market_high") or 0))
                m_sample = int(float(row.get("market_sample_size") or 0))
            except ValueError:
                m_low = m_median = m_high = m_sample = 0
                
            is_override_raw = str(row.get("is_override", "")).lower()
            is_override = is_override_raw in ["true", "1", "yes", "y"]
            
            overrides = {"is_override": is_override}
            if row.get("suggested_commission"):
                try: overrides["suggested_commission"] = int(float(row["suggested_commission"]))
                except Exception: pass
            if row.get("negotiation_buffer"):
                try: overrides["negotiation_buffer"] = int(float(row["negotiation_buffer"]))
                except Exception: pass
            if row.get("advertised_price_ncd55"):
                try: overrides["advertised_price_ncd55"] = int(float(row["advertised_price_ncd55"]))
                except Exception: pass
            if row.get("advertised_price_ncd0"):
                try: overrides["advertised_price_ncd0"] = int(float(row["advertised_price_ncd0"]))
                except Exception: pass
            if row.get("minimum_sell_price"):
                try: overrides["minimum_sell_price"] = int(float(row["minimum_sell_price"]))
                except Exception: pass
                
            checked_at = str(row.get("market_checked_at", "")).strip() or datetime.date.today().isoformat()
            
            entry = {
                "stock_no": stock,
                "chassis": chassis,
                "model": row.get("model", ""),
                "market_low": m_low,
                "market_median": m_median,
                "market_high": m_high,
                "market_sample_size": m_sample,
                "market_checked_at": checked_at,
                "market_sources": row.get("market_sources", ""),
                "market_notes": row.get("market_notes", ""),
                "demand_score": float(row.get("demand_score") or 8.5),
                "manual_overrides": overrides
            }
            
            prev_median = current_data.get(key, {}).get("market_median", "NEW")
            diff_report.append({
                "key": key,
                "stock_no": stock,
                "model": row.get("model", ""),
                "prev_median": prev_median,
                "new_median": m_median,
                "is_override": is_override
            })
            
            updated_data[key] = entry

    print(f"\n{'='*70}")
    print(f"PREVIEW: IMPORT MARKET RESEARCH DARI {csv_path}")
    print(f"{'='*70}")
    for item in diff_report[:10]:
        print(f"[{item['stock_no']}] {item['model'][:25]} | Median Dahulu: {item['prev_median']} -> Baru: RM {item['new_median']:,} (Override: {item['is_override']})")
    if len(diff_report) > 10:
        print(f"... dan {len(diff_report)-10} rekod lain.")
    print(f"{'='*70}")
    
    if apply_changes:
        save_market_research(updated_data)
        print(f"[SUCCESS] {len(diff_report)} rekod penyelidikan pasaran berjaya dikemas kini!")
    else:
        print("[INFO] Ini adalah mod Preview (Dry-Run). Guna parameter --apply untuk menyimpan perubahan.")
        
    return updated_data

def main():
    parser = argparse.ArgumentParser(description="Market Research Importer / Exporter CLI")
    parser.add_argument("--export", type=str, default=None, help="Eksport market research ke fail CSV")
    parser.add_argument("--import-csv", type=str, default=None, help="Import fail CSV")
    parser.add_argument("--apply", action="store_true", help="Gunakan perubahan import ke fail database")
    args = parser.parse_args()
    
    if args.export:
        export_market_research_csv(args.export)
    elif args.import_csv:
        import_market_research_csv(args.import_csv, apply_changes=args.apply)
    else:
        # Default status display
        data = load_market_research()
        print(f"Total Market Research Records: {len(data)}")

if __name__ == "__main__":
    main()
