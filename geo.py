#!/usr/bin/env python3
"""
Geospatial visualization utilities for the Football Predictions Streamlit app.
Handles map creation, team/match visualization, and interactive geospatial components.
"""

import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pydeck as pdk
from typing import Optional, Dict, List, Tuple, Any
import logging

# Configure logging
logger = logging.getLogger(__name__)

# =============================================================================
# MAP CONFIGURATION AND STYLING
# =============================================================================

# Default map styling
MAP_STYLES = {
    'light': 'mapbox://styles/mapbox/light-v10',
    'dark': 'mapbox://styles/mapbox/dark-v10',
    'satellite': 'mapbox://styles/mapbox/satellite-v9',
    'streets': 'mapbox://styles/mapbox/streets-v11'
}

# Team markers styling
TEAM_COLORS = {
    'home': '#FF6B6B',      # Red for home teams
    'away': '#4ECDC4',      # Teal for away teams
    'neutral': '#45B7D1',   # Blue for neutral/general teams
    'selected': '#FFD93D'   # Yellow for selected teams
}

PREDICTION_COLORS = {
    'H': '#FF6B6B',   # Red for home win prediction
    'D': '#FFA726',   # Orange for draw prediction  
    'A': '#4ECDC4',   # Teal for away win prediction
}

# =============================================================================
# CORE MAPPING FUNCTIONS
# =============================================================================

def create_teams_map(
    teams_df: pd.DataFrame,
    selected_team: Optional[str] = None,
    map_style: str = 'dark',
    height: int = 600
) -> go.Figure:
    """
    Create an interactive map showing all teams with their stadiums.
    
    Args:
        teams_df: DataFrame with team locations (must have Team, latitude, longitude, Stadium, City)
        selected_team: Team to highlight on the map
        map_style: Map style ('light', 'dark', 'satellite', 'streets')
        height: Map height in pixels
        
    Returns:
        plotly.graph_objects.Figure: Interactive team map
    """
    if teams_df.empty:
        return go.Figure()
    
    # Create a copy to avoid modifying original data
    df = teams_df.copy()
    
    # Add color and size based on selection
    df['color'] = TEAM_COLORS['neutral']
    df['size'] = 8
    
    if selected_team:
        df.loc[df['Team'] == selected_team, 'color'] = TEAM_COLORS['selected']
        df.loc[df['Team'] == selected_team, 'size'] = 15
    
    # Create hover text
    df['hover_text'] = (
        '<b>' + df['Team'] + '</b><br>' +
        'Stadium: ' + df['Stadium'].fillna('Unknown') + '<br>' +
        'City: ' + df['City'].fillna('Unknown') + '<br>' +
        'Coordinates: (' + df['latitude'].round(3).astype(str) + 
        ', ' + df['longitude'].round(3).astype(str) + ')'
    )
    
    # Create the map
    fig = px.scatter_mapbox(
        df,
        lat='latitude',
        lon='longitude',
        hover_name='Team',
        hover_data={
            'Stadium': True,
            'City': True,
            'latitude': ':.3f',
            'longitude': ':.3f'
        },
        color='color',
        size='size',
        color_discrete_map='identity',
        zoom=5,
        height=height,
        title='Football Teams Locations'
    )
    
    # Update map style and layout
    fig.update_layout(
        mapbox_style=map_style,
        mapbox_accesstoken=None,  # Using open street map
        margin={"r": 0, "t": 50, "l": 0, "b": 0},
        showlegend=False,
        font=dict(color='white' if map_style == 'dark' else 'black'),
        paper_bgcolor='rgba(0,0,0,0)' if map_style == 'dark' else 'white'
    )
    
    return fig

