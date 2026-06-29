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

```