#



# Exercise 1: Create Workflow 
Deterministic suppier onboarding state machine

`src/workflow_engine.py`

```python
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

class WorkflowStatus(str, Enum):
    INTAKE = "INTAKE"
    DUE_DILIGENCE = "DUE_DILIGENCE"
    POLICY_CHECK = "POLICY_CHECK"
    RISK_SCORING = "RISK_SCORING"
    HUMAN_REVIEW = "HUMAN_REVIEW"
    ERP_REGISTRATION = "ERP_REGISTRATION"
    COMPLETED = "COMPLETED"
    REJECTED = "REJECTED"
    
@dataclass
class SupplierRequest:
    supplier_id: str
    legal_name: str
    country: str
    category: str
    annual_spend_usd: float
    contact_email: str
    notes: str = ""
    
@dataclass
class WorkflowContext:
    request: SupplierRequest
    state: WorkflowStatus = WorkflowStatus.INTAKE
    artifacts: dict[str, Any] = field(default_factory=dict)
    history: list[dict[str, str]] = field(default_factory=list)

    def transition(self, new_state: WorkflowStatus, detail: str = ""):
        self.history.append({
            "from": self.state, "to": new_state, "detail": detail})
        self.state = new_state


class SupplierOnboardingWorkflow:
    TRANSITIONS = {
        WorkflowState.INTAKE: WorkflowState.DUE_DILIGENCE,
        WorkflowState.DUE_DILIGENCE: WorkflowState.POLICY_CHECK,
        WorkflowState.POLICY_CHECK: WorkflowState.RISK_SCORING,
    }

    def __init__(self, request: SupplierRequest):
        self.context = WorkflowContext(request=request)
        
    def advance(self, detail: str = ""):
        current = self.context.state
        next_state = self.TRANSITIONS.get(current)
        if not next_state:
            raise ValueError(f"No automatic transition from {current.value}")
        self.context.transition(
            next_state, 
            detail or f"Move from {current.value} to {next_state.value}"
        )
        return self.context
    
    def route_after_risk(self, risk_score: int, threshold: int):
        if risk_score >= threshold:
            self.context.transition(
                WorkflowState.HUMAN_REVIEW,
                f"Risk score {risk_score} exceeds threshold {threshold}, routing to human review"
        else:
            self.context.transition(
                WorkflowState.ERP_REGISTRATION,
                f"risk score {risk_score} within auto-approval limit",
            )    
            return self.context

    def complete(self, approval: bool, detail: str):
        target = WorkflowState.COMPLETED if approved else WorkflowState.REJECTED
        self.context.transition(target, detail)
        return self.context
        
    def summary(self):
        lines = [
            f"Supplier: {self.context.request.legal_name} ({self.context.request.supplier_id})",
            f"Current State: {self.context.state.value}",
            f"Transition History:"
        ]
        for item in self.context.history:
            lines.append(f"  - {item['from']} -> {item['to']}: {item['detail']}")
        return "\n".join(lines)

```

### Step : create Enterprise Tools
Mock enterprise APIs and tools schemas:
- Credit bureau API
- Sanction screening API
- ERP registration API
- Risk score calculator

`src/enterprise_tools.py`

```python
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
```

### Step: create Approval Store
SQLite-backed approval queue for hum-in-the-loop decision.

`src/approval_store.py`

```python
import sqlite3
from datetime import datetime

DB_PATH = "approvals.db"

def init_db():
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()
    cursor.execute("""
         CREATE TABLE IF NOT EXISTS approval_queue (                   
             id INTEGER PRIMARY KEY AUTOINCREMENT,
             supplier_id TEXT,
             legal_name TEXT,
             risk_score INTEGER,
             reason TEXT,
             status TEXT,
             reviewer TEXT,
             created_at TEXT,
             resolved_at TEXT
         )
    """)
    connection.commit()
    connection.close()
    
def submit_for_approval(supplier_id, legal_name. risk_score, reason):
    init_db()
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()
    cursor.execute("""
        INSERT INTO approval_queue (supplier_id, legal_name, risk_score, reason, status, created_at)
        VALUES (?, ?, ?, ?, 'PENDING', ?)
    """, (supplier_id, legal_name, risk_score, reason, datetime.now().isoformat()))
    connection.commit()
    connection.close()
    return approval_id

def get_pending_approvals():
    init_db()
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()
    cursor.execute("""
        SELECT id, supplier_id, legal_name, risk_score, reason, created_at 
        FROM approval_queue WHERE status = 'PENDING' ORDER BY created_at ASC
    """)
    pending_approvals = cursor.fetchall()
    connection.close()
    return pending_approvals

def resolve_approval(approval_id, approved, reviewer="procurement_manager"):
    init_db()
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()
    new_status = "APPROVED" if approved else "REJECTED"
    cursor.execute("""
        UPDATE approval_queue
        SET status = ?, reviewer = ?, resolved_at = ?
        WHERE id = ?
    """, (new_status, reviewer, datetime.now().isoformat(), approval_id))
    connection.commit()
    connection.close()
```

### Step : Create Observability Report Utlity
Aggegates traces and metric files into an architecture-friendly report

`src/observability_report.py`

```python
import csv
import os
from datetime import datetime

from src.trace_logger import METRICS_FILE, TRACE_FILE

def _read_csv(path):
    if not os.path.exists(path):
        return []

    with open(path, new_line="", encoding="utf-8") as file:
        return list(csv.DictReader(file))

def generate_observability_report(module_filter=None):
    traces = _read_csv(TRACE_FILE)
    metrics = _read_csv(METRICS_FILE)

    if module_filter:
        traces = [row from row in traces if row.get("module") == module_filter]
        metrics = [row from row in metrics if row.get("module") == module_filter]

    total_steps = len(traces)
    failed_steps = len([row for row in traces if now.get("status") == "FAILED"])
    success_rate = round(((total_steps - failed_steps) / total_steps) * 100, 2)
    if total_steps else 100.0

    tool_calls = len([row for row in metrics if row.get("metric_name") == "tool_calls_total"])

    return {
        "generated_at": datetime.now(),
        "module_filter": module_filter or "all"m
        "total_trace_event": total_steps,
        "failed_event": failed_stepsm
        "success_rate_percent": success_rate,
        "tool_calls_total": tool_calls,
        "metric_sample": len(metrics)
    }

def print_observability_report(module_filter=None):
    report = generate_observability_report(module_filter)

    print("\n=========AI Observability Report =============\n")
    for key, value in report.items():
        print(f"{key}: {value}")

    traces = _read_csv(TRACE_FILE)
    if module_filter:
        traces = [row for row in traces if row.get("module") == module_filter]

    print("\nRecent Trace Events:")
    for row in traces[-8:]:
        print(
            f" [{row.get('status')}] {row.get('module')} |" 
            f"{row.get('agent')} | {row.get('step')}"
        )

    return report
```

### Step: create Data files
Policy corpus in `data/`:
- `procurement_policy.txt` - onboarding rules and auto-approval criteria
- `anti_bribery_policy.txt` - third party risk and human accountability
- `supplier_data_classification.txt` - confidential data handling and residency
- `onboarding_sla.txt` - workflow stages and SLA targets


### Step: Create Prompt Files
- `workflow_orchestrator.txt` - workflow coordination guidance
