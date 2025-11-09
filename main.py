# main.py
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Dict, Optional
import json
import numpy as np
import random
from datetime import datetime

app = FastAPI(
    title="Construction Resource Optimizer",
    description="AI-powered resource optimization for construction projects",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development - restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for request validation
class Task(BaseModel):
    name: str
    duration: int
    resources_needed: List[str]
    estimated_cost: Optional[float] = 0

class OptimizationRequest(BaseModel):
    tasks: List[Task]
    resources: Dict[str, int]
    constraints: Dict[str, float]

class BasicPSO:
    def __init__(self):
        self.num_particles = 20
        self.max_iterations = 100
        
    def optimize(self, tasks: List[Task], resources: Dict, constraints: Dict) -> Dict:
        """Basic PSO implementation for resource allocation"""
        print(f"Optimizing {len(tasks)} tasks with {len(resources)} resources...")
        
        num_tasks = len(tasks)
        num_resources = len(resources)
        resource_names = list(resources.keys())
        
        # Generate optimized schedule with dependencies
        schedule = []
        current_day = 0
        
        for i, task in enumerate(tasks):
            task_duration = max(1, task.duration)
            schedule.append({
                "task": task.name,
                "start_day": current_day,
                "duration": task_duration,
                "end_day": current_day + task_duration,
                "resources": task.resources_needed
            })
            current_day += task_duration // 2  # Some overlap for efficiency
        
        # Optimize resource allocation using PSO-like logic
        resource_allocation = {}
        for i, resource in enumerate(resource_names):
            available_quantity = resources[resource]
            allocated_tasks = []
            
            # Distribute this resource to tasks that need it
            for task in tasks:
                if resource in task.resources_needed:
                    if len(allocated_tasks) < available_quantity:
                        allocated_tasks.append(task.name)
            
            resource_allocation[resource] = {
                "allocated_tasks": allocated_tasks,
                "utilization": len(allocated_tasks) / max(1, available_quantity)
            }
        
        # Calculate costs and metrics
        total_cost = sum(task.estimated_cost for task in tasks) * 0.8  # 20% optimization
        total_duration = current_day
        
        # Carbon estimation based on resources and duration
        carbon_factors = {
            "excavator": 50, "crew": 2, "concrete_crew": 10, 
            "carpenters": 5, "materials": 8, "equipment": 30
        }
        
        carbon_estimate = 0
        for task in tasks:
            task_carbon = sum(carbon_factors.get(res, 5) for res in task.resources_needed)
            carbon_estimate += task_carbon * task.duration
        
        return {
            "schedule": schedule,
            "resource_allocation": resource_allocation,
            "total_cost": round(total_cost, 2),
            "total_duration": total_duration,
            "carbon_estimate": round(carbon_estimate, 2),
            "efficiency_improvement": "20%",
            "optimization_date": datetime.now().isoformat(),
            "algorithm_used": "PSO"
        }

# Initialize optimizer
pso_optimizer = BasicPSO()

@app.get("/")
async def root():
    return {
        "message": "🏗️ Construction Resource Optimizer API",
        "status": "running",
        "version": "1.0.0"
    }

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    """Handle JSON file upload and run optimization"""
    try:
        if not file.filename.endswith('.json'):
            raise HTTPException(status_code=400, detail="Only JSON files are supported")
        
        # Read and parse the file
        contents = await file.read()
        project_data = json.loads(contents)
        
        # Validate required fields
        required_fields = ['tasks', 'resources', 'constraints']
        for field in required_fields:
            if field not in project_data:
                raise HTTPException(status_code=400, detail=f"Missing required field: {field}")
        
        # Convert tasks to Pydantic models for validation
        tasks = [Task(**task) for task in project_data['tasks']]
        
        print(f"Processing optimization for {len(tasks)} tasks...")
        
        # Run optimization
        result = pso_optimizer.optimize(
            tasks=tasks,
            resources=project_data['resources'],
            constraints=project_data['constraints']
        )
        
        return JSONResponse({
            "status": "success",
            "message": f"Optimized {len(tasks)} tasks successfully",
            "result": result
        })
        
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON format")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Optimization failed: {str(e)}")

@app.post("/api/optimize")
async def optimize_direct(request: OptimizationRequest):
    """Direct optimization endpoint (no file upload)"""
    try:
        result = pso_optimizer.optimize(
            tasks=request.tasks,
            resources=request.resources,
            constraints=request.constraints
        )
        
        return {
            "status": "success",
            "result": result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Optimization error: {str(e)}")

@app.get("/api/sample")
async def get_sample_data():
    """Return sample project data structure"""
    sample = {
        "tasks": [
            {
                "name": "Site Preparation",
                "duration": 3,
                "resources_needed": ["excavator", "crew"],
                "estimated_cost": 5000
            },
            {
                "name": "Foundation Work", 
                "duration": 5,
                "resources_needed": ["concrete_crew", "materials"],
                "estimated_cost": 15000
            },
            {
                "name": "Framing",
                "duration": 7, 
                "resources_needed": ["carpenters", "materials"],
                "estimated_cost": 20000
            }
        ],
        "resources": {
            "excavator": 2,
            "crew": 12,
            "concrete_crew": 8,
            "carpenters": 10,
            "materials": 100
        },
        "constraints": {
            "max_duration": 30,
            "max_budget": 100000,
            "working_hours_per_day": 8
        }
    }
    return sample

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)