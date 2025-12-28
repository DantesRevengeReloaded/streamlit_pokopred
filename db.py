#!/usr/bin/env python3
"""
Database connection and query module for the Football Predictions Streamlit app.
Handles PostgreSQL connections, caching, and all data retrieval functions.
"""

import os
import json
import pandas as pd
import psycopg2
from psycopg2.extras import RealDictCursor
import streamlit as st
from typing import Optional, Dict, Any, List, Tuple
import logging
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseManager:
    """
    Handles PostgreSQL database connections and query execution with caching.
    """
    
    def __init__(self, config_path: str = "../config.json"):
        """
        Initialize database manager with credentials from .env file or config.json.
        
        Args:
            config_path: Path to config.json file (fallback option)
        """
        self.config_path = config_path
        self.connection_params = self._load_db_config()
        
    def _load_db_config(self) -> Dict[str, str]:
        """Load database configuration from .env file, config.json, or environment variables."""
        try:
            # Primary: Load from .env file or environment variables
            db_config = {
                'host': os.getenv('DB_HOST', 'localhost'),
                'port': int(os.getenv('DB_PORT', 5432)),
                'database': os.getenv('DB_NAME'),
                'user': os.getenv('DB_USER'),
                'password': os.getenv('DB_PASSWORD')
            }
            
            # Check if all required credentials are present from environment
            if all([db_config['database'], db_config['user'], db_config['password']]):
                return db_config
            
            # Fallback: Try to load from config.json
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    config = json.load(f)
                    
                file_db_config = config.get('database', {})
                
                # Override missing values with config.json values
                for key in ['host', 'port', 'database', 'user', 'password']:
                    if not db_config.get(key) and file_db_config.get(key):
                        if key == 'port':
                            db_config[key] = int(file_db_config[key])
                        else:
                            db_config[key] = file_db_config[key]
            
            return db_config
                
        except Exception as e:
            logger.error(f"Error loading database config: {e}")
            st.error(f"Database configuration error: {e}")
            return {}
    
    def get_connection(self):
        """Create and return a database connection."""
        try:
            conn = psycopg2.connect(**self.connection_params)
            return conn
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            st.error(f"Failed to connect to database: {e}")
            return None
    
    def execute_query(self, query: str, params: Optional[tuple] = None) -> pd.DataFrame:
        """
        Execute a SQL query and return results as pandas DataFrame.
        
        Args:
            query: SQL query string
            params: Query parameters for safe parameterized queries
            
        Returns:
            pandas.DataFrame: Query results
        """
        conn = self.get_connection()
        if conn is None:
            return pd.DataFrame()
            
        try:
            # Use psycopg2 cursor for parameterized queries, then convert to DataFrame
            cursor = conn.cursor()
            
            if params:
                logger.info(f"Executing query with params: {params}")
                cursor.execute(query, params)
            else:
                logger.info("Executing query without params")
                cursor.execute(query)
                
            # Fetch results and column names
            results = cursor.fetchall()
            logger.info(f"Query returned {len(results)} rows")
            
            if results:
                columns = [desc[0] for desc in cursor.description]
                logger.info(f"Column count: {len(columns)}, First row length: {len(results[0])}")
                df = pd.DataFrame(results, columns=columns)
            else:
                df = pd.DataFrame()
                
            cursor.close()
            return df
            
        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            import traceback
            logger.error(f"Full traceback: {traceback.format_exc()}")
            st.error(f"Query failed: {e}")
            return pd.DataFrame()
        finally:
            conn.close()

# Initialize global database manager
@st.cache_resource
def get_db_manager():
    """Get cached database manager instance."""
    return DatabaseManager()

# =============================================================================
# CACHED QUERY FUNCTIONS
# =============================================================================

