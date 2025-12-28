# Football Predictions Dashboard

A production-ready Streamlit web application for analyzing football match predictions with advanced geospatial visualization capabilities.

## PokoPred Overview

PokoPred is a system that predicts football match outcomes using historical data and machine learning models. It uses PostgreSQL to store all the relevant data.

Models that generate predictions include:
- **Home/Away Model**: Considers team performance to predict outcomes with only home and away results.
**Draw Probability**: Calculates the likelihood of a draw based on various factors and then incorporates it into the final prediction

**Model Ensemble**: Combines Random Forest, XGBoost, Logistic Regression, and Neural Networks using soft voting for improved accuracy.

**Calibrated Models**: Applies probability calibration techniques to enhance prediction reliability.

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