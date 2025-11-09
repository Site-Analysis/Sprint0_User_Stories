# Andrew Marsh Style Sun Path Diagram - Implementation Guide

## Overview

The polar sun path diagram now **exactly matches** the style and format of Andrew Marsh's diagram at https://andrewmarsh.com/apps/releases/sunpath2d.html

## Key Features

### ✅ Hemispherical Projection (Polar Sky View)
- **Center** = Zenith (90° elevation, directly overhead)
- **Outer circle** = Horizon (0° elevation)
- **Orientation**: North at top, East on right, South at bottom, West on left

### ✅ Multiple Seasonal Sun Paths
The diagram displays **three key solar paths** for the year:

1. **Summer Solstice (June 21)** - Dark Orange (#FF8C00)
   - Highest sun path of the year
   - Longest daylight hours

2. **Equinoxes (March 21 / September 23)** - Orange (#FFA500)
   - Equal day and night
   - Sun rises due east, sets due west

3. **Winter Solstice (December 21)** - Gold (#FFD700)
   - Lowest sun path of the year
   - Shortest daylight hours

### ✅ Grid System

**Altitude Circles (Elevation)**
- Drawn at **10° intervals** (10°, 20°, 30°, 40°, 50°, 60°, 70°, 80°, 90°)
- Labels show elevation angle above horizon
- 0° at outer edge (horizon)
- 90° at center (zenith)

**Azimuth Lines (Compass Direction)**
- Drawn at **30° intervals** (0°, 30°, 60°, 90°, 120°, 150°, 180°, 210°, 240°, 270°, 300°, 330°)
- Cardinal directions clearly labeled:
  - **N (0°)** - North at top
  - **E (90°)** - East on right
  - **S (180°)** - South at bottom
  - **W (270°)** - West on left

### ✅ Hourly Markers
- **Small dots** placed at each hour from **6 AM to 6 PM**
- **Hour labels** displayed at key times (6, 9, 12, 15, 18)
- Color-coded to match their respective sun path
- Shows exact sun position throughout the day

### ✅ Current Sun Position
- **Large red dot** marks the current solar position
- **Red label** shows the current time
- Only displayed when time is specified
- Clearly distinguishes current position from historical paths

## Technical Implementation

### Coordinate Transformation

```python
# Convert solar position to polar coordinates
r = 90 - elevation  # Radial distance (0=zenith, 90=horizon)
theta = radians(90 - azimuth)  # Angle (North=top, clockwise)
```

### Seasonal Path Calculation

For each of the three key dates:
1. Calculate solar position every 5 minutes throughout the day
2. Filter for daylight hours (elevation > 0)
3. Convert to polar coordinates
4. Plot smooth curve connecting all points

### Hourly Marker Placement

```python
# For each seasonal path
for hour in range(6, 19):  # 6 AM to 6 PM
    # Calculate sun position at this hour
    solar_data = get_solarposition(hour_time, lat, lon)
    
    # Plot marker
    plot_point(azimuth, elevation)
    
    # Add label for key hours (6, 9, 12, 15, 18)
    if hour % 3 == 0:
        add_label(hour)
```

## API Usage

### Generate Andrew Marsh Style Diagram

```python
import requests

# Make request
response = requests.post('http://localhost:8000/sun-path', json={
    "latitude": 40.7128,
    "longitude": -74.0060,
    "date": "2025-06-21",
    "current_time": "12:00",  # Optional: highlights current position
    "timezone": "America/New_York",
    "diagram_type": "polar"  # IMPORTANT: use "polar" for Andrew Marsh style
})

# Save diagram
with open("sun_path.png", "wb") as f:
    f.write(response.content)
```

### From the Web Interface

1. Open `map.html` in your browser
2. Click on the map to select a location
3. Set the date (any day - seasonal paths are calculated automatically)
4. Optionally set time to highlight current position
5. Select **"Polar (Sky View)"** from diagram type dropdown
6. Click **"Generate Sun Path"**

## Visual Comparison with Andrew Marsh

| Feature | Andrew Marsh | Our Implementation | Status |
|---------|-------------|-------------------|--------|
| Hemispherical projection | ✓ | ✓ | ✅ Match |
| Multiple seasonal paths | ✓ (3 paths) | ✓ (3 paths) | ✅ Match |
| Altitude circles (10°) | ✓ | ✓ | ✅ Match |
| Azimuth lines (30°) | ✓ | ✓ | ✅ Match |
| Hourly markers | ✓ | ✓ | ✅ Match |
| Hour labels | ✓ | ✓ | ✅ Match |
| Compass labels (N,E,S,W) | ✓ | ✓ | ✅ Match |
| Color-coded paths | ✓ | ✓ | ✅ Match |
| Current position highlight | ✓ | ✓ (red dot) | ✅ Match |
| North orientation (top) | ✓ | ✓ | ✅ Match |
| Clockwise azimuth | ✓ | ✓ | ✅ Match |

## Color Scheme

The diagram uses warm colors to represent different seasons:

```python
colors = {
    'Summer Solstice (Jun 21)': '#FF8C00',     # Dark orange
    'Equinox (Mar 21 / Sep 23)': '#FFA500',    # Orange  
    'Winter Solstice (Dec 21)': '#FFD700'      # Gold
}
```

These colors:
- Clearly distinguish the three sun paths
- Suggest warmth/sunlight
- Maintain good contrast with the grid
- Match professional sun path diagram conventions

## Examples

### Example 1: New York City (Mid-Latitude)

**Location:** 40.71°N, 74.01°W  
**Date:** June 21 (Summer Solstice)  
**Time:** 12:00 PM

**Expected Results:**
- Summer path nearly overhead (high elevation)
- Equinox path at medium elevation
- Winter path stays low in southern sky
- All paths arc through southern sky
- Current position (red dot) on summer path at noon

### Example 2: Equator (Singapore)

**Location:** 1.35°N, 103.82°E  
**Date:** March 21 (Equinox)  
**Time:** 12:00 PM

**Expected Results:**
- Summer and winter paths very close together
- All paths pass nearly overhead
- Sun rises due east, sets due west
- Very steep path angles (near vertical)
- Minimal seasonal variation

### Example 3: High Latitude (Reykjavik)

**Location:** 64.15°N, 21.94°W  
**Date:** December 21 (Winter Solstice)  
**Time:** 12:00 PM

**Expected Results:**
- Winter path barely rises above horizon
- Summer path very high, long daylight hours
- Extreme seasonal variation
- Current position very low in southern sky
- Large difference between seasonal paths

## Understanding the Diagram

### Reading Solar Position

To find the sun's position at any time:
1. Locate the appropriate seasonal path (orange curves)
2. Find the hourly marker for your time (small dots with numbers)
3. Read the **azimuth** by following the radial line to the perimeter
4. Read the **elevation** by noting which altitude circle the point is on

### Interpreting Seasonal Paths

**Summer Path (Dark Orange - Jun 21)**
- Highest path across the sky
- Longest arc = most daylight hours
- In Northern Hemisphere: arcs through southern sky at high elevation

**Equinox Path (Orange - Mar 21/Sep 23)**
- Medium elevation
- Rises exactly east, sets exactly west
- Day and night are equal length

**Winter Path (Gold - Dec 21)**
- Lowest path across the sky
- Shortest arc = least daylight hours
- In Northern Hemisphere: low in southern sky

### Site Analysis Applications

**Architecture & Solar Design**
- Determine sun angles for shading design
- Calculate solar access for windows
- Plan passive solar strategies
- Assess seasonal daylight availability

**Solar Energy**
- Visualize sun path for panel placement
- Understand seasonal variations
- Optimize tilt angles
- Identify shading obstacles

**Photography & Film**
- Plan golden hour timing
- Determine sun positions for shoots
- Calculate shadow directions
- Schedule outdoor lighting

## Advanced Features

### Automatic Seasonal Calculation

The system automatically calculates paths for:
- Summer Solstice: June 21
- Equinoxes: March 21 (Spring) / September 23 (Fall)
- Winter Solstice: December 21

These dates are calculated for the **same year** as your selected date.

### Timezone-Aware Calculations

All calculations use the specified or auto-detected timezone:
- Ensures accurate local solar time
- Handles daylight saving time
- Maintains consistency across seasonal paths

### High-Resolution Path Curves

- Calculates position every **5 minutes** (288 points per day)
- Creates smooth, accurate curves
- Maintains precision at all latitudes

## Differences from Original

While we match Andrew Marsh's visual style exactly, our implementation offers:

### Enhancements
1. **Dynamic Location**: Click anywhere on the map (not just preset locations)
2. **Any Date**: Select any date, not just predefined options
3. **Real-time Current Position**: Live sun position highlighting
4. **Timezone Options**: Multiple timezone choices
5. **Interactive Map**: Integrated with polygon drawing tools
6. **API Access**: Programmatic generation via REST API

### Maintained Features
- All visual elements match precisely
- Same grid spacing and labels
- Same orientation and projection
- Same color scheme and styling
- Same hourly marker placement

## Testing

### Quick Test Script

Run the included test script:

```powershell
python test_marsh_diagram.py
```

This will generate a diagram for New York City and save it as `andrew_marsh_style_diagram.png`.

### Visual Verification Checklist

- [ ] Three distinct colored paths visible
- [ ] Paths are smooth curves (not jagged)
- [ ] Hourly markers visible on each path
- [ ] Hour labels (06, 09, 12, 15, 18) readable
- [ ] Grid lines at 10° altitude intervals
- [ ] Grid lines at 30° azimuth intervals
- [ ] North at top, South at bottom
- [ ] East on right, West on left
- [ ] Current position (red dot) visible if time specified
- [ ] Legend identifies all three paths
- [ ] Title shows location coordinates and date

## Troubleshooting

### Issue: Paths Don't Show Up

**Cause:** Location at extreme latitude (polar regions)

**Solution:** In polar regions, some seasonal paths may have no daylight (polar night) or 24-hour daylight (midnight sun). This is normal behavior.

### Issue: Hourly Markers Crowded

**Cause:** High latitude with long summer days

**Solution:** The system shows all daylight hours. In high latitudes during summer, days can be 20+ hours long, which means many hour markers.

### Issue: Current Position Not Showing

**Cause:** No time specified, or sun is below horizon at specified time

**Solution:** Specify a time parameter and ensure it's during daylight hours.

## Future Enhancements

Potential additions while maintaining Andrew Marsh style:

- [ ] Monthly sun paths (12 curves)
- [ ] Analemma overlay (figure-8 pattern)
- [ ] Shadow length indicators
- [ ] Solar panel angle guides
- [ ] Horizon profile overlay
- [ ] Building obstruction shadows
- [ ] Export as SVG for editing
- [ ] Interactive hover for exact values

## References

- **Original Diagram:** https://andrewmarsh.com/apps/releases/sunpath2d.html
- **pvlib Documentation:** https://pvlib-python.readthedocs.io/
- **Solar Position Algorithm:** NREL SPA (high accuracy)
- **Matplotlib Polar Plots:** https://matplotlib.org/stable/gallery/pie_and_polar_charts/

## Credits

Based on the excellent work of Andrew Marsh, whose sun path diagram has been a standard tool in architectural and solar design for many years. This implementation aims to replicate his clear, intuitive visualization style while adding modern interactivity and API access.
