# Data Models Documentation

## Overview
The `data_models.py` module contains the machine learning model implementations for the POKOPRED football prediction system. It provides a comprehensive suite of models including Random Forest, Neural Networks, XGBoost, Logistic Regression, and advanced ensemble methods for accurate match outcome predictions.

## Module Architecture

```
data_models.py
├── PokoPred (Base Class)
├── RandomForestModel
├── LogisticRegressionModel
├── NeuralNetworkModel
├── XGBoostModel
├── EnsembleModel
└── EnsembleDrawAnalyzer
```

## Base Class: PokoPred

### Purpose
Abstract base class providing common functionality for all prediction models, including data loading, preprocessing, and evaluation methods.

### Key Attributes
- `model`: The trained model instance
- `model_name`: String identifier for the model type
- `X_train`, `X_test`: Training and testing feature matrices
- `y_train`, `y_test`: Training and testing target vectors
- `predictions`: Model predictions on test data
- `probabilities`: Prediction probabilities (for classification)

### Core Methods

#### `load_data()`
**Purpose**: Load and prepare training/testing datasets from the database
**Process**:
1. Connects to PostgreSQL database
2. Loads processed model data
3. Splits features and target variables
4. Performs train/test split
**Returns**: Prepared datasets for model training

#### `preprocess_data(X_train, X_test)`
**Purpose**: Standardize and normalize feature data
**Parameters**:
- `X_train`: Training feature matrix
- `X_test`: Testing feature matrix
**Process**:
1. Applies StandardScaler normalization
2. Handles missing values
3. Ensures consistent feature scaling
**Returns**: Preprocessed training and testing data

#### `evaluate_model()`
**Purpose**: Comprehensive model evaluation and performance metrics
**Metrics Calculated**:
- Accuracy score
- Classification report (precision, recall, F1-score)
- Confusion matrix
- ROC-AUC score
- Cross-validation scores
**Output**: Detailed performance analysis

#### `save_model(filename=None)`
**Purpose**: Persist trained model to disk using joblib
**Parameters**:
- `filename` (optional): Custom filename for saved model
**Default Location**: `models/{model_name}_model.pkl`

#### `load_model(filename=None)`
**Purpose**: Load previously trained model from disk
**Parameters**:
- `filename` (optional): Path to model file
**Returns**: Loaded model instance

## Model Implementations

### RandomForestModel

**Purpose**: Ensemble tree-based classifier for robust predictions
**Algorithm**: Random Forest with multiple decision trees

#### Key Parameters
- `n_estimators`: 100 (number of trees)
- `random_state`: 42 (reproducibility)
- `max_depth`: None (unlimited tree depth)
- `min_samples_split`: 2
- `min_samples_leaf`: 1

#### Methods

##### `train_model()`
**Purpose**: Train Random Forest classifier
**Process**:
1. Loads and preprocesses data
2. Initializes RandomForestClassifier
3. Fits model on training data
4. Generates predictions and probabilities
**Features**: Feature importance calculation, OOB scoring

##### `test_model()`
**Purpose**: Comprehensive model testing and validation
**Process**:
1. Loads test data
2. Generates predictions
3. Calculates performance metrics
4. Creates visualizations
**Output**: Test accuracy, classification report, confusion matrix

##### `predict_next_games()`
**Purpose**: Generate predictions for upcoming matches
**Process**:
1. Loads next games data from database
2. Applies same preprocessing as training
3. Generates match outcome predictions
4. Calculates prediction probabilities
**Output**: Match predictions with confidence scores

### LogisticRegressionModel

**Purpose**: Linear classification model with probabilistic outputs
**Algorithm**: Logistic Regression with regularization

#### Key Parameters
- `random_state`: 42
- `max_iter`: 1000 (convergence iterations)
- `solver`: 'liblinear' (optimization algorithm)
- `penalty`: 'l2' (L2 regularization)

#### Methods

##### `train_model()`
**Purpose**: Train logistic regression classifier
**Process**:
1. Data loading and preprocessing
2. Model initialization with parameters
3. Model fitting on scaled features
4. Coefficient analysis
**Features**: Feature coefficient interpretation, regularization

##### `test_model()`
**Purpose**: Model evaluation and testing
**Output**: Accuracy metrics, probability calibration analysis

##### `predict_next_games()`
**Purpose**: Probabilistic match predictions
**Features**: Well-calibrated probability estimates, interpretable coefficients

### NeuralNetworkModel

**Purpose**: Multi-layer perceptron for complex pattern recognition
**Algorithm**: MLPClassifier with backpropagation

#### Key Parameters
- `hidden_layer_sizes`: (100, 50) (two hidden layers)
- `activation`: 'relu' (ReLU activation function)
- `solver`: 'adam' (adaptive moment estimation)
- `alpha`: 0.0001 (L2 regularization)
- `learning_rate`: 'constant'
- `max_iter`: 500

#### Methods

##### `train_model()`
**Purpose**: Train neural network model
**Process**:
1. Data preparation and scaling
2. Network architecture setup
3. Backpropagation training
4. Convergence monitoring
**Features**: Early stopping, learning curve analysis

##### `test_model()`
**Purpose**: Neural network evaluation
**Analysis**: Loss curves, activation patterns, layer weights

##### `predict_next_games()`
**Purpose**: Deep learning predictions for matches
**Features**: Non-linear pattern recognition, complex feature interactions

