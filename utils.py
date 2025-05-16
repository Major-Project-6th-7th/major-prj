"""
Utility functions for construction schedule optimization.
Extended with file conversion, carbon footprint calculation, and reporting.
"""
from typing import List, Dict, Any, Tuple, Optional
from datetime import datetime, timedelta
import sys
import os
import csv
import json
import re
from tabulate import tabulate
import matplotlib.pyplot as plt
from collections import defaultdict

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


def parse_txt_input(filepath: str) -> Tuple[List[Dict[str, Any]], List[str], Dict[str, List[str]], Dict[str, float], Dict[str, float]]:
    """Parse a simple text file format for tasks and resources."""
    tasks = []
    resources = []
    dependencies = {}
    resource_costs = {}
    resource_carbon = {}
    
    with open(filepath, 'r') as file:
        lines = file.readlines()
    
    section = None
    for line in lines:
        line = line.strip()
        if not line or line.startswith('#'):
            continue
            
        if line.upper() == "TASKS:":
            section = "tasks"
            continue
        elif line.upper() == "RESOURCES:":
            section = "resources"
            continue
        elif line.upper() == "DEPENDENCIES:":
            section = "dependencies"
            continue
            
        if section == "tasks":
            # Format: Task Name, Duration, Required Resources (comma-separated)
            parts = line.split('|')
            if len(parts) >= 3:
                task_name = parts[0].strip()
                duration = int(parts[1].strip())
                required_resources = [r.strip() for r in parts[2].split(',')]
                
                # Create task dict in the format expected by scheduler
                task_resources = {res: 1 for res in required_resources}
                
                tasks.append({
                    "id": task_name,
                    "name": task_name,
                    "duration": duration,
                    "resources": task_resources
                })
        
        elif section == "resources":
            # Format: Resource Name | Cost per day | Carbon footprint per day
            parts = line.split('|')
            if len(parts) >= 3:
                resource_name = parts[0].strip()
                cost = float(parts[1].strip())
                carbon = float(parts[2].strip())
                
                resources.append(resource_name)
                resource_costs[resource_name] = cost
                resource_carbon[resource_name] = carbon
        
        elif section == "dependencies":
            # Format: Task | Depends on (comma-separated)
            parts = line.split('|')
            if len(parts) >= 2:
                task = parts[0].strip()
                depends_on = [d.strip() for d in parts[1].split(',')]
                dependencies[task] = depends_on
                
                # Also update the task object with dependencies
                for i, task_obj in enumerate(tasks):
                    if task_obj['id'] == task:
                        tasks[i]['dependencies'] = depends_on
                        break
    
    return tasks, resources, dependencies, resource_costs, resource_carbon


