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
    
def register_supplier_in_erp(supplier_id, legal_name, category, annual_spend_usd):
    return {
        "provider": "ERPSystem",
        "supplier_id": supplier_id,
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
    
    
TOOL_DEFINITIONS = [
    {
        "name": "check_credit_score",
        "description": "Checks the credit score of a supplier based on their legal name and country.",
        "parameters": {
            "type": "object",
            "properties": {
                "legal_name": {"type": "string"},
                "country": {"type": "string"}
            },
            "required": ["legal_name", "country"]
        }
    },
    {
        "name": "screen_sanction_list",
        "description": "Screens a supplier against global sanction lists based on their legal name and country.",
        "parameters": {
            "type": "object",
            "properties": {
                "legal_name": {"type": "string"},
                "country": {"type": "string"}
            },
            "required": ["legal_name", "country"]
        }
    },
    {
        "name": "register_supplier_in_erp",
        "description": "Registers a supplier in the ERP system with their details.",
        "parameters": {
            "type": "object",
            "properties": {
                "supplier_id": {"type": "string"},
                "legal_name": {"type": "string"},
                "category": {"type": "string"},
                "annual_spend_usd": {"type": "number"}
            },
            "required": ["supplier_id", "legal_name", "category", "annual_spend_usd"]
        }
    },
    {
        "name": "calculate_risk_score",
        "description": "Calculates a risk score for a supplier based on credit score, sanction match, and annual spend.",
        "parameters": {
            "type": "object",
            "properties": {
                "credit_score": {"type": "number"},
                "sanction_match": {"type": "boolean"},
                "annual_spend_usd": {"type": "number"}
            },
            "required": ["credit_score", "sanction_match", "annual_spend_usd"]
        }
    }
]

def execute_tool(function_name, arguments):
    if function_name == "check_credit_score":
        return check_credit_score(**arguments)
    if function_name == "screen_sanction_list":
        return screen_sanction_list(**arguments)
    if function_name == "register_supplier_in_erp":
        return register_suppier_in_erp(**arguments)
    if function_name == "calculate_risk_score":
        return calculate_risk_score(**arguments)
    
    return {"error": f"Unknown tool function: {function_name}"}


def execute_tool_with_trace(function_name, arguments, feature="tool_calling"):
    log_trace(feature, "ToolAgent", "tool_call_started", "SUCCESS", f"Executing tool: {function_name} with arguments: {json.dumps(arguments)}")

    try:
        result = execute_tool(function_name, arguments)
        payload = json.dumps(result)
        log_trace(feature, "ToolAgent", "tool_call_completed", "SUCCESS", f"Tool {function_name} executed successfully. Result: {payload}")
        return result
    except Exception as e:
        log_trace(feature, "ToolAgent", "tool_call_failed", "ERROR", f"Tool {function_name} execution failed. Error: {str(e)}")
        return {"error": str(e)}