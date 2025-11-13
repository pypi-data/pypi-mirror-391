# dual_scaler.py
import pandas as pd
import numpy as np
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.preprocessing import StandardScaler

class DualScalerTransformer(BaseEstimator, TransformerMixin):
    """
    Transformer that applies separate scalers to different sets of numeric features,
    e.g., relative vs absolute columns. If numeric_cols is None, it infers all numeric columns.
    """

    def __init__(self, numeric_cols=None):
        """
        numeric_cols : list of column names to scale; if None, infer all numeric columns
        """
        self.numeric_cols = numeric_cols
        self.scalers_ = {}

    def fit(self, X, y=None):
        """
        Fit separate scalers for different groups of features
        """
        X = X.copy()

        # Infer numeric columns if not provided
        if self.numeric_cols is None:
            self.numeric_cols = X.select_dtypes(include=[np.number]).columns.tolist()

        # Example split: relative (_rel) vs absolute
        rel_cols = [c for c in self.numeric_cols if "_rel" in c]
        abs_cols = [c for c in self.numeric_cols if "_rel" not in c]

        if rel_cols:
            scaler_rel = StandardScaler()
            scaler_rel.fit(X[rel_cols])
            self.scalers_['rel'] = scaler_rel

        if abs_cols:
            scaler_abs = StandardScaler()
            scaler_abs.fit(X[abs_cols])
            self.scalers_['abs'] = scaler_abs

        return self

    def transform(self, X):
        """
        Transform X using the fitted scalers
        """
        X = X.copy()
        scaled_dfs = []

        if 'rel' in self.scalers_:
            rel_cols = [c for c in self.numeric_cols if "_rel" in c]
            scaled_rel = self.scalers_['rel'].transform(X[rel_cols])
            df_rel = pd.DataFrame(scaled_rel, columns=rel_cols, index=X.index)
            scaled_dfs.append(df_rel)

        if 'abs' in self.scalers_:
            abs_cols = [c for c in self.numeric_cols if "_rel" not in c]
            scaled_abs = self.scalers_['abs'].transform(X[abs_cols])
            df_abs = pd.DataFrame(scaled_abs, columns=abs_cols, index=X.index)
            scaled_dfs.append(df_abs)

        # Concatenate back
        X_scaled = pd.concat(scaled_dfs, axis=1)
        return X_scaled

