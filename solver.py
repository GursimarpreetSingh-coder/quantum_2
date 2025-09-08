"""
Main Solver - Quantum-Enhanced AI Logistics Engine
Integrates traffic prediction, QUBO optimization, and quantum solving
"""

import numpy as np
import json
import time
from typing import List, Tuple, Dict, Optional
from flask import Flask, request, jsonify
from flask_cors import CORS

from traffic_simulator import TrafficSimulator, create_sample_coordinates
from qubo_builder import QUBOBuilder
from quantum_solver import RouteOptimizer, create_baseline_route

app = Flask(__name__)
CORS(app)

class LogisticsEngine:
    """Main logistics optimization engine"""
    
    def __init__(self):
        self.traffic_simulator = TrafficSimulator()
        self.route_optimizer = RouteOptimizer(solver_type='auto')
        self.optimization_history = []
        
    def optimize_delivery_route(self, 
                              coords: List[Tuple[float, float]],
                              scenario: str = 'normal',
                              time_windows: Optional[List[Tuple[float, float]]] = None,
                              problem_type: str = 'tsp') -> Dict:
        """
        Main optimization function
        
        Args:
            coords: List of (lat, lon) coordinates
            scenario: Traffic scenario ('normal', 'peak', 'incident', 'storm')
            time_windows: Optional time windows for each node
            problem_type: 'tsp' or 'vrp'
            
        Returns:
            Dictionary with optimization results
        """
        print(f"🚀 Starting optimization for {len(coords)} nodes, scenario: {scenario}")
        
        # Step 1: Simulate traffic conditions
        traffic_result = self.traffic_simulator.simulate_scenario(coords, scenario)
        time_matrix = traffic_result['time_matrix']
        
        print(f"📊 Traffic simulation complete - Weather: {traffic_result['weather']}")
        print(f"   Active incidents: {len(traffic_result['incidents'])}")
        
        # Step 2: Create baseline route for comparison
        baseline_route = create_baseline_route(time_matrix)
        baseline_time = self.route_optimizer._calculate_route_time(baseline_route, time_matrix)
        
        print(f"📍 Baseline route: {baseline_route}")
        print(f"   Baseline time: {baseline_time:.2f} minutes")
        
        # Step 3: Optimize route using quantum/classical solver
        optimization_result = self.route_optimizer.optimize_route(
            time_matrix, time_windows, problem_type
        )
        
        print(f"⚛️ Quantum optimization complete!")
        print(f"   Optimized route: {optimization_result['route']}")
        print(f"   Optimized time: {optimization_result['total_time']:.2f} minutes")
        print(f"   Solver: {optimization_result['solver_type']}")
        print(f"   Solve time: {optimization_result['solve_time']:.3f} seconds")
        
        # Step 4: Compare results
        comparison = self.route_optimizer.compare_with_baseline(
            time_matrix, baseline_route, optimization_result['route']
        )
        
        # Step 5: Calculate additional metrics
        co2_savings = self._calculate_co2_savings(comparison['time_saved'])
        fuel_savings = self._calculate_fuel_savings(comparison['time_saved'])
        
        # Compile final result
        result = {
            'success': True,
            'scenario': scenario,
            'traffic_conditions': {
                'weather': traffic_result['weather'],
                'incidents': len(traffic_result['incidents']),
                'current_time': traffic_result['current_time']
            },
            'baseline': {
                'route': baseline_route,
                'total_time': baseline_time,
                'on_time_deliveries': self.route_optimizer._calculate_on_time_deliveries(
                    baseline_route, time_matrix, time_windows
                )
            },
            'optimized': {
                'route': optimization_result['route'],
                'total_time': optimization_result['total_time'],
                'on_time_deliveries': optimization_result['on_time_deliveries'],
                'energy': optimization_result['energy'],
                'solve_time': optimization_result['solve_time'],
                'solver_type': optimization_result['solver_type']
            },
            'improvement': {
                'time_saved_minutes': comparison['time_saved'],
                'improvement_percent': comparison['improvement_percent'],
                'co2_savings_kg': co2_savings,
                'fuel_savings_liters': fuel_savings
            },
            'coordinates': coords,
            'time_matrix': time_matrix.tolist(),
            'timestamp': time.time()
        }
        
        # Store in history
        self.optimization_history.append(result)
        
        return result
    
    def _calculate_co2_savings(self, time_saved_minutes: float) -> float:
        """Calculate CO2 savings from time reduction"""
        # Assume average speed of 30 km/h and 0.2 kg CO2 per km
        distance_saved_km = (time_saved_minutes / 60) * 30  # km
        co2_savings = distance_saved_km * 0.2  # kg CO2
        return co2_savings
    
    def _calculate_fuel_savings(self, time_saved_minutes: float) -> float:
        """Calculate fuel savings from time reduction"""
        # Assume average speed of 30 km/h and 0.08 L fuel per km
        distance_saved_km = (time_saved_minutes / 60) * 30  # km
        fuel_savings = distance_saved_km * 0.08  # liters
        return fuel_savings
    
    def get_optimization_history(self) -> List[Dict]:
        """Get optimization history"""
        return self.optimization_history
    
    def clear_history(self):
        """Clear optimization history"""
        self.optimization_history = []

