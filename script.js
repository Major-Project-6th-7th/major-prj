// // app.js - Pure JavaScript Construction Optimizer MVP

// class ConstructionOptimizer {
//     constructor() {
//         this.init();
//     }

//     init() {
//         // Create the entire UI programmatically
//         document.body.innerHTML = '';
//         this.createUI();
//         this.bindEvents();
//     }

//     createUI() {
//         // Main container
//         const container = document.createElement('div');
//         container.style.cssText = `
//             font-family: Arial, sans-serif;
//             max-width: 900px;
//             margin: 0 auto;
//             padding: 20px;
//         `;

//         // Header
//         const header = document.createElement('h1');
//         header.textContent = '🏗️ Construction Resource Optimizer (MVP)';
//         header.style.color = '#2c3e50';

//         // Upload section
//         const uploadSection = this.createUploadSection();
        
//         // Results section
//         const resultsSection = this.createResultsSection();
        
//         // Sample data section
//         const sampleSection = this.createSampleSection();

//         container.appendChild(header);
//         container.appendChild(uploadSection);
//         container.appendChild(resultsSection);
//         container.appendChild(sampleSection);
        
//         document.body.appendChild(container);
//     }

//     createUploadSection() {
//         const section = document.createElement('div');
//         section.style.cssText = `
//             border: 2px dashed #bdc3c7;
//             border-radius: 10px;
//             padding: 30px;
//             text-align: center;
//             margin: 20px 0;
//             background: #f8f9fa;
//         `;

//         const title = document.createElement('h3');
//         title.textContent = 'Upload Project Data (JSON)';
//         title.style.marginBottom = '20px';

//         const fileInput = document.createElement('input');
//         fileInput.type = 'file';
//         fileInput.id = 'fileInput';
//         fileInput.accept = '.json';
//         fileInput.style.marginBottom = '15px';

//         const optimizeBtn = document.createElement('button');
//         optimizeBtn.textContent = '🚀 Optimize!';
//         optimizeBtn.style.cssText = `
//             padding: 12px 24px;
//             background: #3498db;
//             color: white;
//             border: none;
//             border-radius: 5px;
//             cursor: pointer;
//             font-size: 16px;
//         `;
//         optimizeBtn.onclick = () => this.uploadFile();

//         section.appendChild(title);
//         section.appendChild(fileInput);
//         section.appendChild(document.createElement('br'));
//         section.appendChild(optimizeBtn);

//         return section;
//     }

//     createResultsSection() {
//         const section = document.createElement('div');
//         section.id = 'results';
//         section.style.cssText = `
//             background: #ecf0f1;
//             padding: 20px;
//             border-radius: 8px;
//             margin: 20px 0;
//             display: none;
//         `;

//         const title = document.createElement('h3');
//         title.textContent = 'Optimization Results';
//         title.style.color = '#2c3e50';

//         const content = document.createElement('div');
//         content.id = 'resultContent';

//         section.appendChild(title);
//         section.appendChild(content);

//         return section;
//     }

//     createSampleSection() {
//         const section = document.createElement('div');
//         section.style.cssText = `
//             background: #fff3cd;
//             padding: 20px;
//             border-radius: 8px;
//             border-left: 4px solid #ffc107;
//         `;

//         const title = document.createElement('h3');
//         title.textContent = '📋 Sample Data Format';
//         title.style.marginBottom = '15px';

//         const samplePre = document.createElement('pre');
//         samplePre.id = 'sampleJson';
//         samplePre.style.cssText = `
//             background: #f8f9fa;
//             padding: 15px;
//             border-radius: 5px;
//             overflow-x: auto;
//             border: 1px solid #e9ecef;
//         `;

//         const downloadBtn = document.createElement('button');
//         downloadBtn.textContent = '📥 Download Sample JSON';
//         downloadBtn.style.cssText = `
//             padding: 10px 20px;
//             background: #27ae60;
//             color: white;
//             border: none;
//             border-radius: 5px;
//             cursor: pointer;
//             margin-top: 10px;
//         `;
//         downloadBtn.onclick = () => this.downloadSample();

