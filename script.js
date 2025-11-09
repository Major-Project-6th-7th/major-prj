// app.js - Pure JavaScript Construction Optimizer MVP

class ConstructionOptimizer {
    constructor() {
        this.init();
    }

    init() {
        // Create the entire UI programmatically
        document.body.innerHTML = '';
        this.createUI();
        this.bindEvents();
    }

    createUI() {
        // Main container
        const container = document.createElement('div');
        container.style.cssText = `
            font-family: Arial, sans-serif;
            max-width: 900px;
            margin: 0 auto;
            padding: 20px;
        `;

        // Header
        const header = document.createElement('h1');
        header.textContent = '🏗️ Construction Resource Optimizer (MVP)';
        header.style.color = '#2c3e50';

        // Upload section
        const uploadSection = this.createUploadSection();
        
        // Results section
        const resultsSection = this.createResultsSection();
        
        // Sample data section
        const sampleSection = this.createSampleSection();

        container.appendChild(header);
        container.appendChild(uploadSection);
        container.appendChild(resultsSection);
        container.appendChild(sampleSection);
        
        document.body.appendChild(container);
    }

    createUploadSection() {
        const section = document.createElement('div');
        section.style.cssText = `
            border: 2px dashed #bdc3c7;
            border-radius: 10px;
            padding: 30px;
            text-align: center;
            margin: 20px 0;
            background: #f8f9fa;
        `;

        const title = document.createElement('h3');
        title.textContent = 'Upload Project Data (JSON)';
        title.style.marginBottom = '20px';

        const fileInput = document.createElement('input');
        fileInput.type = 'file';
        fileInput.id = 'fileInput';
        fileInput.accept = '.json';
        fileInput.style.marginBottom = '15px';

        const optimizeBtn = document.createElement('button');
        optimizeBtn.textContent = '🚀 Optimize!';
        optimizeBtn.style.cssText = `
            padding: 12px 24px;
            background: #3498db;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
        `;
        optimizeBtn.onclick = () => this.uploadFile();

        section.appendChild(title);
        section.appendChild(fileInput);
        section.appendChild(document.createElement('br'));
        section.appendChild(optimizeBtn);

        return section;
    }

    createResultsSection() {
        const section = document.createElement('div');
        section.id = 'results';
        section.style.cssText = `
            background: #ecf0f1;
            padding: 20px;
            border-radius: 8px;
            margin: 20px 0;
            display: none;
        `;

        const title = document.createElement('h3');
        title.textContent = 'Optimization Results';
        title.style.color = '#2c3e50';

        const content = document.createElement('div');
        content.id = 'resultContent';

        section.appendChild(title);
        section.appendChild(content);

        return section;
    }

    createSampleSection() {
        const section = document.createElement('div');
        section.style.cssText = `
            background: #fff3cd;
            padding: 20px;
            border-radius: 8px;
            border-left: 4px solid #ffc107;
        `;

        const title = document.createElement('h3');
        title.textContent = '📋 Sample Data Format';
        title.style.marginBottom = '15px';

        const samplePre = document.createElement('pre');
        samplePre.id = 'sampleJson';
        samplePre.style.cssText = `
            background: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
            overflow-x: auto;
            border: 1px solid #e9ecef;
        `;

        const downloadBtn = document.createElement('button');
        downloadBtn.textContent = '📥 Download Sample JSON';
        downloadBtn.style.cssText = `
            padding: 10px 20px;
            background: #27ae60;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            margin-top: 10px;
        `;
        downloadBtn.onclick = () => this.downloadSample();

        section.appendChild(title);
        section.appendChild(samplePre);
        section.appendChild(document.createElement('br'));
        section.appendChild(downloadBtn);

        return section;
    }

    bindEvents() {
        // Display sample data
        this.displaySampleData();
    }

    displaySampleData() {
        const sampleData = {
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
        };

        const samplePre = document.getElementById('sampleJson');
        samplePre.textContent = JSON.stringify(sampleData, null, 2);
    }

