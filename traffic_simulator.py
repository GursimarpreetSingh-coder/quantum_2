"""
AI Traffic Predictor and Time-Dependent Travel Time Simulator
Part of the Quantum-Enhanced AI Logistics Engine
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Tuple, Dict, Optional
import json

class TrafficPredictor:
    """AI-based traffic prediction using historical patterns and real-time data"""
    
    def __init__(self):
        self.base_speed_kmph = 30.0  # Base speed in km/h
        self.peak_hours = [(7, 10), (17, 20)]  # Peak traffic hours
        self.weather_impact = {
            'clear': 1.0,
            'rain': 1.3,
            'fog': 1.5,
            'storm': 1.8
        }
        
    def haversine_distance(self, coord1: Tuple[float, float], coord2: Tuple[float, float]) -> float:
        """Calculate distance between two coordinates in kilometers"""
        lat1, lon1 = coord1
        lat2, lon2 = coord2
        
        # Convert to radians
        lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
        
        # Haversine formula
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2
        c = 2 * np.arcsin(np.sqrt(a))
        r = 6371  # Earth's radius in kilometers
        return c * r
    
    def get_time_multiplier(self, hour: int, day_of_week: int, weather: str = 'clear') -> float:
        """Get traffic multiplier based on time and conditions"""
        multiplier = 1.0
        
        # Peak hour multiplier
        for start_hour, end_hour in self.peak_hours:
            if start_hour <= hour <= end_hour:
                multiplier *= 1.4
                break
        
        # Weekend effect (lighter traffic on weekends)
        if day_of_week >= 5:  # Saturday = 5, Sunday = 6
            multiplier *= 0.8
        
        # Weather impact
        multiplier *= self.weather_impact.get(weather, 1.0)
        
        return multiplier
    
    def predict_incident_impact(self, incident_type: str, severity: float = 1.0) -> float:
        """Predict impact of traffic incidents"""
        incident_multipliers = {
            'accident': 1.8,
            'construction': 1.5,
            'road_closure': 2.0,
            'protest': 1.6,
            'none': 1.0
        }
        return incident_multipliers.get(incident_type, 1.0) * severity

class TrafficSimulator:
    """Simulates time-dependent travel times for route optimization"""
    
    def __init__(self):
        self.predictor = TrafficPredictor()
        self.incidents = {}  # Store active incidents
        
    def add_incident(self, edge_id: str, incident_type: str, severity: float = 1.0, 
                    start_time: Optional[datetime] = None, duration_hours: float = 2.0):
        """Add a traffic incident to the simulation"""
        if start_time is None:
            start_time = datetime.now()
        
        end_time = start_time + timedelta(hours=duration_hours)
        
        self.incidents[edge_id] = {
            'type': incident_type,
            'severity': severity,
            'start_time': start_time,
            'end_time': end_time,
            'multiplier': self.predictor.predict_incident_impact(incident_type, severity)
        }
    
    def get_edge_multiplier(self, edge_id: str, current_time: datetime) -> float:
        """Get traffic multiplier for a specific edge at current time"""
        if edge_id not in self.incidents:
            return 1.0
        
        incident = self.incidents[edge_id]
        if incident['start_time'] <= current_time <= incident['end_time']:
            return incident['multiplier']
        
        return 1.0
    
    def compute_travel_time_matrix(self, coords: List[Tuple[float, float]], 
                                 current_time: Optional[datetime] = None,
                                 weather: str = 'clear') -> np.ndarray:
        """Compute time-dependent travel time matrix"""
        if current_time is None:
            current_time = datetime.now()
        
        n = len(coords)
        time_matrix = np.zeros((n, n))
        
        for i in range(n):
            for j in range(n):
                if i == j:
                    continue
                
                # Base travel time
                distance_km = self.predictor.haversine_distance(coords[i], coords[j])
                base_time_minutes = (distance_km / self.predictor.base_speed_kmph) * 60
                
                # Apply time-based multiplier
                hour = current_time.hour
                day_of_week = current_time.weekday()
                time_multiplier = self.predictor.get_time_multiplier(hour, day_of_week, weather)
                
                # Apply incident multiplier
                edge_id = f"{i}-{j}"
                incident_multiplier = self.get_edge_multiplier(edge_id, current_time)
                
                # Final travel time
                time_matrix[i, j] = base_time_minutes * time_multiplier * incident_multiplier
        
        return time_matrix
    
    def simulate_scenario(self, coords: List[Tuple[float, float]], 
                         scenario: str = 'normal') -> Dict:
        """Simulate different traffic scenarios"""
        current_time = datetime.now()
        
        if scenario == 'normal':
            weather = 'clear'
            incidents = {}
        elif scenario == 'peak':
            weather = 'clear'
            # Force peak hour
            current_time = current_time.replace(hour=8, minute=30)
            incidents = {}
        elif scenario == 'incident':
            weather = 'rain'
            # Add a major incident
            self.add_incident("0-1", "accident", severity=1.5)
            self.add_incident("1-2", "construction", severity=1.2)
        elif scenario == 'storm':
            weather = 'storm'
            # Add multiple incidents
            for i in range(len(coords) - 1):
                self.add_incident(f"{i}-{i+1}", "road_closure", severity=2.0)
        
        time_matrix = self.compute_travel_time_matrix(coords, current_time, weather)
        
        return {
            'time_matrix': time_matrix,
            'scenario': scenario,
            'weather': weather,
            'current_time': current_time.isoformat(),
            'incidents': self.incidents.copy()
        }

def create_sample_coordinates() -> List[Tuple[float, float]]:
    """Create sample coordinates for a district hospital and clinics"""
    # Sample coordinates for a district in India (approximate)
    base_lat, base_lon = 28.6139, 77.2090  # Delhi area
    
    coords = [
        (base_lat, base_lon),  # District Hospital (depot)
        (base_lat + 0.01, base_lon + 0.01),  # Clinic 1
        (base_lat - 0.005, base_lon + 0.015),  # Clinic 2
        (base_lat + 0.008, base_lon - 0.008),  # Clinic 3
        (base_lat - 0.012, base_lon - 0.005),  # Clinic 4
        (base_lat + 0.015, base_lon + 0.005),  # Clinic 5
        (base_lat - 0.008, base_lon + 0.012),  # Clinic 6
        (base_lat + 0.005, base_lon - 0.012),  # Clinic 7
        (base_lat - 0.015, base_lon - 0.008),  # Clinic 8
    ]
    
    return coords

if __name__ == "__main__":
    # Test the traffic simulator
    simulator = TrafficSimulator()
    coords = create_sample_coordinates()
    
    print("🌍 Quantum-Enhanced AI Logistics Engine - Traffic Simulator")
    print("=" * 60)
    
    scenarios = ['normal', 'peak', 'incident', 'storm']
    
    for scenario in scenarios:
        print(f"\n📊 Scenario: {scenario.upper()}")
        result = simulator.simulate_scenario(coords, scenario)
        
        print(f"Weather: {result['weather']}")
        print(f"Time: {result['current_time']}")
        print(f"Active incidents: {len(result['incidents'])}")
        
        # Show sample travel times from depot to first few clinics
        print("Sample travel times from depot (minutes):")
        for i in range(1, min(4, len(coords))):
            time_min = result['time_matrix'][0, i]
            print(f"  Depot → Clinic {i}: {time_min:.1f} min")
        
        print("-" * 40)
