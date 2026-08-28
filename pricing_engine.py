import os
import json
import re
import datetime
from typing import Dict, Any, Tuple, Optional, List

SETTINGS_FILE = "pricing_settings.json"
MARKET_FILE = "market_research.json"
ADMIN_INVENTORY_FILE = "admin_inventory.json"
PUBLIC_DATA_FILE = "cars_data.json"

DEFAULT_SETTINGS = {
    "version": "1.0",
    "updated_at": "2026-08-28T19:25:00+08:00",
    "default_otr_addition_ncd55": 7000,
    "default_otr_addition_ncd0": 10000,
    "default_negotiation_buffer": 1800,
    "freshness_threshold_fresh_days": 7,
    "freshness_threshold_moderate_days": 14,
    "commission_rules": [
        {"max_body": 99999, "target_commission": 3000, "min_commission": 1500},
        {"max_body": 149999, "target_commission": 4500, "min_commission": 2500},
        {"max_body": 199999, "target_commission": 5500, "min_commission": 3000},
        {"max_body": 299999, "target_commission": 7000, "min_commission": 4000},
        {"max_body": 999999999, "target_commission": 10000, "min_commission": 5000}
    ],
    "category_otr_overrides": {
        "performance": {"ncd55": 8500, "ncd0": 12000},
        "luxury": {"ncd55": 10000, "ncd0": 15000}
    },
    "model_otr_overrides": {}
}

def load_settings(path: str = SETTINGS_FILE) -> Dict[str, Any]:
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return DEFAULT_SETTINGS.copy()

def save_settings(settings: Dict[str, Any], path: str = SETTINGS_FILE) -> None:
    settings["updated_at"] = datetime.datetime.now().isoformat()
    with open(path, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=2, ensure_ascii=False)

def get_unique_key(car: Dict[str, Any]) -> str:
    stock = str(car.get("stock_no", "")).strip().replace(" ", "_").upper()
    chassis = str(car.get("chassis", "")).strip().upper()
    if stock and chassis and chassis != "-":
        return f"{stock}_{chassis}"
    if stock:
        return stock
    code = str(car.get("code", "")).strip().upper()
    return code or "UNKNOWN_CAR"

def get_otr_additions(car: Dict[str, Any], settings: Dict[str, Any]) -> Tuple[int, int]:
    model_name = str(car.get("model", "")).upper()
    category = str(car.get("category", "")).lower()
    
    # 1. Model specific override
    model_overrides = settings.get("model_otr_overrides", {})
    for m_key, overrides in model_overrides.items():
        if m_key.upper() in model_name:
            return int(overrides.get("ncd55", settings["default_otr_addition_ncd55"])), int(overrides.get("ncd0", settings["default_otr_addition_ncd0"]))
            
    # 2. Category specific override
    cat_overrides = settings.get("category_otr_overrides", {})
    if category in cat_overrides:
        return int(cat_overrides[category].get("ncd55", settings["default_otr_addition_ncd55"])), int(cat_overrides[category].get("ncd0", settings["default_otr_addition_ncd0"]))
        
    # 3. Global default
    return int(settings.get("default_otr_addition_ncd55", 7000)), int(settings.get("default_otr_addition_ncd0", 10000))

def get_target_commission_bracket(body_price: int, settings: Dict[str, Any]) -> Tuple[int, int]:
    rules = settings.get("commission_rules", DEFAULT_SETTINGS["commission_rules"])
    for r in rules:
        if body_price <= r.get("max_body", 999999999):
            return int(r.get("target_commission", 5000)), int(r.get("min_commission", 2500))
    return 8000, 4000

def get_freshness(checked_at_str: Optional[str], settings: Dict[str, Any]) -> Tuple[str, Optional[int]]:
    if not checked_at_str:
        return "UNRESEARCHED", None
    try:
        # Accept YYYY-MM-DD or ISO
        dt_str = checked_at_str.split("T")[0]
        check_date = datetime.datetime.strptime(dt_str, "%Y-%m-%d").date()
        today = datetime.date.today()
        days = (today - check_date).days
        if days < 0:
            days = 0
        fresh_thresh = settings.get("freshness_threshold_fresh_days", 7)
        mod_thresh = settings.get("freshness_threshold_moderate_days", 14)
        if days <= fresh_thresh:
            return "FRESH", days
        elif days <= mod_thresh:
            return "MODERATE", days
        else:
            return "STALE", days
    except Exception:
        return "UNRESEARCHED", None

