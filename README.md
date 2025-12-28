# Football Predictions Dashboard

A production-ready Streamlit web application for analyzing football match predictions with advanced geospatial visualization capabilities.

## 🎯 Features

### 📊 Core Analytics
- **KPI Dashboard**: Real-time metrics including prediction accuracy, confidence scores, and match statistics
- **Model Performance**: Comprehensive analysis of prediction model accuracy and performance trends
- **League Statistics**: Historical data analysis across different football leagues and seasons
- **Interactive Filtering**: Dynamic filters by team, league, date range, and prediction models

### 🗺️ Geospatial Intelligence
- **Teams Location Map**: Interactive map showing all football teams with stadium locations
- **Match Predictions Map**: Geospatial visualization of match predictions with weather data
- **Geographic Analytics**: Distribution analysis, country statistics, and location-based insights
- **Route Mapping**: Team journey visualization for away matches

### 📈 Interactive Visualizations
- **Prediction Distribution**: Pie charts and histograms showing prediction patterns
- **Confidence Analysis**: Distribution and trends of model confidence scores
- **Weather Impact**: Analysis of weather conditions on match predictions
- **Temporal Trends**: Performance metrics over time periods

## 🏗️ Architecture

### Database Integration
- **PostgreSQL Backend**: Direct connection to local PostgreSQL database
- **Query Optimization**: Parameterized queries with built-in caching (`@st.cache_data`)
- **Multiple Data Sources**: 
  - `enhanced_predictions` - Main prediction data with geospatial joins
  - `predicted_results_ha` - Historical model performance
  - `raw_data` - League and match statistics
  - `teams_general_info` - Team locations and metadata
  - `match_weather_data` - Weather information

### Modular Design
```
streamlit/
├── app.py          # Main Streamlit application
├── db.py           # Database connection and query functions
├── geo.py          # Geospatial visualization utilities
├── requirements.txt # Python dependencies
└── README.md       # Documentation
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+ 
- PostgreSQL database (local or remote)
- Required Python packages (see requirements.txt)

### Installation

1. **Clone and Navigate**
   ```bash
   cd streamlit/
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Database Configuration**
   
   **Option A: Using .env file (Recommended)**
   ```bash
   cd streamlit/
   cp .env.example .env
   # Edit .env file with your database credentials
   ```
   
   Example .env file:
   ```env
   DB_HOST=localhost
   DB_PORT=5432
   DB_NAME=your_actual_database_name
   DB_USER=your_actual_username
   DB_PASSWORD=your_actual_password
   ```
   
   **Option B: Using config.json (Fallback)**
   Create config.json in parent directory:
   ```json
   {
     "database": {
       "host": "localhost",
       "port": 5432,
       "database": "your_db_name",
       "user": "your_username",
       "password": "your_password"
     }
   }
   ```
   
   **Option C: Environment Variables**
   ```bash
   export DB_HOST="localhost"
   export DB_PORT="5432"
   export DB_NAME="your_db_name"
   export DB_USER="your_username"
   export DB_PASSWORD="your_password"
   ```

4. **Launch Application**
   
   **Method 1: Using Python launcher (Recommended)**
   ```bash
   python launch.py
   # OR directly
   ./launch.py
   ```
   
   **Method 2: Using bash script**
   ```bash
   bash start.sh
   ```
   
   **Method 3: Direct Streamlit command**
   ```bash
   streamlit run app.py
   ```

5. **Access Dashboard**
   Open your browser to `http://localhost:8501`

## 🗄️ Database Schema

The application expects the following PostgreSQL tables:

### Core Tables
- **enhanced_predictions**: Main prediction data with model results, odds, and confidence scores
- **teams_general_info**: Team metadata including stadium locations (latitude, longitude)
- **match_weather_data**: Weather conditions for match dates
- **predicted_results_ha**: Historical model performance and accuracy metrics
- **raw_data**: Historical match results and league statistics

