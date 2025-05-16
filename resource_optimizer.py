#!/usr/bin/env python3
import argparse
import csv
import json
import os
import sys
import re
from datetime import datetime
from pathlib import Path
import pandas as pd
import numpy as np
from itertools import product
from collections import defaultdict
import matplotlib.pyplot as plt
from tabulate import tabulate

class ResourceOptimizer:
    def __init__(self, mode="standard"):
        self.tasks = []
        self.resources = []
        self.dependencies = {}
        self.resource_costs = {}
        self.resource_carbon = {}
        self.mode = mode
        self.results = {
            "schedule": [],
            "total_cost": 0,
            "total_duration": 0,
            "carbon_footprint": 0,
            "resource_utilization": {}
        }
    
    def parse_txt_input(self, filepath):
        """Parse a simple text file format for tasks and resources"""
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
                    
                    self.tasks.append({
                        "name": task_name,
                        "duration": duration,
                        "required_resources": required_resources
                    })
            
            elif section == "resources":
                # Format: Resource Name, Cost per day, Carbon footprint per day
                parts = line.split('|')
                if len(parts) >= 3:
                    resource_name = parts[0].strip()
                    cost = float(parts[1].strip())
                    carbon = float(parts[2].strip())
                    
                    self.resources.append(resource_name)
                    self.resource_costs[resource_name] = cost
                    self.resource_carbon[resource_name] = carbon
            
            elif section == "dependencies":
                # Format: Task, Depends on (comma-separated)
                parts = line.split('|')
                if len(parts) >= 2:
                    task = parts[0].strip()
                    depends_on = [d.strip() for d in parts[1].split(',')]
                    self.dependencies[task] = depends_on

    def convert_to_csv(self, output_dir):
        """Convert the parsed data to CSV files"""
        os.makedirs(output_dir, exist_ok=True)
        
        # Tasks CSV
        with open(os.path.join(output_dir, 'tasks.csv'), 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Task Name', 'Duration', 'Required Resources'])
            for task in self.tasks:
                writer.writerow([
                    task['name'], 
                    task['duration'], 
                    ','.join(task['required_resources'])
                ])
        
        # Resources CSV
        with open(os.path.join(output_dir, 'resources.csv'), 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Resource Name', 'Cost per Day', 'Carbon Footprint per Day'])
            for resource in self.resources:
                writer.writerow([
                    resource, 
                    self.resource_costs[resource],
                    self.resource_carbon[resource]
                ])
        
        # Dependencies CSV
        with open(os.path.join(output_dir, 'dependencies.csv'), 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Task', 'Depends On'])
            for task, depends_on in self.dependencies.items():
                writer.writerow([task, ','.join(depends_on)])
                
        return os.path.join(output_dir, 'tasks.csv'), os.path.join(output_dir, 'resources.csv'), os.path.join(output_dir, 'dependencies.csv')

    def convert_to_json(self, output_dir):
        """Convert the parsed data to JSON files"""
        os.makedirs(output_dir, exist_ok=True)
        
        # Tasks JSON
        with open(os.path.join(output_dir, 'tasks.json'), 'w') as file:
            json.dump(self.tasks, file, indent=2)
        
        # Resources JSON
        resources_data = [{"name": res, "cost": self.resource_costs[res], "carbon": self.resource_carbon[res]} 
                         for res in self.resources]
        with open(os.path.join(output_dir, 'resources.json'), 'w') as file:
            json.dump(resources_data, file, indent=2)
        
        # Dependencies JSON
        with open(os.path.join(output_dir, 'dependencies.json'), 'w') as file:
            json.dump(self.dependencies, file, indent=2)
            
        return os.path.join(output_dir, 'tasks.json'), os.path.join(output_dir, 'resources.json'), os.path.join(output_dir, 'dependencies.json')

    def optimize_schedule(self):
        """Optimize the construction schedule based on the selected mode"""
        # Create a topological ordering of tasks based on dependencies
        visited = set()
        temp_visited = set()
        order = []
        
        def visit(task_name):
            if task_name in temp_visited:
                raise ValueError(f"Circular dependency detected involving {task_name}")
            if task_name not in visited:
                temp_visited.add(task_name)
                for dependent in self.dependencies.get(task_name, []):
                    visit(dependent)
                temp_visited.remove(task_name)
                visited.add(task_name)
                order.append(task_name)
        
        for task in self.tasks:
            if task["name"] not in visited:
                visit(task["name"])
                
        order.reverse()  # Reverse to get the correct order
        
        # Create a schedule based on mode
        task_dict = {task["name"]: task for task in self.tasks}
        earliest_start = {task_name: 0 for task_name in order}
        
        # Calculate earliest start times based on dependencies
        for task_name in order:
            for dep in self.dependencies.get(task_name, []):
                earliest_start[task_name] = max(
                    earliest_start[task_name],
                    earliest_start[dep] + task_dict[dep]["duration"]
                )
        
        # Apply mode-specific optimizations
        schedule = []
        resource_utilization = defaultdict(list)
        total_cost = 0
        total_carbon = 0
        
        # Track resource usage over time
        max_end_time = max(earliest_start[task] + task_dict[task]["duration"] for task in order)
        resource_timeline = {res: [0] * (max_end_time + 1) for res in self.resources}
        
        # Mode-specific adjustments
        adjustment_factors = {
            "eco": {"duration": 1.1, "cost": 0.9, "carbon": 0.7},
            "standard": {"duration": 1.0, "cost": 1.0, "carbon": 1.0},
            "performance": {"duration": 0.8, "cost": 1.2, "carbon": 1.5}
        }
        
        factor = adjustment_factors[self.mode]
        
        # Apply the schedule with adjustments
        for task_name in order:
            task = task_dict[task_name]
            start_time = earliest_start[task_name]
            
            # Adjust duration based on mode
            adjusted_duration = max(1, int(task["duration"] * factor["duration"]))
            end_time = start_time + adjusted_duration
            
            # Calculate resources and costs
            task_resources = task["required_resources"]
            task_cost = sum(self.resource_costs[res] * factor["cost"] * adjusted_duration for res in task_resources)
            task_carbon = sum(self.resource_carbon[res] * factor["carbon"] * adjusted_duration for res in task_resources)
            
            # Update resource timeline
            for res in task_resources:
                for t in range(start_time, end_time):
                    if t < len(resource_timeline[res]):
                        resource_timeline[res][t] += 1
            
            schedule.append({
                "task": task_name,
                "start": start_time,
                "end": end_time,
                "duration": adjusted_duration,
                "resources": task_resources,
                "cost": task_cost,
                "carbon": task_carbon
            })
            
            total_cost += task_cost
            total_carbon += task_carbon
        
        # Calculate resource utilization percentages
        for res in self.resources:
            active_periods = sum(1 for usage in resource_timeline[res] if usage > 0)
            if max_end_time > 0:
                utilization = (active_periods / max_end_time) * 100
            else:
                utilization = 0
            resource_utilization[res] = utilization
        
        # Sort schedule by start time
        schedule.sort(key=lambda x: x["start"])
        
        # Store results
        self.results = {
            "schedule": schedule,
            "total_cost": total_cost,
            "total_duration": max(task["end"] for task in schedule) if schedule else 0,
            "carbon_footprint": total_carbon,
            "resource_utilization": resource_utilization,
            "mode": self.mode
        }
        
        return self.results

    def generate_report(self, output_file):
        """Generate a comprehensive report of the optimization results"""
        if not self.results["schedule"]:
            raise ValueError("No optimization results available. Run optimize_schedule() first.")
        
        with open(output_file, 'w') as f:
            # Header
            f.write("=" * 80 + "\n")
            f.write(f"CONSTRUCTION SCHEDULE OPTIMIZATION REPORT - {self.mode.upper()} MODE\n")
            f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 80 + "\n\n")
            
            # Summary
            f.write("SUMMARY\n")
            f.write("-" * 80 + "\n")
            f.write(f"Total project duration: {self.results['total_duration']} days\n")
            f.write(f"Total project cost: ${self.results['total_cost']:.2f}\n")
            f.write(f"Total carbon footprint: {self.results['carbon_footprint']:.2f} units\n")
            f.write("\n")
            
            # Mode description
            mode_descriptions = {
                "eco": "ECO MODE: Optimized for minimal environmental impact and budget constraints.",
                "standard": "STANDARD MODE: Balanced optimization between time, cost, and environmental impact.",
                "performance": "PERFORMANCE MODE: Optimized for minimal project duration, may exceed budget."
            }
            f.write(f"{mode_descriptions[self.mode]}\n\n")
            
            # Schedule
            f.write("TASK SCHEDULE\n")
            f.write("-" * 80 + "\n")
            schedule_data = []
            for item in self.results["schedule"]:
                schedule_data.append([
                    item["task"],
                    item["start"],
                    item["end"],
                    item["duration"],
                    ", ".join(item["resources"]),
                    f"${item['cost']:.2f}",
                    f"{item['carbon']:.2f}"
                ])
            
            headers = ["Task", "Start Day", "End Day", "Duration", "Resources", "Cost", "Carbon"]
            f.write(tabulate(schedule_data, headers=headers, tablefmt="simple") + "\n\n")
            
            # Resource Utilization
            f.write("RESOURCE UTILIZATION\n")
            f.write("-" * 80 + "\n")
            util_data = []
            for res, util in self.results["resource_utilization"].items():
                util_data.append([res, f"{util:.2f}%", f"${self.resource_costs[res]:.2f}", f"{self.resource_carbon[res]:.2f}"])
            
            util_headers = ["Resource", "Utilization", "Cost per Day", "Carbon per Day"]
            f.write(tabulate(util_data, headers=util_headers, tablefmt="simple") + "\n\n")
            
            # Critical Path
            f.write("CRITICAL PATH\n")
            f.write("-" * 80 + "\n")
            # Identifying critical path (tasks with zero slack)
            critical_path = []
            
            # For simplicity, we'll use a heuristic - any task that if delayed would delay the project
            for i, task in enumerate(self.results["schedule"]):
                is_critical = True
                for next_task in self.results["schedule"][i+1:]:
                    if all(dep != task["task"] for dep in self.dependencies.get(next_task["task"], [])):
                        continue
                    if next_task["start"] > task["end"]:
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
            if self.mode == "eco":
                f.write("1. Consider extending project timeline for further cost and carbon reductions.\n")
                f.write("2. Investigate more sustainable resource alternatives.\n")
                f.write("3. Monitor resource usage carefully to maintain eco-friendly targets.\n")
            elif self.mode == "standard":
                f.write("1. Balance resource allocation to maintain consistent progress.\n")
                f.write("2. Consider shifting non-critical tasks to optimize resource utilization.\n")
                f.write("3. Regular monitoring of progress against timeline is recommended.\n")
            elif self.mode == "performance":
                f.write("1. Allocate additional budget for potential cost overruns.\n")
                f.write("2. Consider adding backup resources for critical path tasks.\n")
                f.write("3. Implement intensive progress tracking to maintain accelerated schedule.\n")
            
            f.write("\n")
            f.write("=" * 80 + "\n")
            f.write("END OF REPORT\n")
            
        return output_file

    def generate_charts(self, output_dir):
        """Generate visualization charts for the schedule"""
        os.makedirs(output_dir, exist_ok=True)
        
        # Gantt Chart
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Sort tasks by start time for better visualization
        sorted_schedule = sorted(self.results["schedule"], key=lambda x: x["start"])
        
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
            color = color_map.get(self.mode, "blue")
            
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
        ax.set_title(f'Project Schedule - {self.mode.upper()} Mode')
        ax.grid(axis='x', linestyle='--', alpha=0.7)
        
        # Add project duration line
        plt.axvline(x=self.results["total_duration"], color='red', linestyle='--', 
                    label=f'Project End: Day {self.results["total_duration"]}')
        
        plt.tight_layout()
        gantt_file = os.path.join(output_dir, 'gantt_chart.png')
        plt.savefig(gantt_file)
        plt.close()
        
        # Resource Utilization Chart
        fig, ax = plt.subplots(figsize=(10, 6))
        resources = list(self.results["resource_utilization"].keys())
        utilization = [self.results["resource_utilization"][r] for r in resources]
        
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


def main():
    parser = argparse.ArgumentParser(description='Resource Optimizer for Construction Schedules')
    parser.add_argument('input_file', help='Input TXT file with task and resource data')
    parser.add_argument('--mode', choices=['eco', 'standard', 'performance'], default='standard',
                        help='Optimization mode: eco (budget-friendly), standard, or performance (time-critical)')
    parser.add_argument('--output-dir', default='output', help='Directory for output files')
    parser.add_argument('--generate-csv', action='store_true', help='Generate CSV files from input')
    parser.add_argument('--generate-json', action='store_true', help='Generate JSON files from input')
    parser.add_argument('--charts', action='store_true', help='Generate visualization charts')
    
    args = parser.parse_args()
    
    # Create output directory if it doesn't exist
    os.makedirs(args.output_dir, exist_ok=True)
    
    try:
        # Initialize the optimizer with the selected mode
        optimizer = ResourceOptimizer(mode=args.mode)
        
        # Parse the input file
        optimizer.parse_txt_input(args.input_file)
        
        # Generate CSV files if requested
        if args.generate_csv:
            csv_files = optimizer.convert_to_csv(os.path.join(args.output_dir, 'csv'))
            print(f"CSV files generated: {', '.join(csv_files)}")
        
        # Generate JSON files if requested
        if args.generate_json:
            json_files = optimizer.convert_to_json(os.path.join(args.output_dir, 'json'))
            print(f"JSON files generated: {', '.join(json_files)}")
        
        # Optimize the schedule
        results = optimizer.optimize_schedule()
        
        # Generate a report
        report_file = os.path.join(args.output_dir, f'report_{args.mode}.txt')
        optimizer.generate_report(report_file)
        print(f"Optimization report generated: {report_file}")
        
        # Generate charts if requested
        if args.charts:
            charts_dir = os.path.join(args.output_dir, 'charts')
            gantt_file, util_file = optimizer.generate_charts(charts_dir)
            print(f"Charts generated in {charts_dir}")
            print(f"- Gantt chart: {gantt_file}")
            print(f"- Resource utilization chart: {util_file}")
        
        # Display summary on console
        print("\n" + "=" * 50)
        print(f"SCHEDULE OPTIMIZATION SUMMARY ({args.mode.upper()} MODE)")
        print("=" * 50)
        print(f"Total project duration: {results['total_duration']} days")
        print(f"Total project cost: ${results['total_cost']:.2f}")
        print(f"Total carbon footprint: {results['carbon_footprint']:.2f} units")
        print("=" * 50)
        
        print(f"\nDetailed report available at: {report_file}")
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