# Global engine instance
engine = LogisticsEngine()

@app.route('/api/optimize', methods=['POST'])
def optimize_route():
    """API endpoint for route optimization"""
    try:
        data = request.get_json()
        
        coords = data.get('coordinates', [])
        scenario = data.get('scenario', 'normal')
        time_windows = data.get('time_windows', None)
        problem_type = data.get('problem_type', 'tsp')
        
        if not coords:
            return jsonify({'error': 'No coordinates provided'}), 400
        
        if len(coords) < 2:
            return jsonify({'error': 'At least 2 coordinates required'}), 400
        
        # Run optimization
        result = engine.optimize_delivery_route(coords, scenario, time_windows, problem_type)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/history', methods=['GET'])
def get_history():
    """Get optimization history"""
    return jsonify(engine.get_optimization_history())

@app.route('/api/clear', methods=['POST'])
def clear_history():
    """Clear optimization history"""
    engine.clear_history()
    return jsonify({'success': True})

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': time.time(),
        'available_solvers': engine.route_optimizer.solver.available_solvers
    })

@app.route('/api/sample', methods=['GET'])
def get_sample_data():
    """Get sample coordinates for testing"""
    coords = create_sample_coordinates()
    time_windows = [
        (0, 480),    # Depot: 0 to 8 hours
        (60, 180),   # Clinic 1: 1-3 hours
        (120, 240),  # Clinic 2: 2-4 hours
        (180, 300),  # Clinic 3: 3-5 hours
        (240, 360),  # Clinic 4: 4-6 hours
        (300, 420),  # Clinic 5: 5-7 hours
        (360, 480),  # Clinic 6: 6-8 hours
        (420, 540),  # Clinic 7: 7-9 hours
        (480, 600),  # Clinic 8: 8-10 hours
    ]
    
    return jsonify({
        'coordinates': coords,
        'time_windows': time_windows[:len(coords)],
        'scenarios': ['normal', 'peak', 'incident', 'storm']
    })

def run_demo():
    """Run a demonstration of the logistics engine"""
    print("🌍 Quantum-Enhanced AI Logistics Engine - Demo")
    print("=" * 60)
    
    # Create sample problem
    coords = create_sample_coordinates()
    time_windows = [
        (0, 480),    # Depot: 0 to 8 hours
        (60, 180),   # Clinic 1: 1-3 hours
        (120, 240),  # Clinic 2: 2-4 hours
        (180, 300),  # Clinic 3: 3-5 hours
        (240, 360),  # Clinic 4: 4-6 hours
    ]
    
    scenarios = ['normal', 'peak', 'incident', 'storm']
    
    for scenario in scenarios:
        print(f"\n📊 Scenario: {scenario.upper()}")
        print("-" * 40)
        
        try:
            result = engine.optimize_delivery_route(coords, scenario, time_windows)
            
            print(f"✅ Optimization successful!")
            print(f"Baseline time: {result['baseline']['total_time']:.2f} minutes")
            print(f"Optimized time: {result['optimized']['total_time']:.2f} minutes")
            print(f"Improvement: {result['improvement']['improvement_percent']:.1f}%")
            print(f"Time saved: {result['improvement']['time_saved_minutes']:.2f} minutes")
            print(f"CO2 savings: {result['improvement']['co2_savings_kg']:.2f} kg")
            print(f"Solver: {result['optimized']['solver_type']}")
            print(f"On-time deliveries: {result['optimized']['on_time_deliveries']:.1f}%")
            
        except Exception as e:
            print(f"❌ Error in scenario {scenario}: {e}")
    
    print(f"\n📈 Total optimizations: {len(engine.get_optimization_history())}")

if __name__ == "__main__":
    print("🚀 Starting Quantum-Enhanced AI Logistics Engine")
    print("=" * 60)
    
    # Run demo
    run_demo()
    
    # Start Flask server
    print(f"\n🌐 Starting web server on http://localhost:5000")
    print("Available endpoints:")
    print("  POST /api/optimize - Optimize delivery route")
    print("  GET  /api/history - Get optimization history")
    print("  POST /api/clear - Clear history")
    print("  GET  /api/health - Health check")
    print("  GET  /api/sample - Get sample data")
    
    app.run(host='0.0.0.0', port=5000, debug=True)