### Key Queries
The main dashboard query joins multiple tables:
```sql
SELECT 
    ep.model, ep.game_date, ep.league,
    ep.home_team, ep.away_team, ep.predicted_result_with_draws,
    ep.ha_confidence, ep.draw_probability,
    tgi.stadium, tgi.city, tgi.longitude, tgi.latitude,
    mwd.temperature_2m, mwd.wind_speed_10m, mwd.weather_description
FROM enhanced_predictions ep
LEFT JOIN teams_general_info tgi ON ep.home_team = tgi.team
LEFT JOIN match_weather_data mwd ON ep.home_team = mwd.home_team 
    AND ep.game_date = mwd.match_date
```

## 🎛️ Usage Guide

### Dashboard Navigation

1. **Sidebar Filters**
   - Team selection (home or away matches)
   - League filtering
   - Model comparison
   - Date range selection
   - Map display options

2. **Main Dashboard**
   - **KPI Cards**: Key metrics at the top
   - **Analytics Charts**: Prediction distributions, confidence analysis
   - **Geospatial Maps**: Interactive team and match visualizations
   - **Data Explorer**: Searchable and exportable data tables

3. **Interactive Maps**
   - **Teams Tab**: All team locations with highlighting capability
   - **Matches Tab**: Match predictions with customizable coloring
   - **Stats Tab**: Geographic distribution analysis

### Features Overview

- **Real-time Filtering**: All visualizations update based on sidebar selections
- **Export Capabilities**: Download filtered data as CSV
- **Interactive Tables**: Sortable columns with pagination
- **Responsive Design**: Optimized for desktop and tablet viewing
- **Dark Theme**: Professional dark mode styling throughout

## 🔧 Configuration Options

### Map Styling
- Light, Dark, Satellite, Streets map styles
- Customizable marker colors and sizes
- Interactive tooltips and popups

### Performance Settings
- Configurable caching TTL (Time-To-Live)
- Adjustable row limits for large datasets
- Optimized queries with indexing support

### Visualization Options
- Multiple color schemes for different data dimensions
- Adjustable chart heights and layouts
- Export options for charts and data

## 🚀 Production Deployment

### Local-First Design
- Configured for local PostgreSQL by default
- No hardcoded credentials or API keys
- Environment-based configuration

### Cloud Migration Ready
To deploy to cloud PostgreSQL:
1. Update database credentials in config.json or environment variables
2. Ensure network connectivity to cloud database
3. Verify SSL requirements if needed

### Performance Optimization
- Implement database indexing on frequently queried columns
- Consider connection pooling for high-traffic scenarios
- Monitor query performance and optimize slow queries

## 🐛 Troubleshooting

### Common Issues

1. **Database Connection Failed**
   - Verify PostgreSQL is running
   - Check credentials in config.json or environment variables
   - Ensure network connectivity to database

2. **No Data Displayed**
   - Verify required tables exist in database
   - Check table permissions for database user
   - Review filter selections (may be too restrictive)

3. **Map Not Loading**
   - Check that teams have valid latitude/longitude coordinates
   - Verify geospatial data is not null in database
   - Ensure network access for map tiles

4. **Performance Issues**
   - Reduce date range for large datasets
   - Implement database indexing
   - Adjust caching TTL settings

### Debug Mode
Enable Streamlit debug mode for detailed error information:
```bash
streamlit run app.py --logger.level=debug
```

## 🔮 Future Enhancements

- **Real-time Updates**: WebSocket integration for live match updates
- **Advanced Analytics**: Machine learning insights and trend analysis
- **Mobile Optimization**: Enhanced responsive design for mobile devices
- **Multi-language Support**: Internationalization capabilities
- **User Authentication**: Role-based access control
- **Export Options**: PDF reports and dashboard snapshots

---

**Built with:** Streamlit, PostgreSQL, Plotly, PyDeck  
**Version:** 1.0.0  
**Last Updated:** December 2025