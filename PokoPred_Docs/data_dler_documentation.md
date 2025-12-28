# Data Downloader (Data DLer) Documentation

## Overview
The `data_dler.py` module provides the foundational data acquisition capabilities for the POKOPRED system. It handles downloading football match data from external sources, manages upcoming fixture data, and provides utilities for league and season management.

## Module Architecture

```
data_dler.py
├── DataManager (Web Scraping & Download)
├── UpComingGames (Fixture Management)
└── Utility Functions (League & Season Support)
```

## Class: DataManager

### Purpose
Core class responsible for downloading football match data from external websites, managing HTTP requests, and organizing downloaded CSV files by season and league.

### Key Attributes
- `url`: Base URL for data source
- `session`: HTTP session for connection management
- `headers`: HTTP headers for requests
- `timeout`: Request timeout settings

### Methods

#### `__init__(url)`
**Purpose**: Initialize DataManager with target URL
**Parameters**:
- `url`: Base URL for the football data source
**Setup**:
- Creates HTTP session with proper headers
- Sets up user agent for web scraping
- Configures timeout and retry settings

#### `fetch_html()`
**Purpose**: Retrieve HTML content from the target URL
**Process**:
1. Sends HTTP GET request to target URL
2. Handles response status codes
3. Returns HTML content for parsing
4. Manages connection errors and timeouts
**Returns**: HTML content string or None on failure
**Error Handling**: Connection timeouts, HTTP errors, invalid responses

#### `download_csv(season, league, file_name)`
**Purpose**: Download specific CSV file for a given season and league
**Parameters**:
- `season`: Season identifier (e.g., "2023-2024")
- `league`: League code (e.g., "E0" for Premier League)
- `file_name`: Target filename for downloaded data
**Process**:
1. Constructs download URL from parameters
2. Sends HTTP request for CSV file
3. Downloads and saves file to appropriate directory
4. Validates file integrity and content
5. Handles download errors and retries
**Output**: CSV file saved to local filesystem
**Directory Structure**: `{importfolder}/{season}/{league}.csv`

### Data Source Integration
- **HTTP Session Management**: Persistent connections for efficiency
- **Rate Limiting**: Respectful downloading to avoid server overload
- **Error Recovery**: Automatic retry logic for failed downloads
- **Content Validation**: Verification of downloaded file integrity

## Class: UpComingGames

### Purpose
Specialized class for managing upcoming fixture data, handling future match schedules, and preparing prediction datasets.

### Key Attributes
- `base_url`: URL for fixture data source
- `fixtures_data`: Stored fixture information
- `leagues_mapping`: League code to name mapping
- `date_formats`: Supported date parsing formats

### Methods

#### `__init__()`
**Purpose**: Initialize upcoming games manager
**Setup**:
- Configures fixture data source URLs
- Sets up league mapping dictionaries
- Initializes date parsing utilities
- Prepares data storage structures

#### `fetch_html()`
**Purpose**: Retrieve HTML content containing fixture information
**Process**:
1. Connects to fixture data source
2. Downloads upcoming match schedules
3. Parses HTML for fixture data
4. Handles dynamic content loading
**Returns**: HTML content with fixture information
**Features**: JavaScript rendering support, dynamic content handling

#### `download_csv()`
**Purpose**: Download and process upcoming fixture CSV data
**Process**:
1. Retrieves fixture data from multiple sources
2. Consolidates data into standardized format
3. Processes date and time information
4. Generates CSV files for each league
5. Validates fixture data completeness
**Output**: Standardized CSV files with upcoming matches
**Data Fields**: Date, Time, Home Team, Away Team, League

### Fixture Data Processing
- **Date Standardization**: Converts various date formats to consistent format
- **Time Zone Handling**: Manages different time zones for international leagues
- **Team Name Normalization**: Standardizes team names across data sources
- **League Classification**: Properly categorizes matches by competition

## Utility Functions

### `listofleaguesfordl(season)`
**Purpose**: Generate comprehensive list of leagues available for download for a specific season
**Parameters**:
- `season`: Season identifier to check league availability
**Process**:
1. Checks data source for available leagues
2. Validates league data availability
3. Returns list of downloadable league codes
4. Handles season-specific league variations
**Returns**: List of league codes (e.g., ['E0', 'E1', 'D1', 'I1'])
**Supported Leagues**:
- **England**: Premier League (E0), Championship (E1), League One (E2), League Two (E3)
- **Germany**: Bundesliga (D1), 2. Bundesliga (D2)
- **Italy**: Serie A (I1), Serie B (I2)
- **Spain**: La Liga (SP1), Segunda División (SP2)
- **France**: Ligue 1 (F1), Ligue 2 (F2)
- **Netherlands**: Eredivisie (N1)
- **Belgium**: Jupiler Pro League (B1)
- **Portugal**: Primeira Liga (P1)
- **Turkey**: Süper Lig (T1)
- **Greece**: Super League (G1)

