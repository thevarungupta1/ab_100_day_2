import csv
import os
from datetime import datetime

COST_FILE = "reports/cost_report.csv"

MODEL_PRICING = {
    "gpt-4o-mini": {
        "input": 0.00015 / 1000,
        "output": 0.00060 / 1000
    },
    "gpt-4o": {
        "input": 0.005 / 1000,
        "output": 0.015 / 1000
    },
}

def log_cost(feature, model, input_tokens, output_tokens):
    os.makedirs("reports", exist_ok=True)
    
    pricing = MODEL_PRICING.get(model, MODEL_PRICING["gpt-4o-mini"])
    
    estimated_cost = (
        input_tokens * pricing["input"] +
        output_tokens * pricing["output"]
    )

    file_exists = os.path.exists(COST_FILE)
    
    with open(COST_FILE, "a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        
        if not file_exists:
            writer.writerow([
                "timestamp", 
                "feature", 
                "model", 
                "input_tokens", 
                "output_tokens", 
                "estimated_cost"
        ])
            
        writer.writerow([
            datetime.now(),
            feature,
            model,
            input_tokens,
            output_tokens,
            round(estimated_cost, 6)
        ])