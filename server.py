"""
Solar Position and Sun Path Visualization Server
=================================================
FastAPI server for computing solar position and generating sun path diagrams
using the pvlib library for accurate solar calculations.

Dependencies: fastapi, uvicorn, pvlib, matplotlib, pandas, pytz, Pillow
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from datetime import datetime, timedelta
from typing import Optional, List, Dict
import pvlib
from pvlib import solarposition
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for server
import matplotlib.pyplot as plt
import numpy as np
from io import BytesIO
import pytz
import base64
from datetime import timezone as dt_timezone

# Initialize FastAPI app
app = FastAPI(
    title="Solar Position API",
    description="API for computing solar positions and generating sun path diagrams",
    version="1.0.0"
)

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class SolarPositionRequest(BaseModel):
    """Request model for solar position calculation"""
    latitude: float = Field(..., ge=-90, le=90, description="Latitude in degrees")
    longitude: float = Field(..., ge=-180, le=180, description="Longitude in degrees")
    date: str = Field(..., description="Date in YYYY-MM-DD format")
    time: Optional[str] = Field(None, description="Time in HH:MM format (24-hour). If not provided, calculates hourly data")
    timezone: Optional[str] = Field(None, description="Timezone (e.g., 'America/New_York'). If not provided, uses UTC")


class SolarPositionResponse(BaseModel):
    """Response model for solar position data"""
    latitude: float
    longitude: float
    date: str
    time: str
    timezone: str
    solar_azimuth: float = Field(..., description="Solar azimuth angle in degrees (0=North, 90=East, 180=South, 270=West)")
    solar_elevation: float = Field(..., description="Solar elevation angle in degrees above horizon")
    solar_zenith: float = Field(..., description="Solar zenith angle in degrees from vertical")
    sunrise: Optional[str] = Field(None, description="Sunrise time")
    sunset: Optional[str] = Field(None, description="Sunset time")
    solar_noon: Optional[str] = Field(None, description="Solar noon time")
    day_length: Optional[float] = Field(None, description="Day length in hours")


class SunPathRequest(BaseModel):
    """Request model for sun path diagram generation"""
    latitude: float = Field(..., ge=-90, le=90, description="Latitude in degrees")
    longitude: float = Field(..., ge=-180, le=180, description="Longitude in degrees")
    date: str = Field(..., description="Date in YYYY-MM-DD format")
    current_time: Optional[str] = Field(None, description="Current time to highlight on path (HH:MM format)")
    timezone: Optional[str] = Field(None, description="Timezone (e.g., 'America/New_York'). If not provided, uses UTC")
    diagram_type: str = Field("polar", description="Type of diagram: 'polar' or 'cartesian'")


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def get_timezone(tz_string: Optional[str], longitude: float, latitude: float = None) -> pytz.timezone:
    """
    Get timezone object from string or estimate from longitude
    
    Args:
        tz_string: Timezone string (e.g., 'America/New_York')
        longitude: Longitude in degrees (used for estimation if tz_string is None)
        latitude: Latitude in degrees (optional, for better estimation)
    
    Returns:
        pytz timezone object with proper name
    """
    if tz_string:
        try:
            return pytz.timezone(tz_string)
        except pytz.exceptions.UnknownTimeZoneError:
            raise HTTPException(status_code=400, detail=f"Unknown timezone: {tz_string}")
    else:
        # Calculate UTC offset from longitude (15 degrees per hour)
        offset_hours = round(longitude / 15)
        offset_minutes = int(offset_hours * 60)
        
        # Create a timezone with proper naming
        # Use Etc/GMT notation which is counterintuitive (GMT+5 means UTC-5)
        if offset_hours == 0:
            return pytz.UTC
        elif offset_hours > 0:
            # East of Greenwich: use negative GMT notation
            etc_offset = -offset_hours
            tz_name = f"Etc/GMT{etc_offset:+d}" if etc_offset != 0 else "UTC"
        else:
            # West of Greenwich: use positive GMT notation  
            etc_offset = -offset_hours
            tz_name = f"Etc/GMT{etc_offset:+d}"
        
        try:
            return pytz.timezone(tz_name)
        except:
            # Fallback to FixedOffset if Etc/GMT fails
            return pytz.FixedOffset(offset_minutes)


def calculate_solar_events(latitude: float, longitude: float, date: datetime, tz: pytz.timezone) -> Dict:
    """
    Calculate sunrise, sunset, and solar noon times
    
    Args:
        latitude: Latitude in degrees
        longitude: Longitude in degrees
        date: Date as datetime object
        tz: Timezone object
    
    Returns:
        Dictionary with sunrise, sunset, solar_noon, and day_length
    """
    # Create time range for the entire day
    date_start = tz.localize(datetime.combine(date.date(), datetime.min.time()))
    times = pd.date_range(date_start, date_start + timedelta(days=1), freq='1min', tz=tz)
    
    # Calculate solar position for the entire day
    solar_position = solarposition.get_solarposition(times, latitude, longitude)
    
    # Find sunrise (first time elevation > 0)
    sunrise_mask = solar_position['elevation'] > 0
    sunrise_times = solar_position[sunrise_mask].index
    sunrise = sunrise_times[0] if len(sunrise_times) > 0 else None
    
    # Find sunset (last time elevation > 0)
    sunset = sunrise_times[-1] if len(sunrise_times) > 0 else None
    
    # Find solar noon (maximum elevation)
    if not pd.isna(solar_position['elevation'].max()):
        solar_noon = solar_position['elevation'].idxmax()  # idxmax() returns the index label directly
    else:
        solar_noon = None
    
    # Calculate day length in hours
    day_length = None
    if sunrise and sunset:
        day_length = (sunset - sunrise).total_seconds() / 3600
    
    return {
        'sunrise': sunrise.strftime('%H:%M:%S') if sunrise else None,
        'sunset': sunset.strftime('%H:%M:%S') if sunset else None,
        'solar_noon': solar_noon.strftime('%H:%M:%S') if solar_noon else None,
        'day_length': round(day_length, 2) if day_length else None
    }


# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Solar Position API - Andrew Marsh Style Sun Path Diagrams",
        "version": "2.0.0",
        "endpoints": {
            "/solar-position": "Calculate solar position for specific time",
            "/sun-path": "Generate sun path diagram (polar=seasonal paths, cartesian=single day)",
            "/sun-path/data": "Get sun path data as JSON"
        },
        "features": {
            "polar_diagram": "Multiple seasonal sun paths (Jun 21, Mar 21/Sep 23, Dec 21) with hourly markers",
            "cartesian_diagram": "Single day azimuth vs elevation plot",
            "current_position": "Highlights current sun position on diagram"
        }
    }


@app.post("/solar-position", response_model=SolarPositionResponse)
async def get_solar_position(request: SolarPositionRequest):
    """
    Calculate solar position (azimuth, elevation) for a specific location and time
    
    Returns detailed solar position data including azimuth, elevation, and solar events.
    """
    try:
        # Parse date and time
        date_obj = datetime.strptime(request.date, "%Y-%m-%d")
        
        # Get timezone
        tz = get_timezone(request.timezone, request.longitude)
        
        # If time is provided, use it; otherwise use noon
        if request.time:
            time_obj = datetime.strptime(request.time, "%H:%M").time()
            dt = tz.localize(datetime.combine(date_obj.date(), time_obj))
        else:
            # Default to solar noon (approximate as 12:00)
            dt = tz.localize(datetime.combine(date_obj.date(), datetime.strptime("12:00", "%H:%M").time()))
        
        # Calculate solar position using pvlib
        solar_position = solarposition.get_solarposition(dt, request.latitude, request.longitude)
        
        # Calculate solar events (sunrise, sunset, etc.)
        solar_events = calculate_solar_events(request.latitude, request.longitude, dt, tz)
        
        # Extract values
        azimuth = float(solar_position['azimuth'].iloc[0])
        elevation = float(solar_position['elevation'].iloc[0])
        zenith = float(solar_position['zenith'].iloc[0])
        
        # Prepare response
        response = SolarPositionResponse(
            latitude=request.latitude,
            longitude=request.longitude,
            date=request.date,
            time=dt.strftime("%H:%M:%S"),
            timezone=str(tz),
            solar_azimuth=round(azimuth, 2),
            solar_elevation=round(elevation, 2),
            solar_zenith=round(zenith, 2),
            sunrise=solar_events['sunrise'],
            sunset=solar_events['sunset'],
            solar_noon=solar_events['solar_noon'],
            day_length=solar_events['day_length']
        )
        
        return response
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid date/time format: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating solar position: {str(e)}")


@app.post("/sun-path/data")
async def get_sun_path_data(request: SunPathRequest):
    """
    Get sun path data as JSON for custom visualization
    
    Returns hourly solar position data for the entire day.
    """
    try:
        # Parse date
        date_obj = datetime.strptime(request.date, "%Y-%m-%d")
        
        # Get timezone
        tz = get_timezone(request.timezone, request.longitude)
        
        # Create time range for the day (hourly intervals)
        date_start = tz.localize(datetime.combine(date_obj.date(), datetime.min.time()))
        times = pd.date_range(date_start, date_start + timedelta(days=1), freq='15min', tz=tz)
        
        # Calculate solar position for all times
        solar_position = solarposition.get_solarposition(times, request.latitude, request.longitude)
        
        # Filter out nighttime (elevation < 0)
        daytime_mask = solar_position['elevation'] > 0
        daytime_data = solar_position[daytime_mask]
        
        # Prepare response data
        sun_path_data = []
        for idx, row in daytime_data.iterrows():
            sun_path_data.append({
                'time': idx.strftime('%H:%M:%S'),
                'azimuth': round(float(row['azimuth']), 2),
                'elevation': round(float(row['elevation']), 2)
            })
        
        # Calculate current position if time provided
        current_position = None
        if request.current_time:
            time_obj = datetime.strptime(request.current_time, "%H:%M").time()
            current_dt = tz.localize(datetime.combine(date_obj.date(), time_obj))
            current_solar = solarposition.get_solarposition(current_dt, request.latitude, request.longitude)
            current_position = {
                'time': request.current_time,
                'azimuth': round(float(current_solar['azimuth'].iloc[0]), 2),
                'elevation': round(float(current_solar['elevation'].iloc[0]), 2)
            }
        
        # Calculate solar events
        solar_events = calculate_solar_events(request.latitude, request.longitude, date_obj, tz)
        
        return {
            'latitude': request.latitude,
            'longitude': request.longitude,
            'date': request.date,
            'timezone': str(tz),
            'sun_path': sun_path_data,
            'current_position': current_position,
            'solar_events': solar_events
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid date/time format: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating sun path: {str(e)}")


@app.post("/sun-path")
async def generate_sun_path_diagram(request: SunPathRequest):
    """
    Generate a 2D sun path diagram (polar or cartesian projection)
    
    Polar diagram shows multiple seasonal paths (Andrew Marsh style)
    Returns a PNG image showing the sun's path throughout the day with optional
    current position highlighted.
    """
    try:
        # Parse date
        date_obj = datetime.strptime(request.date, "%Y-%m-%d")
        
        # Get timezone
        tz = get_timezone(request.timezone, request.longitude)
        
        # Create time range for the selected day (for cartesian diagram)
        date_start = tz.localize(datetime.combine(date_obj.date(), datetime.min.time()))
        times = pd.date_range(date_start, date_start + timedelta(days=1), freq='15min', tz=tz)
        
        # Calculate solar position for selected date
        solar_position = solarposition.get_solarposition(times, request.latitude, request.longitude)
        
        # Filter out nighttime (elevation < 0)
        daytime_mask = solar_position['elevation'] > 0
        daytime_data = solar_position[daytime_mask]
        
        if len(daytime_data) == 0 and request.diagram_type.lower() != 'polar':
            raise HTTPException(status_code=400, detail="No daylight hours for this date and location (polar night?)")
        
        # Calculate current position if time provided (for cartesian diagram)
        current_position = None
        if request.current_time:
            time_obj = datetime.strptime(request.current_time, "%H:%M").time()
            current_dt = tz.localize(datetime.combine(date_obj.date(), time_obj))
            current_solar = solarposition.get_solarposition(current_dt, request.latitude, request.longitude)
            if current_solar['elevation'].iloc[0] > 0:
                current_position = {
                    'azimuth': float(current_solar['azimuth'].iloc[0]),
                    'elevation': float(current_solar['elevation'].iloc[0])
                }
        
        # Generate diagram based on type
        if request.diagram_type.lower() == 'polar':
            # Polar diagram shows multiple seasonal paths (Andrew Marsh style)
            # Current position is calculated inside the function from the selected date
            fig = create_polar_sun_path(daytime_data, None, request, date_obj)
        else:
            # Cartesian shows single day path
            fig = create_cartesian_sun_path(daytime_data, current_position, request, date_obj)
        
        # Save figure to bytes buffer
        buf = BytesIO()
        fig.savefig(buf, format='png', dpi=150, bbox_inches='tight')
        buf.seek(0)
        plt.close(fig)
        
        # Return image as streaming response
        return StreamingResponse(buf, media_type="image/png")
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid date/time format: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating sun path diagram: {str(e)}")


# ============================================================================
# VISUALIZATION FUNCTIONS
# ============================================================================

def create_polar_sun_path(daytime_data, current_position, request, date_obj):
    """
    Create a polar projection sun path diagram matching Andrew Marsh's style
    
    Shows multiple seasonal sun paths (summer/winter solstice, equinoxes)
    with hourly markers and precise labeling.
    
    Args:
        daytime_data: DataFrame with solar position data for the selected date
        current_position: Dict with current azimuth/elevation or None
        request: SunPathRequest object
        date_obj: datetime object for the date
    
    Returns:
        matplotlib figure
    """
    # Create figure with white background
    fig = plt.figure(figsize=(10, 10), facecolor='white')
    ax = fig.add_subplot(111, projection='polar', facecolor='white')
    
    # Get timezone for seasonal paths
    tz = get_timezone(request.timezone, request.longitude)
    year = date_obj.year
    
    # Define key dates for seasonal paths
    seasonal_dates = {
        'Summer Solstice (Jun 21)': datetime(year, 6, 21),
        'Equinox (Mar 21 / Sep 23)': datetime(year, 3, 21),
        'Winter Solstice (Dec 21)': datetime(year, 12, 21)
    }
    
    # Colors matching Andrew Marsh's style
    colors = {
        'Summer Solstice (Jun 21)': '#FF8C00',  # Dark orange
        'Equinox (Mar 21 / Sep 23)': '#FFA500',  # Orange
        'Winter Solstice (Dec 21)': '#FFD700'   # Gold
    }
    
    # Plot seasonal sun paths
    for season_name, season_date in seasonal_dates.items():
        # Create time range for this season
        date_start = tz.localize(datetime.combine(season_date.date(), datetime.min.time()))
        times = pd.date_range(date_start, date_start + timedelta(days=1), freq='5min', tz=tz)
        
        # Calculate solar position
        solar_pos = solarposition.get_solarposition(times, request.latitude, request.longitude)
        
        # Filter daylight hours
        daytime_mask = solar_pos['elevation'] > 0
        season_daytime = solar_pos[daytime_mask]
        
        if len(season_daytime) > 0:
            # Convert to polar coordinates
            # r = 90 - elevation (so horizon=90, zenith=0)
            # theta in radians, adjusted so North=top, clockwise
            r = 90 - season_daytime['elevation']
            theta = np.deg2rad(90 - season_daytime['azimuth'])
            
            # Plot the path
            ax.plot(theta, r, color=colors[season_name], linewidth=2, 
                   label=season_name, alpha=0.8)
            
            # Add hourly markers (6 AM to 6 PM)
            for hour in range(6, 19):  # 6 AM to 6 PM
                hour_time = tz.localize(datetime.combine(season_date.date(), 
                                                         datetime.strptime(f"{hour:02d}:00", "%H:%M").time()))
                if hour_time in season_daytime.index:
                    hour_data = season_daytime.loc[hour_time]
                    r_hour = 90 - hour_data['elevation']
                    theta_hour = np.deg2rad(90 - hour_data['azimuth'])
                    
                    # Plot hour marker
                    ax.plot(theta_hour, r_hour, 'o', color=colors[season_name], 
                           markersize=4, zorder=3)
                    
                    # Add hour label (only for key hours to avoid clutter)
                    if hour % 3 == 0 or hour == 12:  # 6, 9, 12, 15, 18
                        ax.text(theta_hour, r_hour - 3, f"{hour:02d}", 
                               fontsize=8, ha='center', va='top',
                               color=colors[season_name], fontweight='bold')
    
    # Plot the sun path for the SELECTED DATE (the day user chose)
    # This is the actual path the sun takes on the selected date with hourly markers
    if date_obj:
        # Create time range for the selected date (full day)
        selected_date_start = tz.localize(datetime.combine(date_obj.date(), datetime.min.time()))
        selected_times = pd.date_range(selected_date_start, selected_date_start + timedelta(days=1), freq='5min', tz=tz)
        
        # Calculate solar position for the selected date
        selected_solar_pos = solarposition.get_solarposition(selected_times, request.latitude, request.longitude)
        
        # Filter daylight hours
        selected_daytime_mask = selected_solar_pos['elevation'] > 0
        selected_daytime = selected_solar_pos[selected_daytime_mask]
        
        if len(selected_daytime) > 0:
            # Convert to polar coordinates
            selected_r = 90 - selected_daytime['elevation']
            selected_theta = np.deg2rad(90 - selected_daytime['azimuth'])
            
            # Plot the selected date's path as a thicker blue line
            ax.plot(selected_theta, selected_r, color='#0066CC', linewidth=3, 
                   label=f"Selected Date ({date_obj.strftime('%b %d, %Y')})", 
                   alpha=0.9, zorder=5)
            
            # Add hourly markers on the selected date path (every hour from sunrise to sunset)
            for hour in range(24):
                hour_time = tz.localize(datetime.combine(date_obj.date(), 
                                                         datetime.strptime(f"{hour:02d}:00", "%H:%M").time()))
                if hour_time in selected_daytime.index:
                    hour_data = selected_daytime.loc[hour_time]
                    r_hour = 90 - hour_data['elevation']
                    theta_hour = np.deg2rad(90 - hour_data['azimuth'])
                    
                    # Plot hour marker as small circle
                    ax.plot(theta_hour, r_hour, 'o', color='#0066CC', 
                           markersize=6, zorder=6, markeredgecolor='white', markeredgewidth=1)
                    
                    # Add hour label for key hours
                    if hour % 2 == 0:  # Every 2 hours
                        ax.text(theta_hour, r_hour - 2.5, f"{hour:02d}h", 
                               fontsize=7, ha='center', va='top',
                               color='#0066CC', fontweight='bold',
                               bbox=dict(boxstyle='round,pad=0.2', facecolor='white', 
                                       edgecolor='#0066CC', linewidth=1, alpha=0.8))
    
    # Calculate and highlight current position for the SELECTED DATE
    # This is separate from seasonal paths and shows sun position on user's chosen date/time
    if request.current_time or date_obj:
        try:
            # Use the actual selected date (not seasonal reference dates)
            if request.current_time:
                time_obj = datetime.strptime(request.current_time, "%H:%M").time()
                current_dt = tz.localize(datetime.combine(date_obj.date(), time_obj))
            else:
                # If no time specified, use noon of selected date
                current_dt = tz.localize(datetime.combine(date_obj.date(), 
                                                         datetime.strptime("12:00", "%H:%M").time()))
            
            # Calculate current sun position for selected date/time
            current_solar = solarposition.get_solarposition(current_dt, request.latitude, request.longitude)
            current_elevation = float(current_solar['elevation'].iloc[0])
            current_azimuth = float(current_solar['azimuth'].iloc[0])
            
            # Only show if sun is above horizon
            if current_elevation > 0:
                current_r = 90 - current_elevation
                current_theta = np.deg2rad(90 - current_azimuth)
                
                # Draw crosshair lines through the current position (like Andrew Marsh)
                # Vertical line (azimuth line)
                ax.plot([current_theta, current_theta], [0, 90], 
                       color='red', linewidth=1.5, linestyle='--', alpha=0.7, zorder=9)
                
                # Horizontal line (altitude circle)
                theta_circle = np.linspace(0, 2*np.pi, 100)
                r_circle = np.full_like(theta_circle, current_r)
                ax.plot(theta_circle, r_circle, 
                       color='red', linewidth=1.5, linestyle='--', alpha=0.7, zorder=9)
                
                # Large red dot for current sun position
                ax.plot(current_theta, current_r, 'ro', markersize=16, 
                       label=f"Current Position", 
                       zorder=10, markeredgecolor='darkred', markeredgewidth=2.5)
                
                # Add star marker on top for emphasis
                ax.plot(current_theta, current_r, 'r*', markersize=22, zorder=11)
                
                # Add time and position label
                time_str = request.current_time if request.current_time else "12:00"
                label_text = f"{time_str}\nAz: {current_azimuth:.1f}°\nEl: {current_elevation:.1f}°"
                
                ax.text(current_theta, current_r - 7, label_text, 
                       fontsize=9, ha='center', va='top', color='red', 
                       fontweight='bold', bbox=dict(boxstyle='round,pad=0.5', 
                       facecolor='yellow', edgecolor='red', linewidth=2, alpha=0.95))
        except Exception as e:
            # If there's an error calculating current position, just skip it
            print(f"Warning: Could not calculate current position: {e}")
    
    # Configure polar plot to match Andrew Marsh's style
    ax.set_theta_zero_location('N')  # North at top
    ax.set_theta_direction(-1)  # Clockwise (East on right)
    
    # Set radial limits (0 at center/zenith, 90 at horizon)
    ax.set_ylim(0, 90)
    
    # Altitude circles at 10° intervals (matching Andrew Marsh)
    altitude_circles = [10, 20, 30, 40, 50, 60, 70, 80, 90]
    ax.set_yticks(altitude_circles)
    
    # Label altitudes (elevation angles)
    altitude_labels = [f"{90-alt}°" for alt in altitude_circles]
    ax.set_yticklabels(altitude_labels, fontsize=9)
    
    # Azimuth lines at 30° intervals
    azimuth_ticks = np.arange(0, 360, 30)
    ax.set_xticks(np.deg2rad(azimuth_ticks))
    
    # Custom azimuth labels matching Andrew Marsh style
    azimuth_labels = []
    for angle in azimuth_ticks:
        if angle == 0:
            azimuth_labels.append('N\n0°')
        elif angle == 90:
            azimuth_labels.append('E\n90°')
        elif angle == 180:
            azimuth_labels.append('S\n180°')
        elif angle == 270:
            azimuth_labels.append('W\n270°')
        else:
            azimuth_labels.append(f'{angle}°')
    
    ax.set_xticklabels(azimuth_labels, fontsize=10)
    
    # Grid styling
    ax.grid(True, linestyle='-', linewidth=0.5, alpha=0.3, color='gray')
    
    # Add radial grid lines for azimuth
    for angle in azimuth_ticks:
        theta_line = np.deg2rad(angle)
        ax.plot([theta_line, theta_line], [0, 90], 'gray', 
               linewidth=0.5, alpha=0.3, zorder=1)
    
    # Title
    title = f"Sun Path Diagram\n"
    title += f"Latitude: {request.latitude}°, Longitude: {request.longitude}°"
    if request.current_time:
        title += f" | {date_obj.strftime('%B %d, %Y')} at {request.current_time}"
    else:
        title += f" | {date_obj.strftime('%B %d, %Y')}"
    ax.set_title(title, fontsize=12, fontweight='bold', pad=20)
    
    # Legend
    ax.legend(loc='upper left', bbox_to_anchor=(0.02, 0.98), 
             fontsize=9, framealpha=0.9, edgecolor='gray')
    
    # Add annotation box with site info
    info_text = f"Altitude circles: 10° intervals\nAzimuth lines: 30° intervals"
    ax.text(0.98, 0.02, info_text, transform=ax.transAxes,
           fontsize=8, verticalalignment='bottom', horizontalalignment='right',
           bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    return fig


def create_cartesian_sun_path(daytime_data, current_position, request, date_obj):
    """
    Create a cartesian (azimuth vs elevation) sun path diagram
    
    Args:
        daytime_data: DataFrame with solar position data
        current_position: Dict with current azimuth/elevation or None
        request: SunPathRequest object
        date_obj: datetime object for the date
    
    Returns:
        matplotlib figure
    """
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Plot sun path
    ax.plot(daytime_data['azimuth'], daytime_data['elevation'], 
           'b-', linewidth=2, label='Sun Path')
    
    # Mark hourly positions
    hourly_times = daytime_data.index[::4]  # Every hour (15min * 4)
    for time_point in hourly_times:
        if time_point in daytime_data.index:
            az = daytime_data.loc[time_point, 'azimuth']
            el = daytime_data.loc[time_point, 'elevation']
            ax.plot(az, el, 'bo', markersize=6)
            # Add time labels
            ax.text(az, el + 2, f"{time_point.strftime('%H:%M')}", 
                   fontsize=8, ha='center', va='bottom')
    
    # Highlight current position if provided
    if current_position:
        ax.plot(current_position['azimuth'], current_position['elevation'], 
               'ro', markersize=12, label=f"Current Position ({request.current_time})", zorder=5)
        ax.plot(current_position['azimuth'], current_position['elevation'], 
               'r*', markersize=20, zorder=6)
    
    # Configure plot
    ax.set_xlabel('Azimuth (degrees)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Elevation (degrees)', fontsize=12, fontweight='bold')
    ax.set_xlim(0, 360)
    ax.set_ylim(0, 90)
    ax.set_xticks(np.arange(0, 361, 45))
    ax.set_xticklabels(['N (0°)', 'NE (45°)', 'E (90°)', 'SE (135°)', 
                        'S (180°)', 'SW (225°)', 'W (270°)', 'NW (315°)', 'N (360°)'])
    ax.grid(True, linestyle='--', alpha=0.5)
    
    # Title
    title = f"Sun Path Diagram - {date_obj.strftime('%B %d, %Y')}\n"
    title += f"Latitude: {request.latitude}°, Longitude: {request.longitude}°"
    ax.set_title(title, fontsize=14, fontweight='bold')
    
    # Legend
    ax.legend(loc='upper right')
    
    plt.tight_layout()
    return fig


# ============================================================================
# RUN SERVER
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    print("Starting Solar Position API Server...")
    print("API Documentation: http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000)
