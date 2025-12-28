# Tools Documentation

## Overview
The `src/tools/` directory contains specialized analysis and optimization tools that extend the core POKOPRED functionality. These tools provide advanced capabilities for model analysis, hyperparameter optimization, data integration, and performance evaluation.

## Tools Architecture

```
src/tools/
├── models_prediction_analysis.py (Model Performance Analysis)
├── hyperparameters_optimizer.py (Model Optimization)
├── team_weather_data_integrator_history.py (Weather Integration)
├── model_performance_evaluator.py (Performance Evaluation)
├── hyperparameters_analyzer.py (Analysis Tools)
├── team_location_scraper.py (Geographic Data)
├── team_map_generator.py (Map Visualization)
├── load_teams_to_db.py (Database Utilities)
└── hyperparameter_visualizations/ (Visualization Assets)
```

## Model Prediction Analysis Tool

### File: `models_prediction_analysis.py`
**Purpose**: Comprehensive analysis of prediction model performance with focus on ROI and betting strategy evaluation.

### Key Features
- **Interactive Session Selection**: Choose specific prediction sessions for analysis
- **ROI Analysis**: Calculate return on investment for different betting strategies  
- **Draw Conversion Strategies**: Specialized analysis for draw predictions
- **Performance Metrics**: Comprehensive model accuracy and reliability metrics
- **Comparative Analysis**: Compare performance across different models and time periods

### Main Functions

#### `main()`
**Purpose**: Entry point for the analysis tool
**Mode Support**: 
- Interactive mode (default)
- Command-line argument mode
- CLI integration mode

#### `interactive_session_selection()`
**Purpose**: Allow users to select specific prediction sessions to analyze
**Features**:
- List available prediction sessions
- Date range selection
- Model type filtering
- Performance preview

#### `calculate_roi_metrics()`
**Purpose**: Calculate detailed return on investment metrics
**Metrics**:
- Total ROI percentage
- Average bet return
- Win rate analysis
- Risk-adjusted returns
- Bankroll growth simulation

#### `analyze_draw_strategies()`
**Purpose**: Specialized analysis for draw betting strategies
**Analysis**:
- Draw prediction accuracy
- Draw-specific ROI calculations
- Optimal draw betting thresholds
- Draw frequency patterns

### Usage Integration
```python
# CLI Integration
from tools.models_prediction_analysis import main as analysis_main
analysis_main()

# Direct Function Usage
from tools.models_prediction_analysis import calculate_roi_metrics
roi_data = calculate_roi_metrics(prediction_data)
```

## Hyperparameter Optimizer Tool

### File: `hyperparameters_optimizer.py`
**Purpose**: Advanced hyperparameter optimization for all machine learning models using various optimization algorithms.

### Key Features
- **Multiple Optimization Algorithms**: Grid search, random search, Bayesian optimization
- **Cross-Validation Integration**: Robust performance evaluation during optimization
- **Database Storage**: Persistent storage of optimization results
- **Performance Benchmarking**: Compare optimization strategies
- **Automated Model Retraining**: Apply best parameters automatically

### Main Functions

#### `optimize_random_forest()`
**Purpose**: Optimize Random Forest hyperparameters
**Parameters Optimized**:
- `n_estimators`: Number of trees (50-500)
- `max_depth`: Tree depth (5-50)
- `min_samples_split`: Minimum samples for split (2-20)
- `min_samples_leaf`: Minimum samples per leaf (1-10)
- `max_features`: Feature selection strategy

#### `optimize_neural_network()`
**Purpose**: Optimize Neural Network architecture and training parameters
**Parameters Optimized**:
- `hidden_layer_sizes`: Network architecture
- `learning_rate`: Adaptive learning rates
- `alpha`: Regularization strength
- `batch_size`: Training batch sizes
- `max_iter`: Training iterations

#### `optimize_xgboost()`
**Purpose**: Optimize XGBoost boosting parameters
**Parameters Optimized**:
- `n_estimators`: Number of boosting rounds
- `learning_rate`: Step size shrinkage
- `max_depth`: Tree complexity
- `subsample`: Sampling ratio
- `colsample_bytree`: Feature sampling

#### `bayesian_optimization()`
**Purpose**: Advanced Bayesian optimization for efficient parameter search
**Features**:
- Gaussian process modeling
- Acquisition function optimization
- Efficient exploration-exploitation balance
- Early stopping for convergence

### Usage Examples
```python
# Optimize specific model
from tools.hyperparameters_optimizer import optimize_random_forest
best_params = optimize_random_forest(X_train, y_train)

# Full optimization pipeline
from tools.hyperparameters_optimizer import main as optimizer_main
optimizer_main()
```

## Weather Data Integrator Tool

### File: `team_weather_data_integrator_history.py`
**Purpose**: Integrate historical weather data with football match information for enhanced prediction features.

### Key Features
- **Historical Weather Retrieval**: Download weather data for match dates and locations
- **Match-Weather Correlation**: Link weather conditions to match outcomes
- **Coverage Statistics**: Track data completeness and quality
- **Batch Processing**: Efficient processing of large datasets
- **Interactive Menu System**: User-friendly interface for data operations

### Main Functions

#### `interactive_menu()`
**Purpose**: Main interface for weather data operations
**Options**:
- Historical data integration
- Coverage analysis
- Data quality checks
- Batch processing setup