def convert_to_csv(tasks: List[Dict[str, Any]], resources: List[str], 
                  dependencies: Dict[str, List[str]], resource_costs: Dict[str, float],
                  resource_carbon: Dict[str, float], output_dir: str) -> Tuple[str, str, str]:
    """Convert the parsed data to CSV files."""
    os.makedirs(output_dir, exist_ok=True)
    
    # Tasks CSV
    with open(os.path.join(output_dir, 'tasks.csv'), 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Task ID', 'Task Name', 'Duration', 'Required Resources'])
        for task in tasks:
            writer.writerow([
                task['id'], 
                task['name'],
                task['duration'], 
                ','.join(task['resources'].keys())
            ])
    
    # Resources CSV
    with open(os.path.join(output_dir, 'resources.csv'), 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Resource Name', 'Cost per Day', 'Carbon Footprint per Day'])
        for resource in resources:
            writer.writerow([
                resource, 
                resource_costs[resource],
                resource_carbon[resource]
            ])
    
    # Dependencies CSV
    with open(os.path.join(output_dir, 'dependencies.csv'), 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Task', 'Depends On'])
        for task, depends_on in dependencies.items():
            writer.writerow([task, ','.join(depends_on)])
            
    return os.path.join(output_dir, 'tasks.csv'), os.path.join(output_dir, 'resources.csv'), os.path.join(output_dir, 'dependencies.csv')


def convert_to_json(tasks: List[Dict[str, Any]], resources: List[str], 
                   dependencies: Dict[str, List[str]], resource_costs: Dict[str, float],
                   resource_carbon: Dict[str, float], output_dir: str) -> Tuple[str, str, str]:
    """Convert the parsed data to JSON files."""
    os.makedirs(output_dir, exist_ok=True)
    
    # Tasks JSON - slightly reformat for better readability
    tasks_json = []
    for task in tasks:
        tasks_json.append({
            "id": task["id"],
            "name": task["name"],
            "duration": task["duration"],
            "resources": list(task["resources"].keys()),
            "dependencies": task.get("dependencies", [])
        })
    
    with open(os.path.join(output_dir, 'tasks.json'), 'w') as file:
        json.dump(tasks_json, file, indent=2)
    
    # Resources JSON
    resources_data = [{"name": res, "cost": resource_costs[res], "carbon": resource_carbon[res]} 
                     for res in resources]
    with open(os.path.join(output_dir, 'resources.json'), 'w') as file:
        json.dump(resources_data, file, indent=2)
    
    # Dependencies JSON
    with open(os.path.join(output_dir, 'dependencies.json'), 'w') as file:
        json.dump(dependencies, file, indent=2)
        
    return os.path.join(output_dir, 'tasks.json'), os.path.join(output_dir, 'resources.json'), os.path.join(output_dir, 'dependencies.json')


def calculate_carbon_footprint(schedule: Dict[str, Dict[str, Any]], resource_carbon: Dict[str, float]) -> float:
    """
    Calculate total carbon footprint based on resource usage using actual resource carbon values.
    """
    total_co2 = 0.0
    
    for task_info in schedule["schedule"]:
        total_co2 += task_info["carbon"]
    
    return total_co2


def calculate_total_cost(schedule: Dict[str, Dict[str, Any]]) -> float:
    """Calculate total project cost based on resource usage."""
    return schedule["total_cost"]


def format_schedule_output(schedule: Dict[str, Any]) -> str:
    """Format the optimized schedule for human-readable output."""
    sorted_tasks = sorted(
        schedule["schedule"],
        key=lambda x: (x["start"], x["task"])
    )
    
    headers = ["Task ID", "Start Day", "End Day", "Duration", "Resources", "Cost", "Carbon"]
    rows = []
    
    for task_info in sorted_tasks:
        rows.append([
            task_info["task"],
            str(task_info["start"]),
            str(task_info["end"]),
            str(task_info["duration"]),
            ", ".join(task_info["resources"]),
            f"${task_info['cost']:.2f}",
            f"{task_info['carbon']:.2f}"
        ])
    
    # Use tabulate for better formatting
    return tabulate(rows, headers=headers, tablefmt="simple")


def generate_report(optimization_result: Dict[str, Any], mode: str, output_file: str) -> str:
    """Generate a comprehensive report of the optimization results."""
    if not optimization_result["schedule"]:
        raise ValueError("No optimization results available.")
    
    with open(output_file, 'w') as f:
        # Header
        f.write("=" * 80 + "\n")
        f.write(f"CONSTRUCTION SCHEDULE OPTIMIZATION REPORT - {mode.upper()} MODE\n")
        f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 80 + "\n\n")
        
        # Summary
        f.write("SUMMARY\n")
        f.write("-" * 80 + "\n")
        f.write(f"Total project duration: {optimization_result['total_duration']} days\n")
        f.write(f"Total project cost: ${optimization_result['total_cost']:.2f}\n")
        f.write(f"Total carbon footprint: {optimization_result['carbon_footprint']:.2f} units\n")
        f.write("\n")
        
        # Mode description
        mode_descriptions = {
            "eco": "ECO MODE: Optimized for minimal environmental impact and budget constraints.",
            "standard": "STANDARD MODE: Balanced optimization between time, cost, and environmental impact.",
            "performance": "PERFORMANCE MODE: Optimized for minimal project duration, may exceed budget."
        }
        f.write(f"{mode_descriptions[mode]}\n\n")
        
        # Schedule
        f.write("TASK SCHEDULE\n")
        f.write("-" * 80 + "\n")
        f.write(format_schedule_output(optimization_result) + "\n\n")
        
        # Resource Utilization
        f.write("RESOURCE UTILIZATION\n")
        f.write("-" * 80 + "\n")
        util_data = []
        for res, util in optimization_result["resource_utilization"].items():
            util_data.append([res, f"{util:.2f}%"])
        
        util_headers = ["Resource", "Utilization"]
        f.write(tabulate(util_data, headers=util_headers, tablefmt="simple") + "\n\n")
        
        # Critical Path
        f.write("CRITICAL PATH\n")
        f.write("-" * 80 + "\n")
        # Identifying critical path (tasks with zero slack)
        critical_path = []
        
        # For simplicity, we'll use a heuristic - any task that if delayed would delay the project
        for i, task in enumerate(optimization_result["schedule"]):
            is_critical = True
            for next_task in optimization_result["schedule"][i+1:]:
                # Check if task is a dependency for any future task
                if task["end"] < next_task["start"]:
                    is_critical = False
                    break
            if is_critical:
                critical_path.append(task["task"])
        
        f.write("The following tasks are on the critical path and should be carefully monitored:\n")
        for task in critical_path:
            f.write(f"- {task}\n")
        f.write("\n")
        
        # Recommendations
        f.write("RECOMMENDATIONS\n")
        f.write("-" * 80 + "\n")
        
        # Mode-specific recommendations
        if mode == "eco":
            f.write("1. Consider extending project timeline for further cost and carbon reductions.\n")
            f.write("2. Investigate more sustainable resource alternatives.\n")
            f.write("3. Monitor resource usage carefully to maintain eco-friendly targets.\n")
        elif mode == "standard":
            f.write("1. Balance resource allocation to maintain consistent progress.\n")
            f.write("2. Consider shifting non-critical tasks to optimize resource utilization.\n")
            f.write("3. Regular monitoring of progress against timeline is recommended.\n")
        elif mode == "performance":
            f.write("1. Allocate additional budget for potential cost overruns.\n")
            f.write("2. Consider adding backup resources for critical path tasks.\n")
            f.write("3. Implement intensive progress tracking to maintain accelerated schedule.\n")
        
        f.write("\n")
        f.write("=" * 80 + "\n")
        f.write("END OF REPORT\n")
        
    return output_file


def generate_charts(optimization_result: Dict[str, Any], output_dir: str) -> Tuple[str, str]:
    """Generate visualization charts for the schedule."""
    os.makedirs(output_dir, exist_ok=True)
    
    # Gantt Chart
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Sort tasks by start time for better visualization
    sorted_schedule = sorted(optimization_result["schedule"], key=lambda x: x["start"])
    
    y_ticks = []
    y_labels = []
    
    for i, task in enumerate(sorted_schedule):
        start = task["start"]
        duration = task["duration"]
        
        # Color based on mode
        color_map = {
            "eco": "green",
            "standard": "blue",
            "performance": "red"
        }
        color = color_map.get(optimization_result["mode"], "blue")
        
        ax.barh(i, duration, left=start, height=0.5, align='center', 
                color=color, alpha=0.8, label=task["task"])
        
        # Add task name inside the bar if there's enough space
        if duration > 3:  # Only add text if bar is wide enough
            ax.text(start + duration/2, i, task["task"], 
                    ha='center', va='center', color='white', fontweight='bold')
        else:
            # Otherwise add it to the right of the bar
            ax.text(start + duration + 0.1, i, task["task"], 
                    ha='left', va='center')
        
        y_ticks.append(i)
        y_labels.append(f"{task['task']}")
    
    ax.set_yticks(y_ticks)
    ax.set_yticklabels(y_labels)
    ax.set_xlabel('Days')
    ax.set_title(f'Project Schedule - {optimization_result["mode"].upper()} Mode')
    ax.grid(axis='x', linestyle='--', alpha=0.7)
    
    # Add project duration line
    plt.axvline(x=optimization_result["total_duration"], color='red', linestyle='--', 
                label=f'Project End: Day {optimization_result["total_duration"]}')
    
    plt.tight_layout()
    gantt_file = os.path.join(output_dir, 'gantt_chart.png')
    plt.savefig(gantt_file)
    plt.close()
    
    # Resource Utilization Chart
    fig, ax = plt.subplots(figsize=(10, 6))
    resources = list(optimization_result["resource_utilization"].keys())
    utilization = [optimization_result["resource_utilization"][r] for r in resources]
    
    # Color based on utilization level
    colors = ['#FF9999' if u > 75 else '#99FF99' if u < 50 else '#9999FF' for u in utilization]
    
    ax.bar(resources, utilization, color=colors)
    ax.set_ylabel('Utilization (%)')
    ax.set_title('Resource Utilization')
    ax.grid(axis='y', linestyle='--', alpha=0.7)
    
    # Add threshold lines
    ax.axhline(y=75, color='red', linestyle='--', alpha=0.5, label='Over-utilized (>75%)')
    ax.axhline(y=50, color='green', linestyle='--', alpha=0.5, label='Under-utilized (<50%)')
    
    ax.set_ylim(0, 100)
    plt.xticks(rotation=45, ha='right')
    plt.legend()
    plt.tight_layout()
    
    util_file = os.path.join(output_dir, 'resource_utilization.png')
    plt.savefig(util_file)
    plt.close()
    
    return gantt_file, util_file
