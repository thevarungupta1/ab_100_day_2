import json
from datatime import datetime

from src.trace_logger import log_trace

def check_credit_score(legal_name, country):
    base_score = 55
    if "global" in legal_name.lower():
        base_score += 20
    if country.upper() in ["US", "CA", "UK"]:
        base_score += 10
        
    return {
        "provider": "CreditCheckAPI",
        "legal_name": legal_name,
        "country": country,
        "credit_score": min(max(base_score, 10), 95),
        "payment_behavior": "Stable" if base_score > 60 else "Watchlist",
        "checked_at": datetime.utcnow().isoformat()
    }

def screen_sanction_list(legal_name, country):
    flagged_keywords = ["shadow", "restricted", "sanction"]
    is_flagged = any(keyword in legal_name.lower() for keyword in flagged_keywords)
    
    return {
        "provider": "SanctionScreenAPI",
        "legal_name": legal_name,
        "country": country,
        "match_found": is_flagged,
        "risk_level": "High" if is_flagged else "Low",
        "list_checked": ["OFAC", "UN Sanctions List", "EU Sanctions List"],
        "checked_at": datetime.utcnow().isoformat()
    }
    
def register_suppier_in_erp(suppier_id, legal_name, category, annual_spend_usd):
    return {
        "provider": "ERPSystem",
        "supplier_id": suppier_id,
        "legal_name": legal_name,
        "category": category,
        "annual_spend_usd": annual_spend_usd,
        "erp_vendor_code": f"VND-{suppier_id[-4:]}",
        "status": "REGISTERED",
        "registered_at": datetime.utcnow().isoformat()
    }

def calculate_risk_score(credit_score, sanction_match, spend_usd):
    score = 100 - credit_score
    if sanction_match:
        score += 40
    if spend_usd > 500000:
        score += 20
        
    score = min(max(score, 5), 100)
    return {
        "risk_score": score,
        "risk_band": "HIGH" if score >=65 else "MEDIUM" if score >=40 else "LOW",
        "factors": {
            "credit_score": credit_score,
            "sanction_match": sanction_match,
            "annual_spend_usd": spend_usd
        },
    }