//         section.appendChild(title);
//         section.appendChild(samplePre);
//         section.appendChild(document.createElement('br'));
//         section.appendChild(downloadBtn);

//         return section;
//     }

//     bindEvents() {
//         // Display sample data
//         this.displaySampleData();
//     }

//     displaySampleData() {
//         const sampleData = {
//             "tasks": [
//                 {
//                     "name": "Site Preparation",
//                     "duration": 3,
//                     "resources_needed": ["excavator", "crew"],
//                     "estimated_cost": 5000
//                 },
//                 {
//                     "name": "Foundation Work", 
//                     "duration": 5,
//                     "resources_needed": ["concrete_crew", "materials"],
//                     "estimated_cost": 15000
//                 },
//                 {
//                     "name": "Framing",
//                     "duration": 7, 
//                     "resources_needed": ["carpenters", "materials"],
//                     "estimated_cost": 20000
//                 }
//             ],
//             "resources": {
//                 "excavator": 2,
//                 "crew": 12,
//                 "concrete_crew": 8,
//                 "carpenters": 10,
//                 "materials": 100
//             },
//             "constraints": {
//                 "max_duration": 30,
//                 "max_budget": 100000,
//                 "working_hours_per_day": 8
//             }
//         };

//         const samplePre = document.getElementById('sampleJson');
//         samplePre.textContent = JSON.stringify(sampleData, null, 2);
//     }

//     async uploadFile() {
//         const fileInput = document.getElementById('fileInput');
//         const file = fileInput.files[0];
        
//         if (!file) {
//             alert('📁 Please select a JSON file first!');
//             return;
//         }

//         try {
//             // Show loading state
//             this.showLoading();

//             const formData = new FormData();
//             formData.append('file', file);

//             const response = await fetch('http://localhost:8000/api/upload', {
//                 method: 'POST',
//                 body: formData
//             });

//             if (!response.ok) {
//                 throw new Error(`Server error: ${response.status}`);
//             }

//             const result = await response.json();
//             this.displayResults(result);

//         } catch (error) {
//             this.showError(`Upload failed: ${error.message}`);
//         }
//     }

//     showLoading() {
//         const resultsDiv = document.getElementById('results');
//         const contentDiv = document.getElementById('resultContent');
        
//         contentDiv.innerHTML = `
//             <div style="text-align: center; padding: 20px;">
//                 <div style="font-size: 24px; margin-bottom: 10px;">⏳</div>
//                 <p>Running optimization algorithms...</p>
//                 <p><small>This may take a few seconds</small></p>
//             </div>
//         `;
//         resultsDiv.style.display = 'block';
//     }

//     showError(message) {
//         const resultsDiv = document.getElementById('results');
//         const contentDiv = document.getElementById('resultContent');
        
//         contentDiv.innerHTML = `
//             <div style="color: #e74c3c; text-align: center; padding: 20px;">
//                 <div style="font-size: 24px; margin-bottom: 10px;">❌</div>
//                 <p><strong>Error:</strong> ${message}</p>
//                 <p>Make sure the backend server is running on http://localhost:8000</p>
//             </div>
//         `;
//         resultsDiv.style.display = 'block';
//     }

//     displayResults(data) {
//         const resultsDiv = document.getElementById('results');
//         const contentDiv = document.getElementById('resultContent');
        
//         const result = data.result;
        
//         contentDiv.innerHTML = `
//             <div style="display: grid; gap: 20px;">
//                 <div style="background: white; padding: 15px; border-radius: 5px;">
//                     <h4 style="color: #2c3e50; margin-bottom: 10px;">📅 Optimized Schedule</h4>
//                     <pre style="background: #f8f9fa; padding: 10px; border-radius: 3px;">${JSON.stringify(result.schedule, null, 2)}</pre>
//                 </div>
                