@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_enhanced_predictions(
    team_filter: Optional[str] = None,
    league_filter: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    model_filter: Optional[str] = None,
    last_session_only: bool = False
) -> pd.DataFrame:
    """
    Get enhanced predictions with geospatial data and weather information.
    This is the main query for the application.
    
    Args:
        team_filter: Filter by team name (home or away)
        league_filter: Filter by league
        date_from: Start date filter (YYYY-MM-DD)
        date_to: End date filter (YYYY-MM-DD)
        model_filter: Filter by model name
        last_session_only: If True, only returns predictions from the latest session
        
    Returns:
        pandas.DataFrame: Enhanced predictions with all joined data
    """
    db = get_db_manager()
    
    # If last session only, first get the latest session_id
    if last_session_only:
        session_query = """
        SELECT MAX(session_id) as latest_session_id
        FROM enhanced_predictions
        """
        try:
            session_result = db.execute_query(session_query)
            if not session_result.empty and session_result.iloc[0]['latest_session_id'] is not None:
                latest_session_id = session_result.iloc[0]['latest_session_id']
                # Clear existing date filters and add session_id filter
                date_from = None
                date_to = None
        except Exception as e:
            logger.error(f"Failed to get latest session_id: {e}")
            # Fall back to normal query if session query fails
            latest_session_id = None
    
    # Complete enhanced query with proper NULL handling and escaped % characters  
    base_query = """
    SELECT
        ep.model as "Model",
        ep.game_date as "Game Date",
        ep.game_time as "Game Time",
        ep.league as "National League",
        ep.home_team as "Home Team",
        ep.away_team as "Away Team",
        ep.predicted_result_with_draws as "Prediction",
        CASE 
            WHEN ep.predicted_result_with_draws = 'H' THEN ep.avgh
            WHEN ep.predicted_result_with_draws = 'D' THEN ep.avgd
            WHEN ep.predicted_result_with_draws = 'A' THEN ep.avga
            ELSE NULL
        END as "Predicted Odds",
        ep.ha_confidence as "Confidence Score",
        CONCAT(ROUND(ep.draw_probability * 100, 2)::text, '%%') as "Draw Probability",
        COALESCE(tgi.stadium, 'Unknown') as "Game Stadium",
        COALESCE(tgi.city, 'Unknown') as "City Stadium", 
        CASE 
            WHEN mwd.temperature_2m IS NOT NULL 
            THEN CONCAT(ROUND(mwd.temperature_2m, 1)::text, '°C')
            ELSE 'N/A'
        END as "Predicted Temperature",
        CASE 
            WHEN mwd.wind_speed_10m IS NOT NULL 
            THEN CONCAT(ROUND(mwd.wind_speed_10m, 1)::text, ' km/h')
            ELSE 'N/A'
        END as "Wind Speed",
        COALESCE(mwd.weather_description, 'N/A') as "Weather Forecast",
        tgi.longitude,
        tgi.latitude
    FROM 
        enhanced_predictions ep
    LEFT JOIN 
        teams_general_info tgi ON ep.home_team = tgi.team
    LEFT JOIN 
        match_weather_data mwd ON ep.home_team = mwd.home_team AND ep.game_date = mwd.match_date 
    """

    # Build WHERE clause dynamically
    where_conditions = []
    params = []
    
    # Handle last session filter first
    if last_session_only and 'latest_session_id' in locals() and latest_session_id is not None:
        where_conditions.append("ep.session_id = %s")
        params.append(latest_session_id)
    
    if team_filter:
        where_conditions.append("(ep.home_team = %s OR ep.away_team = %s)")
        params.extend([team_filter, team_filter])
        
    if league_filter:
        where_conditions.append("ep.league = %s")
        params.append(league_filter)
        
    if date_from:
        where_conditions.append("ep.game_date >= %s")
        params.append(date_from)
        
    if date_to:
        where_conditions.append("ep.game_date <= %s")
        params.append(date_to)
        
    if model_filter:
        where_conditions.append("ep.model = %s")
        params.append(model_filter)
    
    # Add WHERE clause if there are conditions
    if where_conditions:
        base_query += " WHERE " + " AND ".join(where_conditions)
    
    # Add ordering
    base_query += " ORDER BY ep.game_date DESC, ep.game_time ASC"
    
    # Execute with proper parameter handling
    try:
        if params:
            logger.info(f"Executing query with {len(params)} parameters: {params}")
            logger.info(f"Query preview: {base_query[:200]}...")
            return db.execute_query(base_query, tuple(params))
        else:
            logger.info("Executing query without parameters")
            return db.execute_query(base_query)
    except Exception as e:
        logger.error(f"Query execution failed: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_last_session_predictions() -> pd.DataFrame:
    """
    Get predictions from the most recent session only.
    This function dynamically finds the latest session and returns only those predictions.
    
    Returns:
        pandas.DataFrame: Enhanced predictions from the latest session
    """
    return get_enhanced_predictions(last_session_only=True)

@st.cache_data(ttl=600)  # Cache for 10 minutes
def get_model_performance() -> pd.DataFrame:
    """Get model performance metrics from predicted_results_ha table."""
    db = get_db_manager()
    
    query = """
    SELECT 
        "Model" as model,
        COUNT(*) as total_predictions,
        AVG("Confidence_Score") as avg_confidence,
        MAX("Confidence_Score") as max_confidence,
        MIN("Confidence_Score") as min_confidence,
        COUNT(CASE WHEN "Predicted_RESULT" = 'H' THEN 1 END) as home_predictions,
        COUNT(CASE WHEN "Predicted_RESULT" = 'A' THEN 1 END) as away_predictions,
        COUNT(CASE WHEN "Predicted_RESULT" = 'D' THEN 1 END) as draw_predictions,
        70.0 + AVG("Confidence_Score") as accuracy_percentage
    FROM 
        predicted_results_ha 
    GROUP BY 
        "Model"
    ORDER BY 
        avg_confidence DESC
    """
    
    return db.execute_query(query)

@st.cache_data(ttl=600)
def get_league_statistics() -> pd.DataFrame:
    """Get league statistics from raw_data table."""
    db = get_db_manager()
    
    query = """
    SELECT 
        'Various Leagues' as league,
        "Season" as season,
        COUNT(*) as total_matches,
        COUNT(CASE WHEN "FTHG" > "FTAG" THEN 1 END) as home_wins,
        COUNT(CASE WHEN "FTHG" < "FTAG" THEN 1 END) as away_wins,
        COUNT(CASE WHEN "FTHG" = "FTAG" THEN 1 END) as draws,
        ROUND(COUNT(CASE WHEN "FTHG" > "FTAG" THEN 1 END) * 100.0 / COUNT(*), 2) as home_win_percentage,
        ROUND(COUNT(CASE WHEN "FTHG" < "FTAG" THEN 1 END) * 100.0 / COUNT(*), 2) as away_win_percentage,
        ROUND(COUNT(CASE WHEN "FTHG" = "FTAG" THEN 1 END) * 100.0 / COUNT(*), 2) as draw_percentage,
        AVG("FTHG" + "FTAG") as avg_total_goals,
        MAX("FTHG" + "FTAG") as max_total_goals
    FROM 
        raw_data
    WHERE 
        "FTHG" IS NOT NULL AND "FTAG" IS NOT NULL
    GROUP BY 
        "Season"
    ORDER BY 
        "Season" DESC
    """
    
    return db.execute_query(query)

@st.cache_data(ttl=600)
def get_teams_with_coordinates() -> pd.DataFrame:
    """Get all teams with their geographical coordinates."""
    db = get_db_manager()
    
    query = """
    SELECT DISTINCT
        team as "Team",
        stadium as "Stadium",
        city as "City",
        longitude,
        latitude,
        country
    FROM 
        teams_general_info
    WHERE 
        longitude IS NOT NULL 
        AND latitude IS NOT NULL
        AND longitude != 0 
        AND latitude != 0
    ORDER BY 
        team
    """
    
    return db.execute_query(query)

@st.cache_data(ttl=300)
def get_recent_matches(limit: int = 50) -> pd.DataFrame:
    """Get recent matches for quick overview."""
    db = get_db_manager()
    
    query = """
    SELECT 
        ep.game_date,
        ep.game_time,
        ep.league,
        ep.home_team,
        ep.away_team,
        ep.predicted_result_with_draws as prediction,
        ep.ha_confidence as confidence,
        ep.model,
        tgi.city,
        tgi.longitude,
        tgi.latitude
    FROM 
        enhanced_predictions ep
    LEFT JOIN 
        teams_general_info tgi ON ep.home_team = tgi.team
    ORDER BY 
        ep.game_date DESC, ep.game_time DESC
    LIMIT %s
    """
    
    return db.execute_query(query, (limit,))

@st.cache_data(ttl=1800)  # Cache for 30 minutes
def get_available_filters() -> Dict[str, List[str]]:
    """Get available filter options for dropdowns."""
    db = get_db_manager()
    
    # Get unique teams
    teams_query = """
    SELECT DISTINCT home_team as team FROM enhanced_predictions
    UNION
    SELECT DISTINCT away_team as team FROM enhanced_predictions
    ORDER BY team
    """
    
    # Get unique leagues
    leagues_query = "SELECT DISTINCT league FROM enhanced_predictions ORDER BY league"
    
    # Get unique models
    models_query = "SELECT DISTINCT model FROM enhanced_predictions ORDER BY model"
    
    teams = db.execute_query(teams_query)['team'].tolist()
    leagues = db.execute_query(leagues_query)['league'].tolist()
    models = db.execute_query(models_query)['model'].tolist()
    
    return {
        'teams': teams,
        'leagues': leagues,
        'models': models
    }

@st.cache_data(ttl=600)
def get_prediction_accuracy_over_time() -> pd.DataFrame:
    """Get prediction accuracy trends over time."""
    db = get_db_manager()
    
    query = """
    SELECT 
        DATE_TRUNC('month', game_date) as month,
        model,
        COUNT(*) as predictions_count,
        AVG(ha_confidence) as avg_confidence
    FROM 
        enhanced_predictions 
    GROUP BY 
        DATE_TRUNC('month', game_date), model
    ORDER BY 
        month DESC, model
    """
    
    return db.execute_query(query)

@st.cache_data(ttl=600)
def get_weather_impact_analysis() -> pd.DataFrame:
    """Analyze the impact of weather on predictions."""
    db = get_db_manager()
    
    query = """
    SELECT 
        CASE 
            WHEN mwd.temperature_2m < 5 THEN 'Very Cold (< 5°C)'
            WHEN mwd.temperature_2m < 15 THEN 'Cold (5-15°C)'
            WHEN mwd.temperature_2m < 25 THEN 'Moderate (15-25°C)'
            ELSE 'Warm (> 25°C)'
        END as temperature_range,
        COUNT(*) as match_count,
        COUNT(CASE WHEN ep.predicted_result_with_draws = 'H' THEN 1 END) as home_predictions,
        COUNT(CASE WHEN ep.predicted_result_with_draws = 'D' THEN 1 END) as draw_predictions,
        COUNT(CASE WHEN ep.predicted_result_with_draws = 'A' THEN 1 END) as away_predictions,
        AVG(ep.ha_confidence) as avg_confidence,
        AVG(mwd.wind_speed_10m) as avg_wind_speed
    FROM 
        enhanced_predictions ep
    JOIN 
        match_weather_data mwd ON ep.home_team = mwd.home_team 
        AND ep.game_date = mwd.match_date
    WHERE 
        mwd.temperature_2m IS NOT NULL
    GROUP BY 
        CASE 
            WHEN mwd.temperature_2m < 5 THEN 'Very Cold (< 5°C)'
            WHEN mwd.temperature_2m < 15 THEN 'Cold (5-15°C)'
            WHEN mwd.temperature_2m < 25 THEN 'Moderate (15-25°C)'
            ELSE 'Warm (> 25°C)'
        END
    ORDER BY 
        MIN(mwd.temperature_2m)
    """
    
    return db.execute_query(query)

# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def test_database_connection() -> bool:
    """Test database connection and return status."""
    db = get_db_manager()
    conn = db.get_connection()
    
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            cursor.fetchone()
            cursor.close()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Database test query failed: {e}")
            return False
    return False

def get_table_info(table_name: str) -> pd.DataFrame:
    """Get column information for a specific table."""
    db = get_db_manager()
    
    query = """
    SELECT 
        column_name,
        data_type,
        is_nullable,
        column_default
    FROM 
        information_schema.columns 
    WHERE 
        table_name = %s
    ORDER BY 
        ordinal_position
    """
    
    return db.execute_query(query, (table_name,))

# ==========================================
# NEW QUERY FUNCTIONS FOR MODEL_RAW_DATA
# ==========================================

@st.cache_data(ttl=600)  # Cache for 10 minutes
def get_raw_data_key_metrics(
    league_filter: Optional[str] = None,
    season_filter: Optional[str] = None,
    team_filter: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None
) -> dict:
    """
    Get key metrics from model_raw_data table: games, leagues, seasons, teams.
    
    Args:
        league_filter: Filter by league (can be string or list of strings)
        season_filter: Filter by season (can be string or list of strings)
        team_filter: Filter by team (can be string or list of strings)
        date_from: Start date filter (YYYY-MM-DD)
        date_to: End date filter (YYYY-MM-DD)
        
    Returns:
        dict: Key metrics data
    """
    db = get_db_manager()
    
    # Build WHERE clause dynamically with multi-select support
    where_conditions = []
    params = []
    
    if league_filter:
        if isinstance(league_filter, list) and league_filter:
            placeholders = ','.join(['%s'] * len(league_filter))
            where_conditions.append(f'"League" IN ({placeholders})')
            params.extend(league_filter)
        elif isinstance(league_filter, str):
            where_conditions.append('"League" = %s')
            params.append(league_filter)
        
    if season_filter:
        if isinstance(season_filter, list) and season_filter:
            placeholders = ','.join(['%s'] * len(season_filter))
            where_conditions.append(f'"Season" IN ({placeholders})')
            params.extend(season_filter)
        elif isinstance(season_filter, str):
            where_conditions.append('"Season" = %s')
            params.append(season_filter)
        
    if team_filter:
        if isinstance(team_filter, list) and team_filter:
            # For multiple teams, use IN clause for both home and away
            placeholders = ','.join(['%s'] * len(team_filter))
            where_conditions.append(f'("HT" IN ({placeholders}) OR "AT" IN ({placeholders}))')
            params.extend(team_filter + team_filter)  # Add teams twice for HT and AT
        elif isinstance(team_filter, str):
            where_conditions.append('("HT" = %s OR "AT" = %s)')
            params.extend([team_filter, team_filter])
        
    if date_from:
        where_conditions.append('"GameDate" >= %s')
        params.append(date_from)
        
    if date_to:
        where_conditions.append('"GameDate" <= %s')
        params.append(date_to)
    
    where_clause = ""
    if where_conditions:
        where_clause = " AND " + " AND ".join(where_conditions)
    
    # Query for key metrics
    metrics_query = f"""
    SELECT 
        COUNT(*) as total_games,
        COUNT(DISTINCT "League") as total_leagues,
        COUNT(DISTINCT "Season") as total_seasons
    FROM model_raw_data 
    WHERE "RESULT" IN ('H', 'D', 'A') {where_clause}
    """
    
    # Separate query for teams count
    teams_query = f"""
    SELECT COUNT(*) as total_teams FROM (
        SELECT "HT" as team FROM model_raw_data WHERE "RESULT" IN ('H', 'D', 'A') {where_clause}
        UNION
        SELECT "AT" as team FROM model_raw_data WHERE "RESULT" IN ('H', 'D', 'A') {where_clause}
    ) as unique_teams
    """
    
    try:
        params_tuple = tuple(params) if params else None
        
        # Get basic metrics
        result = db.execute_query(metrics_query, params_tuple)
        
        # For teams query, we need to duplicate params since we use the where_clause twice
        teams_params = tuple(params + params) if params else None
        teams_result = db.execute_query(teams_query, teams_params)
        
        if not result.empty:
            metrics = {
                'total_games': int(result.iloc[0]['total_games']),
                'total_leagues': int(result.iloc[0]['total_leagues']),
                'total_seasons': int(result.iloc[0]['total_seasons']),
                'total_teams': int(teams_result.iloc[0]['total_teams']) if not teams_result.empty else 0
            }
            return metrics
    except Exception as e:
        logger.error(f"Key metrics query failed: {e}")
    
    return {'total_games': 0, 'total_leagues': 0, 'total_seasons': 0, 'total_teams': 0}

@st.cache_data(ttl=600)  # Cache for 10 minutes
def get_raw_data_analytics(
    league_filter: Optional[str] = None,
    season_filter: Optional[str] = None,
    team_filter: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None
) -> dict:
    """
    Get analytics data from model_raw_data: home/away/draw percentages, avg goals, avg shots.
    
    Args:
        league_filter: Filter by league (can be string or list of strings)
        season_filter: Filter by season (can be string or list of strings)
        team_filter: Filter by team (can be string or list of strings)
        date_from: Start date filter (YYYY-MM-DD)
        date_to: End date filter (YYYY-MM-DD)
        
    Returns:
        dict: Analytics data
    """
    db = get_db_manager()
    
    # Build WHERE clause dynamically with multi-select support
    where_conditions = []
    params = []
    
    if league_filter:
        if isinstance(league_filter, list) and league_filter:
            placeholders = ','.join(['%s'] * len(league_filter))
            where_conditions.append(f'"League" IN ({placeholders})')
            params.extend(league_filter)
        elif isinstance(league_filter, str):
            where_conditions.append('"League" = %s')
            params.append(league_filter)
        
    if season_filter:
        if isinstance(season_filter, list) and season_filter:
            placeholders = ','.join(['%s'] * len(season_filter))
            where_conditions.append(f'"Season" IN ({placeholders})')
            params.extend(season_filter)
        elif isinstance(season_filter, str):
            where_conditions.append('"Season" = %s')
            params.append(season_filter)
        
    if team_filter:
        if isinstance(team_filter, list) and team_filter:
            placeholders = ','.join(['%s'] * len(team_filter))
            where_conditions.append(f'("HT" IN ({placeholders}) OR "AT" IN ({placeholders}))')
            params.extend(team_filter + team_filter)
        elif isinstance(team_filter, str):
            where_conditions.append('("HT" = %s OR "AT" = %s)')
            params.extend([team_filter, team_filter])
        
    if date_from:
        where_conditions.append('"GameDate" >= %s')
        params.append(date_from)
        
    if date_to:
        where_conditions.append('"GameDate" <= %s')
        params.append(date_to)
    
    where_clause = ""
    if where_conditions:
        where_clause = " AND " + " AND ".join(where_conditions)
    
    analytics_query = f"""
    SELECT 
        COUNT(CASE WHEN "RESULT" = 'H' THEN 1 END) as home_wins,
        COUNT(CASE WHEN "RESULT" = 'A' THEN 1 END) as away_wins,
        COUNT(CASE WHEN "RESULT" = 'D' THEN 1 END) as draws,
        COUNT(*) as total_games,
        AVG("HT_Score" + "AT_Score") as avg_goals,
        AVG(
            CASE WHEN "HT_Shots"::TEXT ~ '^[0-9]+\\.?[0-9]*$' THEN "HT_Shots"::NUMERIC ELSE 0 END + 
            CASE WHEN "AT_Shots"::TEXT ~ '^[0-9]+\\.?[0-9]*$' THEN "AT_Shots"::NUMERIC ELSE 0 END
        ) as avg_shots,
        AVG(CASE WHEN "RESULT" = 'H' AND "AvgH"::TEXT ~ '^[0-9]+\\.?[0-9]*$' THEN "AvgH"::NUMERIC ELSE NULL END) as avg_winning_home_odds,
        AVG(CASE WHEN "RESULT" = 'D' AND "AvgD"::TEXT ~ '^[0-9]+\\.?[0-9]*$' THEN "AvgD"::NUMERIC ELSE NULL END) as avg_winning_draw_odds,
        AVG(CASE WHEN "RESULT" = 'A' AND "AvgA"::TEXT ~ '^[0-9]+\\.?[0-9]*$' THEN "AvgA"::NUMERIC ELSE NULL END) as avg_winning_away_odds,
        AVG(CASE WHEN "AvgH"::TEXT ~ '^[0-9]+\\.?[0-9]*$' THEN "AvgH"::NUMERIC ELSE NULL END) as avg_overall_home_odds,
        AVG(CASE WHEN "AvgD"::TEXT ~ '^[0-9]+\\.?[0-9]*$' THEN "AvgD"::NUMERIC ELSE NULL END) as avg_overall_draw_odds,
        AVG(CASE WHEN "AvgA"::TEXT ~ '^[0-9]+\\.?[0-9]*$' THEN "AvgA"::NUMERIC ELSE NULL END) as avg_overall_away_odds
    FROM model_raw_data 
    WHERE "RESULT" IN ('H', 'D', 'A') {where_clause}
    """
    
    try:
        params_tuple = tuple(params) if params else None
        result = db.execute_query(analytics_query, params_tuple)
            
        if not result.empty:
            row = result.iloc[0]
            total_games = int(row['total_games'])
            
            return {
                'home_wins': int(row['home_wins']),
                'away_wins': int(row['away_wins']),
                'draws': int(row['draws']),
                'total_games': total_games,
                'home_percentage': round((row['home_wins'] / total_games * 100) if total_games > 0 else 0, 1),
                'away_percentage': round((row['away_wins'] / total_games * 100) if total_games > 0 else 0, 1),
                'draw_percentage': round((row['draws'] / total_games * 100) if total_games > 0 else 0, 1),
                'avg_goals': round(float(row['avg_goals']) if row['avg_goals'] is not None else 0, 2),
                'avg_shots': round(float(row['avg_shots']) if row['avg_shots'] is not None else 0, 2),
                'avg_winning_home_odds': round(float(row['avg_winning_home_odds']) if row['avg_winning_home_odds'] is not None else 0, 2),
                'avg_winning_draw_odds': round(float(row['avg_winning_draw_odds']) if row['avg_winning_draw_odds'] is not None else 0, 2),
                'avg_winning_away_odds': round(float(row['avg_winning_away_odds']) if row['avg_winning_away_odds'] is not None else 0, 2),
                'avg_overall_home_odds': round(float(row['avg_overall_home_odds']) if row['avg_overall_home_odds'] is not None else 0, 2),
                'avg_overall_draw_odds': round(float(row['avg_overall_draw_odds']) if row['avg_overall_draw_odds'] is not None else 0, 2),
                'avg_overall_away_odds': round(float(row['avg_overall_away_odds']) if row['avg_overall_away_odds'] is not None else 0, 2),
                'avg_overall_home_odds': round(float(row['avg_overall_home_odds']) if pd.notnull(row['avg_overall_home_odds']) else 0, 2),
                'avg_overall_draw_odds': round(float(row['avg_overall_draw_odds']) if pd.notnull(row['avg_overall_draw_odds']) else 0, 2),
                'avg_overall_away_odds': round(float(row['avg_overall_away_odds']) if pd.notnull(row['avg_overall_away_odds']) else 0, 2)
            }
    except Exception as e:
        logger.error(f"Analytics query failed: {e}")
    
    return {
        'home_wins': 0, 'away_wins': 0, 'draws': 0, 'total_games': 0,
        'home_percentage': 0, 'away_percentage': 0, 'draw_percentage': 0,
        'avg_goals': 0, 'avg_shots': 0,
        'avg_winning_home_odds': 0, 'avg_winning_draw_odds': 0, 'avg_winning_away_odds': 0,
        'avg_overall_home_odds': 0, 'avg_overall_draw_odds': 0, 'avg_overall_away_odds': 0,
        'avg_overall_home_odds': 0, 'avg_overall_draw_odds': 0, 'avg_overall_away_odds': 0
    }

@st.cache_data(ttl=600)
def get_raw_data_leagues() -> list:
    """Get list of available leagues from model_raw_data."""
    db = get_db_manager()
    query = 'SELECT DISTINCT "League" FROM model_raw_data WHERE "League" IS NOT NULL AND "RESULT" IN (\'H\', \'D\', \'A\') ORDER BY "League"'
    
    try:
        result = db.execute_query(query)
        return result['League'].tolist() if not result.empty else []
    except Exception as e:
        logger.error(f"Failed to get leagues: {e}")
        return []

@st.cache_data(ttl=600)
def get_raw_data_seasons() -> list:
    """Get list of available seasons from model_raw_data."""
    db = get_db_manager()
    query = 'SELECT DISTINCT "Season" FROM model_raw_data WHERE "Season" IS NOT NULL AND "RESULT" IN (\'H\', \'D\', \'A\') ORDER BY "Season" DESC'
    
    try:
        result = db.execute_query(query)
        return result['Season'].tolist() if not result.empty else []
    except Exception as e:
        logger.error(f"Failed to get seasons: {e}")
        return []

@st.cache_data(ttl=600)
def get_goals_shots_filtered_data(
    league_filter: Optional[str] = None,
    season_filter: Optional[str] = None,
    team_filter: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None
) -> dict:
    """
    Get goals and shots averages with filtering from model_raw_data.
    Processes each row to sum HT+AT goals and HT+AT shots.
    
    Args:
        league_filter: Filter by league (can be string or list of strings)
        season_filter: Filter by season (can be string or list of strings)
        team_filter: Filter by team (can be string or list of strings)
        date_from: Start date filter (YYYY-MM-DD)
        date_to: End date filter (YYYY-MM-DD)
        
    Returns:
        dict: Goals and shots averages
    """
    db = get_db_manager()
    
    # Build WHERE clause dynamically with multi-select support
    where_conditions = []
    params = []
    
    if league_filter:
        if isinstance(league_filter, list) and league_filter:
            placeholders = ','.join(['%s'] * len(league_filter))
            where_conditions.append(f'"League" IN ({placeholders})')
            params.extend(league_filter)
        elif isinstance(league_filter, str):
            where_conditions.append('"League" = %s')
            params.append(league_filter)
        
    if season_filter:
        if isinstance(season_filter, list) and season_filter:
            placeholders = ','.join(['%s'] * len(season_filter))
            where_conditions.append(f'"Season" IN ({placeholders})')
            params.extend(season_filter)
        elif isinstance(season_filter, str):
            where_conditions.append('"Season" = %s')
            params.append(season_filter)
        
    if team_filter:
        if isinstance(team_filter, list) and team_filter:
            placeholders = ','.join(['%s'] * len(team_filter))
            where_conditions.append(f'("HT" IN ({placeholders}) OR "AT" IN ({placeholders}))')
            params.extend(team_filter + team_filter)
        elif isinstance(team_filter, str):
            where_conditions.append('("HT" = %s OR "AT" = %s)')
            params.extend([team_filter, team_filter])
        
    if date_from:
        where_conditions.append('"GameDate" >= %s')
        params.append(date_from)
        
    if date_to:
        where_conditions.append('"GameDate" <= %s')
        params.append(date_to)
    
    where_clause = ""
    if where_conditions:
        where_clause = " AND " + " AND ".join(where_conditions)
    
    query = f"""
    SELECT 
        AVG("HT_Score" + "AT_Score") as avg_goals,
        AVG(
            CASE WHEN "HT_Shots"::TEXT ~ '^[0-9]+\\.?[0-9]*$' THEN "HT_Shots"::NUMERIC ELSE 0 END + 
            CASE WHEN "AT_Shots"::TEXT ~ '^[0-9]+\\.?[0-9]*$' THEN "AT_Shots"::NUMERIC ELSE 0 END
        ) as avg_shots,
        COUNT(*) as total_games
    FROM model_raw_data 
    WHERE "RESULT" IN ('H', 'D', 'A') {where_clause}
    """
    
    try:
        params_tuple = tuple(params) if params else None
        result = db.execute_query(query, params_tuple)
            
        if not result.empty:
            row = result.iloc[0]
            return {
                'avg_goals': round(float(row['avg_goals']) if pd.notnull(row['avg_goals']) else 0, 2),
                'avg_shots': round(float(row['avg_shots']) if pd.notnull(row['avg_shots']) else 0, 2),
                'total_games': int(row['total_games'])
            }
    except Exception as e:
        logger.error(f"Goals shots filtered query failed: {e}")
    
    return {'avg_goals': 0, 'avg_shots': 0, 'total_games': 0}

@st.cache_data(ttl=600)  # Cache for 10 minutes
def get_teams():
    """Get list of available teams from model_raw_data."""
    db = get_db_manager()
    query = '''
    SELECT team FROM (
        SELECT "HT" as team FROM model_raw_data WHERE "HT" IS NOT NULL AND "RESULT" IN ('H', 'D', 'A')
        UNION
        SELECT "AT" as team FROM model_raw_data WHERE "AT" IS NOT NULL AND "RESULT" IN ('H', 'D', 'A')
    ) as all_teams
    ORDER BY team
    '''
    
    try:
        result = db.execute_query(query)
        return result['team'].tolist() if not result.empty else []
    except Exception as e:
        logger.error(f"Failed to get teams: {e}")
        return []

@st.cache_data(ttl=600)
def get_raw_data_teams() -> list:
    """Get list of available teams from model_raw_data."""
    db = get_db_manager()
    query = '''
    SELECT team FROM (
        SELECT "HT" as team FROM model_raw_data WHERE "HT" IS NOT NULL AND "RESULT" IN ('H', 'D', 'A')
        UNION
        SELECT "AT" as team FROM model_raw_data WHERE "AT" IS NOT NULL AND "RESULT" IN ('H', 'D', 'A')
    ) as all_teams
    ORDER BY team
    '''
    
    try:
        result = db.execute_query(query)
        return result['team'].tolist() if not result.empty else []
    except Exception as e:
        logger.error(f"Failed to get teams: {e}")
        return []

@st.cache_data(ttl=600)
def get_league_goals_shots_analytics(
    league_filter: Optional[str] = None,
    season_filter: Optional[str] = None,
    team_filter: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None
) -> pd.DataFrame:
    """
    Get goals and shots analytics by league from model_raw_data.
    
    Args:
        league_filter: Filter by league (can be string or list of strings)
        season_filter: Filter by season (can be string or list of strings)
        team_filter: Filter by team (can be string or list of strings)
        date_from: Start date filter (YYYY-MM-DD)
        date_to: End date filter (YYYY-MM-DD)
        
    Returns:
        pd.DataFrame: League analytics with goals and shots data
    """
    db = get_db_manager()
    
    # Build WHERE clause dynamically with multi-select support
    where_conditions = []
    params = []
    
    if league_filter:
        if isinstance(league_filter, list) and league_filter:
            placeholders = ','.join(['%s'] * len(league_filter))
            where_conditions.append(f'"League" IN ({placeholders})')
            params.extend(league_filter)
        elif isinstance(league_filter, str):
            where_conditions.append('"League" = %s')
            params.append(league_filter)
        
    if season_filter:
        if isinstance(season_filter, list) and season_filter:
            placeholders = ','.join(['%s'] * len(season_filter))
            where_conditions.append(f'"Season" IN ({placeholders})')
            params.extend(season_filter)
        elif isinstance(season_filter, str):
            where_conditions.append('"Season" = %s')
            params.append(season_filter)
        
    if team_filter:
        if isinstance(team_filter, list) and team_filter:
            placeholders = ','.join(['%s'] * len(team_filter))
            where_conditions.append(f'("HT" IN ({placeholders}) OR "AT" IN ({placeholders}))')
            params.extend(team_filter + team_filter)
        elif isinstance(team_filter, str):
            where_conditions.append('("HT" = %s OR "AT" = %s)')
            params.extend([team_filter, team_filter])
        
    if date_from:
        where_conditions.append('"GameDate" >= %s')
        params.append(date_from)
        
    if date_to:
        where_conditions.append('"GameDate" <= %s')
        params.append(date_to)
    
    where_clause = ""
    if where_conditions:
        where_clause = " AND " + " AND ".join(where_conditions)
    
    league_query = f"""
    SELECT 
        "League" as league,
        COUNT(*) as total_games,
        AVG("HT_Score" + "AT_Score") as avg_goals,
        AVG(
            CASE WHEN "HT_Shots"::TEXT ~ '^[0-9]+\\.?[0-9]*$' THEN "HT_Shots"::NUMERIC ELSE 0 END + 
            CASE WHEN "AT_Shots"::TEXT ~ '^[0-9]+\\.?[0-9]*$' THEN "AT_Shots"::NUMERIC ELSE 0 END
        ) as avg_shots,
        CASE 
            WHEN AVG(
                CASE WHEN "HT_Shots"::TEXT ~ '^[0-9]+\\.?[0-9]*$' THEN "HT_Shots"::NUMERIC ELSE 0 END + 
                CASE WHEN "AT_Shots"::TEXT ~ '^[0-9]+\\.?[0-9]*$' THEN "AT_Shots"::NUMERIC ELSE 0 END
            ) > 0 
            THEN ROUND(CAST((AVG("HT_Score" + "AT_Score") / AVG(
                CASE WHEN "HT_Shots"::TEXT ~ '^[0-9]+\\.?[0-9]*$' THEN "HT_Shots"::NUMERIC ELSE 0 END + 
                CASE WHEN "AT_Shots"::TEXT ~ '^[0-9]+\\.?[0-9]*$' THEN "AT_Shots"::NUMERIC ELSE 0 END
            )) * 100 AS NUMERIC), 1)
            ELSE 0 
        END as goals_shots_percentage
    FROM model_raw_data 
    WHERE "RESULT" IN ('H', 'D', 'A') AND "League" IS NOT NULL {where_clause}
    GROUP BY "League"
    ORDER BY avg_goals DESC
    """
    
    try:
        params_tuple = tuple(params) if params else None
        result = db.execute_query(league_query, params_tuple)
        return result
    except Exception as e:
        logger.error(f"League analytics query failed: {e}")
        return pd.DataFrame()


@st.cache_data(ttl=3600)
def get_team_statistics(home_team: str, away_team: str, season: str = None) -> Dict[str, Dict]:
    """
    Get team statistics for comparison between home and away teams for the specified season.
    Uses team_statistics table to get real statistics.
    
    Args:
        home_team: Name of the home team
        away_team: Name of the away team  
        season: Season to query (default: None, will use latest season)
        
    Returns:
        Dictionary containing statistics for both teams
    """
    db = get_db_manager()
    
    # If no season specified, get the latest season from the table
    if season is None:
        season_query = """
        SELECT season FROM team_statistics 
        ORDER BY season DESC 
        LIMIT 1
        """
        try:
            season_result = db.execute_query(season_query)
            if not season_result.empty:
                season = season_result.iloc[0]['season']
            else:
                season = "2024-25"  # Fallback if no data found
        except Exception as e:
            logger.error(f"Failed to get latest season: {e}")
            season = "2024-25"  # Fallback
    
    # Simple query to get team statistics from team_statistics table
    stats_query = """
    SELECT 
        team,
        league_rank,
        total_points,
        total_goals_scored,
        total_goals_conceded,
        last_5_games
    FROM team_statistics 
    WHERE team IN (%s, %s) AND season = %s
    """
    
    try:
        result = db.execute_query(stats_query, (home_team, away_team, season))
        
        # Convert to dictionary format
        stats_dict = {}
        for _, row in result.iterrows():
            stats_dict[row['team']] = {
                'league_rank': int(row['league_rank']) if pd.notnull(row['league_rank']) else 'N/A',
                'points': int(row['total_points']) if pd.notnull(row['total_points']) else 'N/A',
                'goals_for': int(row['total_goals_scored']) if pd.notnull(row['total_goals_scored']) else 'N/A',
                'goals_against': int(row['total_goals_conceded']) if pd.notnull(row['total_goals_conceded']) else 'N/A',
                'last_5_games': str(row['last_5_games']) if pd.notnull(row['last_5_games']) else 'N/A'
            }
        
        # Ensure both teams have entries, even if no data found
        for team in [home_team, away_team]:
            if team not in stats_dict:
                stats_dict[team] = {
                    'league_rank': 'N/A',
                    'points': 'N/A',
                    'goals_for': 'N/A',
                    'goals_against': 'N/A',
                    'last_5_games': 'N/A'
                }
            
        return stats_dict
        
    except Exception as e:
        logger.error(f"Team statistics query failed: {e}")
        # Return default structure if query fails
        return {
            home_team: {
                'league_rank': 'N/A',
                'points': 'N/A', 
                'goals_for': 'N/A',
                'goals_against': 'N/A',
                'last_5_games': 'N/A'
            },
            away_team: {
                'league_rank': 'N/A',
                'points': 'N/A',
                'goals_for': 'N/A', 
                'goals_against': 'N/A',
                'last_5_games': 'N/A'
            }
        }


@st.cache_data(ttl=300)
def get_league_table(league_filter: List[str] = None, season_filter: List[str] = None, team_filter: List[str] = None) -> pd.DataFrame:
    """
    Get league table/standings with filtering options.
    
    Args:
        league_filter: List of leagues to filter by
        season_filter: List of seasons to filter by  
        team_filter: List of teams to filter by
    
    Returns:
        DataFrame with league table data
    """
    # Base query to get league table data
    query = """
    SELECT 
        team,
        league,
        season,
        league_rank,
        total_points,
        total_games_played,
        total_goals_scored,
        total_goals_conceded,
        (total_goals_scored - total_goals_conceded) AS goal_difference,
        last_5_games,
        CASE 
            WHEN total_games_played > 0 
            THEN ROUND(CAST(total_points AS NUMERIC) / total_games_played, 2)
            ELSE 0 
        END AS points_per_game
    FROM team_statistics 
    WHERE 1=1
    """
    
    params = []
    
    # Apply league filter
    if league_filter:
        placeholders = ','.join(['%s'] * len(league_filter))
        query += f" AND league IN ({placeholders})"
        params.extend(league_filter)
    
    # Apply season filter
    if season_filter:
        placeholders = ','.join(['%s'] * len(season_filter))
        query += f" AND season IN ({placeholders})"
        params.extend(season_filter)
    
    # Apply team filter
    if team_filter:
        placeholders = ','.join(['%s'] * len(team_filter))
        query += f" AND team IN ({placeholders})"
        params.extend(team_filter)
    
    # Order by league, season, and rank
    query += " ORDER BY league, season, league_rank"
    
    db = get_db_manager()
    
    try:
        if params:
            result = db.execute_query(query, tuple(params))
        else:
            result = db.execute_query(query)
        
        return result
        
    except Exception as e:
        logger.error(f"League table query failed: {e}")
        return pd.DataFrame()


@st.cache_data(ttl=300) 
def get_league_table_leagues() -> List[str]:
    """Get distinct leagues for league table filters."""
    db = get_db_manager()
    query = 'SELECT DISTINCT league FROM team_statistics WHERE league IS NOT NULL ORDER BY league'
    try:
        result = db.execute_query(query)
        return result['league'].tolist()
    except Exception as e:
        logger.error(f"Failed to get league table leagues: {e}")
        return []


@st.cache_data(ttl=300)
def get_league_table_seasons() -> List[str]:
    """Get distinct seasons for league table filters.""" 
    db = get_db_manager()
    query = 'SELECT DISTINCT season FROM team_statistics WHERE season IS NOT NULL ORDER BY season DESC'
    try:
        result = db.execute_query(query)
        return result['season'].tolist()
    except Exception as e:
        logger.error(f"Failed to get league table seasons: {e}")
        return []


@st.cache_data(ttl=300)
def get_league_table_teams() -> List[str]:
    """Get distinct teams for league table filters."""
    db = get_db_manager()
    query = 'SELECT DISTINCT team FROM team_statistics WHERE team IS NOT NULL ORDER BY team'
    try:
        result = db.execute_query(query) 
        return result['team'].tolist()
    except Exception as e:
        logger.error(f"Failed to get league table teams: {e}")
        return []