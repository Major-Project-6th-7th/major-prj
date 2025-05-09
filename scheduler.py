"""
Genetic Algorithm-based Construction Schedule Optimizer
"""
from typing import List, Dict, Any, Tuple
import random
from deap import base, creator, tools, algorithms
import numpy as np

class GeneticAlgorithmScheduler:
    """Genetic Algorithm implementation for construction schedule optimization."""
    
    def __init__(
        self,
        tasks: List[Dict[str, Any]],
        population_size: int = 50,
        generations: int = 100,
        mutation_rate: float = 0.1,
        max_cost: float = None
    ):
        self.tasks = tasks
        self.population_size = population_size
        self.generations = generations
        self.mutation_rate = mutation_rate
        self.max_cost = max_cost
        self.resource_types = self._extract_resource_types()
        self.task_ids = [task['id'] for task in tasks]
        
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
        creator.create("FitnessMulti", base.Fitness, weights=(-1.0, -1.0))  # Minimize duration and cost
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
    
    def _evaluate_schedule(self, individual: list) -> Tuple[float, float]:
        """Evaluate fitness of a schedule (duration and cost)."""
        schedule = self._create_schedule_dict(individual)
        
        # Calculate project duration (makespan)
        end_times = [
            schedule[task['id']]['start'] + int(task['duration'])
            for task in self.tasks
        ]
        duration = max(end_times) if end_times else 0
        
        # Calculate resource usage and cost
        daily_resources = self._calculate_daily_resource_usage(schedule)
        cost = sum(
            day_cost 
            for day in daily_resources.values() 
            for day_cost in day['cost'].values()
        )
        
        # Apply cost constraint if specified
        if self.max_cost is not None and cost > self.max_cost:
            duration *= 1.5  # Penalize solutions that exceed cost limit
            cost *= 1.5
        
        return duration, cost
    
    def _create_schedule_dict(self, individual: list) -> Dict[str, Dict[str, Any]]:
        """Convert individual (list of start times) to schedule dictionary."""
        return {
            task['id']: {
                'start': individual[i],
                'resources': task.get('resources', {}),
                'duration': int(task['duration'])
            }
            for i, task in enumerate(self.tasks)
        }
    
    def _calculate_daily_resource_usage(self, schedule: Dict) -> Dict[int, Dict]:
        """Calculate resource usage and cost per day."""
        daily_usage = {}
        
        for task_id, task_info in schedule.items():
            start_day = task_info['start']
            duration = task_info['duration']
            resources = task_info['resources']
            
            for day in range(start_day, start_day + duration):
                if day not in daily_usage:
                    daily_usage[day] = {
                        'resources': {rt: 0 for rt in self.resource_types},
                        'cost': {rt: 0 for rt in self.resource_types}
                    }
                
                for res_type, quantity in resources.items():
                    if res_type in self.resource_types:
                        daily_usage[day]['resources'][res_type] += int(quantity)
                        # Simple cost model: $100/worker/day, $1000/crane/day, etc.
                        cost_per_unit = 1000 if 'crane' in res_type.lower() else 100
                        daily_usage[day]['cost'][res_type] += int(quantity) * cost_per_unit
        
        return daily_usage
    
    def optimize(self) -> Dict[str, Dict[str, Any]]:
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
        return self._create_schedule_dict(best_individual)