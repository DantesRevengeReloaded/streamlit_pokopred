# Draw Conversion Implementation

## Overview

This implementation provides enhanced prediction capabilities by converting Home/Away (H/A) predictions to Draw (D) predictions based on configurable confidence and probability thresholds.

## Components

### 1. DrawConvertor Class (data_extraction.py)

**Purpose**: Converts H/A predictions to Draw predictions based on:
- Maximum H/A model confidence threshold
- Minimum draw probability threshold

**Key Method**: `convert_draw_data_for_model(max_model_confidence=None, min_draw_probability=None)`

**Features**:
- Loads parameters from `config.json` automatically
- Creates `Predicted_Result_With_Draws` column
- Tracks conversion statistics and metadata
- Handles missing data gracefully

### 2. DrawPredictionProcessor Class (data_betproj_postgres.py)

**Purpose**: Orchestrates the complete draw prediction workflow by combining:
- Data retrieval (via DrawDataRetriever)  
- Draw conversion logic (via DrawConvertor)
- **Database storage** (via StoreEnhancedPredictions)

**Key Method**: `process_last_session_with_draws(max_model_confidence=None, min_draw_probability=None)`

**Storage Methods**:
- `save_enhanced_predictions_to_db()`: **NEW** - Stores predictions in database with constraints
- `save_enhanced_predictions_csv()`: Legacy CSV export for backup/compatibility
- `save_enhanced_predictions()`: Main method (now defaults to database storage)

### 3. StoreEnhancedPredictions Class (data_center_postgres.py)

**Purpose**: **NEW** - Handles database storage of enhanced predictions

**Key Features**:
- **Database Table**: `enhanced_predictions` with composite unique constraint
- **Constraint**: `(model, game_date, home_team)` - prevents duplicates
- **Upsert Logic**: Uses `ON CONFLICT` to update existing or insert new records
- **Batch Processing**: Efficient bulk inserts with configurable batch size
- **Data Mapping**: Automatic column mapping and type conversion
- **Retrieval**: Query methods for accessing stored predictions

## Configuration Parameters

In `config.json`:

```json
"draw_conversion_parameters": {
    "max_model_confidence": 7.0,
    "min_draw_probability": 0.35,
    "model_to_convert": "RF_comp"
}
```

**Parameters**:
- `max_model_confidence`: Maximum H/A confidence allowed for conversion (lower = more conversions)
- `min_draw_probability`: Minimum draw probability required for conversion (higher = fewer conversions)
- `model_to_convert`: Which model's predictions to process

## Usage Examples

### Basic Usage (Database Storage)

```python
from data_betproj_postgres import DrawPredictionProcessor

# Initialize processor
processor = DrawPredictionProcessor()

# Process with default config parameters
enhanced_df = processor.process_last_session_with_draws()

# Store results in database (NEW default behavior)
successful_inserts, total_rows = processor.save_enhanced_predictions()
print(f"Stored {successful_inserts}/{total_rows} predictions in database")
```

### Database Storage with CSV Backup

```python
# Store in database AND create CSV backup
db_result = processor.save_enhanced_predictions("backup_predictions.csv")
successful_inserts, total_rows, csv_path = db_result
print(f"Database: {successful_inserts} records, CSV: {csv_path}")
```

### Custom Parameters

```python
# Use custom thresholds
enhanced_df = processor.process_last_session_with_draws(
    max_model_confidence=5.0,  # More restrictive (lower confidence)
    min_draw_probability=0.4   # More restrictive (higher probability)
)

# Store with parameter tracking
successful_inserts, total_rows = processor.save_enhanced_predictions_to_db(
    max_model_confidence=5.0,
    min_draw_probability=0.4
)
```

### Direct Database Access

```python
from data_center_postgres import StoreEnhancedPredictions
import pandas as pd

# For retrieval and analysis
storage = StoreEnhancedPredictions(pd.DataFrame())  # Empty df for queries

# Get recent predictions
recent_preds = storage.get_stored_predictions(
    model="RF_comp",
    date_from="2025-12-01", 
    limit=100
)

# Get all predictions for a specific model
model_preds = storage.get_stored_predictions(model="RF_comp")
```

### Legacy CSV-Only Usage

```python
# For backward compatibility or debugging
csv_path = processor.save_enhanced_predictions_csv("debug_predictions.csv")
```

## Output Data

### Database Storage (Primary)

**Table**: `enhanced_predictions`
**Constraint**: `UNIQUE(model, game_date, home_team)` - prevents duplicate match predictions

