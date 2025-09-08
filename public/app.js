// Quantum-Enhanced AI Logistics Engine - Frontend Application

class LogisticsApp {
    constructor() {
        this.map = null;
        this.markers = [];
        this.routes = [];
        this.coordinates = [];
        this.currentScenario = 'normal';
        this.isOptimizing = false;
        
        this.init();
    }
    
    async fetchWithRetry(url, options = {}, retries = 3, backoffMs = 700) {
        for (let attempt = 1; attempt <= retries; attempt++) {
            try {
                const res = await fetch(url, options);
                if (!res.ok) {
                    let details = '';
                    try { const err = await res.json(); details = err.error || JSON.stringify(err); } catch {}
                    throw new Error(`HTTP ${res.status} ${res.statusText}${details ? ` - ${details}` : ''}`);
                }
                return res;
            } catch (e) {
                if (attempt === retries) throw e;
                await new Promise(r => setTimeout(r, backoffMs * attempt));
            }
        }
    }
    
    init() {
        this.initMap();
        this.bindEvents();
        this.updateStatus('Ready');
    }
    
    initMap() {
        // Initialize Leaflet map centered on Delhi, India
        this.map = L.map('map').setView([28.6139, 77.2090], 11);
        
        // Add OpenStreetMap tiles
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap contributors',
            maxZoom: 18
        }).addTo(this.map);
        
        // Add click handler for adding nodes
        this.map.on('click', (e) => {
            if (!this.isOptimizing) {
                this.addNode(e.latlng);
            }
        });
    }
    
    bindEvents() {
        document.getElementById('loadSample').addEventListener('click', () => {
            this.loadSampleData();
        });
        
        document.getElementById('clearMap').addEventListener('click', () => {
            this.clearMap();
        });
        
        document.getElementById('optimizeRoute').addEventListener('click', () => {
            this.optimizeRoute();
        });
        
        document.getElementById('scenario').addEventListener('change', (e) => {
            this.currentScenario = e.target.value;
        });

        const toggle = document.getElementById('themeToggle');
        if (toggle) {
            toggle.addEventListener('change', (e) => {
                document.documentElement.classList.toggle('dark', e.target.checked);
                this.toast(e.target.checked ? 'Dark mode enabled' : 'Light mode enabled', 'success');
            });
        }
    }
    
    addNode(latlng) {
        const nodeIndex = this.coordinates.length;
        this.coordinates.push([latlng.lat, latlng.lng]);
        
        // Create marker
        const marker = L.circleMarker(latlng, {
            radius: nodeIndex === 0 ? 12 : 8,
            fillColor: nodeIndex === 0 ? '#dc3545' : '#667eea',
            color: 'white',
            weight: 3,
            opacity: 1,
            fillOpacity: 0.8
        }).addTo(this.map);
        
        // Add popup
        const label = nodeIndex === 0 ? 'Depot' : `Node ${nodeIndex}`;
        marker.bindPopup(`<b>${label}</b><br>Lat: ${latlng.lat.toFixed(4)}<br>Lng: ${latlng.lng.toFixed(4)}`);
        
        this.markers.push(marker);
        
        console.log(`Added node ${nodeIndex}:`, latlng);
    }
    
    loadSampleData() {
        this.clearMap();
        
        // Load sample data from API (with retry)
        this.fetchWithRetry('/api/sample')
            .then(response => response.json())
            .then(data => {
                this.coordinates = data.coordinates;
                this.timeWindows = data.time_windows;
                
                // Add markers to map
                this.coordinates.forEach((coord, index) => {
                    const latlng = L.latLng(coord[0], coord[1]);
                    this.addNode(latlng);
                });
                
                // Fit map to show all markers
                if (this.markers.length > 0) {
                    const group = new L.featureGroup(this.markers);
                    this.map.fitBounds(group.getBounds().pad(0.1));
                }
                
                this.updateStatus(`Loaded ${this.coordinates.length} sample nodes`);
            })
            .catch(error => {
                console.error('Error loading sample data:', error);
                this.updateStatus('Sample load failed. Please retry.', 'error');
            });
    }
    
    clearMap() {
        // Remove all markers
        this.markers.forEach(marker => {
            this.map.removeLayer(marker);
        });
        this.markers = [];
        
        // Remove all routes
        this.routes.forEach(route => {
            this.map.removeLayer(route);
        });
        this.routes = [];
        
        this.coordinates = [];
        this.updateStatus('Map cleared');
    }
    
    async optimizeRoute() {
        if (this.coordinates.length < 2) {
            this.updateStatus('Please add at least 2 nodes', 'error');
            return;
        }
        
        if (this.isOptimizing) {
            return;
        }
        
        this.isOptimizing = true;
        this.updateStatus('Optimizing route...', 'optimizing');
        this.showLoading(true);
        this.setButtonsDisabled(true);
        
        try {
            const response = await this.fetchWithRetry('/api/optimize', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    coordinates: this.coordinates,
                    scenario: this.currentScenario,
                    time_windows: this.timeWindows,
                    problem_type: 'tsp'
                })
            }, 3, 800);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const result = await response.json();
            this.displayResults(result);
            
        } catch (error) {
            console.error('Optimization error:', error);
            const hint = `${error?.message || error}`;
            this.updateStatus(`Optimization failed. ${hint.includes('404') ? 'Endpoint missing. Refresh and try again.' : 'Please try again.'}`, 'error');
            this.toast('Optimization failed', 'error');
        } finally {
            this.isOptimizing = false;
            this.showLoading(false);
            this.setButtonsDisabled(false);
        }
    }
    
    displayResults(result) {
        if (!result.success) {
            this.updateStatus('Optimization failed', 'error');
            return;
        }
        
        // Update status
        this.updateStatus(`Optimization complete! ${result.improvement.improvement_percent.toFixed(1)}% improvement`);
        
        // Display routes
        this.displayRoutes(result);
        
        // Update metrics
        this.updateMetrics(result);
        
        // Display detailed results
        this.displayDetailedResults(result);
    }
    
    displayRoutes(result) {
        // Clear existing routes
        this.routes.forEach(route => {
            this.map.removeLayer(route);
        });
        this.routes = [];
        
        // Display baseline route
        if (result.baseline.route) {
            this.drawRoute(result.baseline.route, '#dc3545', 'Baseline Route', true, result.baseline.total_time);
        }
        
        // Display optimized route
        if (result.optimized.route) {
            this.drawRoute(result.optimized.route, '#28a745', 'Optimized Route', false, result.optimized.total_time);
        }
    }
    
    drawRoute(route, color, label, isDashed, totalTimeMinutes) {
        if (route.length < 2) return;
        
        const routeCoords = route.map(nodeIndex => {
            const coord = this.coordinates[nodeIndex];
            return [coord[0], coord[1]];
        });
        
        // Add return to depot if needed
        if (route[route.length - 1] !== 0) {
            routeCoords.push([this.coordinates[0][0], this.coordinates[0][1]]);
        }
        
        const polyline = L.polyline(routeCoords, {
            color: color,
            weight: isDashed ? 4 : 5,
            opacity: 0.8,
            dashArray: isDashed ? '10, 10' : null
        }).addTo(this.map);
        
        const timeStr = typeof totalTimeMinutes === 'number' ? totalTimeMinutes.toFixed(1) : 'N/A';
        polyline.bindPopup(`<b>${label}</b><br>Total time: ${timeStr} minutes`);
        
        this.routes.push(polyline);
    }
    
    updateMetrics(result) {
        document.getElementById('timeImprovement').textContent = 
            `${result.improvement.improvement_percent.toFixed(1)}%`;
        
        document.getElementById('co2Savings').textContent = 
            `${result.improvement.co2_savings_kg.toFixed(2)} kg`;
        
        document.getElementById('fuelSavings').textContent = 
            `${result.improvement.fuel_savings_liters.toFixed(2)} L`;
        
        document.getElementById('onTimeRate').textContent = 
            `${result.optimized.on_time_deliveries.toFixed(1)}%`;
    }
    
    displayDetailedResults(result) {
        const resultsDiv = document.getElementById('results');
        
        resultsDiv.innerHTML = `
            <div class="route-info">
                <h4>🚚 Baseline Route</h4>
                <p><strong>Route:</strong> ${result.baseline.route.join(' → ')}</p>
                <p><strong>Total Time:</strong> ${result.baseline.total_time.toFixed(2)} minutes</p>
                <p><strong>On-Time Deliveries:</strong> ${result.baseline.on_time_deliveries.toFixed(1)}%</p>
            </div>
            
            <div class="route-info">
                <h4>⚛️ Optimized Route</h4>
                <p><strong>Route:</strong> ${result.optimized.route.join(' → ')}</p>
                <p><strong>Total Time:</strong> ${result.optimized.total_time.toFixed(2)} minutes</p>
                <p><strong>On-Time Deliveries:</strong> ${result.optimized.on_time_deliveries.toFixed(1)}%</p>
                <p><strong>Solver:</strong> ${result.optimized.solver_type}</p>
                <p><strong>Solve Time:</strong> ${result.optimized.solve_time.toFixed(3)} seconds</p>
            </div>
            
            <div class="route-info">
                <h4>📊 Improvement Metrics</h4>
                <p><strong>Time Saved:</strong> ${result.improvement.time_saved_minutes.toFixed(2)} minutes</p>
                <p><strong>Improvement:</strong> ${result.improvement.improvement_percent.toFixed(1)}%</p>
                <p><strong>CO₂ Savings:</strong> ${result.improvement.co2_savings_kg.toFixed(2)} kg</p>
                <p><strong>Fuel Savings:</strong> ${result.improvement.fuel_savings_liters.toFixed(2)} liters</p>
            </div>
            
            <div class="route-info">
                <h4>🌦️ Traffic Conditions</h4>
                <p><strong>Scenario:</strong> ${result.scenario}</p>
                <p><strong>Weather:</strong> ${result.traffic_conditions.weather}</p>
                <p><strong>Active Incidents:</strong> ${result.traffic_conditions.incidents}</p>
            </div>
        `;
    }
    
    updateStatus(message, type = 'normal') {
        const statusDiv = document.getElementById('status');
        statusDiv.textContent = message;
        statusDiv.className = `status ${type}`;
        
        console.log(`Status: ${message}`);
    }

    showLoading(show) {
        const overlay = document.getElementById('loadingOverlay');
        if (!overlay) return;
        overlay.classList.toggle('hidden', !show);
    }

    setButtonsDisabled(disabled) {
        ['loadSample','clearMap','optimizeRoute'].forEach(id => {
            const el = document.getElementById(id);
            if (el) el.disabled = disabled;
        });
    }

    toast(message, variant = 'success') {
        const container = document.getElementById('toasts');
        if (!container) return;
        const node = document.createElement('div');
        node.className = `toast ${variant}`;
        node.textContent = message;
        container.appendChild(node);
        setTimeout(() => container.removeChild(node), 3500);
    }
}

// Initialize the application when the page loads
document.addEventListener('DOMContentLoaded', () => {
    new LogisticsApp();
});