def create_matches_map(
    matches_df: pd.DataFrame,
    color_by: str = 'Prediction',
    map_style: str = 'dark',
    height: int = 600
) -> go.Figure:
    """
    Create an interactive map showing matches with predictions.
    
    Args:
        matches_df: DataFrame with match data including coordinates
        color_by: Column to color points by ('Prediction', 'Model', 'National League')
        map_style: Map style
        height: Map height in pixels
        
    Returns:
        plotly.graph_objects.Figure: Interactive matches map
    """
    if matches_df.empty:
        return go.Figure()
    
    # Filter out rows without coordinates
    df = matches_df.dropna(subset=['latitude', 'longitude']).copy()
    
    if df.empty:
        st.warning("No matches with valid coordinates found.")
        return go.Figure()
    
    # Create hover text
    df['hover_text'] = (
        '<b style="font-size:20px; text-align:center; display:block;">' + df['Home Team'] + ' vs ' + df['Away Team'] + '</b><br>' +
        '<span style="font-size:14px; color:#FF6B6B; text-align:center; display:block;">──────────────────────</span><br>' +
        '<span style="font-size:16px; line-height:2.0;">' +
        '📅 ' + pd.to_datetime(df['Game Date']).dt.strftime('%Y-%m-%d') + '<br>' +
        '🕒 ' + df['Game Time'].astype(str) + '<br>' +
        '🏟️ ' + df['Game Stadium'].fillna('Unknown') + '<br>' +
        '🏙️ ' + df['City Stadium'].fillna('Unknown') + '<br>' +
        '🏆 ' + df['National League'].fillna('Unknown') + '<br>' +
        '🎯 ' + df['Prediction'].fillna('Unknown') + '<br>' +
        '💰 ' + df['Predicted Odds'].astype(str) + '<br>' +
        '📊 ' + pd.to_numeric(df['Confidence Score'], errors='coerce').fillna(0).round(3).astype(str) +
        '</span>'
    )
    
    # Set up color mapping
    color_discrete_map = None
    if color_by == 'Prediction':
        color_discrete_map = PREDICTION_COLORS
    
    # Ensure confidence score is numeric for sizing
    df['confidence_numeric'] = pd.to_numeric(df['Confidence Score'], errors='coerce').fillna(0.5)
    
    # Create the map
    fig = px.scatter_mapbox(
        df,
        lat='latitude',
        lon='longitude',
        color=color_by,
        size='confidence_numeric',
        hover_name='hover_text',
        color_discrete_map=color_discrete_map,
        size_max=15,
        zoom=5,
        height=height,
        title=f'Football Matches - Colored by {color_by}'
    )
    
    # Update layout
    fig.update_layout(
        mapbox_style=map_style,
        mapbox_accesstoken=None,
        margin={"r": 0, "t": 50, "l": 0, "b": 0},
        font=dict(color='white' if map_style == 'dark' else 'black'),
        paper_bgcolor='rgba(0,0,0,0)' if map_style == 'dark' else 'white'
    )
    
    return fig

def create_pydeck_map(
    data: pd.DataFrame,
    view_state: Optional[Dict] = None,
    map_style: str = 'dark'
) -> pdk.Deck:
    """
    Create a PyDeck map for more advanced visualizations.
    
    Args:
        data: DataFrame with lat/lon and other attributes
        view_state: Optional view state configuration
        map_style: Map style
        
    Returns:
        pdk.Deck: PyDeck map object
    """
    if data.empty:
        return pdk.Deck()
    
    # Default view state (centered on Europe)
    if view_state is None:
        view_state = {
            'latitude': 50.0,
            'longitude': 10.0,
            'zoom': 5,
            'pitch': 0,
            'bearing': 0
        }
    
    # Create scatter plot layer
    scatter_layer = pdk.Layer(
        'ScatterplotLayer',
        data=data,
        get_position='[longitude, latitude]',
        get_color='[255, 107, 107, 160]',  # Red with transparency
        get_radius=10000,
        radius_scale=1,
        pickable=True,
        auto_highlight=True
    )
    
    # Map style mapping for PyDeck
    pydeck_styles = {
        'dark': 'mapbox://styles/mapbox/dark-v10',
        'light': 'mapbox://styles/mapbox/light-v10'
    }
    
    # Create the deck
    deck = pdk.Deck(
        layers=[scatter_layer],
        initial_view_state=view_state,
        map_style=pydeck_styles.get(map_style, 'mapbox://styles/mapbox/dark-v10'),
        tooltip={
            "html": "<b>{Team}</b><br/>Stadium: {Stadium}<br/>City: {City}",
            "style": {"backgroundColor": "steelblue", "color": "white"}
        }
    )
    
    return deck

# =============================================================================
# SPECIALIZED VISUALIZATION FUNCTIONS
# =============================================================================

def create_prediction_density_map(
    matches_df: pd.DataFrame,
    prediction_type: str = 'H',
    map_style: str = 'dark'
) -> go.Figure:
    """
    Create a heatmap showing density of specific prediction types.
    
    Args:
        matches_df: DataFrame with match predictions and coordinates
        prediction_type: Type of prediction to show density for ('H', 'D', 'A')
        map_style: Map style
        
    Returns:
        plotly.graph_objects.Figure: Density heatmap
    """
    if matches_df.empty:
        return go.Figure()
    
    # Filter for specific prediction type and valid coordinates
    df = matches_df[
        (matches_df['Prediction'] == prediction_type) &
        matches_df['latitude'].notna() &
        matches_df['longitude'].notna()
    ].copy()
    
    if df.empty:
        return go.Figure()
    
    fig = px.density_mapbox(
        df,
        lat='latitude',
        lon='longitude',
        z='Confidence Score',
        radius=20,
        center=dict(lat=50.0, lon=10.0),
        zoom=4,
        mapbox_style=map_style,
        title=f'Density of {prediction_type} Predictions by Confidence'
    )
    
    fig.update_layout(
        margin={"r": 0, "t": 50, "l": 0, "b": 0},
        font=dict(color='white' if map_style == 'dark' else 'black')
    )
    
    return fig

