# Solar Position API - Usage Examples

## Example 1: Calculate Solar Position for Specific Location and Time

### New York City - Summer Solstice at Noon

```python
import requests
import json

# API endpoint
url = "http://localhost:8000/solar-position"

# Request data
data = {
    "latitude": 40.7128,
    "longitude": -74.0060,
    "date": "2025-06-21",  # Summer solstice
    "time": "12:00",       # Noon
    "timezone": "America/New_York"
}

# Make request
response = requests.post(url, json=data)
result = response.json()

print(f"Solar Azimuth: {result['solar_azimuth']}°")
print(f"Solar Elevation: {result['solar_elevation']}°")
print(f"Sunrise: {result['sunrise']}")
print(f"Sunset: {result['sunset']}")
print(f"Day Length: {result['day_length']} hours")
```

**Expected Output:**
```
Solar Azimuth: 180.23° (S)
Solar Elevation: 72.92°
Sunrise: 05:25:12
Sunset: 20:31:08
Day Length: 15.1 hours
```

---

## Example 2: Winter Solstice Comparison

### Same Location - Winter Solstice

```python
data = {
    "latitude": 40.7128,
    "longitude": -74.0060,
    "date": "2025-12-21",  # Winter solstice
    "time": "12:00",
    "timezone": "America/New_York"
}

response = requests.post(url, json=data)
result = response.json()
```

**Results:**
- Solar Elevation: ~26° (much lower than summer)
- Day Length: ~9.2 hours (much shorter)
- Sun path stays in southern sky

---

## Example 3: Get Complete Sun Path Data

```python
url = "http://localhost:8000/sun-path/data"

data = {
    "latitude": 40.7128,
    "longitude": -74.0060,
    "date": "2025-06-21",
    "current_time": "14:30",
    "timezone": "America/New_York"
}

response = requests.post(url, json=data)
result = response.json()

# Access hourly data
for point in result['sun_path']:
    print(f"{point['time']}: Az={point['azimuth']}°, El={point['elevation']}°")

# Current position
current = result['current_position']
print(f"\nCurrent position at {current['time']}:")
print(f"  Azimuth: {current['azimuth']}°")
print(f"  Elevation: {current['elevation']}°")
```

---

## Example 4: Generate Sun Path Diagrams

### Polar Diagram (Sky View)

```python
url = "http://localhost:8000/sun-path"

data = {
    "latitude": 40.7128,
    "longitude": -74.0060,
    "date": "2025-06-21",
    "current_time": "12:00",
    "timezone": "America/New_York",
    "diagram_type": "polar"
}

response = requests.post(url, json=data)

# Save the image
with open("sun_path_polar.png", "wb") as f:
    f.write(response.content)
```

### Cartesian Diagram (Azimuth vs Elevation)

```python
data["diagram_type"] = "cartesian"
response = requests.post(url, json=data)

with open("sun_path_cartesian.png", "wb") as f:
    f.write(response.content)
```

---

## Example 5: Compare Multiple Dates

### Analyze Seasonal Variations

```python
dates = {
    "Winter Solstice": "2025-12-21",
    "Spring Equinox": "2025-03-20",
    "Summer Solstice": "2025-06-21",
    "Fall Equinox": "2025-09-22"
}

for season, date in dates.items():
    data = {
        "latitude": 40.7128,
        "longitude": -74.0060,
        "date": date,
        "time": "12:00",
        "timezone": "America/New_York"
    }
    
    response = requests.post("http://localhost:8000/solar-position", json=data)
    result = response.json()
    
    print(f"\n{season} ({date}):")
    print(f"  Max Elevation: {result['solar_elevation']}°")
    print(f"  Day Length: {result['day_length']} hours")
```

**Expected Results:**
```
Winter Solstice (2025-12-21):
  Max Elevation: 26.5°
  Day Length: 9.2 hours

Spring Equinox (2025-03-20):
  Max Elevation: 49.8°
  Day Length: 12.0 hours

Summer Solstice (2025-06-21):
  Max Elevation: 73.5°
  Day Length: 15.1 hours

Fall Equinox (2025-09-22):
  Max Elevation: 49.8°
  Day Length: 12.0 hours
```

