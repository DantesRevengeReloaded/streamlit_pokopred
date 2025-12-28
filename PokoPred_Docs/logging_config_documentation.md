# Logging Configuration Documentation

## Overview
The `logging_config.py` module provides centralized logging configuration for the entire POKOPRED system. It implements a sophisticated logging framework with JSON-based configuration, file rotation, module-specific log levels, and both console and file output capabilities.

## Module Architecture

```
logging_config.py
├── Configuration Loading (JSON-based)
├── Logger Setup (Module-specific)
├── File Rotation (Size-based)
├── Console Output (Configurable)
└── Fallback Mechanisms (Error-safe)
```

## Core Functions

### `load_logging_config()`
**Purpose**: Load logging configuration from JSON configuration file
**Process**:
1. Reads `config.json` file from project root
2. Extracts logging section from configuration
3. Provides fallback configuration if file missing
4. Validates configuration parameters
**Returns**: Dictionary with logging configuration
**Default Configuration**:
```json
{
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "file": "logs/pokopred.log",
    "console": true,
    "max_file_size": "10MB",
    "backup_count": 5,
    "module_levels": {}
}
```

### `setup_logging(module_name=None)`
**Purpose**: Configure and return a logger instance for a specific module
**Parameters**:
- `module_name` (optional): Name of the module requesting logger
**Process**:
1. Loads configuration from JSON
2. Sets up root logger if not already configured
3. Creates module-specific logger if requested
4. Applies appropriate log levels
5. Configures handlers (file and console)
**Returns**: Logger instance configured for the module

## Configuration Features

### JSON-Based Configuration
**File**: `config.json` - logging section
**Structure**:
```json
{
    "logging": {
        "level": "INFO",
        "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        "file": "logs/pokopred.log",
        "console": true,
        "max_file_size": "10MB",
        "backup_count": 5,
        "module_levels": {
            "data_models": "DEBUG",
            "data_betproj_postgres": "INFO",
            "cli_pokopred": "INFO"
        }
    }
}
```

### Configuration Parameters

#### `level`
**Purpose**: Default logging level for all modules
**Options**: DEBUG, INFO, WARNING, ERROR, CRITICAL
**Default**: "INFO"
**Usage**: Controls minimum severity of messages logged

#### `format`
**Purpose**: Log message formatting template
**Default**: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
**Components**:
- `%(asctime)s`: Timestamp of log event
- `%(name)s`: Logger name (usually module name)
- `%(levelname)s`: Log level (INFO, ERROR, etc.)
- `%(message)s`: Actual log message

#### `file`
**Purpose**: Path to log file
**Default**: "logs/pokopred.log"
**Features**: Automatic directory creation if path doesn't exist

#### `console`
**Purpose**: Enable/disable console output
**Type**: Boolean
**Default**: true
**Usage**: Controls whether logs appear in terminal/console

#### `max_file_size`
**Purpose**: Maximum size before log rotation
**Format**: String with unit (e.g., "10MB", "50MB", "1GB")
**Default**: "10MB"
**Features**: Automatic file rotation when size exceeded

#### `backup_count`
**Purpose**: Number of backup log files to maintain
**Type**: Integer
**Default**: 5
**Usage**: Keeps specified number of rotated log files

#### `module_levels`
**Purpose**: Module-specific log level overrides
**Type**: Dictionary mapping module names to log levels
**Usage**: Allows fine-grained control over logging verbosity per module
**Example**:
```json
"module_levels": {
    "data_models": "DEBUG",
    "data_betproj_postgres": "WARNING",
    "cli_pokopred": "INFO"
}
```

## Logging Handlers

### File Handler (RotatingFileHandler)
**Purpose**: Write logs to file with automatic rotation
**Features**:
- Size-based rotation (configurable maximum file size)
- Automatic backup file management
- UTF-8 encoding support
- Thread-safe operations
- Automatic directory creation

**File Naming Pattern**:
- Primary log: `pokopred.log`
- Rotated files: `pokopred.log.1`, `pokopred.log.2`, etc.

### Console Handler (StreamHandler)
**Purpose**: Display logs in terminal/console output
**Features**:
- Real-time log display
- Color-coded output (where supported)
- Configurable enable/disable
- Same formatting as file output

## Logger Hierarchy

### Root Logger Configuration
**Name**: "pokopred"
**Purpose**: Base logger for entire system
**Configuration**: Applied from JSON settings
**Propagation**: Disabled to prevent duplicate messages