//                 <div style="background: white; padding: 15px; border-radius: 5px;">
//                     <h4 style="color: #2c3e50; margin-bottom: 10px;">👥 Resource Allocation</h4>
//                     <pre style="background: #f8f9fa; padding: 10px; border-radius: 3px;">${JSON.stringify(result.resource_allocation, null, 2)}</pre>
//                 </div>
                
//                 <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px;">
//                     <div style="background: #d4edda; padding: 15px; border-radius: 5px; text-align: center;">
//                         <h4 style="color: #155724; margin: 0;">💰 Total Cost</h4>
//                         <p style="font-size: 24px; font-weight: bold; color: #155724;">$${result.total_cost}</p>
//                     </div>
                    
//                     <div style="background: #cce7ff; padding: 15px; border-radius: 5px; text-align: center;">
//                         <h4 style="color: #004085; margin: 0;">⏱️ Duration</h4>
//                         <p style="font-size: 24px; font-weight: bold; color: #004085;">${result.total_duration} days</p>
//                     </div>
                    
//                     <div style="background: #e8f5e8; padding: 15px; border-radius: 5px; text-align: center;">
//                         <h4 style="color: #1b5e20; margin: 0;">🌱 Carbon Footprint</h4>
//                         <p style="font-size: 24px; font-weight: bold; color: #1b5e20;">${result.carbon_estimate} kg CO₂</p>
//                     </div>
//                 </div>
//             </div>
//         `;
        
//         resultsDiv.style.display = 'block';
//     }

//     downloadSample() {
//         const sampleData = {
//             "tasks": [
//                 {
//                     "name": "Site Preparation",
//                     "duration": 3,
//                     "resources_needed": ["excavator", "crew"],
//                     "estimated_cost": 5000
//                 },
//                 {
//                     "name": "Foundation Work", 
//                     "duration": 5,
//                     "resources_needed": ["concrete_crew", "materials"],
//                     "estimated_cost": 15000
//                 }
//             ],
//             "resources": {
//                 "excavator": 2,
//                 "crew": 12,
//                 "concrete_crew": 8,
//                 "materials": 100
//             },
//             "constraints": {
//                 "max_duration": 30,
//                 "max_budget": 100000
//             }
//         };

//         const blob = new Blob([JSON.stringify(sampleData, null, 2)], {type: 'application/json'});
//         const url = URL.createObjectURL(blob);
//         const a = document.createElement('a');
//         a.href = url;
//         a.download = 'construction_project_sample.json';
//         document.body.appendChild(a);
//         a.click();
//         document.body.removeChild(a);
//         URL.revokeObjectURL(url);
//     }
// }

// // Initialize the app when page loads
// document.addEventListener('DOMContentLoaded', () => {
//     new ConstructionOptimizer();
// });
// script.js - Enhanced with multiple formats and optimization modes
class ConstructionOptimizer {
    constructor() {
        this.init();
    }

    init() {
        document.body.innerHTML = '';
        this.createEnhancedUI();
    }

    createEnhancedUI() {
        const container = document.createElement('div');
        container.style.cssText = `
            font-family: Arial, sans-serif;
            max-width: 1000px;
            margin: 0 auto;
            padding: 20px;
        `;

        // Header
        const header = document.createElement('h1');
        header.innerHTML = '🏗️ Construction Resource Optimizer <small style="font-size: 16px; color: #666;">v2.0</small>';
        header.style.color = '#2c3e50';

        // Upload Section with Format Selection
        const uploadSection = this.createUploadSection();
        
        // Optimization Mode Selection
        const modeSection = this.createModeSection();
        
        // Results Section
        const resultsSection = this.createResultsSection();
        
        // Sample Data Section
        const sampleSection = this.createSampleSection();

        container.appendChild(header);
        container.appendChild(modeSection);
        container.appendChild(uploadSection);
        container.appendChild(resultsSection);
        container.appendChild(sampleSection);
        
        document.body.appendChild(container);
    }

