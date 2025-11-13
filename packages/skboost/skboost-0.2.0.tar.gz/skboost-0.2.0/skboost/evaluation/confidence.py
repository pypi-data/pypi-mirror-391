import numpy as np
import pandas as pd
from sklearn.metrics import classification_report

def confidence_report(y_true, y_proba, thresholds=(0.5, 0.7, 0.9), target_names=None):
    """
    Produces classification reports stratified by prediction confidence for each class.

    Parameters
    ----------
    y_true : array-like, shape (n_samples,)
        True class labels.
    y_proba : array-like, shape (n_samples, n_classes)
        Predicted probabilities from classifier.
    thresholds : list of floats
        Confidence thresholds. For each threshold, only predictions with probability >= threshold are included.
    target_names : list of str, optional
        Names of the classes.

    Returns
    -------
    dict
        Nested dictionary: {class_label: {threshold: classification_report_df}}
    """
    y_true = np.asarray(y_true)
    y_proba = np.asarray(y_proba)
    n_classes = y_proba.shape[1]

    if target_names is None:
        target_names = [str(c) for c in range(n_classes)]

    reports = {}

    # Loop over each class
    for class_idx, class_name in enumerate(target_names):
        class_reports = {}
        # Predictions where class probability >= threshold
        for thr in thresholds:
            mask = y_proba[:, class_idx] >= thr
            if mask.sum() == 0:
                # No samples meet threshold
                class_reports[thr] = pd.DataFrame(
                    {"precision": [np.nan], "recall": [np.nan], "f1-score": [np.nan], "support": [0]},
                    index=[class_name]
                )
                continue

            y_true_sub = y_true[mask]
            y_pred_sub = np.argmax(y_proba[mask], axis=1)
            cr = classification_report(
                y_true_sub, y_pred_sub, labels=[class_idx], target_names=[class_name], output_dict=True
            )
            class_reports[thr] = pd.DataFrame(cr).transpose().loc[[class_name]]
        reports[class_name] = class_reports

    return reports


import matplotlib.pyplot as plt

def plot_confidence_report(reports, metrics=('precision', 'recall', 'f1-score'), fig_size=(10, 6)):
    """
    Plot metrics vs. confidence threshold for each class from confidence_report output.

    Parameters
    ----------
    reports : dict
        Output from confidence_report()
    metrics : list of str
        Metrics to plot, e.g. ['precision','recall','f1-score']
    fig_size : tuple
        Figure size
    """
    n_classes = len(reports)
    fig, axes = plt.subplots(1, n_classes, figsize=(fig_size[0] * n_classes, fig_size[1]), squeeze=False)

    for idx, (class_name, class_dict) in enumerate(reports.items()):
        ax = axes[0, idx]
        thresholds = []
        data = {m: [] for m in metrics}

        for thr, df in class_dict.items():
            thresholds.append(thr)
            for m in metrics:
                data[m].append(df[m].values[0])

        for m in metrics:
            ax.plot(thresholds, data[m], marker='o', label=m)

        ax.set_title(f'Class {class_name}')
        ax.set_xlabel('Confidence threshold')
        ax.set_ylabel('Metric')
        ax.set_ylim(0,1)
        ax.grid(True)
        ax.legend()

    plt.tight_layout()
    plt.show()


if __name__ == '__main__':
    from sklearn.datasets import make_classification
    from sklearn.ensemble import RandomForestClassifier

    X, y = make_classification(n_samples=500, n_classes=3, n_informative=4, random_state=42)
    clf = RandomForestClassifier(n_estimators=50, random_state=42)
    clf.fit(X, y)
    y_proba = clf.predict_proba(X)

    # Compute confidence reports for thresholds 0.5, 0.7, 0.9
    c_reports = confidence_report(y, y_proba, thresholds=[0.5, 0.7, 0.9], target_names=['class0', 'class1', 'class2'])

    # Print reports
    for class_name, class_dict in c_reports.items():
        print(f"\nClass: {class_name}")
        for thr, df in class_dict.items():
            print(f"\nThreshold >= {thr}")
            print(df)

    plot_confidence_report(c_reports)