    async uploadFile() {
        const fileInput = document.getElementById('fileInput');
        const file = fileInput.files[0];
        
        if (!file) {
            alert('📁 Please select a JSON file first!');
            return;
        }

        try {
            // Show loading state
            this.showLoading();

            const formData = new FormData();
            formData.append('file', file);

            const response = await fetch('http://localhost:8000/api/upload', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                throw new Error(`Server error: ${response.status}`);
            }

            const result = await response.json();
            this.displayResults(result);

        } catch (error) {
            this.showError(`Upload failed: ${error.message}`);
        }
    }

    showLoading() {
        const resultsDiv = document.getElementById('results');
        const contentDiv = document.getElementById('resultContent');
        
        contentDiv.innerHTML = `
            <div style="text-align: center; padding: 20px;">
                <div style="font-size: 24px; margin-bottom: 10px;">⏳</div>
                <p>Running optimization algorithms...</p>
                <p><small>This may take a few seconds</small></p>
            </div>
        `;
        resultsDiv.style.display = 'block';
    }

    showError(message) {
        const resultsDiv = document.getElementById('results');
        const contentDiv = document.getElementById('resultContent');
        
        contentDiv.innerHTML = `
            <div style="color: #e74c3c; text-align: center; padding: 20px;">
                <div style="font-size: 24px; margin-bottom: 10px;">❌</div>
                <p><strong>Error:</strong> ${message}</p>
                <p>Make sure the backend server is running on http://localhost:8000</p>
            </div>
        `;
        resultsDiv.style.display = 'block';
    }

    displayResults(data) {
        const resultsDiv = document.getElementById('results');
        const contentDiv = document.getElementById('resultContent');
        
        const result = data.result;
        
        contentDiv.innerHTML = `
            <div style="display: grid; gap: 20px;">
                <div style="background: white; padding: 15px; border-radius: 5px;">
                    <h4 style="color: #2c3e50; margin-bottom: 10px;">📅 Optimized Schedule</h4>
                    <pre style="background: #f8f9fa; padding: 10px; border-radius: 3px;">${JSON.stringify(result.schedule, null, 2)}</pre>
                </div>
                
                <div style="background: white; padding: 15px; border-radius: 5px;">
                    <h4 style="color: #2c3e50; margin-bottom: 10px;">👥 Resource Allocation</h4>
                    <pre style="background: #f8f9fa; padding: 10px; border-radius: 3px;">${JSON.stringify(result.resource_allocation, null, 2)}</pre>
                </div>
                
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px;">
                    <div style="background: #d4edda; padding: 15px; border-radius: 5px; text-align: center;">
                        <h4 style="color: #155724; margin: 0;">💰 Total Cost</h4>
                        <p style="font-size: 24px; font-weight: bold; color: #155724;">$${result.total_cost}</p>
                    </div>
                    
                    <div style="background: #cce7ff; padding: 15px; border-radius: 5px; text-align: center;">
                        <h4 style="color: #004085; margin: 0;">⏱️ Duration</h4>
                        <p style="font-size: 24px; font-weight: bold; color: #004085;">${result.total_duration} days</p>
                    </div>
                    
                    <div style="background: #e8f5e8; padding: 15px; border-radius: 5px; text-align: center;">
                        <h4 style="color: #1b5e20; margin: 0;">🌱 Carbon Footprint</h4>
                        <p style="font-size: 24px; font-weight: bold; color: #1b5e20;">${result.carbon_estimate} kg CO₂</p>
                    </div>
                </div>
            </div>
        `;
        
        resultsDiv.style.display = 'block';
    }

    downloadSample() {
        const sampleData = {
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
                }
            ],
            "resources": {
                "excavator": 2,
                "crew": 12,
                "concrete_crew": 8,
                "materials": 100
            },
            "constraints": {
                "max_duration": 30,
                "max_budget": 100000
            }
        };

        const blob = new Blob([JSON.stringify(sampleData, null, 2)], {type: 'application/json'});
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'construction_project_sample.json';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }
}

// Initialize the app when page loads
document.addEventListener('DOMContentLoaded', () => {
    new ConstructionOptimizer();
});