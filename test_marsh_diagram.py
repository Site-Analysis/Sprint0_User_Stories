"""
Quick test script for the updated Andrew Marsh style sun path diagram
"""

import requests
import json

API_BASE_URL = "http://localhost:8000"

def test_polar_diagram():
    """Test the new multi-seasonal polar diagram"""
    print("=" * 60)
    print("Testing Andrew Marsh Style Sun Path Diagram")
    print("=" * 60)
    
    # Test data: New York City
    data = {
        "latitude": 40.7128,
        "longitude": -74.0060,
        "date": "2025-06-21",  # Summer solstice
        "current_time": "12:00",
        "timezone": "America/New_York",
        "diagram_type": "polar"
    }
    
    print(f"\nGenerating diagram for:")
    print(f"  Location: NYC (40.71°N, 74.01°W)")
    print(f"  Date: {data['date']}")
    print(f"  Time: {data['current_time']}")
    print(f"  Type: {data['diagram_type']}")
    
    try:
        response = requests.post(f"{API_BASE_URL}/sun-path", json=data)
        
        if response.status_code == 200:
            print("\n✅ SUCCESS! Diagram generated.")
            
            # Save the image
            with open("andrew_marsh_style_diagram.png", "wb") as f:
                f.write(response.content)
            print("   Saved to: andrew_marsh_style_diagram.png")
            print("\n📊 The diagram should show:")
            print("   • Summer Solstice path (Jun 21) - Dark orange")
            print("   • Equinox path (Mar 21/Sep 23) - Orange")
            print("   • Winter Solstice path (Dec 21) - Gold")
            print("   • Hourly markers (6 AM - 6 PM) with labels")
            print("   • Current sun position as red dot at 12:00")
            print("   • Altitude circles at 10° intervals")
            print("   • Azimuth lines at 30° intervals")
            print("   • Compass labels (N, E, S, W)")
            
        else:
            error = response.json()
            print(f"\n❌ ERROR: {error}")
            
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Cannot connect to server!")
        print("   Make sure the server is running:")
        print("   python server.py")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")

if __name__ == "__main__":
    test_polar_diagram()
