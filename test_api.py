#!/usr/bin/env python3
"""
Test script to verify API endpoints
"""

import requests
import json

def test_endpoints():
    """Test all API endpoints"""
    base_url = "http://localhost:5000"
    
    print("🧪 Testing API Endpoints")
    print("=" * 40)
    
    # Test health endpoint
    try:
        response = requests.get(f"{base_url}/api/health")
        print(f"✅ Health: {response.status_code}")
        if response.status_code == 200:
            print(f"   Data: {response.json()}")
    except Exception as e:
        print(f"❌ Health: {e}")
    
    # Test sample endpoint
    try:
        response = requests.get(f"{base_url}/api/sample")
        print(f"✅ Sample: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Coordinates: {len(data.get('coordinates', []))}")
    except Exception as e:
        print(f"❌ Sample: {e}")
    
    # Test optimize endpoint
    try:
        test_data = {
            "coordinates": [[28.6139, 77.2090], [28.6239, 77.2190]],
            "scenario": "normal"
        }
        response = requests.post(f"{base_url}/api/optimize", json=test_data)
        print(f"✅ Optimize: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Improvement: {data.get('improvement', {}).get('improvement_percent', 0):.1f}%")
    except Exception as e:
        print(f"❌ Optimize: {e}")

if __name__ == "__main__":
    test_endpoints()

