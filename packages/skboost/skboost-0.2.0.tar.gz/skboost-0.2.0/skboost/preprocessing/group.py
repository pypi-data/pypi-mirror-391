import pandas as pd
import numpy as np
from sklearn.base import BaseEstimator, TransformerMixin


from sklearn.base import BaseEstimator, TransformerMixin


class GroupValueCountsTransformer(BaseEstimator, TransformerMixin):
    """
    Adds value count features within groups.

    For each group, computes:
    - Raw count of how often each value appears
    - Normalized count (count / max count in group)
    """

    def __init__(self, group_col, value_col, prefix=None):
        self.group_col = group_col
        self.value_col = value_col
        self.prefix = prefix

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        X = pd.DataFrame(X).copy()
        prefix = self.prefix or f"{self.group_col}_{self.value_col}"

        counts = X.groupby(self.group_col)[self.value_col].transform(
            lambda x: x.map(x.value_counts())
        )
        max_counts = X.groupby(self.group_col)[self.value_col].transform(
            lambda x: x.value_counts().max()
        )

        X[f"{prefix}_counts"] = counts
        X[f"{prefix}_norm"] = counts / max_counts

        return X


class GroupDiffTransformer(BaseEstimator, TransformerMixin):
    """
    Adds difference/equality features per group key:
      - Difference from previous row with same key
      - Difference from first row with same key
    For numeric cols: subtract values.
    For categorical cols: equality indicators (1 if equal, else 0).
    First rows per group get 0 for numeric diffs, 1 for equality flags.
    """

    def __init__(self, key_col, numeric_cols=None, categorical_cols=None,
                 add_prev=True, add_first=True):
        self.key_col = key_col
        self.numeric_cols = numeric_cols
        self.categorical_cols = categorical_cols
        self.add_prev = add_prev
        self.add_first = add_first

    def fit(self, X, y=None):
        return self  # stateless transformer

    def transform(self, X):
        X = pd.DataFrame(X).copy()

        if self.numeric_cols is None:
            self.numeric_cols = X.select_dtypes(include=[np.number]).columns.tolist()
            if self.key_col in self.numeric_cols:
                self.numeric_cols.remove(self.key_col)

        if self.categorical_cols is None:
            self.categorical_cols = X.select_dtypes(exclude=[np.number]).columns.tolist()

        X_aug = X.copy()
        grouped = X.groupby(self.key_col, sort=False)

        # === Numeric differences ===
        if self.add_prev:
            prev_num = grouped[self.numeric_cols].shift(1)
            diff_prev = (X[self.numeric_cols] - prev_num).fillna(0)
            diff_prev.columns = [f"{c}_diff_prev" for c in self.numeric_cols]
            X_aug = pd.concat([X_aug, diff_prev], axis=1)

        if self.add_first:
            first_num = grouped[self.numeric_cols].transform('first')
            diff_first = (X[self.numeric_cols] - first_num).fillna(0)
            diff_first.columns = [f"{c}_diff_first" for c in self.numeric_cols]
            X_aug = pd.concat([X_aug, diff_first], axis=1)

        # === Categorical equality flags ===
        if len(self.categorical_cols) > 0:
            if self.add_prev:
                prev_cat = grouped[self.categorical_cols].shift(1)
                eq_prev = (X[self.categorical_cols] == prev_cat).astype(float)
                eq_prev = eq_prev.fillna(1.0)  # first rows: treat as equal to themselves
                eq_prev.columns = [f"{c}_eq_prev" for c in self.categorical_cols]
                X_aug = pd.concat([X_aug, eq_prev], axis=1)

            if self.add_first:
                first_cat = grouped[self.categorical_cols].transform('first')
                eq_first = (X[self.categorical_cols] == first_cat).astype(float)
                eq_first = eq_first.fillna(1.0)
                eq_first.columns = [f"{c}_eq_first" for c in self.categorical_cols]
                X_aug = pd.concat([X_aug, eq_first], axis=1)

        return X_aug

