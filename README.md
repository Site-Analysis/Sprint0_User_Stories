# Solar Test - Interactive Map with Sun Path Visualization

A web-based interactive mapping tool that combines polygon drawing capabilities with advanced sun path analysis using the pvlib solar position library.

## Features

### Map Drawing Tools
- **Polygon Tool**: Click to create custom polygons
- **Rectangle Tool**: Click and drag for rectangles
- **Freehand Tool**: Draw freehand shapes
- **Edit/Delete**: Modify or remove existing shapes
- **GeoJSON Export**: Export shapes as GeoJSON

### Sun Path Analysis ☀️
- **Solar Position Calculation**: Real-time azimuth, elevation, and zenith angles using pvlib's NREL SPA algorithm
- **Andrew Marsh Style Diagram**: Multiple seasonal sun paths (Summer Solstice, Equinox, Winter Solstice) 🌟
- **Hemispherical Projection**: Polar sky view matching industry-standard visualization
- **Enhanced Selected Date Path**: Your chosen date displayed as a prominent blue line with hourly markers (separate from seasonal paths)
- **Seasonal Reference Paths**: Summer (orange), Equinox (light orange), Winter (gold) with 6 AM - 6 PM markers at 3-hour intervals
- **Selected Date Hourly Markers**: Every hour marked with time labels (00h, 02h, 04h, etc.) on the blue path
- **Current Position Highlighting**: Red star with crosshair lines (azimuth and altitude) showing sun's exact position
- **Position Labels**: Time, azimuth, and elevation displayed in yellow callout box at current position
- **Solar Events**: Sunrise, sunset, solar noon, and day length
- **Multiple Diagram Types**: Polar (multi-seasonal + selected date) and Cartesian (single day) projections
- **Timezone Support**: Automatic longitude-based estimation or manual timezone selection

## Tech Stack

### Backend
- **FastAPI**: Modern Python web framework
- **pvlib**: Solar position calculations
- **matplotlib**: Sun path diagram generation
- **pandas**: Data processing
- **pytz**: Timezone handling

### Frontend
- **Leaflet.js**: Interactive mapping
- **Leaflet Draw**: Drawing tools
- **OpenStreetMap**: Base map tiles

## Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Step 1: Install Python Dependencies

Open PowerShell in the project directory and run:

```powershell
pip install -r requirements.txt
```

This will install:
- fastapi
- uvicorn
- pvlib
- matplotlib
- pandas
- pytz
- Pillow

### Step 2: Start the Backend Server

Run the FastAPI server:

```powershell
python server.py
```

The server will start on `http://localhost:8000`