    createModeSection() {
        const section = document.createElement('div');
        section.style.cssText = `
            background: #e8f4fd;
            padding: 20px;
            border-radius: 10px;
            margin: 20px 0;
            border-left: 4px solid #3498db;
        `;

        const title = document.createElement('h3');
        title.innerHTML = '🎯 Optimization Mode';
        title.style.marginBottom = '15px';

        const modeContainer = document.createElement('div');
        modeContainer.style.display = 'flex';
        modeContainer.style.gap = '15px';
        modeContainer.style.flexWrap = 'wrap';

        const modes = [
            { id: 'balanced', name: 'Balanced', desc: 'Cost-effective & reasonable timeline', emoji: '⚖️' },
            { id: 'eco', name: 'Eco-Friendly', desc: 'Reduce carbon footprint, sustainable', emoji: '🌱' },
            { id: 'performance', name: 'Performance', desc: 'Fastest completion, no limits', emoji: '🚀' }
        ];

        modes.forEach(mode => {
            const modeDiv = document.createElement('div');
            modeDiv.style.cssText = `
                flex: 1;
                min-width: 200px;
                background: white;
                padding: 15px;
                border-radius: 8px;
                cursor: pointer;
                border: 2px solid #ddd;
                transition: all 0.3s;
            `;
            modeDiv.innerHTML = `
                <div style="font-size: 24px; margin-bottom: 10px;">${mode.emoji}</div>
                <strong>${mode.name}</strong>
                <div style="font-size: 12px; color: #666; margin-top: 5px;">${mode.desc}</div>
            `;
            
            modeDiv.onclick = () => this.selectMode(mode.id, modeDiv);
            modeContainer.appendChild(modeDiv);
        });

        section.appendChild(title);
        section.appendChild(modeContainer);
        
        // Store selected mode
        this.selectedMode = 'balanced';
        this.selectMode('balanced', modeContainer.children[0]);

        return section;
    }

    selectMode(modeId, element) {
        // Update visual selection
        const parent = element.parentElement;
        Array.from(parent.children).forEach(child => {
            child.style.borderColor = '#ddd';
            child.style.background = 'white';
        });
        element.style.borderColor = '#3498db';
        element.style.background = '#f0f8ff';
        
        this.selectedMode = modeId;
        console.log(`Selected mode: ${modeId}`);
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
        title.innerHTML = '📁 Upload Project Data';
        title.style.marginBottom = '20px';

        // Format Selection
        const formatLabel = document.createElement('div');
        formatLabel.innerHTML = '<strong>Select File Format:</strong>';
        formatLabel.style.marginBottom = '10px';

        const formatSelect = document.createElement('select');
        formatSelect.id = 'formatSelect';
        formatSelect.style.cssText = `
            padding: 8px 12px;
            border: 1px solid #ddd;
            border-radius: 5px;
            margin-bottom: 15px;
        `;
        
        const formats = [
            { value: 'auto', text: 'Auto-detect' },
            { value: 'json', text: 'JSON' },
            { value: 'csv', text: 'CSV' },
            { value: 'txt', text: 'TXT' }
        ];
        
        formats.forEach(format => {
            const option = document.createElement('option');
            option.value = format.value;
            option.textContent = format.text;
            formatSelect.appendChild(option);
        });

        const fileInput = document.createElement('input');
        fileInput.type = 'file';
        fileInput.id = 'fileInput';
        fileInput.accept = '.json,.csv,.txt';
        fileInput.style.marginBottom = '15px';

        const optimizeBtn = document.createElement('button');
        optimizeBtn.innerHTML = '🚀 Optimize Project';
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
        section.appendChild(formatLabel);
        section.appendChild(formatSelect);
        section.appendChild(document.createElement('br'));
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
        title.innerHTML = '📋 Sample Data Formats';
        title.style.marginBottom = '15px';

        const formatTabs = document.createElement('div');
        formatTabs.style.cssText = `
            display: flex;
            gap: 10px;
            margin-bottom: 15px;
        `;

        const samples = [
            { id: 'csv', name: 'CSV', desc: 'Excel-friendly format' },
            { id: 'txt', name: 'TXT', desc: 'Simple text format' },
            { id: 'json', name: 'JSON', desc: 'Technical format' }
        ];

        const sampleContent = document.createElement('div');
        sampleContent.id = 'sampleContent';
        sampleContent.style.cssText = `
            background: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
            border: 1px solid #e9ecef;
            min-height: 150px;
            font-family: monospace;
            white-space: pre-wrap;
            font-size: 12px;
        `;

        samples.forEach(sample => {
            const tab = document.createElement('button');
            tab.textContent = sample.name;
            tab.style.cssText = `
                padding: 8px 16px;
                border: 1px solid #ffc107;
                background: white;
                border-radius: 5px;
                cursor: pointer;
            `;
            tab.onclick = () => this.showSample(sample.id, tab, sampleContent);
            formatTabs.appendChild(tab);
        });

        const downloadBtn = document.createElement('button');
        downloadBtn.innerHTML = '📥 Download Sample';
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
        section.appendChild(formatTabs);
        section.appendChild(sampleContent);
        section.appendChild(document.createElement('br'));
        section.appendChild(downloadBtn);

        // Show default sample
        this.showSample('csv', formatTabs.children[0], sampleContent);

        return section;
    }