def calculate_demand_score(model_str: str, category: str) -> float:
    m = model_str.upper()
    if any(k in m for k in ["TYPE R", "FL5", "M4", "M2", "GT3", "812 GTS", "GRMN", "GR YARIS"]):
        return 9.5
    if any(k in m for k in ["N-BOX", "NBOX", "STEPWAGON", "STEPWGN", "ALPHARD", "VELLFIRE"]):
        return 9.0
    if any(k in m for k in ["M135", "M135I", "HARRIER", "RX300", "RX350", "JIMNY"]):
        return 8.2
    if category == "mpv":
        return 8.5
    if category == "performance":
        return 8.8
    return 7.5

def calculate_car_pricing(
    car: Dict[str, Any],
    market_data: Optional[Dict[str, Any]] = None,
    settings: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    if settings is None:
        settings = load_settings()
    if market_data is None:
        market_data = {}

    body_price = int(car.get("body_price") or car.get("price_rm") or 0)
    otr_ncd55, otr_ncd0 = get_otr_additions(car, settings)
    
    est_otr_base_ncd55 = body_price + otr_ncd55
    est_otr_base_ncd0 = body_price + otr_ncd0
    
    # Extract Market Data
    m_low = int(market_data.get("market_low") or 0)
    m_median = int(market_data.get("market_median") or 0)
    m_high = int(market_data.get("market_high") or 0)
    m_sample = int(market_data.get("market_sample_size") or 0)
    m_checked_at = market_data.get("market_checked_at")
    m_sources = market_data.get("market_sources", "")
    m_notes = market_data.get("market_notes", "")
    
    freshness, days_ago = get_freshness(m_checked_at, settings)
    target_comm, min_comm = get_target_commission_bracket(body_price, settings)
    default_buffer = int(settings.get("default_negotiation_buffer", 1800))
    
    # Check Manual Overrides
    manual_overrides = market_data.get("manual_overrides", {})
    is_manual_override = bool(manual_overrides.get("is_override", False))
    
    if m_median > 0:
        available_market_spread = m_median - est_otr_base_ncd55
    else:
        available_market_spread = 0
        
    if is_manual_override:
        suggested_commission = int(manual_overrides.get("suggested_commission", target_comm))
        negotiation_buffer = int(manual_overrides.get("negotiation_buffer", default_buffer))
        adv_ncd55 = int(manual_overrides.get("advertised_price_ncd55", est_otr_base_ncd55 + suggested_commission + negotiation_buffer))
        adv_ncd0 = int(manual_overrides.get("advertised_price_ncd0", est_otr_base_ncd0 + suggested_commission + negotiation_buffer))
        min_sell = int(manual_overrides.get("minimum_sell_price", est_otr_base_ncd55 + min_comm))
        override_type = "MANUAL OVERRIDE"
    else:
        negotiation_buffer = default_buffer
        if m_median > 0:
            # Spread-conscious commission calculation
            headroom = available_market_spread - negotiation_buffer
            if headroom >= target_comm:
                suggested_commission = target_comm
            elif headroom >= min_comm:
                suggested_commission = max(min_comm, headroom)
            else:
                suggested_commission = max(1000, headroom if headroom > 0 else min_comm // 2)
        else:
            suggested_commission = target_comm

        adv_ncd55 = est_otr_base_ncd55 + suggested_commission + negotiation_buffer
        adv_ncd0 = est_otr_base_ncd0 + suggested_commission + negotiation_buffer
        min_sell = est_otr_base_ncd55 + min_comm
        override_type = "AUTO"

    # Scores
    demand_score = float(market_data.get("demand_score") or calculate_demand_score(car.get("model", ""), car.get("category", "")))
    
    if m_median > 0 and available_market_spread > 0:
        spread_ratio = available_market_spread / max(1, m_median)
        market_score = round(min(10.0, 5.5 + (spread_ratio * 45)), 1)
        
        # Ad Score calculation
        potential_saving = m_median - adv_ncd55
        saving_ratio = max(0, potential_saving) / max(1, m_median)
        base_ad = (demand_score * 0.40) + (market_score * 0.45) + (saving_ratio * 25)
        ad_score = round(min(10.0, max(1.0, base_ad)), 1)
    else:
        market_score = 5.0
        ad_score = round(demand_score * 0.7, 1)

    # Status Determination
    if freshness == "UNRESEARCHED" or m_median <= 0:
        pricing_status = "UNRESEARCHED"
    elif available_market_spread < 2000:
        pricing_status = "LOW_MARGIN"
    elif ad_score >= 9.0 and available_market_spread >= 5000:
        pricing_status = "HIGH_PRIORITY"
    elif ad_score >= 8.0 and available_market_spread >= 3000:
        pricing_status = "GOOD_DEAL"
    else:
        pricing_status = "RESEARCHED"

    # Monthly installment for public loan calculator
    principal = adv_ncd55 * 0.9
    total_interest = principal * 0.025 * 9
    monthly = int((principal + total_interest) / 108) if adv_ncd55 > 0 else 0

    return {
        "stock_no": car.get("stock_no"),
        "code": car.get("code"),
        "unique_key": get_unique_key(car),
        "brand": car.get("brand"),
        "model": car.get("model"),
        "category": car.get("category"),
        "year": car.get("year"),
        "color": car.get("color"),
        "chassis": car.get("chassis"),
        "mileage": car.get("mileage"),
        "grade": car.get("grade"),
        "specs": car.get("specs"),
        "status": car.get("status"),
        "source_label": car.get("source_label"),
        "thumbnail": car.get("thumbnail"),
        "images": car.get("images", []),
        "image_count": car.get("image_count", len(car.get("images", []))),
        "slug": car.get("slug"),
        "detail_url": car.get("detail_url"),
        
        # Internal Pricing (Admin Only)
        "body_price": body_price,
        "body_price_display": f"RM {body_price:,}" if body_price > 0 else "Bincang",
        "otr_addition_ncd55": otr_ncd55,
        "otr_addition_ncd0": otr_ncd0,
        "estimated_otr_base_ncd55": est_otr_base_ncd55,
        "estimated_otr_base_ncd0": est_otr_base_ncd0,
        "market_low": m_low,
        "market_median": m_median,
        "market_high": m_high,
        "market_sample_size": m_sample,
        "market_checked_at": m_checked_at,
        "market_days_ago": days_ago,
        "market_freshness": freshness,
        "market_sources": m_sources,
        "market_notes": m_notes,
        "available_market_spread": available_market_spread,
        "suggested_commission": suggested_commission,
        "negotiation_buffer": negotiation_buffer,
        "minimum_sell_price": min_sell,
        "advertised_price_ncd55": adv_ncd55,
        "advertised_price_ncd0": adv_ncd0,
        "override_type": override_type,
        "is_manual_override": is_manual_override,
        
        # Scores & Badges
        "market_score": market_score,
        "demand_score": demand_score,
        "ad_score": ad_score,
        "pricing_status": pricing_status,
        
        # Public Sanitized Computed Fields
        "public_price_display": f"Anggaran OTR dari RM {adv_ncd55:,}*" if m_median > 0 or is_manual_override else "Hubungi untuk Harga OTR",
        "public_price_rm": adv_ncd55,
        "public_monthly_estimate": f"~RM {monthly:,} / bln" if monthly > 0 else "Bincang"
    }

def sanitize_for_public(admin_car: Dict[str, Any]) -> Dict[str, Any]:
    """Strips dealer body price, salesman commission, and commercial secrets before publishing."""
    has_pricing = (admin_car.get("market_median", 0) > 0 or admin_car.get("is_manual_override", False))
    adv_ncd55 = admin_car.get("advertised_price_ncd55", 0)
    adv_ncd0 = admin_car.get("advertised_price_ncd0", 0)
    
    if has_pricing and adv_ncd55 > 0:
        price_disp = f"Anggaran OTR dari RM {adv_ncd55:,}*"
        price_rm = adv_ncd55
        monthly_disp = admin_car.get("public_monthly_estimate", "~RM 2,000 / bln")
    else:
        price_disp = "Hubungi untuk Harga OTR"
        price_rm = 0
        monthly_disp = "Hubungi Sales Advisor"
        
    return {
        "stock_no": admin_car.get("stock_no"),
        "code": admin_car.get("code"),
        "brand": admin_car.get("brand"),
        "model": admin_car.get("model"),
        "category": admin_car.get("category"),
        "year": admin_car.get("year"),
        "color": admin_car.get("color"),
        "chassis": admin_car.get("chassis"),
        "mileage": admin_car.get("mileage"),
        "grade": admin_car.get("grade"),
        "specs": admin_car.get("specs"),
        "status": admin_car.get("status"),
        "source_label": admin_car.get("source_label"),
        "thumbnail": admin_car.get("thumbnail"),
        "images": admin_car.get("images", []),
        "image_count": admin_car.get("image_count", 0),
        "slug": admin_car.get("slug"),
        "detail_url": admin_car.get("detail_url"),
        
        # Public Commercial Fields (Safe)
        "price_display": price_disp,
        "price_rm": price_rm,
        "monthly_estimate": monthly_disp,
        "estimated_otr_ncd55": adv_ncd55 if has_pricing else None,
        "estimated_otr_ncd0": adv_ncd0 if has_pricing else None,
        "has_researched_pricing": has_pricing,
        "otr_disclaimer": "*Anggaran OTR berdasarkan NCD terpilih. Harga akhir tertakluk kepada sebut harga insurans rasmi & caj pendaftaran spesifik kenderaan."
    }

if __name__ == "__main__":
    print("Pricing Engine Module loaded successfully.")
