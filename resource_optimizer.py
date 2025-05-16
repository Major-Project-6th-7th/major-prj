#!/usr/bin/env python3
"""
AI-Driven Resource Optimizer for Construction Schedules - Main CLI Module
"""
import argparse
from typing import Dict, List, Any
import json
import csv
from pathlib import Path
from scheduler import GeneticAlgorithmScheduler
from utils import (
    validate_input_data,
    calculate_carbon_footprint,
    calculate_total_cost,
    format_schedule_output
)

def parse_input_file(file_path: str) -> List[Dict[str, Any]]:
    """Parse input file (CSV or JSON) into task data structure."""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Input file {file_path} not found")
    
    if path.suffix == '.json':
        with open(path, 'r') as f:
            return json.load(f)
    elif path.suffix == '.csv':
        with open(path, 'r') as f:
            reader = csv.DictReader(f)
            return list(reader)
    else:
        raise ValueError("Unsupported file format. Please provide CSV or JSON")

def optimize_schedule(args: argparse.Namespace) -> None:
    """Main optimization workflow."""
    try:
        # Parse and validate input
        tasks = parse_input_file(args.input)
        validate_input_data(tasks)
        
        # Initialize and run scheduler
        scheduler = GeneticAlgorithmScheduler(
            tasks=tasks,
            population_size=args.population_size,
            generations=args.generations,
            mutation_rate=args.mutation_rate,
            max_cost=args.max_cost
        )
        optimized_schedule = scheduler.optimize()
        
        # Calculate metrics
        total_cost = calculate_total_cost(optimized_schedule)
        carbon_footprint = calculate_carbon_footprint(optimized_schedule)
        
        # Output results
        print("\nOptimized Construction Schedule:")
        print(format_schedule_output(optimized_schedule))
        print(f"\nTotal Project Cost: ${total_cost:,.2f}")
        print(f"Estimated Carbon Footprint: {carbon_footprint:,.2f} kg CO₂\n")
        
    except Exception as e:
        print(f"Error during optimization: {str(e)}")
        raise

def main():
    """CLI argument parser and command router."""
    parser = argparse.ArgumentParser(
        description="AI-Driven Resource Optimizer for Construction Schedules"
    )
    subparsers = parser.add_subparsers(dest='command', required=True)
    
    # Optimize command
    optimize_parser = subparsers.add_parser('optimize', help='Optimize construction schedule')
    optimize_parser.add_argument(
        '--input', 
        type=str, 
        required=True,
        help='Path to input CSV/JSON file with task data'
    )
    optimize_parser.add_argument(
        '--population-size',
        type=int,
        default=50,
        help='Genetic algorithm population size (default: 50)'
    )
    optimize_parser.add_argument(
        '--generations',
        type=int,
        default=100,
        help='Number of generations to evolve (default: 100)'
    )
    optimize_parser.add_argument(
        '--mutation-rate',
        type=float,
        default=0.1,
        help='Mutation rate for genetic algorithm (default: 0.1)'
    )
    optimize_parser.add_argument(
        '--max-cost',
        type=float,
        default=None,
        help='Maximum allowed project cost (optional constraint)'
    )
    optimize_parser.set_defaults(func=optimize_schedule)
    
    args = parser.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()
