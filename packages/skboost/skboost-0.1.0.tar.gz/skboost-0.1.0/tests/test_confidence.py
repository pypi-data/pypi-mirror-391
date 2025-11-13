from sklearn.datasets import make_classification
from sklearn.ensemble import RandomForestClassifier
from skboost.evaluation import confidence_report, plot_confidence_report


def test_confidence_report_output():
    X, y = make_classification(n_samples=50, n_features=5, n_classes=3, n_informative=3, random_state=42)
    clf = RandomForestClassifier(random_state=42)
    clf.fit(X, y)
    y_proba = clf.predict_proba(X)
    reports = confidence_report(y, y_proba, thresholds=[0.5,0.7])
    assert isinstance(reports, dict)
    for class_name, class_dict in reports.items():
        for thr, df in class_dict.items():
            assert df.shape[0] == 1
            assert 'precision' in df.columns

def test_plot_runs():
    X, y = make_classification(n_samples=50, n_features=5, n_classes=3, n_informative=3, random_state=42)
    clf = RandomForestClassifier(random_state=42)
    clf.fit(X, y)
    y_proba = clf.predict_proba(X)
    reports = confidence_report(y, y_proba, thresholds=[0.5,0.7])
    # Should not raise errors
    plot_confidence_report(reports)
