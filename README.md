# Football Predictions Dashboard

A production-ready Streamlit web application for analyzing football match predictions with advanced geospatial visualization capabilities.

## PokoPred Overview

PokoPred is a system that predicts football match outcomes using historical data and machine learning models. It uses PostgreSQL to store all the relevant data.

Models that generate predictions include:
- **Home/Away Model**: Considers team performance to predict outcomes with only home and away results.
**Draw Probability**: Calculates the likelihood of a draw based on various factors and then incorporates it into the final prediction

The Models that are trained are:
 Random Forest, XGBoost, Logistic Regression, and Neural Networks.
 Then using ensemble soft voting to combine the predictions from multiple models to improve accuracy.

Complete explanation of the models and methodology can be found in the [PokoPred Documentation](#PokoPred_Docs).

## 🎯 Features

### 📊 Core Analytics

- **League Statistics**: Historical data analysis across different football leagues and seasons
- **Interactive Filtering**: Dynamic filters by team, league, date range, and prediction models
- **KPI Cards**: Key performance indicators for quick insights
- **Data Explorer**: Searchable and exportable data tables with pagination

### 🗺️ Geospatial Intelligence
- **Teams Location Map**: Interactive map showing all football teams with stadium locations
- **Match Predictions Map**: Geospatial visualization of match predictions with weather data
- **Geographic Analytics**: Distribution analysis, country statistics, and location-based insights
- **Route Mapping**: Team journey visualization for away matches


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

## 📚 PokoPred Documentation

### System Documentation Overview
The PokoPred system includes comprehensive documentation for all core components. Each documentation file provides detailed technical specifications, usage examples, and implementation details.

#### 📋 Core Documentation Files

##### [System Documentation Index](PokoPred_Docs/SYSTEM_DOCUMENTATION_INDEX.md)
**Summary**: Master index and navigation guide for all PokoPred documentation
- Complete overview of documentation structure
- Navigation links to all component documentation
- Quick reference for finding specific functionality
- Architecture overview and component relationships

##### [Data Models Documentation](PokoPred_Docs/data_models_documentation.md)
**Summary**: Machine learning model implementations and ensemble methods
- Base PokoPred class architecture and common functionality
- Individual model implementations (Random Forest, Neural Networks, XGBoost, Logistic Regression)
- Advanced ensemble methods and model combinations
- Draw analysis and specialized prediction techniques
- Model training, evaluation, and prediction workflows

##### [Data BetProj Postgres Documentation](PokoPred_Docs/data_betproj_postgres_documentation.md)
**Summary**: Core data processing pipeline and database operations
- Data download and management classes
- PostgreSQL database storage and raw data processing
- Team statistics calculation and automated storage
- Model data preparation and feature engineering
- Complete pipeline orchestration and workflow automation

##### [Data Downloader Documentation](PokoPred_Docs/data_dler_documentation.md)
**Summary**: Data acquisition and download management system
- Web scraping and HTTP data retrieval mechanisms
- Football data source integration and management
- Upcoming fixtures and schedule management
- League and season support utilities
- Error handling and download optimization strategies

##### [Tools Documentation](PokoPred_Docs/tools_documentation.md)
**Summary**: Advanced analysis and optimization tools
- Model performance analysis with ROI calculations
- Hyperparameter optimization and tuning tools
- Weather data integration for enhanced predictions
- Geographic data scraping and map visualization
- Performance evaluation and analysis utilities

##### [Draw Conversion Implementation](PokoPred_Docs/draw_conversion_implementation.md)
**Summary**: Enhanced prediction system for draw outcomes
- DrawConvertor class for H/A to Draw prediction conversion
- Configurable confidence and probability thresholds
- DrawPredictionProcessor for complete workflow orchestration
- Database integration for enhanced predictions storage

##### [Logging Configuration Documentation](PokoPred_Docs/logging_config_documentation.md)
**Summary**: Centralized logging framework and configuration
- JSON-based logging configuration system
- Module-specific log levels and file rotation
- Console and file output capabilities
- Error-safe fallback mechanisms and validation

### 🔗 Quick Navigation

| Component | File | Purpose |
|-----------|------|---------|
| **System Index** | [SYSTEM_DOCUMENTATION_INDEX.md](PokoPred_Docs/SYSTEM_DOCUMENTATION_INDEX.md) | Master documentation index |
| **ML Models** | [data_models_documentation.md](PokoPred_Docs/data_models_documentation.md) | Machine learning implementations |
| **Data Pipeline** | [data_betproj_postgres_documentation.md](PokoPred_Docs/data_betproj_postgres_documentation.md) | Core data processing |
| **Data Acquisition** | [data_dler_documentation.md](PokoPred_Docs/data_dler_documentation.md) | Download management |
| **Analysis Tools** | [tools_documentation.md](PokoPred_Docs/tools_documentation.md) | Advanced analysis utilities |
| **Draw Predictions** | [draw_conversion_implementation.md](PokoPred_Docs/draw_conversion_implementation.md) | Draw outcome enhancement |
| **Logging System** | [logging_config_documentation.md](PokoPred_Docs/logging_config_documentation.md) | Centralized logging framework |

### 📖 Documentation Features

- **Comprehensive Coverage**: Every major system component is documented
- **Technical Specifications**: Detailed function and class documentation
- **Usage Examples**: Practical implementation examples
- **Architecture Diagrams**: Visual representation of system structure
- **Cross-References**: Links between related components
- **Implementation Details**: Deep-dive technical information

For the most up-to-date and detailed information about any component, refer to the specific documentation file in the `PokoPred_Docs/` directory.