### League Configuration Management
**Purpose**: Manage league-specific download parameters and configurations
**Features**:
- League code standardization
- URL pattern management for different leagues
- File naming conventions
- Season-specific availability checks

## Data Download Workflow

### Historical Data Download Process
1. **Season Iteration**: Loop through all historical seasons
2. **League Discovery**: Identify available leagues for each season
3. **File Download**: Download CSV files for each league/season combination
4. **Validation**: Verify download completeness and data integrity
5. **Organization**: Store files in structured directory hierarchy
6. **Error Handling**: Retry failed downloads and log errors

### Current Season Updates
1. **Incremental Updates**: Download only new match results
2. **File Merging**: Combine new data with existing files
3. **Duplicate Handling**: Prevent duplicate match entries
4. **Consistency Checks**: Validate data consistency across updates

### Fixture Management
1. **Schedule Download**: Retrieve upcoming match schedules
2. **Date Processing**: Parse and standardize fixture dates
3. **Team Mapping**: Match team names to database entries
4. **Prediction Preparation**: Format data for model consumption

## Error Handling and Reliability

### Network Error Management
- **Connection Timeouts**: Graceful handling of slow connections
- **HTTP Errors**: Proper response to 404, 500, and other HTTP errors
- **Retry Logic**: Automatic retry with exponential backoff
- **Rate Limiting**: Respect server rate limits and terms of service

### Data Validation
- **File Integrity**: Check downloaded file completeness
- **Format Validation**: Verify CSV structure and content
- **Date Validation**: Ensure proper date formatting
- **Team Name Consistency**: Validate team name mappings

### Logging and Monitoring
- **Download Progress**: Track download completion status
- **Error Logging**: Record failed downloads and reasons
- **Performance Metrics**: Monitor download speeds and success rates
- **Data Quality**: Log data validation results

## Integration with Main System

### Configuration Integration
- Reads league and season settings from `config.json`
- Uses centralized logging from `logging_config`
- Integrates with database connection settings
- Respects system-wide path configurations

### Data Pipeline Integration
- **Raw Data Provision**: Supplies data to `DbPosgresRawDataStore`
- **Statistics Support**: Provides data for `DbTeamStatsStore`
- **Model Data**: Feeds into `PostgresModelStore`
- **Prediction Input**: Supplies fixture data for predictions

## Performance Considerations

### Download Optimization
- **Concurrent Downloads**: Parallel downloading for multiple leagues
- **Connection Pooling**: Reuse HTTP connections for efficiency
- **Compression**: Handle gzip and other compressed responses
- **Caching**: Local caching of frequently accessed data

### Resource Management
- **Memory Usage**: Efficient handling of large CSV files
- **Disk Space**: Monitor storage requirements for downloaded data
- **Network Bandwidth**: Optimize download patterns for available bandwidth
- **CPU Usage**: Balance processing speed with system resources

## Usage Examples

### Basic Data Download
```python
# Initialize data manager
downloader = DataManager('https://data-source.com')

# Download specific league data
downloader.download_csv('2023-2024', 'E0', 'premier_league.csv')
```

### Upcoming Fixtures
```python
# Get upcoming games
fixtures = UpComingGames()
fixture_data = fixtures.download_csv()
```

### League Discovery
```python
# Get available leagues for season
available_leagues = listofleaguesfordl('2023-2024')
print(f"Available leagues: {available_leagues}")
```

## Best Practices

### Data Download Guidelines
1. **Respectful Scraping**: Follow robots.txt and rate limits
2. **Error Resilience**: Implement robust error handling
3. **Data Validation**: Always verify downloaded data integrity
4. **Resource Efficiency**: Optimize network and storage usage
5. **Monitoring**: Track download success rates and performance

### Maintenance Considerations
- **URL Updates**: Monitor and update data source URLs
- **Format Changes**: Adapt to changes in CSV structure
- **New Leagues**: Add support for additional leagues
- **Season Management**: Handle new seasons and date ranges
- **Error Analysis**: Regular review of download failures and issues