def create_team_route_map(
    team_matches: pd.DataFrame,
    team_name: str,
    map_style: str = 'dark'
) -> go.Figure:
    """
    Create a map showing a team's matches with connecting lines (journey map).
    
    Args:
        team_matches: DataFrame with team's matches and coordinates
        team_name: Name of the team
        map_style: Map style
        
    Returns:
        plotly.graph_objects.Figure: Team journey map
    """
    if team_matches.empty:
        return go.Figure()
    
    # Sort by date to show journey progression
    df = team_matches.sort_values('Game Date').copy()
    
    # Create the base map
    fig = go.Figure()
    
    # Add match points
    fig.add_trace(go.Scattermapbox(
        lat=df['latitude'],
        lon=df['longitude'],
        mode='markers+text',
        marker=dict(
            size=12,
            color=[TEAM_COLORS['home'] if ht == team_name else TEAM_COLORS['away'] 
                   for ht in df['Home Team']]
        ),
        text=df.index + 1,  # Match number
        textposition="middle center",
        hovertemplate=(
            '<b>Match %{text}</b><br>' +
            'Date: %{customdata[0]}<br>' +
            'Opponent: %{customdata[1]}<br>' +
            'Venue: %{customdata[2]}<br>' +
            'Prediction: %{customdata[3]}<br>' +
            '<extra></extra>'
        ),
        customdata=list(zip(
            df['Game Date'],
            [f"{row['Away Team']}" if row['Home Team'] == team_name else f"{row['Home Team']}"
             for _, row in df.iterrows()],
            df['Game Stadium'].fillna('Unknown'),
            df['Prediction']
        )),
        name='Matches'
    ))
    
    # Add connecting lines to show journey
    if len(df) > 1:
        fig.add_trace(go.Scattermapbox(
            lat=df['latitude'],
            lon=df['longitude'],
            mode='lines',
            line=dict(width=2, color='rgba(255, 255, 255, 0.5)'),
            hoverinfo='skip',
            name='Journey'
        ))
    
    # Update layout
    fig.update_layout(
        mapbox=dict(
            style=map_style,
            center=dict(
                lat=df['latitude'].mean(),
                lon=df['longitude'].mean()
            ),
            zoom=6
        ),
        margin={"r": 0, "t": 50, "l": 0, "b": 0},
        title=f"{team_name} - Match Journey",
        font=dict(color='white' if map_style == 'dark' else 'black')
    )
    
    return fig

# =============================================================================
# UTILITY AND HELPER FUNCTIONS
# =============================================================================

def calculate_map_center(df: pd.DataFrame) -> Tuple[float, float]:
    """
    Calculate the center point for a map based on data coordinates.
    
    Args:
        df: DataFrame with latitude and longitude columns
        
    Returns:
        Tuple[float, float]: (latitude, longitude) center point
    """
    if df.empty or 'latitude' not in df.columns or 'longitude' not in df.columns:
        return 50.0, 10.0  # Default to Europe center
    
    # Filter out invalid coordinates
    valid_coords = df.dropna(subset=['latitude', 'longitude'])
    valid_coords = valid_coords[
        (valid_coords['latitude'] != 0) & (valid_coords['longitude'] != 0)
    ]
    
    if valid_coords.empty:
        return 50.0, 10.0
    
    lat_center = valid_coords['latitude'].mean()
    lon_center = valid_coords['longitude'].mean()
    
    return float(lat_center), float(lon_center)

def get_optimal_zoom_level(df: pd.DataFrame) -> int:
    """
    Calculate optimal zoom level based on data spread.
    
    Args:
        df: DataFrame with latitude and longitude columns
        
    Returns:
        int: Optimal zoom level (1-15)
    """
    if df.empty:
        return 5
    
    # Filter valid coordinates
    valid_coords = df.dropna(subset=['latitude', 'longitude'])
    
    if len(valid_coords) < 2:
        return 8
    
    # Calculate the bounding box
    lat_range = valid_coords['latitude'].max() - valid_coords['latitude'].min()
    lon_range = valid_coords['longitude'].max() - valid_coords['longitude'].min()
    
    # Determine zoom level based on coordinate spread
    max_range = max(lat_range, lon_range)
    
    if max_range > 30:
        return 3
    elif max_range > 15:
        return 4
    elif max_range > 8:
        return 5
    elif max_range > 4:
        return 6
    elif max_range > 2:
        return 7
    elif max_range > 1:
        return 8
    elif max_range > 0.5:
        return 9
    else:
        return 10