### Module-Specific Loggers
**Naming Convention**: Uses `__name__` of importing module
**Examples**:
- `data_models`
- `data_betproj_postgres`
- `cli_pokopred`
- `logging_config`

### Logger Inheritance
- Module loggers inherit from root logger
- Module-specific levels override default
- Handler inheritance from root logger
- Formatter consistency across all loggers

## Error Handling and Fallbacks

### Configuration Error Handling
**Missing Config File**:
- Falls back to default configuration
- Logs warning about missing config
- Continues operation with defaults

**Invalid Config Values**:
- Uses default values for invalid settings
- Logs errors about configuration problems
- Maintains system stability

**Directory Creation**:
- Automatically creates log directory if missing
- Handles permission errors gracefully
- Falls back to current directory if needed

### Fallback Configuration
```python
default_config = {
    'level': 'INFO',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'file': 'logs/pokopred.log',
    'console': True,
    'max_file_size': '10MB',
    'backup_count': 5,
    'module_levels': {}
}
```

## Integration with System Components

### Module Integration Pattern
**Import Pattern**:
```python
from logging_config import setup_logging
logger = setup_logging(__name__)
```

**Usage Pattern**:
```python
logger.info("Operation completed successfully")
logger.warning("Potential issue detected")
logger.error("Error occurred during processing")
logger.debug("Detailed debugging information")
```

### Database Integration
- Database operations logged with appropriate levels
- Connection status and errors tracked
- Query performance monitoring (if enabled)
- Transaction logging for debugging

### Model Training Integration
- Training progress logging
- Performance metrics recording
- Error tracking and debugging
- Model saving/loading status

### CLI Integration
- User interaction logging
- Command execution tracking
- Error reporting for troubleshooting
- Operation timing and performance

## Performance Considerations

### Logging Overhead
- Minimal impact on system performance
- Efficient file I/O operations
- Configurable levels to reduce overhead
- Lazy evaluation of log messages

### File Management
- Automatic rotation prevents disk space issues
- Efficient file handling with proper closing
- Backup management to prevent accumulation
- Compressed backup files (if supported)

### Memory Usage
- Minimal memory footprint
- Efficient handler management
- Proper resource cleanup
- Thread-safe operations

## Usage Examples

### Basic Setup
```python
from logging_config import setup_logging

# Module-specific logger
logger = setup_logging(__name__)

# Log messages
logger.info("Starting data processing")
logger.error("Failed to connect to database")
```

### Module-Specific Configuration
**In config.json**:
```json
{
    "logging": {
        "level": "INFO",
        "module_levels": {
            "data_models": "DEBUG",
            "data_extraction": "WARNING"
        }
    }
}
```

### Advanced Usage
```python
# Different log levels
logger.debug("Detailed debugging information")
logger.info("General information")
logger.warning("Warning message")
logger.error("Error occurred")
logger.critical("Critical system error")

# Formatted messages
logger.info("Processing %d records", record_count)
logger.error("Failed to process file: %s", filename)
```

## Log Analysis and Monitoring

### Log File Structure
- Chronological order of events
- Consistent formatting across modules
- Module identification for troubleshooting
- Severity levels for filtering

### Common Log Patterns
- System startup and shutdown
- Database operations
- Model training progress
- Error conditions and recovery
- Performance metrics

### Troubleshooting Support
- Clear error messages with context
- Stack traces for debugging
- Module identification for issue isolation
- Timing information for performance analysis

## Best Practices

### Configuration Management
1. **Centralized Configuration**: Use JSON config for all logging settings
2. **Module-Specific Levels**: Configure appropriate levels per module
3. **File Rotation**: Enable rotation to prevent log files from growing too large
4. **Console Output**: Use for development, disable for production if needed

### Logging Practices
1. **Appropriate Levels**: Use correct log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
2. **Meaningful Messages**: Write clear, actionable log messages
3. **Context Information**: Include relevant context in log messages
4. **Error Handling**: Always log exceptions and errors
5. **Performance Monitoring**: Log key performance metrics and timing

### Maintenance
1. **Regular Cleanup**: Monitor and clean old log files if needed
2. **Configuration Review**: Periodically review and update log levels
3. **Performance Monitoring**: Monitor logging overhead and adjust if needed
4. **Error Analysis**: Regularly review error logs for system health