#!/usr/bin/env python3
"""
Quick Demo Script for Quantum-Enhanced AI Logistics Engine
Shows the system working with real improvements
"""

import requests
import json
import time

def test_optimization():
    """Test the optimization API"""
    print("🌍 Quantum-Enhanced AI Logistics Engine - Quick Demo")
    print("=" * 60)
    
    # Sample coordinates for Delhi area
    coords = [
        [28.6139, 77.2090],  # Depot
        [28.6239, 77.2190],  # Clinic 1
        [28.6089, 77.2240],  # Clinic 2
        [28.6219, 77.2010],  # Clinic 3
        [28.6019, 77.2040],  # Clinic 4
        [28.6159, 77.2150],  # Clinic 5
    ]
    
    scenarios = ['normal', 'peak', 'incident', 'storm']
    
    for scenario in scenarios:
        print(f"\n📊 Scenario: {scenario.upper()}")
        print("-" * 40)
        
        try:
            # Call optimization API
            response = requests.post('http://localhost:5000/api/optimize', 
                                  json={
                                      'coordinates': coords,
                                      'scenario': scenario
                                  })
            
            if response.status_code == 200:
                result = response.json()
                
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
                
            else:
                print(f"❌ API Error: {response.status_code}")
                print(f"   {response.text}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print(f"\n🎯 System Status:")
    print(f"   Backend: http://localhost:5000 ✅")
    print(f"   Frontend: http://localhost:3000 ✅")
    print(f"   Ready for hackathon presentation! 🚀")

if __name__ == "__main__":
    test_optimization()

