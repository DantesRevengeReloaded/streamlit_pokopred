# Data BetProj Postgres Documentation

## Overview
The `data_betproj_postgres.py` module is the core data processing pipeline for the POKOPRED system. It orchestrates data download, storage, processing, and model preparation through a series of interconnected classes that automate the entire football data workflow.

## Module Architecture

```
data_betproj_postgres.py
├── DataHandler (Base Class)
├── DataDL (Data Download)
├── DbTeamStatsStore (Statistics Processing)
├── DbPosgresRawDataStore (Raw Data Storage)
├── PostgresModelStore (Model Data Preparation)
├── ModelRun (Model Execution)
└── DrawDataProcessor (Draw Analysis)
```

## Database Connection

### `get_db_connection()`
**Purpose**: Establish PostgreSQL database connection using environment variables
**Returns**: `psycopg2.connection` object
**Environment Variables Required**:
- `DB_NAME`: Database name
- `DB_USER`: Database user
- `DB_PASSWORD`: Database password
- `DB_HOST`: Database host
- `DB_PORT`: Database port

## Base Class: DataHandler

### Purpose
Base class providing common attributes and configuration for all data processing classes.

### Key Attributes
- `old_seasons`: List of historical seasons to process
- `current_season`: Current active season identifier
- `importfolder`: Directory for raw CSV data storage
- `newcsv_folder`: Directory for processed model-ready data
- `leagues`: Supported football leagues
- `folders`: Season-specific folder mapping
- `model_folders`: Model data folder mapping

### Configuration Loading
Loads settings from `config.json` including:
- Season definitions
- File paths and directories
- League configurations
- Database settings

## Class: DataDL (Data Download)

### Purpose
Handles all data download operations from external sources, managing both historical and current season data.

### Key Methods

#### `get_old_seasons_files(old_seasons=None)`
**Purpose**: Download historical season data for all supported leagues
**Parameters**:
- `old_seasons` (optional): List of seasons to download
**Process**:
1. Confirms and cleans existing folders if needed
2. Iterates through all old seasons
3. Downloads data for each supported league
4. Organizes files by season and league
**Output**: CSV files stored in `importfolder/{season}/`

#### `get_current_season_files(current_season=None)`
**Purpose**: Download current season match data
**Parameters**:
- `current_season` (optional): Specific season to download
**Process**:
1. Creates current season folder structure
2. Downloads match data for all active leagues
3. Handles ongoing season data updates
**Output**: Current season CSV files

#### `update_current_season_files(current_season=None, current_season_folder=None, leagues=None)`
**Purpose**: Update current season with latest results
**Parameters**:
- `current_season` (optional): Season to update
- `current_season_folder` (optional): Target folder path
- `leagues` (optional): Specific leagues to update
**Process**:
1. Downloads latest match results
2. Updates existing files with new data
3. Maintains data consistency
**Usage**: Regular updates for current matches

#### `import_next_fixtures(current_season_path=None)`
**Purpose**: Import upcoming fixture data for predictions
**Parameters**:
- `current_season_path` (optional): Path to current season data
**Process**:
1. Downloads upcoming match fixtures
2. Processes fixture data for each league
3. Stores in standardized format for model consumption
**Output**: Next games data for predictions

### Data Sources
- External football data APIs
- League-specific data feeds
- Fixture and result databases
- Real-time match information

## Class: DbTeamStatsStore (Statistics Processing)

### Purpose
Processes raw match data and calculates comprehensive team statistics for model features.

### Key Methods

#### `team_stats_all()`
**Purpose**: Calculate complete team statistics for all seasons and leagues
**Process**:
1. Processes all historical seasons
2. Calculates team performance metrics
3. Generates statistical features
4. Stores results in database
**Statistics Calculated**:
- Win/loss/draw ratios
- Goals scored and conceded
- Home/away performance
- Form indicators
- Head-to-head records
- League position metrics

#### `team_stats_current_season_update()`
**Purpose**: Update team statistics for current season only
**Process**:
1. Processes current season matches
2. Updates existing team statistics
3. Maintains historical data integrity
4. Calculates season-to-date metrics
**Usage**: Regular updates after new match results

### Statistical Features Generated
- **Performance Metrics**: Win rate, goal difference, points per game
- **Form Analysis**: Recent match trends, momentum indicators
- **Situational Stats**: Home/away splits, against specific opponents
- **Advanced Metrics**: Expected goals, defensive efficiency, attack strength

## Class: DbPosgresRawDataStore (Raw Data Storage)

### Purpose
Manages storage of raw CSV data into PostgreSQL database with proper normalization and indexing.

### Key Methods

#### `store_raw_data_init()`
**Purpose**: Initial storage of all downloaded raw data into database
**Process**:
1. Creates database schema if needed
2. Imports all historical season data
3. Normalizes data structure
4. Creates appropriate indexes
5. Validates data integrity
**Tables Created**:
- Match results by league and season
- Team information
- League structures
- Historical records

#### `store_raw_data_update()`
**Purpose**: Update database with new raw data
**Process**:
1. Imports new match results
2. Updates existing records
3. Maintains referential integrity
4. Handles duplicate detection
**Usage**: Regular updates with new match data

