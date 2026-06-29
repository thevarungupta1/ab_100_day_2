from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
    
from src.trace_logger import log_trace
from src.workflow_engine import SupplierOnboardingWorkflow, SupplierRequest

def main():
    module = "01_workflow_automation"
    
    request = SupplierRequest(
        supplier_id="SUP123",
        legal_name="Acme Corp",
        country="USA",
        category="Electronics",
        annual_spend_usd=500000,
        contact_email="vendor@acme.com",
        notes="Strategic supplier for electronics components."
    )
    
    workflow = SupplierOnboardingWorkflow(request)
    
    log_trace(module, "WorkflowEngine", "Input received", "SUCCESS", request.legal_name)
    workflow.advance("Supplier intake from validated/")
    
    workflow.context.artifacts["kyc_status"] = "Documents uploaded"
    log_trace(module, "WorkflowEngine", "Due diligence", "SUCCESS", "KYC package complete")
    workflow.advance("Due diligence completed")
    
    workflow.context.artifacts["policy_check"] = "Policy check passed"
    log_trace(module, "WorkflowEngine", "Policy check", "SUCCESS", "Policy check passed")
    workflow.advance("Policy check completed")
    
    workflow.context.artifacts["risk_score"] = 80
    log_trace(module, "WorkflowEngine", "Risk scoring", "SUCCESS", "Risk score calculated")
    workflow.route_after_risk(risk_score=80, threshold=70)
    
    print("\n====Workflow automation done==========\n")
    print(workflow.summary())
    print("\nArtifacts")
    for key, value in workflow.context.artifacts.items():
        print(f"{key}: {value}")
        
        
        
    
    


if __name__ == "__main__":
    main()