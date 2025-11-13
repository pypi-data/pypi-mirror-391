# skboost

**skboost** is a lightweight Python library designed to **boost your models** — whether trees, linear models, neural networks, or anything else. It provides relational feature engineering, adaptive hyperparameter search, and confidence-aware evaluation tools that enhance model performance and interpretability.

## Installation

```bash
pip install skboost
```

## Features

### Preprocessing

**RelationalFeaturesTransformer** - Boost model performance with compact relational features
```python
from skboost.preprocessing import RelationalFeaturesTransformer

transformer = RelationalFeaturesTransformer(direction='larger')
X_transformed = transformer.fit_transform(X)
# For each feature, finds indices and distances to next larger/smaller values
# Adds O(N) features instead of O(N²) pairwise combinations
# Helps models learn inter-feature relationships
# Useful for: computer vision, ranking tasks, any data with meaningful ordering
```

**DualScalerTransformer** - Boost classification with class-specific scaling
```python
from skboost.preprocessing import DualScalerTransformer

transformer = DualScalerTransformer()
X_scaled = transformer.fit_transform(X)
# Scales features separately for different target classes
# Useful for: imbalanced datasets, multi-class problems with different distributions
```

### Hyperparameter Tuning

**zoom_search_cv** - Boost efficiency with adaptive hyperparameter search
```python
from skboost.tuning import zoom_search_cv

best_params, best_score = zoom_search_cv(
    estimator, X, y,
    param_grid={'n_estimators': [50, 100, 150], 'max_depth': [3, 6, 9]},
    n_iter=3, cv=5
)
# Starts with 3 values per parameter, iteratively zooms around best region
# Works for both numeric and categorical hyperparameters
# Useful for: faster optimization than exhaustive grid search
```

### Model Evaluation

**confidence_report** - Boost reliability with confidence-aware evaluation
```python
from skboost.evaluation import confidence_report, plot_confidence_report

reports = confidence_report(y_true, y_proba, thresholds=[0.5, 0.7, 0.9])
plot_confidence_report(reports)
# Shows precision/recall/f1 at different confidence thresholds per class
# Visualize which predictions your model is reliable on
# Useful for: production deployment decisions, finding usable subsets, model monitoring
```

### Additional Tools

**GroupDiffTransformer** - Sequential feature engineering within groups
```python
from skboost.preprocessing import GroupDiffTransformer

transformer = GroupDiffTransformer(key_col='user_id')
X_transformed = transformer.fit_transform(X)
# Adds: difference from previous row, difference from first row per group
```

**GroupValueCountsTransformer** - Value frequency features within groups
```python
from skboost.preprocessing import GroupValueCountsTransformer

transformer = GroupValueCountsTransformer(group_col='session_id', value_col='action')
X_transformed = transformer.fit_transform(X)
# Adds: raw counts and normalized counts per group
```

## Quick Example

```python
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.datasets import make_classification
from skboost.preprocessing import RelationalFeaturesTransformer
from skboost.tuning import zoom_search_cv
from skboost.evaluation import confidence_report, plot_confidence_report

# Generate data
X, y = make_classification(n_samples=500, n_classes=3, n_informative=5, random_state=42)

# Add relational features
transformer = RelationalFeaturesTransformer(direction='larger')
X_boosted = transformer.fit_transform(X)

# Adaptive hyperparameter search
param_grid = {'n_estimators': [50, 100, 150], 'max_depth': [3, 6, 9]}
clf = RandomForestClassifier(random_state=42)
best_params, best_score = zoom_search_cv(clf, X_boosted, y, param_grid, n_iter=3)

# Train with best params and evaluate confidence
clf.set_params(**best_params)
clf.fit(X_boosted, y)
y_proba = clf.predict_proba(X_boosted)

# Confidence-stratified evaluation
reports = confidence_report(y, y_proba, thresholds=[0.5, 0.7, 0.9])
plot_confidence_report(reports)
```

## Testing
```bash
pytest tests/
```

See `tests/` directory for usage examples in test form.

## License

MIT
