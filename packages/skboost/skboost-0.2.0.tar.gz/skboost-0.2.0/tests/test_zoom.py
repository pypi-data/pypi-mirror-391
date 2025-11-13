from sklearn.datasets import make_classification
from sklearn.ensemble import RandomForestClassifier
from skboost.tuning import zoom_search_cv

def test_numeric_zoom():
    X, y = make_classification(n_samples=50, n_features=5, n_classes=2, random_state=42)
    param_grid = {'n_estimators':[10,20,30], 'max_depth':[2,4,6]}
    clf = RandomForestClassifier(random_state=42)
    best_params, best_score = zoom_search_cv(clf, X, y, param_grid, n_iter=2, verbose=False)
    assert isinstance(best_params, dict)
    assert isinstance(best_score, float)

def test_categorical_zoom():
    X, y = make_classification(n_samples=50, n_features=5, n_classes=2, random_state=42)
    param_grid = {
        'n_estimators':[10,20,30],
        'criterion':['gini','entropy']
    }
    param_types = {'n_estimators':'numeric','criterion':'categorical'}
    clf = RandomForestClassifier(random_state=42)
    best_params, best_score = zoom_search_cv(clf, X, y, param_grid, param_types=param_types, n_iter=2, verbose=False)
    assert best_params['criterion'] in ['gini','entropy']