You should see output like:
```
Starting Solar Position API Server...
API Documentation: http://localhost:8000/docs
INFO:     Started server process
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Step 3: Open the Web Interface

Open `map.html` in your web browser. You can:
- Double-click the file
- Right-click and select "Open with" → your browser
- Use VS Code's Live Server extension

## Usage Guide

### Drawing Polygons

1. **Select a Drawing Tool** from the toolbar on the map
2. **Draw Your Shape**:
   - **Polygon**: Click points, double-click to finish
   - **Rectangle**: Click and drag
   - **Freehand**: Click and drag to draw
3. **View Coordinates** in the sidebar (GeoJSON format)
4. **Edit or Delete** using the edit/delete tools

### Sun Path Analysis

#### 1. Select a Location
- Click anywhere on the map to select a location
- A sun marker (☀️) will appear
- Coordinates will display in the "Sun Path Analysis" section

#### 2. Set Parameters
- **Date**: Select any date (defaults to today)
- **Time** (optional): Set specific time to highlight on path
- **Timezone**: Auto-detect or select manually
- **Diagram Type**: Choose polar (sky view) or cartesian

#### 3. Calculate Solar Position
Click **"Calculate Solar Position"** to get:
- Solar Azimuth (compass direction)
- Solar Elevation (angle above horizon)
- Solar Zenith (angle from vertical)
- Sunrise time
- Sunset time
- Solar noon
- Day length in hours

#### 4. Generate Sun Path Diagram
Click **"Generate Sun Path"** to create a visualization showing:
- **Seasonal Reference Paths**: Three colored paths showing sun's trajectory on key dates:
  - Dark Orange: Summer Solstice (June 21) - highest sun path
  - Orange: Equinox (March 21 / September 23) - mid-height path
  - Gold: Winter Solstice (December 21) - lowest sun path
- **Your Selected Date Path**: Bold blue line showing sun's path on your chosen date with hourly markers
- **Hourly Markers**: Blue circles every hour (labeled every 2 hours) on selected date path
- **Current Position**: If time is specified, red star with crosshair lines showing exact sun position
- **Position Details**: Callout box showing time, azimuth angle, and elevation angle at current position
- **Polar Grid**: 10° altitude circles and 30° azimuth lines for precise angle reading

### Understanding the Diagrams

#### Polar Diagram (Sky View) - Andrew Marsh Style
- **Projection**: Hemispherical view as if looking up at the sky dome
- **Center**: Directly overhead (zenith = 90° elevation)
- **Outer edge**: Horizon (0° elevation)
- **North at top**: Compass oriented with North up, clockwise rotation (East on right)
- **Multiple Paths**: Shows four sun paths simultaneously:
  1. **Summer Solstice** (dark orange) - longest day, highest sun path
  2. **Equinox** (orange) - equal day/night, mid-height path  
  3. **Winter Solstice** (gold) - shortest day, lowest sun path
  4. **Selected Date** (blue) - your chosen date with detailed hourly markers
- **Altitude Circles**: Concentric circles at 10° intervals (labeled with elevation: 80°, 70°, 60°... 0°)
- **Azimuth Lines**: Radial lines at 30° intervals (N, 30°, 60°, E, 120°, etc.)
- **Current Position Marker**: Red star with crosshair lines showing:
  - Vertical line = sun's azimuth direction
  - Circular line = sun's elevation angle
  - Yellow callout = precise time and position data
- **Best for**: Understanding seasonal sun patterns, shadow casting directions, and daylighting design

#### Cartesian Diagram (Azimuth vs Elevation)
- **X-axis**: Azimuth (0° = North, 90° = East, 180° = South, 270° = West, 360° = North)
- **Y-axis**: Elevation (0° = horizon, 90° = zenith)
- **Shows**: Single day sun path with hourly markers and timestamps
- **Current position**: Red star marker if time specified
- **Best for**: Analyzing elevation changes, determining maximum sun height, sunrise/sunset azimuths

## API Endpoints

The backend provides three main endpoints:

### 1. Calculate Solar Position
**POST** `/solar-position`

```json
{
  "latitude": 40.7128,
  "longitude": -74.0060,
  "date": "2025-06-21",
  "time": "12:00",
  "timezone": "America/New_York"
}
```

Returns solar azimuth, elevation, sunrise, sunset, etc.

### 2. Generate Sun Path Diagram
**POST** `/sun-path`

```json
{
  "latitude": 40.7128,
  "longitude": -74.0060,
  "date": "2025-06-21",
  "current_time": "12:00",
  "timezone": "America/New_York",
  "diagram_type": "polar"
}
```

Returns PNG image of sun path diagram.

### 3. Get Sun Path Data
**POST** `/sun-path/data`

```json
{
  "latitude": 40.7128,
  "longitude": -74.0060,
  "date": "2025-06-21",
  "timezone": "America/New_York"
}
```

Returns JSON with hourly solar position data.

### Interactive API Documentation

Visit `http://localhost:8000/docs` for interactive API documentation where you can:
- Test all endpoints
- View request/response schemas
- See example data
- Try different parameters

## Diagram Enhancements

### What Makes This Special?
The polar sun path diagram has been enhanced to match the professional "Andrew Marsh" style used in architectural solar analysis:

1. **Four Simultaneous Paths**: Instead of showing just one day, see your selected date PLUS three seasonal reference paths
   - Helps understand how sun position varies throughout the year
   - Instant comparison between summer/winter extremes and equinox mid-points

2. **Selected Date Prominence**: Your chosen date appears as a distinct blue path with comprehensive hourly markers
   - Every hour marked (00h through 23h during daylight)
   - Labels every 2 hours to avoid clutter
   - White-bordered circles for visibility

3. **Precise Current Position**: When time is specified, see exactly where the sun is:
   - Red star marker with dark red border
   - Vertical crosshair = azimuth bearing (compass direction)
   - Horizontal crosshair = altitude circle (elevation angle)
   - Yellow callout with time, azimuth, and elevation values

4. **Professional Grid System**: 
   - 10° altitude circles (easy angle estimation)
   - 30° azimuth radials (12 divisions like a clock)
   - Cardinal and intercardinal directions labeled
   - Clean gray grid lines for precise reading

5. **Color-Coded Seasonal Paths**:
   - Dark Orange = Summer (highest path, longest day)
   - Orange = Equinox (mid path, 12-hour day)
   - Gold = Winter (lowest path, shortest day)
   - Blue = Your Selected Date (shows where it falls in annual cycle)

## Solar Position Concepts

### Azimuth
The compass direction of the sun (0° = North, 90° = East, 180° = South, 270° = West)

### Elevation
Angle of the sun above the horizon (0° = at horizon, 90° = directly overhead)

### Zenith
Angle from directly overhead (90° - elevation)