---

## Example 6: Different Latitudes

### Compare Arctic vs Equatorial Locations

```python
locations = {
    "Reykjavik (Arctic)": {"lat": 64.1466, "lng": -21.9426},
    "New York (Mid-latitude)": {"lat": 40.7128, "lng": -74.0060},
    "Singapore (Equatorial)": {"lat": 1.3521, "lng": 103.8198}
}

date = "2025-06-21"  # Summer solstice

for name, coords in locations.items():
    data = {
        "latitude": coords["lat"],
        "longitude": coords["lng"],
        "date": date,
        "timezone": None  # Auto-detect
    }
    
    response = requests.post("http://localhost:8000/solar-position", json=data)
    result = response.json()
    
    print(f"\n{name}:")
    print(f"  Day Length: {result['day_length']} hours")
```

**Expected Results:**
```
Reykjavik (Arctic):
  Day Length: 20.9 hours (almost no night!)

New York (Mid-latitude):
  Day Length: 15.1 hours

Singapore (Equatorial):
  Day Length: 12.2 hours (consistent year-round)
```

---

## Example 7: Solar Panel Optimization

### Find Optimal Panel Angle

```python
def find_optimal_angle(latitude, longitude, date):
    """
    Calculate optimal solar panel tilt angle
    (approximately equal to latitude for fixed installations)
    """
    url = "http://localhost:8000/solar-position"
    
    # Sample throughout the day
    elevations = []
    
    for hour in range(6, 20):  # 6 AM to 8 PM
        data = {
            "latitude": latitude,
            "longitude": longitude,
            "date": date,
            "time": f"{hour:02d}:00",
            "timezone": None
        }
        
        response = requests.post(url, json=data)
        result = response.json()
        
        if result['solar_elevation'] > 0:
            elevations.append(result['solar_elevation'])
    
    # Optimal angle is roughly latitude for fixed panels
    # Or average elevation for tracking systems
    avg_elevation = sum(elevations) / len(elevations)
    
    return {
        "optimal_tilt_fixed": latitude,
        "average_elevation": round(avg_elevation, 2)
    }

# Example usage
result = find_optimal_angle(40.7128, -74.0060, "2025-06-21")
print(f"Optimal fixed tilt angle: {result['optimal_tilt_fixed']}°")
print(f"Average elevation: {result['average_elevation']}°")
```

---

## Example 8: Shadow Length Calculator

### Calculate Shadow Length at Given Time

```python
def calculate_shadow_length(object_height, solar_elevation):
    """
    Calculate shadow length based on object height and sun elevation
    
    Args:
        object_height: Height of object in meters
        solar_elevation: Solar elevation angle in degrees
    
    Returns:
        Shadow length in meters
    """
    import math
    
    if solar_elevation <= 0:
        return float('inf')  # Nighttime - infinite shadow
    
    elevation_rad = math.radians(solar_elevation)
    shadow_length = object_height / math.tan(elevation_rad)
    
    return shadow_length

# Example: 10-meter pole at noon on summer solstice in NYC
data = {
    "latitude": 40.7128,
    "longitude": -74.0060,
    "date": "2025-06-21",
    "time": "12:00",
    "timezone": "America/New_York"
}

response = requests.post("http://localhost:8000/solar-position", json=data)
result = response.json()

pole_height = 10  # meters
shadow = calculate_shadow_length(pole_height, result['solar_elevation'])

print(f"10m pole shadow at solar noon: {shadow:.2f}m")
# Expected: ~3m (sun is high, short shadow)
```

---

## Example 9: Web Integration (JavaScript)

### Frontend Integration Example