    async showSample(format, button, contentDiv) {
        // Update active tab
        Array.from(button.parentElement.children).forEach(child => {
            child.style.background = 'white';
            child.style.fontWeight = 'normal';
        });
        button.style.background = '#fff3cd';
        button.style.fontWeight = 'bold';

        try {
            const response = await fetch(`http://localhost:8000/api/sample/${format}`);
            const data = await response.json();
            contentDiv.textContent = data.sample;
        } catch (error) {
            contentDiv.textContent = `Error loading sample: ${error.message}`;
        }
    }

    async uploadFile() {
        const fileInput = document.getElementById('fileInput');
        const formatSelect = document.getElementById('formatSelect');
        const file = fileInput.files[0];
        
        if (!file) {
            alert('📁 Please select a file first!');
            return;
        }

        try {
            this.showLoading();

            const formData = new FormData();
            formData.append('file', file);
            
            const response = await fetch(`http://localhost:8000/api/upload?format_type=${formatSelect.value}&optimization_mode=${this.selectedMode}`, {
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
        
        const modeEmojis = {
            'balanced': '⚖️',
            'eco': '🌱', 
            'performance': '🚀'
        };
        
        contentDiv.innerHTML = `
            <div style="text-align: center; padding: 30px;">
                <div style="font-size: 48px; margin-bottom: 20px;">${modeEmojis[this.selectedMode]}</div>
                <p style="font-size: 18px; margin-bottom: 10px;">Running ${this.selectedMode} optimization...</p>
                <p><small>Processing your project data with AI algorithms</small></p>
                <div style="margin-top: 20px; color: #666;">
                    <div>📊 Analyzing tasks...</div>
                    <div>🔧 Optimizing resources...</div>
                    <div>🌱 Calculating carbon impact...</div>
                </div>
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
        const mode = result.mode;
        
        const modeStyles = {
            'balanced': { color: '#3498db', icon: '⚖️', title: 'Balanced Optimization' },
            'eco_friendly': { color: '#27ae60', icon: '🌱', title: 'Eco-Friendly Optimization' },
            'performance': { color: '#e74c3c', icon: '🚀', title: 'Performance Optimization' }
        };
        
        const style = modeStyles[mode] || modeStyles.balanced;

        let specialFeatures = '';
        if (mode === 'eco_friendly' && result.substitutions_made) {
            specialFeatures = `
                <div style="background: #d4edda; padding: 15px; border-radius: 5px; margin: 15px 0;">
                    <h4 style="color: #155724; margin-bottom: 10px;">🌿 Eco-Substitutions Applied:</h4>
                    <ul>
                        ${result.substitutions_made.map(sub => `<li>${sub}</li>`).join('')}
                    </ul>
                    <p><strong>${result.eco_notes}</strong></p>
                </div>
            `;
        } else if (mode === 'performance') {
            specialFeatures = `
                <div style="background: #f8d7da; padding: 15px; border-radius: 5px; margin: 15px 0;">
                    <h4 style="color: #721c24; margin-bottom: 10px;">⚡ Performance Features:</h4>
                    <p><strong>${result.performance_notes}</strong></p>
                    <p>🚨 Note: This mode prioritizes speed over cost and environmental impact</p>
                </div>
            `;
        }

        contentDiv.innerHTML = `
            <div style="border-left: 4px solid ${style.color}; padding-left: 15px; margin-bottom: 20px;">
                <h2 style="color: ${style.color}; margin: 0;">${style.icon} ${style.title}</h2>
                <p style="color: #666; margin: 5px 0 0 0;">${result.message}</p>
            </div>

            ${specialFeatures}

            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 15px; margin: 20px 0;">
                <div style="background: white; padding: 20px; border-radius: 8px; text-align: center; border: 1px solid #ddd;">
                    <h4 style="color: #2c3e50; margin: 0 0 10px 0;">💰 Total Cost</h4>
                    <div style="font-size: 28px; font-weight: bold; color: #e74c3c;">$${result.total_cost}</div>
                </div>
                
                <div style="background: white; padding: 20px; border-radius: 8px; text-align: center; border: 1px solid #ddd;">
                    <h4 style="color: #2c3e50; margin: 0 0 10px 0;">⏱️ Duration</h4>
                    <div style="font-size: 28px; font-weight: bold; color: #3498db;">${result.total_duration} days</div>
                </div>
                
                <div style="background: white; padding: 20px; border-radius: 8px; text-align: center; border: 1px solid #ddd;">
                    <h4 style="color: #2c3e50; margin: 0 0 10px 0;">🌱 Carbon Footprint</h4>
                    <div style="font-size: 28px; font-weight: bold; color: #27ae60;">${result.carbon_estimate} kg CO₂</div>
                </div>
            </div>

            <div style="background: white; padding: 20px; border-radius: 8px; margin: 20px 0;">
                <h4 style="color: #2c3e50; margin-bottom: 15px;">📅 Optimized Schedule</h4>
                <div style="max-height: 300px; overflow-y: auto;">
                    <pre style="background: #f8f9fa; padding: 15px; border-radius: 5px; font-size: 12px;">${JSON.stringify(result.schedule, null, 2)}</pre>
                </div>
            </div>

            <div style="text-align: center; margin-top: 20px;">
                <button onclick="location.reload()" style="padding: 10px 20px; background: #3498db; color: white; border: none; border-radius: 5px; cursor: pointer;">
                    🔄 Optimize Another Project
                </button>
            </div>
        `;
        
        resultsDiv.style.display = 'block';
    }

    downloadSample() {
        const sampleContent = document.getElementById('sampleContent');
        const activeTab = Array.from(document.querySelectorAll('button')).find(btn => 
            btn.style.background === 'rgb(255, 243, 205)'
        );
        
        let format = 'csv';
        if (activeTab) {
            format = activeTab.textContent.toLowerCase();
        }
        
        const content = sampleContent.textContent;
        const blob = new Blob([content], {type: 'text/plain'});
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `construction_sample.${format}`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }
}

// Initialize the app
document.addEventListener('DOMContentLoaded', () => {
    new ConstructionOptimizer();
});