### Solar Noon
Time when the sun reaches its highest point in the sky (maximum elevation)

### Sunrise/Sunset
Times when the sun's elevation crosses the horizon (0°)

## Use Cases

### Architecture & Design
- Analyze sun exposure for buildings
- Plan natural lighting strategies
- Design shading systems
- Optimize solar panel placement

### Site Analysis
- Assess daylight availability
- Plan outdoor spaces
- Evaluate seasonal sun patterns
- Shadow analysis preparation

### Solar Energy
- Calculate solar panel angles
- Estimate energy production potential
- Plan array layouts
- Seasonal performance analysis

### Photography & Cinematography
- Plan golden hour shoots
- Determine sun positions for lighting
- Schedule outdoor photography

### Urban Planning
- Design sun-friendly public spaces
- Plan building orientations
- Assess shadow impacts on neighborhoods

## Customization

### Modify Sun Path Appearance
Edit the visualization functions in `server.py`:
- `create_polar_sun_path()`: Customize polar diagram
- `create_cartesian_sun_path()`: Customize cartesian diagram

### Add More Timezones
Update the timezone dropdown in `map.html` line 134-146

### Change API URL
If deploying to a different server, update `API_BASE_URL` in `map.html` line 423

### Adjust Map Center/Zoom
Edit line 119 in `map.html`:
```javascript
const map = L.map('map').setView([latitude, longitude], zoom);
```

## Troubleshooting

### Server won't start
- Check Python version: `python --version` (need 3.8+)
- Ensure all dependencies installed: `pip list`
- Try: `python -m uvicorn server:app --reload`

### "Connection refused" error
- Verify server is running on port 8000
- Check firewall settings
- Ensure `http://localhost:8000` is accessible

### Sun path calculation errors
- Verify latitude/longitude are valid
- Check date format (YYYY-MM-DD)
- Ensure timezone is correct
- Some polar locations may have extreme conditions (polar night/day)

### Image not displaying
- Check browser console for errors
- Verify CORS is enabled in server
- Ensure matplotlib is installed correctly

## Technical Notes

### Solar Position Calculations
Uses pvlib's `get_solarposition()` which implements:
- **NREL SPA algorithm**: Sub-0.0003° accuracy (high precision solar position)
- **Atmospheric refraction**: Accounts for light bending near horizon
- **Timezone handling**: Automatic estimation from longitude or manual selection with pytz
- **5-minute intervals**: Sun paths calculated at 5-minute resolution for smooth curves
- **Multi-seasonal analysis**: Generates three reference dates (solstices + equinox) plus selected date simultaneously

### Coordinate Systems
- **Geographic**: Latitude/Longitude (WGS84)
- **Solar Azimuth**: 0° = North, clockwise
- **Solar Elevation**: 0° = horizon, 90° = zenith

### Performance
- Solar position calculations: ~10ms per point using pvlib's optimized algorithms
- Sun path generation: ~2-3 seconds for polar diagram (4 paths × 288 points @ 5-min intervals)
- Cartesian diagram: ~500ms (single day path)
- Data resolution: 5-minute intervals for smooth path visualization (288 points per day)
- Image output: 150 DPI PNG with transparent background

## License

This project uses open-source libraries:
- pvlib (BSD-3-Clause)
- FastAPI (MIT)
- Leaflet (BSD-2-Clause)

## Support

For questions or issues:
1. Check the interactive API docs at `http://localhost:8000/docs`
2. Review pvlib documentation: https://pvlib-python.readthedocs.io/
3. Check Leaflet documentation: https://leafletjs.com/

## Recent Improvements ✨

### Version 1.1 - Enhanced Andrew Marsh Style Diagrams
- ✅ **Multi-seasonal polar diagrams**: Shows 4 paths simultaneously (Summer, Equinox, Winter, + Selected Date)
- ✅ **Selected date highlighting**: Bold blue path with hourly markers for your chosen date
- ✅ **Precise current position**: Red star with azimuth/altitude crosshairs and detailed callout
- ✅ **5-minute resolution**: Smooth sun path curves using pvlib 5-minute interval calculations
- ✅ **Professional styling**: Color-coded paths, clean grid, cardinal direction labels

## Future Enhancements

Potential additions:
- Analemma diagram (showing sun position at same time throughout year)
- Shadow length calculator with building height input
- Solar radiation estimates (kWh/m²/day)
- Export sun path data to CSV/JSON
- 3D sun path hemisphere visualization
- Stereographic projection option
- Multiple location comparison view
- Mobile-responsive design improvements
- Database storage for saved locations and analyses
- Solar panel tilt angle optimizer
- Shade analysis for building arrays

---

**Built with ❤️ for solar analysis and site planning**