### XGBoostModel

**Purpose**: Gradient boosting for high-performance predictions
**Algorithm**: XGBoost with tree-based learners

#### Key Parameters
- `n_estimators`: 100
- `learning_rate`: 0.1
- `max_depth`: 6
- `subsample`: 0.8
- `colsample_bytree`: 0.8
- `random_state`: 42

#### Methods

##### `train_model()`
**Purpose**: Train XGBoost classifier
**Process**:
1. Data preparation for XGBoost format
2. Model training with boosting
3. Feature importance calculation
4. Model validation
**Features**: Advanced boosting, feature importance, early stopping

##### `test_model()`
**Purpose**: XGBoost model evaluation
**Analysis**: Boosting performance, feature contribution, overfitting checks

##### `predict_next_games()`
**Purpose**: Gradient-boosted predictions
**Features**: High accuracy, robust to overfitting, feature importance insights

### EnsembleModel

**Purpose**: Combine multiple models for improved predictions
**Algorithm**: Voting classifier with multiple base estimators

#### Base Models
- Random Forest
- Logistic Regression
- Neural Network
- XGBoost

#### Methods

##### `train_model()`
**Purpose**: Train ensemble of models
**Process**:
1. Initialize all base models
2. Train each model individually
3. Combine using voting strategy
4. Validate ensemble performance
**Voting Types**: Hard voting (majority), Soft voting (probability averaging)

##### `test_model()`
**Purpose**: Ensemble evaluation
**Analysis**: Individual model performance, ensemble improvement, diversity metrics

##### `predict_next_games()`
**Purpose**: Ensemble predictions for matches
**Features**: Improved robustness, reduced overfitting, higher accuracy

## Advanced Analysis: EnsembleDrawAnalyzer

### Purpose
Specialized analyzer for draw prediction and ensemble model evaluation with focus on betting strategy optimization.

### Key Methods

#### `__init__()`
**Purpose**: Initialize analyzer with database connection and evaluation framework
**Features**:
- Database connectivity
- Evaluation metric setup
- Result storage preparation

#### `analyze_ensemble_performance()`
**Purpose**: Comprehensive ensemble model analysis
**Analysis Types**:
- Individual model performance
- Ensemble combination strategies
- Draw prediction accuracy
- ROI and betting performance
**Output**: Detailed performance reports, comparison matrices

#### `evaluate_draw_predictions()`
**Purpose**: Specialized draw outcome evaluation
**Metrics**:
- Draw prediction accuracy
- Draw probability calibration
- False positive/negative rates for draws
- Betting ROI for draw strategies
**Features**: Draw-specific threshold optimization

#### `generate_betting_insights()`
**Purpose**: Convert predictions into actionable betting insights
**Analysis**:
- Optimal betting thresholds
- Risk-adjusted returns
- Bankroll management strategies
- Market efficiency analysis
**Output**: Betting recommendations with confidence intervals

## Data Flow and Integration

### Database Integration
- PostgreSQL connectivity for data loading
- Prepared statement usage for security
- Connection pooling for performance
- Transaction management for data consistency

### Feature Pipeline
1. **Raw Data**: Match results and team statistics
2. **Feature Engineering**: Advanced metrics calculation
3. **Preprocessing**: Scaling and normalization
4. **Model Training**: Individual model training
5. **Ensemble Creation**: Model combination
6. **Prediction Generation**: Next game predictions

### Model Persistence
- Joblib serialization for model storage
- Version control for model artifacts
- Model metadata tracking
- Performance history maintenance

## Performance Optimization

### Training Optimization
- Parallel processing for ensemble models
- Memory-efficient data loading
- GPU acceleration (where applicable)
- Hyperparameter caching

### Prediction Optimization
- Batch prediction processing
- Model result caching
- Efficient probability calculations
- Streamlined feature preprocessing

## Error Handling and Validation

### Model Validation
- Cross-validation scoring
- Overfitting detection
- Convergence monitoring
- Performance regression checks

### Error Management
- Try-catch blocks for model operations
- Graceful handling of data issues
- Logging of training problems
- Model fallback strategies

## Logging and Monitoring

### Training Logs
- Model training progress
- Performance metrics tracking
- Error documentation
- Feature importance logging

### Prediction Logs
- Prediction confidence scores
- Model selection decisions
- Performance monitoring
- Accuracy tracking over time

## Usage Examples

### Individual Model Training
```python
# Random Forest Example
rf_model = RandomForestModel()
rf_model.train_model()
rf_model.test_model()
predictions = rf_model.predict_next_games()
```

### Ensemble Model Training
```python
# Ensemble Example
ensemble = EnsembleModel()
ensemble.train_model()
ensemble_predictions = ensemble.predict_next_games()
```

### Draw Analysis
```python
# Draw Analysis Example
analyzer = EnsembleDrawAnalyzer()
performance = analyzer.analyze_ensemble_performance()
draw_insights = analyzer.evaluate_draw_predictions()
```

## Best Practices

### Model Development
- Regular model retraining
- Performance monitoring
- Feature engineering iteration
- Hyperparameter optimization

### Production Usage
- Model versioning
- A/B testing for improvements
- Performance degradation detection
- Automated retraining triggers

### Evaluation Standards
- Multiple evaluation metrics
- Out-of-sample testing
- Cross-validation consistency
- Business metric alignment (ROI, accuracy)