```javascript
// Calculate solar position from web page
async function getSolarPosition(lat, lng, date, time) {
    const response = await fetch('http://localhost:8000/solar-position', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            latitude: lat,
            longitude: lng,
            date: date,
            time: time,
            timezone: null  // Auto-detect
        })
    });
    
    return await response.json();
}

// Display sun path diagram
async function displaySunPath(lat, lng, date) {
    const response = await fetch('http://localhost:8000/sun-path', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            latitude: lat,
            longitude: lng,
            date: date,
            diagram_type: 'polar'
        })
    });
    
    const blob = await response.blob();
    const imageUrl = URL.createObjectURL(blob);
    
    document.getElementById('sun-path-img').src = imageUrl;
}

// Usage
getSolarPosition(40.7128, -74.0060, '2025-06-21', '12:00')
    .then(data => {
        console.log('Solar Azimuth:', data.solar_azimuth);
        console.log('Solar Elevation:', data.solar_elevation);
    });

displaySunPath(40.7128, -74.0060, '2025-06-21');
```

---

## Example 10: Timezone Handling

### Different Timezone Formats

```python
# 1. Auto-detect from longitude
data = {
    "latitude": 40.7128,
    "longitude": -74.0060,
    "date": "2025-06-21",
    "timezone": None  # Will use longitude to estimate
}

# 2. Named timezone
data = {
    "latitude": 40.7128,
    "longitude": -74.0060,
    "date": "2025-06-21",
    "timezone": "America/New_York"
}

# 3. UTC
data = {
    "latitude": 40.7128,
    "longitude": -74.0060,
    "date": "2025-06-21",
    "timezone": "UTC"
}

# 4. Other timezones
timezones = [
    "Europe/London",
    "Asia/Tokyo",
    "Australia/Sydney",
    "America/Los_Angeles"
]
```

---

## Common Use Cases

### Architecture & Site Planning
- Analyze sun exposure for building facades
- Calculate daylight hours for different orientations
- Plan shading strategies
- Optimize window placement

### Solar Energy
- Determine optimal panel angles
- Calculate energy production potential
- Plan array layouts
- Seasonal performance analysis

### Agriculture
- Plan greenhouse orientations
- Calculate growing season daylight hours
- Optimize crop placement

### Photography
- Find golden hour times
- Plan sun positions for outdoor shoots
- Calculate shadow patterns

### Urban Planning
- Assess shadow impacts on buildings
- Design sun-friendly public spaces
- Plan park and plaza orientations

---

## API Response Format

### Solar Position Response
```json
{
  "latitude": 40.7128,
  "longitude": -74.0060,
  "date": "2025-06-21",
  "time": "12:00:00",
  "timezone": "America/New_York",
  "solar_azimuth": 180.23,
  "solar_elevation": 72.92,
  "solar_zenith": 17.08,
  "sunrise": "05:25:12",
  "sunset": "20:31:08",
  "solar_noon": "13:02:45",
  "day_length": 15.1
}
```

### Sun Path Data Response
```json
{
  "latitude": 40.7128,
  "longitude": -74.0060,
  "date": "2025-06-21",
  "timezone": "America/New_York",
  "sun_path": [
    {"time": "05:25:00", "azimuth": 58.23, "elevation": 0.12},
    {"time": "06:00:00", "azimuth": 62.45, "elevation": 5.67},
    ...
  ],
  "current_position": {
    "time": "12:00",
    "azimuth": 180.23,
    "elevation": 72.92
  },
  "solar_events": {
    "sunrise": "05:25:12",
    "sunset": "20:31:08",
    "solar_noon": "13:02:45",
    "day_length": 15.1
  }
}
```

---

## Tips & Best Practices

1. **Always specify timezone** for consistent results across locations
2. **Use date strings** in YYYY-MM-DD format
3. **Time is optional** - if not provided, returns data for solar noon
4. **Check elevation** - negative values mean sun is below horizon
5. **Cache results** - solar calculations are deterministic, cache by location+date
6. **Handle errors** - polar regions may have extreme conditions (polar night/day)
7. **Coordinate precision** - 6 decimal places is ~0.1m accuracy

---

## Error Handling

```python
try:
    response = requests.post(url, json=data)
    response.raise_for_status()  # Raise exception for bad status codes
    result = response.json()
except requests.exceptions.ConnectionError:
    print("Error: Cannot connect to server. Is it running?")
except requests.exceptions.HTTPError as e:
    print(f"HTTP Error: {e}")
    print(f"Details: {response.json()}")
except Exception as e:
    print(f"Unexpected error: {e}")
```