def filter_matches_by_team(
    matches_df: pd.DataFrame,
    team_name: str,
    match_type: str = 'all'
) -> pd.DataFrame:
    """
    Filter matches for a specific team.
    
    Args:
        matches_df: DataFrame with match data
        team_name: Name of the team to filter for
        match_type: Type of matches ('home', 'away', 'all')
        
    Returns:
        pd.DataFrame: Filtered matches
    """
    if matches_df.empty:
        return matches_df
    
    if match_type == 'home':
        return matches_df[matches_df['Home Team'] == team_name]
    elif match_type == 'away':
        return matches_df[matches_df['Away Team'] == team_name]
    else:  # 'all'
        return matches_df[
            (matches_df['Home Team'] == team_name) | 
            (matches_df['Away Team'] == team_name)
        ]

def add_map_controls(map_container):
    """
    Add interactive controls to a map container.
    
    Args:
        map_container: Streamlit container for the map
    """
    with map_container:
        col1, col2, col3 = st.columns([2, 2, 2])
        
        with col1:
            map_style = st.selectbox(
                'Map Style',
                ['dark', 'light', 'satellite', 'streets'],
                key='map_style'
            )
        
        with col2:
            color_by = st.selectbox(
                'Color by',
                ['Prediction', 'Model', 'National League', 'Confidence Score'],
                key='color_by'
            )
        
        with col3:
            show_labels = st.checkbox('Show Labels', value=True, key='show_labels')
    
    return map_style, color_by, show_labels

def create_legend_for_predictions():
    """Create a legend explaining prediction colors."""
    legend_html = """
    <div style='padding: 10px; background-color: rgba(0,0,0,0.1); border-radius: 5px; margin: 10px 0;'>
        <h4>Prediction Legend:</h4>
        <p><span style='color: #FF6B6B; font-weight: bold;'>●</span> H - Home Win</p>
        <p><span style='color: #FFA726; font-weight: bold;'>●</span> D - Draw</p>
        <p><span style='color: #4ECDC4; font-weight: bold;'>●</span> A - Away Win</p>
    </div>
    """
    return legend_html

# =============================================================================
# MAP STATS AND ANALYTICS
# =============================================================================

def calculate_geographic_stats(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Calculate geographic statistics for matches/teams.
    
    Args:
        df: DataFrame with geographic data
        
    Returns:
        Dict[str, Any]: Geographic statistics
    """
    if df.empty or 'latitude' not in df.columns or 'longitude' not in df.columns:
        return {}
    
    valid_coords = df.dropna(subset=['latitude', 'longitude'])
    
    if valid_coords.empty:
        return {}
    
    stats = {
        'total_locations': len(valid_coords),
        'unique_coordinates': len(valid_coords[['latitude', 'longitude']].drop_duplicates()),
        'center_lat': float(valid_coords['latitude'].mean()),
        'center_lon': float(valid_coords['longitude'].mean()),
        'lat_range': float(valid_coords['latitude'].max() - valid_coords['latitude'].min()),
        'lon_range': float(valid_coords['longitude'].max() - valid_coords['longitude'].min()),
        'northernmost': float(valid_coords['latitude'].max()),
        'southernmost': float(valid_coords['latitude'].min()),
        'easternmost': float(valid_coords['longitude'].max()),
        'westernmost': float(valid_coords['longitude'].min())
    }
    
    return stats

@st.cache_data(ttl=300)
def get_country_distribution(teams_df: pd.DataFrame) -> pd.DataFrame:
    """
    Get distribution of teams by country for geographic analysis.
    
    Args:
        teams_df: DataFrame with team information including country
        
    Returns:
        pd.DataFrame: Country distribution statistics
    """
    if teams_df.empty or 'country' not in teams_df.columns:
        return pd.DataFrame()
    
    country_stats = teams_df.groupby('country').agg({
        'Team': 'count',
        'latitude': 'mean',
        'longitude': 'mean'
    }).reset_index()
    
    country_stats.columns = ['Country', 'Team_Count', 'Avg_Latitude', 'Avg_Longitude']
    country_stats = country_stats.sort_values('Team_Count', ascending=False)
    
    return country_stats