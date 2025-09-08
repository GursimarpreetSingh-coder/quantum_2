#!/usr/bin/env python3
"""
Demo script for Quantum-Enhanced AI Logistics Engine
D3CODE 2025 Hackathon Project
"""

import time
import json
from solver import LogisticsEngine
from traffic_simulator import create_sample_coordinates

def run_demo():
    """Run a comprehensive demonstration"""
    print("🌍 Quantum-Enhanced AI Logistics Engine - Demo")
    print("=" * 60)
    print("D3CODE 2025 Hackathon Project")
    print("AI + Quantum + Data Ecosystems")
    print("=" * 60)
    
    # Initialize the engine
    engine = LogisticsEngine()
    
    # Create sample problem
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
    
    print(f"📍 Sample Problem: {len(coords)} nodes")
    print(f"   Depot: {coords[0]}")
    print(f"   Clinics: {len(coords)-1} locations")
    print()
    
    scenarios = [
        ('normal', 'Normal Day - Clear weather, no incidents'),
        ('peak', 'Peak Traffic - Rush hour conditions'),
        ('incident', 'Traffic Incident - Accident blocking major route'),
        ('storm', 'Storm Conditions - Weather delays and closures')
    ]
    
    results = []
    
    for scenario, description in scenarios:
        print(f"📊 Scenario: {scenario.upper()}")
        print(f"   {description}")
        print("-" * 50)
        
        try:
            start_time = time.time()
            result = engine.optimize_delivery_route(coords, scenario, time_windows)
            solve_time = time.time() - start_time
            
            print(f"✅ Optimization successful!")
            print(f"   Baseline time: {result['baseline']['total_time']:.2f} minutes")
            print(f"   Optimized time: {result['optimized']['total_time']:.2f} minutes")
            print(f"   Improvement: {result['improvement']['improvement_percent']:.1f}%")
            print(f"   Time saved: {result['improvement']['time_saved_minutes']:.2f} minutes")
            print(f"   CO₂ savings: {result['improvement']['co2_savings_kg']:.2f} kg")
            print(f"   Fuel savings: {result['improvement']['fuel_savings_liters']:.2f} L")
            print(f"   On-time rate: {result['optimized']['on_time_deliveries']:.1f}%")
            print(f"   Solver: {result['optimized']['solver_type']}")
            print(f"   Solve time: {result['optimized']['solve_time']:.3f} seconds")
            print(f"   Total demo time: {solve_time:.3f} seconds")
            
            results.append({
                'scenario': scenario,
                'description': description,
                'result': result,
                'demo_time': solve_time
            })
            
        except Exception as e:
            print(f"❌ Error in scenario {scenario}: {e}")
            results.append({
                'scenario': scenario,
                'description': description,
                'error': str(e)
            })
        
        print()
    
    # Summary
    print("📈 DEMO SUMMARY")
    print("=" * 60)
    
    successful_scenarios = [r for r in results if 'result' in r]
    
    if successful_scenarios:
        avg_improvement = sum(r['result']['improvement']['improvement_percent'] 
                            for r in successful_scenarios) / len(successful_scenarios)
        total_time_saved = sum(r['result']['improvement']['time_saved_minutes'] 
                             for r in successful_scenarios)
        total_co2_saved = sum(r['result']['improvement']['co2_savings_kg'] 
                            for r in successful_scenarios)
        total_fuel_saved = sum(r['result']['improvement']['fuel_savings_liters'] 
                             for r in successful_scenarios)
        
        print(f"✅ Successful scenarios: {len(successful_scenarios)}/{len(scenarios)}")
        print(f"📊 Average improvement: {avg_improvement:.1f}%")
        print(f"⏱️ Total time saved: {total_time_saved:.2f} minutes")
        print(f"🌱 Total CO₂ saved: {total_co2_saved:.2f} kg")
        print(f"⛽ Total fuel saved: {total_fuel_saved:.2f} L")
        
        # Show best scenario
        best_scenario = max(successful_scenarios, 
                          key=lambda x: x['result']['improvement']['improvement_percent'])
        print(f"🏆 Best scenario: {best_scenario['scenario']} "
              f"({best_scenario['result']['improvement']['improvement_percent']:.1f}% improvement)")
    
    print(f"\n🎯 Key Benefits Demonstrated:")
    print(f"   • Real-time traffic adaptation")
    print(f"   • Quantum-inspired optimization")
    print(f"   • Time window compliance")
    print(f"   • Environmental impact reduction")
    print(f"   • Scalable to larger problems")
    
    print(f"\n🚀 Ready for hackathon presentation!")
    print(f"   Frontend: http://localhost:3000")
    print(f"   API: http://localhost:5000")
    
    return results

def run_quick_test():
    """Run a quick test with minimal output"""
    print("🧪 Quick Test - Quantum Logistics Engine")
    print("=" * 40)
    
    engine = LogisticsEngine()
    coords = create_sample_coordinates()[:5]  # Use only 5 nodes for quick test
    time_windows = [(0, 480), (60, 180), (120, 240), (180, 300), (240, 360)]
    
    result = engine.optimize_delivery_route(coords, 'normal', time_windows)
    
    print(f"✅ Test passed!")
    print(f"   Improvement: {result['improvement']['improvement_percent']:.1f}%")
    print(f"   Solver: {result['optimized']['solver_type']}")
    print(f"   Solve time: {result['optimized']['solve_time']:.3f}s")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == '--quick':
        run_quick_test()
    else:
        run_demo()
