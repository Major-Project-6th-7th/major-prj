"""
Utility functions for construction schedule optimization.
"""
from typing import List, Dict, Any
from datetime import datetime, timedelta
import sys

def validate_input_data(tasks: List[Dict[str, Any]]) -> None:
    """Validate input task data structure."""
    if not tasks:
        raise ValueError("No tasks provided in input data")
    
    required_fields = {'id', 'duration'}
    for task in tasks:
        if not all(field in task for field in required_fields):
            raise ValueError(f"Task {task.get('id', 'unnamed')} missing required fields")
        
        try:
            int(task['duration'])
        except (ValueError, TypeError):
            raise ValueError(f"Invalid duration for task {task['id']}")
        
        if 'resources' in task and not isinstance(task['resources'], dict):
            raise ValueError(f"Resources for task {task['id']} should be a dictionary")

def calculate_carbon_footprint(schedule: Dict[str, Dict[str, Any]]) -> float:
    """
    Calculate total carbon footprint based on resource usage.
    Simple model: workers = 5kg CO₂/day, cranes = 50kg CO₂/day, other = 10kg CO₂/day
    """
    total_co2 = 0.0
    
    for task_id, task_info in schedule.items():
        duration = task_info['duration']
        resources = task_info.get('resources', {})
        
        for res_type, quantity in resources.items():
            quantity = int(quantity)
            if 'worker' in res_type.lower():
                total_co2 += quantity * 5 * duration
            elif 'crane' in res_type.lower():
                total_co2 += quantity * 50 * duration
            else:
                total_co2 += quantity * 10 * duration
    
    return total_co2

def calculate_total_cost(schedule: Dict[str, Dict[str, Any]]) -> float:
    """Calculate total project cost based on resource usage."""
    total_cost = 0.0
    
    for task_id, task_info in schedule.items():
        duration = task_info['duration']
        resources = task_info.get('resources', {})
        
        for res_type, quantity in resources.items():
            quantity = int(quantity)
            # Same cost model as in scheduler
            cost_per_unit = 1000 if 'crane' in res_type.lower() else 100
            total_cost += quantity * cost_per_unit * duration
    
    return total_cost

def format_schedule_output(schedule: Dict[str, Dict[str, Any]]) -> str:
    """Format the optimized schedule for human-readable output."""
    sorted_tasks = sorted(
        schedule.items(),
        key=lambda x: (x[1]['start'], x[0])
    )
    
    headers = ["Task ID", "Start Day", "Duration", "Resources"]
    rows = []
    
    for task_id, task_info in sorted_tasks:
        rows.append([
            task_id,
            str(task_info['start']),
            str(task_info['duration']),
            ", ".join(f"{k}:{v}" for k, v in task_info.get('resources', {}).items())
        ])
    
    # Simple table formatting
    col_widths = [max(len(str(x)) for x in col] for col in zip(headers, *rows)]
    header_line = " | ".join(h.ljust(w) for h, w in zip(headers, col_widths))
    separator = "-+-".join("-" * w for w in col_widths)
    row_lines = [
        " | ".join(str(cell).ljust(w) for cell, w in zip(row, col_widths))
        for row in rows
    ]
    
    return "\n".join([header_line, separator] + row_lines)