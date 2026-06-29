import csv
import os
from datetime import datetime

TRACE_FILE = "reports/execution_trace.csv"

def log_trace(module, agent, step, status, details):
    os.makedirs("reports", exist_ok=True)
    
    file_exists = os.path.exists(TRACE_FILE)
    
    with open(TRACE_FILE, "a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        
        if not file_exists:
            writer.writerow([
                "timestamp", 
                "module", 
                "agent", 
                "step", 
                "status", 
                "details"
            ])
            
        writer.writerow([
            datetime.now(),
            module,
            agent,
            step,
            status,
            details
        ])