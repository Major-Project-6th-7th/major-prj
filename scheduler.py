"""
Genetic Algorithm-based Construction Schedule Optimizer
Integrated with the Resource Optimizer for Construction Schedules
"""
from typing import List, Dict, Any, Tuple, Optional
import random
from deap import base, creator, tools, algorithms
import numpy as np
from collections import defaultdict

class GeneticAlgorithmScheduler:
    """Genetic Algorithm implementation for construction schedule optimization."""
    
    def __init__(
        self,
        tasks: List[Dict[str, Any]],
        population_size: int = 50,
        generations: int = 100,
        mutation_rate: float = 0.1,
        max_cost: float = None,
        mode: str = "standard"
    ):
        self.tasks = tasks
        self.population_size = population_size
        self.generations = generations
        self.mutation_rate = mutation_rate
        self.max_cost = max_cost
        self.mode = mode
        self.resource_types = self._extract_resource_types()
        self.task_ids = [task['id'] for task in tasks]
        
        # Adjustment factors based on mode
        self.adjustment_factors = {
            "eco": {"duration": 1.1, "cost": 0.9, "carbon": 0.7},
            "standard": {"duration": 1.0, "cost": 1.0, "carbon": 1.0},
            "performance": {"duration": 0.8, "cost": 1.2, "carbon": 1.5}
        }
        
        # DEAP framework setup
        self._setup_deap_framework()
    
    def _extract_resource_types(self) -> List[str]:
        """Extract unique resource types from tasks."""
        resource_types = set()
        for task in self.tasks:
            if 'resources' in task and isinstance(task['resources'], dict):
                resource_types.update(task['resources'].keys())
        return list(resource_types)
    
    def _setup_deap_framework(self) -> None:
        """Initialize DEAP creator and toolbox."""
        # Clear any previously created classes to avoid errors
        if 'FitnessMulti' in creator.__dict__:
            del creator.FitnessMulti
        if 'Individual' in creator.__dict__:
            del creator.Individual
            
        # For eco mode, we prioritize cost and carbon over duration
        # For performance mode, we prioritize duration over cost/carbon
        # For standard mode, we balance all factors
        weights = None
        if self.mode == "eco":
            weights = (-0.5, -1.0, -1.0)  # (duration, cost, carbon)
        elif self.mode == "performance":
            weights = (-1.0, -0.5, -0.5)  # Prioritize duration
        else:  # standard
            weights = (-1.0, -1.0, -1.0)  # Equal weights
            
        creator.create("FitnessMulti", base.Fitness, weights=weights)
        creator.create("Individual", list, fitness=creator.FitnessMulti)
        
        self.toolbox = base.Toolbox()
        
        # Attribute generator for start times
        max_duration = sum(int(task['duration']) for task in self.tasks)
        self.toolbox.register("attr_start_time", random.randint, 0, max_duration)
        
        # Individual and population creators
        self.toolbox.register(
            "individual", 
            tools.initRepeat, 
            creator.Individual, 
            self.toolbox.attr_start_time, 
            len(self.tasks)
        )
        self.toolbox.register("population", tools.initRepeat, list, self.toolbox.individual)
        
        # Genetic operators
        self.toolbox.register("mate", tools.cxTwoPoint)
        self.toolbox.register("mutate", self._mutate_individual, indpb=self.mutation_rate)
        self.toolbox.register("select", tools.selNSGA2)
        self.toolbox.register("evaluate", self._evaluate_schedule)
    
    def _mutate_individual(self, individual: list, indpb: float) -> Tuple[list]:
        """Custom mutation operator that respects task dependencies."""
        for i in range(len(individual)):
            if random.random() < indpb:
                task = self.tasks[i]
                min_start = 0
                
                # Consider dependencies for minimum start time
                if 'dependencies' in task and task['dependencies']:
                    deps = task['dependencies'].split(',') if isinstance(task['dependencies'], str) else task['dependencies']
                    min_start = max(
                        individual[self.task_ids.index(dep)] + int(self.tasks[self.task_ids.index(dep)]['duration'])
                        for dep in deps
                    )
                
                individual[i] = random.randint(min_start, min_start + int(task['duration']) * 2)
        return individual,
    
    def _evaluate_schedule(self, individual: list) -> Tuple[float, float, float]:
        """Evaluate fitness of a schedule (duration, cost, and carbon footprint)."""
        schedule = self._create_schedule_dict(individual)
        
        # Apply mode-specific adjustments
        factor = self.adjustment_factors[self.mode]
        
        # Calculate project duration (makespan)
        end_times = [
            schedule[task['id']]['start'] + max(1, int(int(task['duration']) * factor["duration"]))
            for task in self.tasks
        ]
        duration = max(end_times) if end_times else 0
        
        # Calculate resource usage, cost, and carbon footprint
        daily_resources = self._calculate_daily_resource_usage(schedule, factor)
        
        cost = sum(
            day_cost 
            for day in daily_resources.values() 
            for day_cost in day['cost'].values()
        )
        
        carbon = sum(
            day_carbon
            for day in daily_resources.values() 
            for day_carbon in day['carbon'].values()
        )
        
        # Apply cost constraint if specified
        if self.max_cost is not None and cost > self.max_cost:
            if self.mode != "performance":  # In performance mode, we can exceed the budget
                duration *= 1.5  # Penalize solutions that exceed cost limit
                cost *= 1.5
        
        return duration, cost, carbon
    
    def _create_schedule_dict(self, individual: list) -> Dict[str, Dict[str, Any]]:
        """Convert individual (list of start times) to schedule dictionary."""
        factor = self.adjustment_factors[self.mode]
        
        return {
            task['id']: {
                'start': individual[i],
                'resources': task.get('resources', {}),
                'duration': max(1, int(int(task['duration']) * factor["duration"]))
            }
            for i, task in enumerate(self.tasks)
        }
    
    def _calculate_daily_resource_usage(self, schedule: Dict, factor: Dict) -> Dict[int, Dict]:
        """Calculate resource usage, cost and carbon footprint per day."""
        daily_usage = {}
        
        for task_id, task_info in schedule.items():
            start_day = task_info['start']
            duration = task_info['duration']
            resources = task_info['resources']
            
            for day in range(start_day, start_day + duration):
                if day not in daily_usage:
                    daily_usage[day] = {
                        'resources': {rt: 0 for rt in self.resource_types},
                        'cost': {rt: 0 for rt in self.resource_types},
                        'carbon': {rt: 0 for rt in self.resource_types}
                    }
                
                for res_type, quantity in resources.items():
                    if res_type in self.resource_types:
                        quantity_int = int(quantity)
                        daily_usage[day]['resources'][res_type] += quantity_int
                        
                        # Cost model adjustments based on mode
                        if 'crane' in res_type.lower():
                            base_cost = 1000
                            base_carbon = 50
                        elif 'worker' in res_type.lower() or 'team' in res_type.lower() or 'labor' in res_type.lower():
                            base_cost = 100
                            base_carbon = 5
                        else:
                            base_cost = 200
                            base_carbon = 10
                        
                        # Apply mode factors to cost and carbon
                        daily_usage[day]['cost'][res_type] += quantity_int * base_cost * factor["cost"]
                        daily_usage[day]['carbon'][res_type] += quantity_int * base_carbon * factor["carbon"]
        
        return daily_usage
    
    def optimize(self) -> Dict[str, Any]:
        """Run genetic algorithm optimization."""
        pop = self.toolbox.population(n=self.population_size)
        hof = tools.ParetoFront()
        stats = tools.Statistics(lambda ind: ind.fitness.values)
        stats.register("avg", np.mean, axis=0)
        stats.register("min", np.min, axis=0)
        
        algorithms.eaSimple(
            pop, 
            self.toolbox,
            cxpb=0.7,
            mutpb=self.mutation_rate,
            ngen=self.generations,
            stats=stats,
            halloffame=hof,
            verbose=True
        )
        
        # Return the best schedule found
        best_individual = tools.selBest(pop, k=1)[0]
        best_schedule = self._create_schedule_dict(best_individual)
        
        # Calculate final duration, cost, and carbon footprint
        end_times = [
            best_schedule[task['id']]['start'] + best_schedule[task['id']]['duration']
            for task in self.tasks
        ]
        total_duration = max(end_times) if end_times else 0
        
        daily_resources = self._calculate_daily_resource_usage(
            best_schedule, 
            self.adjustment_factors[self.mode]
        )
        
        total_cost = sum(
            day_cost 
            for day in daily_resources.values() 
            for day_cost in day['cost'].values()
        )
        
        total_carbon = sum(
            day_carbon
            for day in daily_resources.values() 
            for day_carbon in day['carbon'].values()
        )
        
        # Calculate resource utilization
        max_day = max(daily_resources.keys()) if daily_resources else 0
        resource_utilization = {}
        
        for res_type in self.resource_types:
            active_days = sum(1 for day in range(max_day + 1) 
                             if day in daily_resources and daily_resources[day]['resources'][res_type] > 0)
            if max_day > 0:
                utilization = (active_days / (max_day + 1)) * 100
            else:
                utilization = 0
            resource_utilization[res_type] = utilization
        
        # Create optimized result structure
        schedule_items = []
        for task in self.tasks:
            task_id = task['id']
            task_info = best_schedule[task_id]
            
            task_resources = task.get('resources', {})
            task_cost = sum(daily_resources.get(day, {}).get('cost', {}).get(res_type, 0) 
                           for res_type in task_resources
                           for day in range(task_info['start'], task_info['start'] + task_info['duration']))
            
            task_carbon = sum(daily_resources.get(day, {}).get('carbon', {}).get(res_type, 0)
                             for res_type in task_resources
                             for day in range(task_info['start'], task_info['start'] + task_info['duration']))
            
            schedule_items.append({
                "task": task_id,
                "start": task_info['start'],
                "end": task_info['start'] + task_info['duration'],
                "duration": task_info['duration'],
                "resources": list(task_resources.keys()),
                "cost": task_cost,
                "carbon": task_carbon
            })
        
        # Sort by start time
        schedule_items.sort(key=lambda x: x["start"])
        
        optimization_result = {
            "schedule": schedule_items,
            "total_cost": total_cost,
            "total_duration": total_duration,
            "carbon_footprint": total_carbon,
            "resource_utilization": resource_utilization,
            "mode": self.mode
        }
        
        return optimization_result