**Key Columns**:
- `predicted_result_with_draws`: Final prediction (H/A/D) after conversion
- `conversion_applied`: Boolean indicating if conversion was applied  
- `original_prediction`: Original H/A prediction before conversion
- `ha_confidence`: Confidence score from H/A model
- `draw_probability`: Calculated draw probability
- `max_model_confidence`: Threshold parameter used for conversion
- `min_draw_probability`: Threshold parameter used for conversion
- Match info: `game_date`, `home_team`, `away_team`, `league`, `model`
- Team characteristics: `is_derby`, `ht_strength`, `at_strength`, etc.

### DataFrame Columns (In-Memory)

The enhanced dataframe includes:
- `Predicted_Result_With_Draws`: Final prediction (H/A/D) after conversion
- `Conversion_Applied`: Boolean indicating if conversion was applied
- `Original_Prediction`: Original H/A prediction before conversion  
- All original columns (predictions, probabilities, team info, etc.)

## Conversion Logic

A prediction is converted from H/A to D when **BOTH** conditions are met:

1. **Low H/A Confidence**: `ha_confidence <= max_model_confidence`
2. **High Draw Probability**: `draw_probability >= min_draw_probability`

This logic identifies matches where:
- The model is uncertain about the H/A outcome (low confidence)
- There's significant evidence for a draw outcome (high draw probability)

## Testing

Run the test script to verify functionality:

```bash
# From the project root directory
source bet_proj_2_0/bin/activate
python test_draw_conversion.py
```

## Integration Points

This implementation integrates with:

- **Data Retrieval**: Uses `DrawDataRetriever.get_last_session_with_draw_probability()`
- **Model Predictions**: Works with any model that provides H/A predictions and confidence scores
- **Draw Analysis**: Utilizes draw probability calculations from existing pipeline
- **Configuration**: Reads parameters from centralized `config.json`
- **Database**: **NEW** - Stores enhanced predictions in PostgreSQL with proper constraints
- **Constraints**: Prevents duplicate predictions using `(model, game_date, home_team)` composite key

## Database Schema

### Enhanced Predictions Table

```sql
CREATE TABLE enhanced_predictions (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(100),
    model VARCHAR(50) NOT NULL,
    game_date DATE NOT NULL, 
    home_team VARCHAR(100) NOT NULL,
    away_team VARCHAR(100) NOT NULL,
    
    -- Original H/A Predictions
    predicted_ha_result VARCHAR(1),
    ha_confidence DECIMAL(5,3),
    
    -- Draw Analysis
    draw_probability DECIMAL(5,3),
    avgh DECIMAL(6,3),
    avgd DECIMAL(6,3), 
    avga DECIMAL(6,3),
    
    -- Enhanced Predictions
    predicted_result_with_draws VARCHAR(1),
    conversion_applied BOOLEAN DEFAULT FALSE,
    original_prediction VARCHAR(1),
    
    -- Conversion Parameters
    max_model_confidence DECIMAL(5,2),
    min_draw_probability DECIMAL(5,3),
    
    -- Team Characteristics
    is_derby VARCHAR(3),
    ht_strength DECIMAL(6,3),
    at_strength DECIMAL(6,3),
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT unique_enhanced_prediction 
        UNIQUE (model, game_date, home_team)
);
```

## Logging

The implementation provides comprehensive logging at different levels:

- **INFO**: Major steps and summary statistics
- **DEBUG**: Detailed conversion decisions per match
- **ERROR**: Issues with data or processing

## Error Handling

- Missing required columns are detected and reported
- Invalid data values are handled gracefully
- Configuration loading failures fall back to default parameters
- Processing errors are logged with full context

## Summary

✅ **Complete Implementation Achieved:**

1. **DrawConvertor Class** - Enhanced with configurable draw conversion logic
2. **DrawPredictionProcessor Class** - Full workflow orchestration with database storage  
3. **StoreEnhancedPredictions Class** - Robust database storage with proper constraints
4. **CSV Export Tool Integration** - Enhanced predictions available as menu option 4
5. **CLI Integration** - Full integration through existing CSV export system
6. **Configuration Management** - Flexible parameters from config.json
7. **Database Schema** - Complete table with unique constraints and performance indexes

The implementation successfully combines H/A predictions with draw probability analysis, stores results in database with proper constraints `(model, game_date, home_team)`, and exports to CSV files for analysis. All functionality is accessible through the interactive CLI interface.