#### `integrate_weather_data()`
**Purpose**: Core weather data integration function
**Process**:
1. Retrieve match data from database
2. Lookup historical weather for match dates/locations
3. Correlate weather conditions with match outcomes
4. Store enhanced data for model training

#### `analyze_weather_coverage()`
**Purpose**: Analyze completeness and quality of weather data
**Metrics**:
- Coverage percentage by league and season
- Data quality indicators
- Missing data patterns
- Weather source reliability

#### `batch_process_seasons()`
**Purpose**: Process multiple seasons of weather data efficiently
**Features**:
- Parallel processing support
- Progress tracking
- Error recovery
- Memory optimization

### Weather Features Integrated
- **Temperature**: Match day temperature conditions
- **Precipitation**: Rain, snow, and humidity data  
- **Wind**: Wind speed and direction
- **Visibility**: Weather visibility conditions
- **Pressure**: Atmospheric pressure readings

## Model Performance Evaluator

### File: `model_performance_evaluator.py`
**Purpose**: Standalone model evaluation system with comprehensive metrics and reporting.

### Key Features
- **Multi-Model Evaluation**: Test all models simultaneously
- **Custom Metrics**: Define and calculate custom performance metrics
- **Report Generation**: Automated performance reports
- **Comparison Framework**: Side-by-side model comparison
- **Historical Tracking**: Track performance over time

### Evaluation Metrics
- **Accuracy Metrics**: Precision, recall, F1-score, accuracy
- **Probabilistic Metrics**: AUC-ROC, log loss, calibration
- **Business Metrics**: ROI, profit/loss, bet success rate
- **Robustness Metrics**: Stability across different data splits

## Hyperparameter Analyzer

### File: `hyperparameters_analyzer.py`
**Purpose**: Analyze and visualize hyperparameter optimization results.

### Key Features
- **Optimization History**: Track parameter changes over time
- **Performance Visualization**: Plot performance vs. parameters
- **Sensitivity Analysis**: Identify most important parameters
- **Interaction Effects**: Analyze parameter interactions
- **Convergence Analysis**: Study optimization convergence patterns

## Geographic and Visualization Tools

### Team Location Scraper (`team_location_scraper.py`)
**Purpose**: Collect geographic data for football teams
**Features**:
- Stadium location coordinates
- Team geographic information  
- Distance calculations between venues
- Geographic clustering analysis

### Map Generator Tools
**Files**: `team_map_generator.py`, `team_map_with_tables_generator.py`
**Purpose**: Create interactive maps with team and performance data
**Features**:
- Interactive HTML maps
- Performance overlay data
- Statistical information display
- Geographic analysis visualization

### Database Utility (`load_teams_to_db.py`)
**Purpose**: Database utility for team data management
**Features**:
- Team data loading and updating
- Database schema management
- Data consistency checks
- Bulk operation support

## Tool Integration with CLI

### Interactive Mode Integration
All tools are designed to integrate seamlessly with the main CLI system:

```python
# CLI Integration Pattern
def launch_tool():
    tools_path = os.path.join(src_path, 'tools')
    if tools_path not in sys.path:
        sys.path.insert(0, tools_path)
    
    from tools.tool_name import main as tool_main
    tool_main()
```

### Command Line Access
Tools support both interactive and direct command-line access:

```bash
# Direct tool execution
python src/tools/models_prediction_analysis.py --interactive
python src/tools/hyperparameters_optimizer.py --help

# CLI integration
clipokopred  # Then select tool from menu
```

## Configuration and Setup

### Tool Configuration
Tools use shared configuration from main `config.json`:
- Database connection settings
- File paths and directories
- Model parameters and settings
- Logging configuration

### Dependencies
Common dependencies across tools:
- Database connectivity (psycopg2)
- Data processing (pandas, numpy)
- Machine learning (scikit-learn, xgboost)
- Visualization (matplotlib, plotly)
- Web scraping (requests, beautifulsoup4)

## Error Handling and Logging

### Centralized Error Handling
- Integration with main logging system
- Tool-specific error categorization
- User-friendly error messages
- Recovery and retry mechanisms

### Progress Tracking
- Long operation progress indicators
- Batch processing status
- Performance monitoring
- Resource usage tracking

## Best Practices for Tool Usage

### Performance Optimization
1. **Batch Operations**: Use batch processing for large datasets
2. **Resource Management**: Monitor memory and CPU usage
3. **Database Efficiency**: Use efficient queries and connection pooling
4. **Caching**: Cache intermediate results where appropriate

### Analysis Workflow
1. **Data Quality**: Always verify data quality before analysis
2. **Baseline Establishment**: Establish performance baselines
3. **Iterative Improvement**: Use tools iteratively for continuous improvement
4. **Documentation**: Document analysis results and insights

### Integration Guidelines
1. **CLI Integration**: Follow established patterns for CLI integration
2. **Configuration Consistency**: Use shared configuration systems
3. **Logging Standards**: Follow centralized logging practices
4. **Error Handling**: Implement robust error handling and recovery

## Future Development

### Planned Enhancements
- **Real-time Analysis**: Live model performance monitoring
- **Advanced Visualizations**: Interactive dashboards and reports
- **Machine Learning Pipelines**: Automated ML pipeline tools
- **API Integration**: External data source integration tools
- **Cloud Integration**: Cloud-based analysis and processing tools

### Extension Framework
Tools are designed for easy extension and customization:
- Modular architecture for adding new analysis types
- Plugin system for custom metrics and evaluations
- Template system for creating new tools
- Integration APIs for external tool development