### Database Schema
- **Normalized Structure**: Separate tables for teams, matches, leagues
- **Indexing Strategy**: Optimized for query performance
- **Data Types**: Appropriate PostgreSQL data types for each field
- **Constraints**: Foreign keys and data validation rules

## Class: PostgresModelStore (Model Data Preparation)

### Purpose
Prepares feature-engineered datasets optimized for machine learning model training and prediction.

### Key Methods

#### `store_model_data_init()`
**Purpose**: Create initial model-ready datasets from raw data and statistics
**Process**:
1. Joins raw match data with team statistics
2. Calculates advanced features
3. Creates training and testing datasets
4. Handles missing data and outliers
5. Stores processed data for model consumption
**Output**: ML-ready datasets with engineered features

#### `store_model_data_update()`
**Purpose**: Update model datasets with new information
**Process**:
1. Processes new match data
2. Updates existing feature calculations
3. Maintains dataset consistency
4. Prepares data for model retraining

### Feature Engineering
- **Historical Performance**: Rolling averages, trend analysis
- **Matchup Analysis**: Head-to-head statistics, style comparisons
- **Context Features**: Home advantage, fixture congestion, league position
- **Advanced Metrics**: Team strength ratings, momentum indicators
- **Target Variables**: Match outcomes, goal predictions, draw probabilities

## Class: ModelRun (Model Execution)

### Purpose
Orchestrates the execution of all machine learning models for generating predictions.

### Key Methods

#### `run_model()`
**Purpose**: Execute complete model training and prediction pipeline
**Process**:
1. Loads prepared model data
2. Trains all model types sequentially
3. Generates individual model predictions
4. Creates ensemble predictions
5. Stores results and model artifacts
**Models Executed**:
- Random Forest Classifier
- Neural Network (MLP)
- XGBoost Gradient Boosting
- Logistic Regression
- Calibrated Ensemble
- Soft Voting Ensemble

### Model Integration
- **Data Loading**: Retrieves feature-engineered datasets
- **Model Training**: Individual model training with hyperparameters
- **Prediction Generation**: Creates predictions for upcoming matches
- **Ensemble Methods**: Combines individual model outputs
- **Result Storage**: Saves predictions and model performance metrics

## Class: DrawDataProcessor (Draw Analysis)

### Purpose
Specialized processor for draw prediction analysis and probability calculation.

### Key Methods

#### `get_draw_model_data()`
**Purpose**: Generate specialized datasets and models for draw prediction
**Process**:
1. Creates draw-specific feature sets
2. Analyzes historical draw patterns
3. Calculates draw probabilities
4. Generates draw prediction models
5. Stores draw analysis results

### Draw-Specific Analysis
- **Draw Patterns**: Historical draw frequency by team and league
- **Draw Indicators**: Factors that increase draw probability
- **Situational Analysis**: Conditions favoring draw outcomes
- **Probability Calculation**: Statistical models for draw likelihood

## Error Handling and Logging

### Exception Management
- Try-catch blocks around database operations
- Connection retry logic
- Data validation and error reporting
- Graceful failure handling

### Logging Integration
- Centralized logging through `logging_config`
- Operation progress tracking
- Error documentation
- Performance monitoring

### Data Validation
- Schema validation for imported data
- Duplicate detection and handling
- Missing data identification
- Data quality checks

## Dependencies and Integration

### Module Dependencies
- `data_dler`: Data download functionality
- `data_extraction`: Data processing utilities
- `data_center_postgres`: Database operations
- `data_models`: Machine learning models
- `logging_config`: Centralized logging

### External Dependencies
- `psycopg2`: PostgreSQL connectivity
- `pandas`: Data manipulation
- `numpy`: Numerical operations
- `dotenv`: Environment variable management

## Performance Considerations

### Optimization Strategies
- Batch processing for large datasets
- Database indexing for query performance
- Memory-efficient data loading
- Parallel processing where applicable

### Monitoring Points
- Data download speeds
- Database operation timing
- Memory usage during processing
- Model training performance

## Usage Patterns

### Initial Setup Workflow
1. `DataDL.get_old_seasons_files()` - Download historical data
2. `DataDL.get_current_season_files()` - Download current data
3. `DbPosgresRawDataStore.store_raw_data_init()` - Store raw data
4. `DbTeamStatsStore.team_stats_all()` - Calculate statistics
5. `PostgresModelStore.store_model_data_init()` - Prepare model data
6. `ModelRun.run_model()` - Train models

### Regular Update Workflow
1. `DataDL.update_current_season_files()` - Update current data
2. `DbPosgresRawDataStore.store_raw_data_update()` - Update database
3. `DbTeamStatsStore.team_stats_current_season_update()` - Update stats
4. `PostgresModelStore.store_model_data_update()` - Update model data
5. `ModelRun.run_model()` - Retrain models (optional)

### Prediction Workflow
1. `DataDL.import_next_fixtures()` - Get upcoming matches
2. `ModelRun.run_model()` - Generate predictions
3. `DrawDataProcessor.get_draw_model_data()` - Analyze draw probabilities

## Best Practices

### Data Management
- Regular database maintenance
- Backup procedures for critical data
- Data archiving strategies
- Performance monitoring

### Model Updates
- Regular retraining schedules
- Performance validation
- Model versioning
- A/B testing for improvements