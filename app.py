#!/usr/bin/env python3
"""
Football Predictions Dashboard - Main Streamlit Application
A production-ready analytics dashboard for football match predictions with geospatial visualization.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date, timedelta
import warnings
warnings.filterwarnings('ignore')

# Import local modules
import db
import geo

# =============================================================================
# PAGE CONFIGURATION
# =============================================================================

st.set_page_config(
    page_title="PokoPred Dashboard",
    page_icon="images/pokopred_logo.png",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': """
        # PokoPred - Football Predictions Analytics Dashboard
        
        ## Overview
        PokoPred is an advanced football analytics platform that leverages machine learning 
        and geospatial intelligence to predict match outcomes with high accuracy.
        
        ## Features
        - **Geospatial Analysis**: Interactive maps showing team locations and match venues
        - **Comprehensive Analytics**: Detailed statistics across multiple leagues and seasons
        - **Model Performance Tracking**: Continuous monitoring of prediction accuracy and model effectiveness
        
        ## Data Coverage
        - **13+ Leagues**: Coverage across major football leagues in Europe
        - **Historical Data**: Analysis of matches from 2019 onwards
        - **Team Intelligence**: Detailed analytics for 300+ football teams
        - **Venue Mapping**: Geographic data for stadiums and match locations
        
        ## Technology Stack
        - **Frontend**: Streamlit with Plotly visualizations
        - **Backend**: PostgreSQL database with optimized queries
        - **ML Models**: Multiple ensemble models for prediction accuracy
        - **Mapping**: Advanced geospatial analysis and visualization
        
        ## Version
        PokoPred Dashboard v2.0 - Production Release
        
        Built with ❤️ for football analytics enthusiasts
        """
    }
)

# Custom CSS for dark theme and styling
st.markdown("""
<style>
    .main > div {
        padding-top: 2rem;
    }
    .stMetric {
        background-color: #262730;
        border: 1px solid #464853;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .stSelectbox > div > div {
        background-color: #262730;
    }
    h1 {
        color: #FAFAFA;
        text-align: center;
        padding: 1rem 0;
        border-bottom: 2px solid #FF6B6B;
        margin-bottom: 2rem;
    }
    .kpi-container {
        background: linear-gradient(90deg, #FF6B6B, #4ECDC4);
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    .sidebar .sidebar-content {
        background-color: #1E1E1E;
    }
    /* Custom button styling */
    .stButton > button {
        background-color: #FF6B6B;
        color: white;
        border: none;
        border-radius: 5px;
        padding: 0.5rem 1rem;
    }
    .stButton > button:hover {
        background-color: #FF5252;
    }
    /* Map container styling */
    .map-container {
        border: 1px solid #464853;
        border-radius: 10px;
        padding: 1rem;
        background-color: #262730;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

@st.cache_data(ttl=60)
def load_dashboard_data(filters):
    """Load all data needed for the dashboard with caching."""
    try:
        # Raw data analysis (affected by filters)
        raw_data_metrics = db.get_raw_data_key_metrics(
            league_filter=filters.get('leagues'),
            season_filter=filters.get('seasons'),
            team_filter=filters.get('teams'),
            date_from=filters.get('date_from'),
            date_to=filters.get('date_to')
        )
        
        raw_data_analytics = db.get_raw_data_analytics(
            league_filter=filters.get('leagues'),
            season_filter=filters.get('seasons'),
            team_filter=filters.get('teams'),
            date_from=filters.get('date_from'),
            date_to=filters.get('date_to')
        )
        
        # Predictions data - use last session for dynamic updates
        predictions = db.get_last_session_predictions()
        
        # Supporting data (NOT affected by filters)
        model_performance = db.get_model_performance()
        league_stats = db.get_league_statistics()
        teams_coords = db.get_teams_with_coordinates()
        recent_matches = db.get_recent_matches(50)
        
        return {
            'raw_data_metrics': raw_data_metrics,
            'raw_data_analytics': raw_data_analytics,
            'predictions': predictions,
            'model_performance': model_performance,
            'league_stats': league_stats,
            'teams_coords': teams_coords,
            'recent_matches': recent_matches
        }
    except Exception as e:
        st.error(f"Error loading dashboard data: {e}")
        return {
            'predictions': pd.DataFrame(),
            'model_performance': pd.DataFrame(),
            'league_stats': pd.DataFrame(),
            'teams_coords': pd.DataFrame(),
            'recent_matches': pd.DataFrame()
        }

def create_kpi_cards(raw_data_metrics):
    """Create modern, visually appealing KPI cards with key metrics from model_raw_data."""
    
    # Custom CSS for modern metric cards and sidebar styling
    st.markdown("""
    <style>
    /* Sidebar Styling */
    .css-1d391kg {
        background: linear-gradient(180deg, #1e3c72 0%, #2a5298 100%);
    }
    
    .css-1lcbmhc {
        background-color: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 10px;
        padding: 10px;
        margin: 10px 0;
    }
    
    .stSelectbox > div > div {
        background-color: rgba(255, 255, 255, 0.1);
        border-radius: 8px;
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    .stMultiSelect > div > div {
        background-color: rgba(255, 255, 255, 0.1);
        border-radius: 8px;
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    .stDateInput > div > div {
        background-color: rgba(255, 255, 255, 0.1);
        border-radius: 8px;
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    .filter-section {
        background: linear-gradient(135deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0.05) 100%);
        border-radius: 12px;
        padding: 15px;
        margin: 10px 0;
        border: 1px solid rgba(255,255,255,0.1);
        backdrop-filter: blur(10px);
    }
    
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 8px 25px rgba(0,0,0,0.1);
        text-align: center;
        color: white;
        margin-bottom: 1rem;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        border: 1px solid rgba(255,255,255,0.1);
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 35px rgba(0,0,0,0.15);
    }
    
    .metric-card.games {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    .metric-card.leagues {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
    }
    
    .metric-card.seasons {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
    }
    
    .metric-card.teams {
        background: linear-gradient(135deg, #2c5530 0%, #1a4c96 100%);
    }
    
    .metric-icon {
        font-size: 2.5rem;
        margin-bottom: 0.5rem;
        display: block;
    }
    
    .metric-value {
        font-size: 2.2rem;
        font-weight: bold;
        margin: 0.5rem 0;
        text-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }
    
    .metric-label {
        font-size: 0.9rem;
        opacity: 0.9;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-weight: 500;
    }
    </style>
    """, unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card games">
            <div class="metric-icon">📊</div>
            <div class="metric-value">{raw_data_metrics['total_games']:,}</div>
            <div class="metric-label">Total Games Analyzed</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card leagues">
            <div class="metric-icon">🏆</div>
            <div class="metric-value">{raw_data_metrics['total_leagues']}</div>
            <div class="metric-label">Total Leagues Covered</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card seasons">
            <div class="metric-icon">📅</div>
            <div class="metric-value">{raw_data_metrics['total_seasons']}</div>
            <div class="metric-label">Total Seasons Covered</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-card teams">
            <div class="metric-icon">👕</div>
            <div class="metric-value">{raw_data_metrics['total_teams']}</div>
            <div class="metric-label">Total Teams Covered</div>
        </div>
        """, unsafe_allow_html=True)

def create_home_away_draw_chart(analytics_data):
    """Create a beautiful modern gradient donut chart showing home/away/draw percentages."""
    # Calculate percentages
    total_games = analytics_data['total_games']
    home_pct = round((analytics_data['home_wins'] / total_games * 100), 1) if total_games > 0 else 0
    away_pct = round((analytics_data['away_wins'] / total_games * 100), 1) if total_games > 0 else 0
    draw_pct = round((analytics_data['draws'] / total_games * 100), 1) if total_games > 0 else 0
    
    # Modern gradient colors with improved contrast
    colors = [
        '#FF6B6B',  # Modern coral red for home
        '#4ECDC4',  # Modern teal for away
        '#FFD93D'   # Modern gold for draw
    ]
    
    # Create enhanced donut chart
    fig = go.Figure(data=[go.Pie(
        labels=[f'<b>Home</b><br>{home_pct}%', f'<b>Away</b><br>{away_pct}%', f'<b>Draw</b><br>{draw_pct}%'],
        values=[analytics_data['home_wins'], analytics_data['away_wins'], analytics_data['draws']],
        hole=0.45,  # Larger hole for modern look
        marker=dict(
            colors=colors,
            line=dict(color='rgba(255,255,255,0.4)', width=3)
        ),
        textinfo='label',
        textfont=dict(size=14, color='black', family='Arial Black'),
        textposition='inside',
        hovertemplate='<b>%{label}</b><br><span style="font-size:12px;">Games: %{value:,}</span><br><span style="font-size:12px;">Percentage: %{percent}</span><extra></extra>',
        rotation=90,
        sort=False,
        pull=[0.02, 0.02, 0.02]  # Slight separation for modern effect
    )])
    
    # Enhanced center content with gradient styling
    fig.add_annotation(
        text=f'<b style="font-size:18px; color:#FFD93D;">{total_games:,}</b><br><span style="font-size:13px; color:rgba(255,255,255,0.9); font-weight:bold;">Total Games</span>',
        x=0.5, y=0.5,
        font=dict(size=16, color='white', family='Arial Black'),
        showarrow=False,
        align='center'
    )
    
    fig.update_layout(
        title=dict(
            text='<b style="font-size:18px; background: linear-gradient(45deg, #FF6B6B, #4ECDC4); -webkit-background-clip: text;">Match Results Distribution</b>',
            x=0.5,
            y=0.96,
            font=dict(size=18, color='white', family='Arial Black'),
            xanchor='center'
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        showlegend=True,
        legend=dict(
            orientation='h',
            yanchor='top',
            y=-0.05,
            xanchor='center',
            x=0.5,
            font=dict(size=12, color='white', family='Arial'),
            bgcolor='rgba(0,0,0,0.3)',
            bordercolor='rgba(255,255,255,0.2)',
            borderwidth=1
        ),
        height=480,
        margin=dict(t=80, b=80, l=40, r=40),
        annotations=[
            dict(
                text='<span style="font-size:10px; color:rgba(255,255,255,0.6);">Interactive • Hover for details</span>',
                x=0.5, y=-0.25,
                xanchor='center',
                showarrow=False
            )
        ]
    )
    
    return fig

def create_predicted_odds_chart(analytics_data):
    """Create a modern stacked bar chart with 3 separate bars showing winning odds vs overall odds for each result type."""
    result_types = ['Home Wins', 'Draws', 'Away Wins']
    winning_odds = [
        analytics_data['avg_winning_home_odds'],
        analytics_data['avg_winning_draw_odds'], 
        analytics_data['avg_winning_away_odds']
    ]
    overall_odds = [
        analytics_data['avg_overall_home_odds'],
        analytics_data['avg_overall_draw_odds'],
        analytics_data['avg_overall_away_odds']
    ]
    colors = ['rgba(255, 107, 107, 0.9)', 'rgba(255, 217, 61, 0.9)', 'rgba(78, 205, 196, 0.9)']
    
    # Create stacked bar chart
    fig = go.Figure()
    
    # Add winning odds bars (base layer)
    fig.add_trace(go.Bar(
        x=result_types,
        y=winning_odds,
        name='Winning Odds',
        marker=dict(
            color=colors,
            opacity=0.9,
            line=dict(color='rgba(255,255,255,0.3)', width=2),
            pattern=dict(shape="", solidity=0.8)
        ),
        text=[f'<b>{odds:.2f}</b>' for odds in winning_odds],
        textposition='inside',
        textfont=dict(size=13, color='black', family='Arial Black'),
        hovertemplate='<b>%{x}</b><br><span style="font-size:14px;">Winning Odds: <b>%{y:.2f}</b></span><br><span style="font-size:12px; opacity:0.8;">When this result occurred</span><extra></extra>',
        width=0.6
    ))
    
    # Add overall odds difference (additional layer on top)
    differences = [max(0, overall - winning) for winning, overall in zip(winning_odds, overall_odds)]
    fig.add_trace(go.Bar(
        x=result_types,
        y=differences,
        name='Overall Premium',
        marker=dict(
            color=colors,
            opacity=0.6,
            line=dict(color='rgba(255,255,255,0.3)', width=2),
            pattern=dict(shape="", solidity=0.8)
        ),
        text=[f'<b>{overall:.2f}</b>' if diff > 0 else '' for overall, diff in zip(overall_odds, differences)],
        textposition='inside',
        textfont=dict(size=13, color='white', family='Arial Black'),
        customdata=overall_odds,
        hovertemplate='<b>%{x}</b><br><span style="font-size:14px;">Overall Odds: <b>%{customdata:.2f}</b></span><br><span style="font-size:12px; opacity:0.8;">All matches average</span><extra></extra>',
        width=0.6
    ))
    
    fig.update_layout(
        title=dict(
            text='<b style="font-size:18px;">Average Winning Odds by Result</b>',
            x=0.5,
            y=0.95,
            font=dict(size=16, color='white', family='Arial Black'),
            xanchor='center'
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        xaxis=dict(
            title='',
            showgrid=False,
            showticklabels=True,
            tickfont=dict(color='white', size=12, family='Arial'),
            zeroline=False
        ),
        yaxis=dict(
            title='<b>Average Odds</b>',
            showgrid=True,
            gridcolor='rgba(255,255,255,0.15)',
            title_font=dict(color='white', size=13, family='Arial Black'),
            tickfont=dict(color='white', size=11),
            zeroline=False
        ),
        barmode='stack',
        showlegend=True,
        legend=dict(
            orientation='h',
            yanchor='top',
            y=1.15,
            xanchor='center',
            x=0.5,
            font=dict(size=12, color='white', family='Arial Black'),
            bgcolor='rgba(0,0,0,0.3)',
            bordercolor='rgba(255,255,255,0.2)',
            borderwidth=1
        ),
        height=480,
        margin=dict(t=100, b=50, l=60, r=40),
        bargap=0.3
    )
    
    return fig

def create_goals_shots_chart(filters):
    """Create a modern stacked bar chart showing average goals and shots with filtering."""
    # Get filtered goals and shots data
    goals_shots_data = db.get_goals_shots_filtered_data(
        league_filter=filters.get('leagues'),
        season_filter=filters.get('seasons'),
        team_filter=filters.get('teams'),
        date_from=filters.get('date_from'),
        date_to=filters.get('date_to')
    )
    
    avg_goals = goals_shots_data['avg_goals']
    avg_shots = goals_shots_data['avg_shots']
    total_games = goals_shots_data['total_games']
    
    # Create modern stacked bar chart
    fig = go.Figure()
    
    # Enhanced Goals layer with gradient effect
    fig.add_trace(go.Bar(
        x=['Per Game Average'],
        y=[avg_goals],
        name='Goals',
        marker=dict(
            color='rgba(255, 107, 107, 0.9)',
            line=dict(color='rgba(255,255,255,0.3)', width=2),
            pattern=dict(shape="", solidity=0.8)
        ),
        text=[f'<b>{avg_goals:.1f} Goals</b>'],
        textposition='inside',
        textfont=dict(size=13, color='black', family='Arial Black'),
        hovertemplate='<b>⚽ Goals per Game</b><br><span style="font-size:14px;">Average: <b>%{y:.2f}</b></span><extra></extra>',
        width=0.6
    ))
    
    # Enhanced Shots layer with gradient effect
    fig.add_trace(go.Bar(
        x=['Per Game Average'],
        y=[avg_shots],
        name='Shots',
        marker=dict(
            color='rgba(78, 205, 196, 0.9)',
            line=dict(color='rgba(255,255,255,0.3)', width=2),
            pattern=dict(shape="", solidity=0.8)
        ),
        text=[f'<b>{avg_shots:.1f} Shots</b>'],
        textposition='inside',
        textfont=dict(size=13, color='black', family='Arial Black'),
        hovertemplate='<b>🎯 Shots per Game</b><br><span style="font-size:14px;">Average: <b>%{y:.2f}</b></span><extra></extra>',
        width=0.6
    ))
    
    fig.update_layout(
        title=dict(
            text=f'<b style="font-size:18px;">Goals & Shots Analysis</b>',
            x=0.5,
            y=0.95,
            font=dict(size=16, color='white', family='Arial Black'),
            xanchor='center'
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        xaxis=dict(
            title='',
            showgrid=False,
            showticklabels=False,
            zeroline=False
        ),
        yaxis=dict(
            title='<b>Average per Game</b>',
            showgrid=True,
            gridcolor='rgba(255,255,255,0.15)',
            title_font=dict(color='white', size=13, family='Arial Black'),
            tickfont=dict(color='white', size=11),
            zeroline=False
        ),
        barmode='stack',
        showlegend=True,
        legend=dict(
            orientation='h',
            yanchor='top',
            y=1.15,
            xanchor='center',
            x=0.5,
            font=dict(size=12, color='white', family='Arial Black'),
            bgcolor='rgba(0,0,0,0.3)',
            bordercolor='rgba(255,255,255,0.2)',
            borderwidth=1
        ),
        height=480,
        margin=dict(t=100, b=50, l=60, r=40),
        bargap=0.3
    )
    
    return fig

def create_goals_shots_percentage_chart(filters):
    """Create a bar chart showing goals/shots percentage by league with filtering."""
    # Get league-specific data with proper filtering including leagues
    league_data = db.get_league_goals_shots_analytics(
        league_filter=filters.get('leagues'),
        season_filter=filters.get('seasons'),
        team_filter=filters.get('teams'),
        date_from=filters.get('date_from'),
        date_to=filters.get('date_to')
    )
    
    if league_data.empty:
        return go.Figure()
    
    # Sort by percentage for this chart
    league_data_sorted = league_data.sort_values('goals_shots_percentage', ascending=False)
    
    # Create percentage bar chart
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=league_data_sorted['league'],
        y=league_data_sorted['goals_shots_percentage'],
        name='Goals/Shots Percentage',
        marker=dict(
            color='#E5941E',
            opacity=0.8,
            line=dict(color='rgba(255,255,255,0.2)', width=1)
        ),
        text=[f'{val:.1f}%' for val in league_data_sorted['goals_shots_percentage']],
        textposition='outside',
        textfont=dict(size=11, color='white', family='Arial Black'),
        hovertemplate='<b>%{x}</b><br>Goals/Shots: %{y:.1f}%<extra></extra>'
    ))
    
    fig.update_layout(
        title=dict(
            text='<b>Goals/Shots Efficiency by League</b>',
            x=0.5,
            y=0.95,
            font=dict(size=14, color='white', family='Arial Black'),
            xanchor='center'
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        xaxis=dict(
            title='League',
            showgrid=False,
            title_font=dict(color='white', size=11),
            tickfont=dict(color='white', size=9),
            tickangle=45
        ),
        yaxis=dict(
            title='Efficiency (%)',
            showgrid=True,
            gridcolor='rgba(255,255,255,0.1)',
            title_font=dict(color='white', size=11),
            tickfont=dict(color='white', size=9)
        ),
        showlegend=False,
        height=350,
        margin=dict(t=60, b=60, l=50, r=30)
    )
    
    return fig

def create_prediction_distribution_chart(predictions_df):
    """Create prediction distribution pie chart."""
    if predictions_df.empty:
        return go.Figure()
    
    pred_counts = predictions_df['Prediction'].value_counts()
    
    fig = px.pie(
        values=pred_counts.values,
        names=pred_counts.index,
        title="Prediction Distribution",
        color_discrete_map=geo.PREDICTION_COLORS,
        hole=0.4
    )
    
    fig.update_layout(
        font=dict(color='white'),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        height=400
    )
    
    return fig

def create_confidence_distribution(predictions_df):
    """Create confidence score distribution histogram."""
    if predictions_df.empty or 'Confidence Score' not in predictions_df.columns:
        return go.Figure()
    
    fig = px.histogram(
        predictions_df,
        x='Confidence Score',
        nbins=20,
        title="Confidence Score Distribution",
        color_discrete_sequence=['#FF6B6B']
    )
    
    fig.update_layout(
        font=dict(color='white'),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(title='Confidence Score'),
        yaxis=dict(title='Number of Predictions'),
        height=400
    )
    
    return fig

def create_league_performance_chart(league_stats_df):
    """Create league performance comparison chart."""
    if league_stats_df.empty:
        return go.Figure()
    
    # Group by league and calculate averages across seasons
    league_summary = league_stats_df.groupby('league').agg({
        'home_win_percentage': 'mean',
        'draw_percentage': 'mean',
        'away_win_percentage': 'mean',
        'total_matches': 'sum'
    }).reset_index()
    
    # Create grouped bar chart
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=league_summary['league'],
        y=league_summary['home_win_percentage'],
        name='Home Win %',
        marker_color='#FF6B6B'
    ))
    
    fig.add_trace(go.Bar(
        x=league_summary['league'],
        y=league_summary['draw_percentage'],
        name='Draw %',
        marker_color='#FFA726'
    ))
    
    fig.add_trace(go.Bar(
        x=league_summary['league'],
        y=league_summary['away_win_percentage'],
        name='Away Win %',
        marker_color='#4ECDC4'
    ))
    
    fig.update_layout(
        title="League Performance Comparison",
        font=dict(color='white'),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(title='League'),
        yaxis=dict(title='Percentage'),
        barmode='group',
        height=400
    )
    
    return fig

def create_model_accuracy_chart(model_perf_df):
    """Create model accuracy comparison chart."""
    if model_perf_df.empty:
        return go.Figure()
    
    fig = px.bar(
        model_perf_df.sort_values('accuracy_percentage', ascending=True),
        x='accuracy_percentage',
        y='model',
        orientation='h',
        title="Model Accuracy Comparison",
        color='accuracy_percentage',
        color_continuous_scale='RdYlGn',
        text='accuracy_percentage'
    )
    
    fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
    fig.update_layout(
        font=dict(color='white'),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(title='Accuracy (%)'),
        yaxis=dict(title='Model'),
        height=400,
        showlegend=False
    )
    
    return fig

# =============================================================================
# MAIN APPLICATION
# =============================================================================

def main():
    """Main application function."""
    
    # Modern Header Section with lighter gradient styling
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
        padding: 2.5rem 1.5rem;
        border-radius: 20px;
        margin-bottom: 2rem;
        text-align: center;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        border: 1px solid rgba(255,255,255,0.2);
    ">
        <h1 style="
            color: white;
            font-size: 3rem;
            font-weight: bold;
            margin: 0 0 0.5rem 0;
            text-shadow: 0 2px 10px rgba(0,0,0,0.3);
            letter-spacing: -0.02em;
        ">
            PokoPred Dashboard
        </h1>
        <p style="
            color: rgba(255,255,255,0.9);
            font-size: 1.2rem;
            margin: 0;
            font-weight: bold;
            font-style: italic;
            letter-spacing: 0.5px;
        ">
            Advanced Analytics for Football Match Predictions with Geospatial Intelligence
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Compact connection status indicator with gradient background
    if not db.test_database_connection():
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #ff6b6b 0%, #ee5a52 100%);
            padding: 1rem 1.5rem;
            border-radius: 15px;
            margin-bottom: 1rem;
            text-align: center;
            color: white;
            box-shadow: 0 8px 25px rgba(255,107,107,0.3);
            border: 1px solid rgba(255,255,255,0.1);
        ">
            <div style="font-size: 1.5rem; margin-bottom: 0.5rem;">❌</div>
            <div style="font-weight: bold; font-size: 1.1rem;">Database Connection Failed</div>
            <div style="opacity: 0.9; font-size: 0.9rem;">Please check your configuration</div>
        </div>
        """, unsafe_allow_html=True)
        st.stop()
    else:
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
            padding: 0.7rem 1.2rem;
            border-radius: 12px;
            margin-bottom: 1rem;
            text-align: center;
            color: #333;
            box-shadow: 0 4px 15px rgba(67,233,123,0.3);
            border: 1px solid rgba(255,255,255,0.2);
            font-size: 0.9rem;
            font-weight: 500;
        ">
            ✅ Database connected successfully
        </div>
        """, unsafe_allow_html=True)
    
    # Modern Sidebar for filters
    st.sidebar.markdown("""
    <div class="filter-section">
        <h2 style="color: white; text-align: center; margin-bottom: 20px;">
            🎯 Analysis Filters
        </h2>
        <p style="color: rgba(255,255,255,0.8); text-align: center; font-size: 0.9em; margin-bottom: 0;">
            📊 Applied to Key Metrics & Analytics only
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Load available filter options from model_raw_data
    try:
        raw_leagues = db.get_raw_data_leagues()
        raw_seasons = db.get_raw_data_seasons() 
        raw_teams = db.get_raw_data_teams()
    except Exception as e:
        st.error(f"Error loading filter options: {e}")
        raw_leagues, raw_seasons, raw_teams = [], [], []
    
    selected_leagues = st.sidebar.multiselect(
        "🏆 Select Leagues",
        options=raw_leagues,
        default=[],
        help="Select one or more leagues to filter. Leave empty for all leagues."
    )
    
    selected_seasons = st.sidebar.multiselect(
        "📅 Select Seasons",
        options=raw_seasons,
        default=[],
        help="Select one or more seasons to filter. Leave empty for all seasons."
    )
    
    selected_teams = st.sidebar.multiselect(
        "👕 Select Teams",
        options=raw_teams[:100],  # Increased limit for better selection
        default=[],
        help="Select one or more teams to filter. Leave empty for all teams."
    )
    
    # Date range filter section
    st.sidebar.subheader("📅 Date Range Filter")
    
    from datetime import datetime, date, timedelta
    
    # Default to a reasonable range for raw data analysis
    # Set default date range to include all historical data
    default_start = date(2019, 1, 1)  # Start from 2019 to include all data
    default_end = date.today()
    
    date_from = st.sidebar.date_input(
        "From Date",
        value=default_start,
        min_value=date(2019, 1, 1),  # Allow selection from 2019 to include all data
        max_value=date.today() + timedelta(days=365)
    )
    
    date_to = st.sidebar.date_input(
        "To Date",
        value=default_end,
        min_value=date(2019, 1, 1),  # Consistent with from date
        max_value=date.today() + timedelta(days=365)
    )
    
    # Prepare filters with multi-select support
    filters = {
        'teams': selected_teams if selected_teams else None,
        'leagues': selected_leagues if selected_leagues else None,
        'seasons': selected_seasons if selected_seasons else None,
        'date_from': str(date_from),
        'date_to': str(date_to)
    }
    
    # Add separator and Predictions Filters section
    st.sidebar.markdown("---")
    st.sidebar.markdown("""
    <div class="filter-section">
        <h2 style="color: white; text-align: center; margin-bottom: 20px;">
            📋 Predictions Filters
        </h2>
        <p style="color: rgba(255,255,255,0.8); text-align: center; font-size: 0.9em; margin-bottom: 0;">
            🎯 Applied to Predictions Table & Map only
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Load dashboard data first to get predictions data for filters
    with st.spinner("Loading dashboard data..."):
        data = load_dashboard_data(filters)

    # Initialize session state for predictions filters
    if 'selected_leagues' not in st.session_state:
        st.session_state.selected_leagues = []
    if 'selected_date_range' not in st.session_state:
        st.session_state.selected_date_range = None

    # Add predictions filters to sidebar if we have predictions data
    if not data['predictions'].empty:
        # Convert Game Date to datetime
        if 'Game Date' in data['predictions'].columns:
            data['predictions']['Game Date'] = pd.to_datetime(data['predictions']['Game Date'])
        
        # Date filter in sidebar
        st.sidebar.subheader("📅 Predictions Date Range")
        if 'Game Date' in data['predictions'].columns:
            min_date = data['predictions']['Game Date'].min().date()
            max_date = data['predictions']['Game Date'].max().date()
            
            # If leagues are selected, filter dates based on available leagues
            if st.session_state.selected_leagues:
                league_filtered_data = data['predictions'][
                    data['predictions']['National League'].isin(st.session_state.selected_leagues)
                ]
                if not league_filtered_data.empty:
                    min_date = league_filtered_data['Game Date'].min().date()
                    max_date = league_filtered_data['Game Date'].max().date()
            
            date_range = st.sidebar.date_input(
                "Select date range:",
                value=(min_date, max_date),
                min_value=min_date,
                max_value=max_date,
                key="sidebar_cascading_date_filter",
                help="Select date range for predictions table and map"
            )
            
            # Update session state
            st.session_state.selected_date_range = date_range

        # League filter in sidebar
        st.sidebar.subheader("🏆 Predictions Leagues")
        if 'National League' in data['predictions'].columns:
            # Get available leagues based on date selection
            available_data = data['predictions'].copy()
            
            # If date range is selected, filter leagues based on available dates
            if st.session_state.selected_date_range:
                if isinstance(st.session_state.selected_date_range, tuple) and len(st.session_state.selected_date_range) == 2:
                    start_date, end_date = st.session_state.selected_date_range
                    available_data = available_data[
                        (available_data['Game Date'].dt.date >= start_date) &
                        (available_data['Game Date'].dt.date <= end_date)
                    ]
            
            available_leagues = sorted(available_data['National League'].dropna().unique())
            
            # Set default leagues if none selected yet
            if not st.session_state.selected_leagues:
                default_leagues = available_leagues
            else:
                # Keep only leagues that are still available
                default_leagues = [l for l in st.session_state.selected_leagues if l in available_leagues]
            
            selected_leagues = st.sidebar.multiselect(
                "Select leagues:",
                options=available_leagues,
                default=default_leagues,
                key="sidebar_cascading_league_filter",
                help="Select leagues for predictions table and map"
            )
            
            # Update session state
            st.session_state.selected_leagues = selected_leagues
    
    # Main dashboard content
    
    # Key Metrics Section (from model_raw_data)
    st.header("💎 Key Metrics")
    create_kpi_cards(data['raw_data_metrics'])
    
    st.divider()
    
    # Analytics & Insights Section with detailed game analytics
    st.header("📈 Analytics & Insights")
    
    # Create three columns for analytics charts
    chart_col1, chart_col2, chart_col3 = st.columns(3)
    
    with chart_col1:
        # Home/Away/Draw distribution
        hda_fig = create_home_away_draw_chart(data['raw_data_analytics'])
        st.plotly_chart(hda_fig, use_container_width=True, key="hda_chart")
    
    with chart_col2:
        # Average Goals and Shots per game with filtering
        goals_shots_fig = create_goals_shots_chart(filters)
        st.plotly_chart(goals_shots_fig, use_container_width=True, key="goals_shots_chart")
    
    with chart_col3:
        # Average predicted odds that won
        odds_fig = create_predicted_odds_chart(data['raw_data_analytics'])
        st.plotly_chart(odds_fig, use_container_width=True, key="odds_chart")
    
    st.divider()

    # Simple Table Section with Cascading Filters
    st.header("📋 Predictions Table")
    
    if not data['predictions'].empty:
        # Convert Game Date to datetime if it's not already
        if 'Game Date' in data['predictions'].columns:
            data['predictions']['Game Date'] = pd.to_datetime(data['predictions']['Game Date'])
        
        # Apply cascading filters from sidebar
        filtered_predictions = data['predictions'].copy()
        
        # Apply date filter from sidebar
        if st.session_state.selected_date_range and 'Game Date' in filtered_predictions.columns:
            if isinstance(st.session_state.selected_date_range, tuple) and len(st.session_state.selected_date_range) == 2:
                start_date, end_date = st.session_state.selected_date_range
                filtered_predictions = filtered_predictions[
                    (filtered_predictions['Game Date'].dt.date >= start_date) &
                    (filtered_predictions['Game Date'].dt.date <= end_date)
                ]
        
        # Apply league filter from sidebar
        if st.session_state.selected_leagues and 'National League' in filtered_predictions.columns:
            filtered_predictions = filtered_predictions[
                filtered_predictions['National League'].isin(st.session_state.selected_leagues)
            ]
        
        # Display filter summary
        total_matches = len(data['predictions'])
        filtered_matches = len(filtered_predictions)
        
        if filtered_matches != total_matches:
            st.info(f"📊 Showing {filtered_matches:,} of {total_matches:,} matches (filtered)")
        else:
            st.info(f"📊 Showing all {filtered_matches:,} matches")
        
        # Get model name
        model_name = filtered_predictions['Model'].iloc[0] if 'Model' in filtered_predictions.columns and not filtered_predictions.empty else 'Unknown'
        st.subheader(f"Model Used: {model_name}")
        
        # Select only the specified columns (Game Date to Confidence Score + Draw Probability)
        columns_to_show = ['Game Date', 'Game Time', 'National League', 'Home Team', 'Away Team', 'Prediction', 'Predicted Odds', 'Confidence Score', 'Draw Probability']
        available_columns = [col for col in columns_to_show if col in filtered_predictions.columns]
        
        if not filtered_predictions.empty:
            display_df = filtered_predictions[available_columns].copy()
        else:
            st.warning("No matches found with the selected filters. Please adjust your date range or league selection.")
            display_df = pd.DataFrame()
        if not display_df.empty:
            # Rename columns to more attractive headers
            column_renames = {
                'Game Date': '📅 Date',
                'Game Time': '⏰ Time',
                'National League': '🏆 League',
                'Home Team': '🏠 Home',
                'Away Team': '✈️ Away',
                'Prediction': '🎯 Result',
                'Predicted Odds': '💰 Odds',
                'Confidence Score': '📊 Confidence',
                'Draw Probability': '⚖️ Draw Probability'
            }
            
            display_df = display_df.rename(columns=column_renames)
            
            # Format numeric columns for better display
            if '📊 Confidence' in display_df.columns:
                display_df['📊 Confidence'] = display_df['📊 Confidence'].apply(lambda x: f"{float(x):.2f}" if pd.notnull(x) else "N/A")
            
            if '💰 Odds' in display_df.columns:
                display_df['💰 Odds'] = display_df['💰 Odds'].apply(lambda x: f"{float(x):.2f}" if pd.notnull(x) else "N/A")
        
        # Apply modern styling with rounded corners and bright colors
        def style_predictions_table(df):
            def highlight_prediction(val):
                if val == 'H':
                    return 'background: linear-gradient(135deg, #4CAF50, #66BB6A); color: white; font-weight: bold; border-radius: 8px; padding: 8px; text-align: center; box-shadow: 0 2px 4px rgba(76,175,80,0.3);'
                elif val == 'A':
                    return 'background: linear-gradient(135deg, #F44336, #EF5350); color: white; font-weight: bold; border-radius: 8px; padding: 8px; text-align: center; box-shadow: 0 2px 4px rgba(244,67,54,0.3);'
                elif val == 'D':
                    return 'background: linear-gradient(135deg, #FF9800, #FFB74D); color: white; font-weight: bold; border-radius: 8px; padding: 8px; text-align: center; box-shadow: 0 2px 4px rgba(255,152,0,0.3);'
                return 'padding: 8px; text-align: center;'
            
            def highlight_confidence(val):
                try:
                    score = float(val)
                    if score >= 0.8:
                        return 'background: linear-gradient(135deg, #2196F3, #42A5F5); color: white; font-weight: bold; border-radius: 8px; padding: 8px; text-align: center; box-shadow: 0 2px 4px rgba(33,150,243,0.3);'
                    elif score >= 0.6:
                        return 'background: linear-gradient(135deg, #9C27B0, #BA68C8); color: white; font-weight: bold; border-radius: 8px; padding: 8px; text-align: center; box-shadow: 0 2px 4px rgba(156,39,176,0.3);'
                    else:
                        return 'background: linear-gradient(135deg, #607D8B, #78909C); color: white; font-weight: bold; border-radius: 8px; padding: 8px; text-align: center; box-shadow: 0 2px 4px rgba(96,125,139,0.3);'
                except:
                    return 'padding: 8px; text-align: center;'
            
            def highlight_draw_probability(val):
                if val and '%' in str(val):
                    try:
                        percent = float(str(val).replace('%', ''))
                        if percent >= 40:
                            return 'background: linear-gradient(135deg, #E91E63, #EC407A); color: white; font-weight: bold; border-radius: 8px; padding: 8px; text-align: center; box-shadow: 0 2px 4px rgba(233,30,99,0.3);'
                        elif percent >= 25:
                            return 'background: linear-gradient(135deg, #00BCD4, #26C6DA); color: white; font-weight: bold; border-radius: 8px; padding: 8px; text-align: center; box-shadow: 0 2px 4px rgba(0,188,212,0.3);'
                        else:
                            return 'background: linear-gradient(135deg, #795548, #8D6E63); color: white; font-weight: bold; border-radius: 8px; padding: 8px; text-align: center; box-shadow: 0 2px 4px rgba(121,85,72,0.3);'
                    except:
                        pass
                return 'padding: 8px; text-align: center;'
            
            def style_team_names(val):
                return 'background: linear-gradient(135deg, #37474F, #546E7A); color: white; font-weight: bold; border-radius: 8px; padding: 8px; text-align: center; box-shadow: 0 2px 4px rgba(55,71,79,0.3);'
            
            # Create styled dataframe
            styled_df = df.style.format({
                'Game Date': lambda x: x.strftime('%Y-%m-%d') if pd.notnull(x) else 'N/A',
                'Game Time': lambda x: x.strftime('%H:%M') if pd.notnull(x) else 'N/A'
            })
            
            # Apply conditional formatting with bright gradients
            if '🎯 Result' in df.columns:
                styled_df = styled_df.applymap(highlight_prediction, subset=['🎯 Result'])
            
            if '📊 Confidence' in df.columns:
                styled_df = styled_df.applymap(highlight_confidence, subset=['📊 Confidence'])
            
            if '⚖️ Draw %' in df.columns:
                styled_df = styled_df.applymap(highlight_draw_probability, subset=['⚖️ Draw %'])
                
            if '🏠 Home' in df.columns:
                styled_df = styled_df.applymap(style_team_names, subset=['🏠 Home'])
                
            if '✈️ Away' in df.columns:
                styled_df = styled_df.applymap(style_team_names, subset=['✈️ Away'])
            
            # Set modern colorful table properties with bright skeleton
            styled_df = styled_df.set_properties(**{
                'text-align': 'center',
                'font-size': '14px',
                'font-family': 'Arial, sans-serif',
                'padding': '12px',
                'border-radius': '15px',
                'border': '2px solid transparent',
                'background': 'linear-gradient(135deg, #FF6B6B, #4ECDC4, #45B7D1, #96CEB4, #FFEAA7, #DDA0DD)'
            }).set_table_styles([
                {'selector': 'table', 'props': [
                    ('border-collapse', 'separate'),
                    ('border-spacing', '8px'),
                    ('border-radius', '20px'),
                    ('overflow', 'hidden'),
                    ('box-shadow', '0 10px 30px rgba(255,107,107,0.4), 0 0 0 3px rgba(78,205,196,0.3)'),
                    ('background', 'linear-gradient(45deg, #FF6B6B 0%, #4ECDC4 25%, #45B7D1 50%, #96CEB4 75%, #FFEAA7 100%)'),
                    ('backdrop-filter', 'blur(10px)'),
                    ('border', '3px solid rgba(255,255,255,0.3)')
                ]},
                {'selector': 'thead th', 'props': [
                    ('background', 'linear-gradient(135deg, #FF6B6B, #4ECDC4, #45B7D1)'),
                    ('color', 'white'),
                    ('font-weight', '900'),
                    ('font-size', '15px'),
                    ('text-align', 'center'),
                    ('padding', '20px 15px'),
                    ('border-radius', '15px'),
                    ('box-shadow', '0 6px 15px rgba(255,107,107,0.6), inset 0 1px 0 rgba(255,255,255,0.3)'),
                    ('border', '2px solid rgba(255,255,255,0.4)'),
                    ('text-shadow', '0 2px 4px rgba(0,0,0,0.4)'),
                    ('letter-spacing', '0.8px'),
                    ('text-transform', 'uppercase'),
                    ('background-size', '200% 200%'),
                    ('animation', 'gradient-shift 3s ease infinite')
                ]},
                {'selector': 'tbody td', 'props': [
                    ('border-radius', '12px'),
                    ('margin', '4px'),
                    ('box-shadow', '0 4px 8px rgba(0,0,0,0.1), inset 0 1px 0 rgba(255,255,255,0.2)'),
                    ('border', '2px solid rgba(255,255,255,0.3)'),
                    ('backdrop-filter', 'blur(5px)')
                ]},
                {'selector': 'tbody tr:nth-child(even) td', 'props': [
                    ('background', 'linear-gradient(135deg, rgba(255,107,107,0.1), rgba(78,205,196,0.1), rgba(69,183,209,0.1))'),
                    ('border', '2px solid rgba(78,205,196,0.3)')
                ]},
                {'selector': 'tbody tr:nth-child(odd) td', 'props': [
                    ('background', 'linear-gradient(135deg, rgba(150,206,180,0.1), rgba(255,234,167,0.1), rgba(221,160,221,0.1))'),
                    ('border', '2px solid rgba(150,206,180,0.3)')
                ]},
                {'selector': 'tbody tr:hover td', 'props': [
                    ('transform', 'scale(1.03)'),
                    ('transition', 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)'),
                    ('box-shadow', '0 8px 20px rgba(255,107,107,0.3), 0 0 0 3px rgba(78,205,196,0.5)'),
                    ('background', 'linear-gradient(135deg, rgba(255,107,107,0.2), rgba(78,205,196,0.2))'),
                    ('border', '2px solid rgba(255,107,107,0.6)')
                ]},
                {'selector': '@keyframes gradient-shift', 'props': [
                    ('0%', 'background-position: 0% 50%'),
                    ('50%', 'background-position: 100% 50%'),
                    ('100%', 'background-position: 0% 50%')
                ]}
            ])
            
            return styled_df
        
        # Display the styled table
        st.dataframe(
            style_predictions_table(display_df),
            use_container_width=True,
            height=400
        )
        
        # Download button for the filtered data
        csv = display_df.to_csv(index=False)
        st.download_button(
            label="📥 Download Filtered Predictions as CSV",
            data=csv,
            file_name=f"football_predictions_filtered_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
    else:
        st.warning("No predictions found for the selected filters. Try adjusting your date range or league selection.")

    st.divider()

    # Geospatial Map Section - Now with same filtering as table
    st.header("🗺️ Match Predictions Map")
    
    # Use filtered data if we're in the predictions section, otherwise use all data
    if not data['predictions'].empty:
        # Check if we have filtered data from the table section above
        try:
            map_data = filtered_predictions if 'filtered_predictions' in locals() else data['predictions']
        except:
            map_data = data['predictions']
            
        # Filter matches with valid coordinates from the filtered dataset
        matches_with_coords = map_data.dropna(subset=['latitude', 'longitude']).copy()
        
        if not matches_with_coords.empty:
            # Show map info with filter status
            if 'filtered_predictions' in locals() and len(map_data) != len(data['predictions']):
                st.subheader(f"📍 {len(matches_with_coords):,} Filtered Matches on Map (of {len(data['predictions']):,} total)")
            else:
                st.subheader(f"📍 {len(matches_with_coords):,} Matches on Map")
            
            # Create dark themed map
            fig = go.Figure()
            
            fig.add_trace(go.Scattermapbox(
                lat=matches_with_coords['latitude'],
                lon=matches_with_coords['longitude'],
                mode='markers',
                marker=dict(
                    size=15,
                    color='#C0C0C0',  # Silver color
                    opacity=0.9
                ),
                text=matches_with_coords['Home Team'] + ' vs ' + matches_with_coords['Away Team'],
                hovertemplate=(
                    '<b style="font-size:20px; text-align:center; display:block;">%{text}</b><br>' +
                    '<span style="font-size:14px; color:#FF6B6B; text-align:center; display:block;">──────────────────────</span><br>' +
                    '<span style="font-size:16px; text-align:center;">' +
                    '📅 %{customdata[0]}<br>' +
                    '🕒 %{customdata[1]}<br>' +
                    '🏟️ %{customdata[2]}<br>' +
                    '🏙️ %{customdata[3]}<br>' +
                    '🎯 %{customdata[4]}<br>' +
                    '💰 %{customdata[5]}' +
                    '</span>' +
                    '<extra></extra>'
                ),
                customdata=list(zip(
                    pd.to_datetime(matches_with_coords['Game Date']).dt.strftime('%Y-%m-%d'),
                    matches_with_coords['Game Time'].astype(str),
                    matches_with_coords['Game Stadium'].fillna('Unknown Stadium'),
                    matches_with_coords['City Stadium'].fillna('Unknown City'),
                    matches_with_coords['Prediction'].fillna('Unknown'),
                    matches_with_coords['Predicted Odds'].astype(str)
                )),
                showlegend=False
            ))
            
            # Dark theme layout
            fig.update_layout(
                mapbox=dict(
                    style='carto-darkmatter',
                    center=dict(
                        lat=matches_with_coords['latitude'].mean(),
                        lon=matches_with_coords['longitude'].mean()
                    ),
                    zoom=5
                ),
                height=800,
                margin=dict(r=0, t=20, l=0, b=0),
                paper_bgcolor='#0E1117',
                plot_bgcolor='#0E1117',
                font=dict(color='white')
            )
            
            # Display the map with selection capability
            selected_data = st.plotly_chart(fig, use_container_width=True, key="map_chart", on_select="rerun")
            
            # Alternative: Use session state to track clicks
            if 'selected_match_idx' not in st.session_state:
                st.session_state.selected_match_idx = None
            
            # Show infographic table when a point is clicked
            if selected_data and hasattr(selected_data, 'selection') and selected_data.selection and hasattr(selected_data.selection, 'points') and selected_data.selection.points:
                try:
                    # Access point_index correctly from the dictionary
                    point_data = selected_data.selection.points[0]
                    if isinstance(point_data, dict):
                        point_idx = point_data['point_index']
                    else:
                        point_idx = point_data.point_index
                    
                    # Always update the session state when a new point is selected
                    if st.session_state.selected_match_idx != point_idx:
                        st.session_state.selected_match_idx = point_idx
                        st.rerun()
                    
                except Exception as e:
                    st.error(f"Error getting point index: {e}")
            
            # Display match info if we have a selected match
            if st.session_state.selected_match_idx is not None:
                try:
                    selected_match = matches_with_coords.iloc[st.session_state.selected_match_idx]
                    
                    st.markdown("---")
                    
                    # Create enhanced match display
                    st.markdown(f"""
                    <div style="
                        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
                        padding: 2.5rem;
                        border-radius: 20px;
                        margin: 1.5rem 0;
                        box-shadow: 0 15px 35px rgba(0,0,0,0.4), 0 5px 15px rgba(0,0,0,0.2);
                        border: 2px solid rgba(255,255,255,0.15);
                        backdrop-filter: blur(10px);
                    ">
                        <h2 style="
                            color: #FFD93D; 
                            text-align: center; 
                            margin-bottom: 2rem; 
                            font-size: 2.2rem; 
                            font-weight: bold;
                            text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
                        ">
                            {selected_match['Home Team']} vs {selected_match['Away Team']}
                        </h2>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Team Comparison Section - First, positioned before the three detail boxes
                    home_team = selected_match.get('Home Team', '')
                    away_team = selected_match.get('Away Team', '')
                    
                    if home_team and away_team:
                        team_stats = db.get_team_statistics(home_team, away_team)
                        
                        # Team comparison with very light green container styling
                        st.markdown(f"""
                        <div style="
                            background: linear-gradient(135deg, rgba(76,175,80,0.08) 0%, rgba(129,199,132,0.05) 100%);
                            padding: 1rem;
                            border-radius: 15px;
                            margin: 1rem 0;
                            border: 2px solid rgba(76,175,80,0.2);
                            box-shadow: 0 4px 12px rgba(76,175,80,0.1);
                            text-align: center;
                        ">
                            <h3 style="color: #4CAF50; margin-bottom: 0.75rem; font-size: 1.4rem; font-weight: bold;">⚔️ Teams Comparison</h3>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Team names header
                        col1, col2, col3 = st.columns([2, 1, 2])
                        
                        # Statistics rows with better alignment
                        stats_data = [
                            ("League Rank", team_stats.get(home_team, {}).get('league_rank', 'N/A'), team_stats.get(away_team, {}).get('league_rank', 'N/A')),
                            ("Points", team_stats.get(home_team, {}).get('points', 'N/A'), team_stats.get(away_team, {}).get('points', 'N/A')),
                            ("Goals", f"{team_stats.get(home_team, {}).get('goals_for', 'N/A')}-{team_stats.get(home_team, {}).get('goals_against', 'N/A')}", 
                             f"{team_stats.get(away_team, {}).get('goals_for', 'N/A')}-{team_stats.get(away_team, {}).get('goals_against', 'N/A')}"),
                            ("Last 5 Games", team_stats.get(home_team, {}).get('last_5_games', 'N/A'), team_stats.get(away_team, {}).get('last_5_games', 'N/A'))
                        ]
                        
                        # Container for stats with centered alignment
                        st.markdown('<div style="display: flex; flex-direction: column; align-items: center;">', unsafe_allow_html=True)
                        
                        for stat_name, home_val, away_val in stats_data:
                            col1, col2, col3 = st.columns([1, 1, 1])
                            with col1:
                                st.markdown(f"""
                                <div style='
                                    text-align: center; 
                                    font-size: 1rem; 
                                    font-weight: bold; 
                                    color: white; 
                                    padding: 8px; 
                                    background: rgba(156,39,176,0.15); 
                                    border-radius: 8px; 
                                    margin: 3px;
                                    border: 1px solid rgba(156,39,176,0.3);
                                '>{home_val}</div>
                                """, unsafe_allow_html=True)
                            with col2:
                                st.markdown(f"""
                                <div style='
                                    text-align: center; 
                                    font-weight: bold; 
                                    color: #FFD700; 
                                    padding: 8px;
                                    font-size: 0.95rem;
                                    display: flex;
                                    align-items: center;
                                    justify-content: center;
                                    height: 100%;
                                '>{stat_name}</div>
                                """, unsafe_allow_html=True)
                            with col3:
                                st.markdown(f"""
                                <div style='
                                    text-align: center; 
                                    font-size: 1rem; 
                                    font-weight: bold; 
                                    color: white; 
                                    padding: 8px; 
                                    background: rgba(156,39,176,0.15); 
                                    border-radius: 8px; 
                                    margin: 3px;
                                    border: 1px solid rgba(156,39,176,0.3);
                                '>{away_val}</div>
                                """, unsafe_allow_html=True)
                        
                        st.markdown('</div>', unsafe_allow_html=True)
                    
                    # Three column layout for match details
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.markdown(f"""
                        <div style="
                            background: linear-gradient(135deg, rgba(78,205,196,0.15) 0%, rgba(78,205,196,0.08) 100%);
                            padding: 2rem;
                            border-radius: 15px;
                            margin-bottom: 1rem;
                            border: 2px solid rgba(78,205,196,0.3);
                            box-shadow: 0 8px 25px rgba(78,205,196,0.1), 0 4px 15px rgba(0,0,0,0.2);
                            backdrop-filter: blur(8px);
                            transition: transform 0.3s ease;
                            height: 320px;
                            min-height: 320px;
                        ">
                            <h4 style="
                                color: #4ECDC4; 
                                margin-bottom: 1.5rem;
                                font-size: 1.3rem;
                                font-weight: bold;
                                text-shadow: 1px 1px 2px rgba(0,0,0,0.3);
                                border-bottom: 2px solid rgba(78,205,196,0.3);
                                padding-bottom: 0.5rem;
                            ">⚽ Match Details</h4>
                            <p style="color: white; margin: 0.5rem 0;"><strong>📅 Date:</strong> {selected_match.get('Game Date', 'Unknown')}</p>
                            <p style="color: white; margin: 0.5rem 0;"><strong>⏰ Time:</strong> {selected_match.get('Game Time', 'Unknown')}</p>
                            <p style="color: white; margin: 0.5rem 0;"><strong>🏟️ Stadium:</strong> {selected_match.get('Game Stadium', 'Unknown')}</p>
                            <p style="color: white; margin: 0.5rem 0;"><strong>🏙️ City:</strong> {selected_match.get('City Stadium', 'Unknown')}</p>
                            <p style="color: white; margin: 0.5rem 0;"><strong>🏆 League:</strong> {selected_match.get('National League', 'Unknown')}</p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col2:
                        st.markdown(f"""
                        <div style="
                            background: linear-gradient(135deg, rgba(255,167,38,0.15) 0%, rgba(255,167,38,0.08) 100%);
                            padding: 2rem;
                            border-radius: 15px;
                            margin-bottom: 1rem;
                            border: 2px solid rgba(255,167,38,0.3);
                            box-shadow: 0 8px 25px rgba(255,167,38,0.1), 0 4px 15px rgba(0,0,0,0.2);
                            backdrop-filter: blur(8px);
                            transition: transform 0.3s ease;
                            height: 320px;
                            min-height: 320px;
                        ">
                            <h4 style="
                                color: #FFA726; 
                                margin-bottom: 1.5rem;
                                font-size: 1.3rem;
                                font-weight: bold;
                                text-shadow: 1px 1px 2px rgba(0,0,0,0.3);
                                border-bottom: 2px solid rgba(255,167,38,0.3);
                                padding-bottom: 0.5rem;
                            ">🌤️ Weather Info</h4>
                            <p style="color: white; margin: 0.5rem 0;"><strong>🌡️ Temperature:</strong> {selected_match.get('Predicted Temperature', 'N/A')}</p>
                            <p style="color: white; margin: 0.5rem 0;"><strong>💨 Wind Speed:</strong> {selected_match.get('Wind Speed', 'N/A')}</p>
                            <p style="color: white; margin: 0.5rem 0;"><strong>🌤️ Weather:</strong> {selected_match.get('Weather Forecast', 'N/A')}</p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col3:
                        st.markdown(f"""
                        <div style="
                            background: linear-gradient(135deg, rgba(255,107,107,0.15) 0%, rgba(255,107,107,0.08) 100%);
                            padding: 2rem;
                            border-radius: 15px;
                            margin-bottom: 1rem;
                            border: 2px solid rgba(255,107,107,0.3);
                            box-shadow: 0 8px 25px rgba(255,107,107,0.1), 0 4px 15px rgba(0,0,0,0.2);
                            backdrop-filter: blur(8px);
                            transition: transform 0.3s ease;
                            height: 320px;
                            min-height: 320px;
                        ">
                            <h4 style="
                                color: #FF6B6B; 
                                margin-bottom: 1.5rem;
                                font-size: 1.3rem;
                                font-weight: bold;
                                text-shadow: 1px 1px 2px rgba(0,0,0,0.3);
                                border-bottom: 2px solid rgba(255,107,107,0.3);
                                padding-bottom: 0.5rem;
                            ">🎯 Prediction Details</h4>
                            <p style="color: white; margin: 0.5rem 0;"><strong>🔮 Model:</strong> {selected_match.get('Model', 'N/A')}</p>
                            <p style="color: white; margin: 0.5rem 0;"><strong>🎯 Prediction:</strong> {selected_match.get('Prediction', 'N/A')}</p>
                            <p style="color: white; margin: 0.5rem 0;"><strong>📊 Confidence:</strong> {selected_match.get('Confidence Score', 'N/A')}</p>
                            <p style="color: white; margin: 0.5rem 0;"><strong>⚖️ Draw Probability:</strong> {selected_match.get('Draw Probability', 'N/A')}</p>
                            <p style="color: white; margin: 0.5rem 0;"><strong>💰 Predicted Odds:</strong> {selected_match.get('Predicted Odds', 'N/A')}</p>
                        </div>
                        """, unsafe_allow_html=True)
                    

                    
                    # Add a button to clear selection
                    if st.button("Clear Selection"):
                        st.session_state.selected_match_idx = None
                        st.rerun()
                        
                except Exception as e:
                    st.error(f"Error displaying match details: {e}")
            
            else:
                st.info("👆 Click on any silver pin to see detailed match information")
        
        else:
            st.warning("⚠️ No matches with valid coordinates found.")
    else:
        st.warning("⚠️ No prediction data available.")
    
    st.divider()
    
    # League Table Viewer Section
    st.header("🏆 League Table Viewer")
    
    # League Table Filters - Separate from main filters
    st.subheader("⚙️ League Table Filters")
    
    # Load filter options specifically for league table
    try:
        league_table_leagues = db.get_league_table_leagues()
        league_table_seasons = db.get_league_table_seasons()
        league_table_teams = db.get_league_table_teams()
    except Exception as e:
        st.error(f"Error loading league table filter options: {e}")
        league_table_leagues, league_table_seasons, league_table_teams = [], [], []
    
    # Create three columns for league table filters
    lt_col1, lt_col2, lt_col3 = st.columns(3)
    
    with lt_col1:
        selected_lt_leagues = st.multiselect(
            "🏆 Select Leagues",
            options=league_table_leagues,
            default=[],
            help="Select leagues to display in the table",
            key="league_table_leagues"
        )
    
    with lt_col2:
        selected_lt_seasons = st.multiselect(
            "📅 Select Seasons", 
            options=league_table_seasons,
            default=[league_table_seasons[0]] if league_table_seasons else [],
            help="Select seasons to display",
            key="league_table_seasons"
        )
    
    with lt_col3:
        selected_lt_teams = st.multiselect(
            "👕 Select Teams",
            options=league_table_teams[:50],  # Limit for performance
            default=[],
            help="Select specific teams (optional)",
            key="league_table_teams"
        )
    
    # Get league table data
    with st.spinner("Loading league table data..."):
        league_table_data = db.get_league_table(
            league_filter=selected_lt_leagues if selected_lt_leagues else None,
            season_filter=selected_lt_seasons if selected_lt_seasons else None,
            team_filter=selected_lt_teams if selected_lt_teams else None
        )
    
    # Display league table
    if not league_table_data.empty:
        st.subheader(f"📊 League Standings ({len(league_table_data):,} teams)")
        
        # Format the data for better display
        display_table = league_table_data.copy()
        
        # Rename columns for better readability
        column_renames = {
            'team': '👕 Team',
            'league': '🏆 League', 
            'season': '📅 Season',
            'league_rank': '📍 Rank',
            'total_points': '⭐ Points',
            'total_games_played': '🎮 Games',
            'total_goals_scored': '⚽ Goals For',
            'total_goals_conceded': '🥅 Goals Against',
            'goal_difference': '📊 Goal Diff',
            'last_5_games': '📈 Last 5',
            'points_per_game': '💯 PPG'
        }
        
        display_table = display_table.rename(columns=column_renames)
        
        # Format numeric columns
        if '💯 PPG' in display_table.columns:
            display_table['💯 PPG'] = display_table['💯 PPG'].apply(
                lambda x: f"{float(x):.2f}" if pd.notnull(x) else "0.00"
            )
        
        # Style the league table
        def style_league_table(df):
            def highlight_rank(val):
                if pd.notnull(val):
                    rank = int(val)
                    if rank <= 4:  # Top 4 - Champions League
                        return 'background: linear-gradient(135deg, #4CAF50, #66BB6A); color: white; font-weight: bold; border-radius: 8px; padding: 8px; text-align: center;'
                    elif rank <= 6:  # Europa League
                        return 'background: linear-gradient(135deg, #FF9800, #FFB74D); color: white; font-weight: bold; border-radius: 8px; padding: 8px; text-align: center;'
                    elif rank >= len(df) - 2:  # Relegation zone (bottom 3)
                        return 'background: linear-gradient(135deg, #F44336, #EF5350); color: white; font-weight: bold; border-radius: 8px; padding: 8px; text-align: center;'
                return 'background: linear-gradient(135deg, #607D8B, #78909C); color: white; font-weight: bold; border-radius: 8px; padding: 8px; text-align: center;'
            
            def highlight_points(val):
                if pd.notnull(val):
                    points = int(val)
                    if points >= 70:
                        return 'background: linear-gradient(135deg, #2196F3, #42A5F5); color: white; font-weight: bold; border-radius: 8px; padding: 8px; text-align: center;'
                    elif points >= 50:
                        return 'background: linear-gradient(135deg, #9C27B0, #BA68C8); color: white; font-weight: bold; border-radius: 8px; padding: 8px; text-align: center;'
                return 'background: linear-gradient(135deg, #795548, #8D6E63); color: white; font-weight: bold; border-radius: 8px; padding: 8px; text-align: center;'
            
            def style_team_names(val):
                return 'background: linear-gradient(135deg, #37474F, #546E7A); color: white; font-weight: bold; border-radius: 8px; padding: 8px; text-align: center;'
            
            styled_df = df.style
            
            # Apply conditional formatting
            if '📍 Rank' in df.columns:
                styled_df = styled_df.applymap(highlight_rank, subset=['📍 Rank'])
            
            if '⭐ Points' in df.columns:
                styled_df = styled_df.applymap(highlight_points, subset=['⭐ Points'])
                
            if '👕 Team' in df.columns:
                styled_df = styled_df.applymap(style_team_names, subset=['👕 Team'])
            
            # Set table styling
            styled_df = styled_df.set_properties(**{
                'text-align': 'center',
                'font-size': '13px',
                'font-family': 'Arial, sans-serif',
                'padding': '10px'
            }).set_table_styles([
                {'selector': 'table', 'props': [
                    ('border-collapse', 'separate'),
                    ('border-spacing', '6px'),
                    ('border-radius', '15px'),
                    ('overflow', 'hidden'),
                    ('box-shadow', '0 8px 25px rgba(0,0,0,0.2)'),
                    ('background', 'linear-gradient(135deg, #1a1a2e 0%, #16213e 100%)')
                ]},
                {'selector': 'thead th', 'props': [
                    ('background', 'linear-gradient(135deg, #FF6B6B, #4ECDC4)'),
                    ('color', 'white'),
                    ('font-weight', 'bold'),
                    ('font-size', '14px'),
                    ('text-align', 'center'),
                    ('padding', '15px 10px'),
                    ('border-radius', '10px')
                ]},
                {'selector': 'tbody tr:hover td', 'props': [
                    ('transform', 'scale(1.02)'),
                    ('transition', 'all 0.2s ease'),
                    ('box-shadow', '0 4px 15px rgba(255,107,107,0.3)')
                ]}
            ])
            
            return styled_df
        
        # Display the styled league table
        st.dataframe(
            style_league_table(display_table),
            use_container_width=True,
            height=500
        )
        
        # Download button for league table
        csv = display_table.to_csv(index=False)
        st.download_button(
            label="📥 Download League Table as CSV",
            data=csv,
            file_name=f"league_table_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            key="download_league_table"
        )
        
    else:
        st.warning("No league table data found for the selected filters. Please adjust your selection.")
    
    # Footer
    st.divider()
    st.markdown("""
    <div style='text-align: center; color: #888; padding: 2rem;'>
        <p>Football Predictions Dashboard | Built with Streamlit & PostgreSQL</p>
        <p>Last updated: {}</p>
    </div>
    """.format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")), unsafe_allow_html=True)

# =============================================================================
# APPLICATION ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        st.error(f"Application error: {e}")
        st.exception(e)