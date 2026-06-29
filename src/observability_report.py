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


