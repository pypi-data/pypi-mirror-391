import numpy as np
from sklearn.base import BaseEstimator, TransformerMixin


class RelationalFeaturesTransformer(BaseEstimator, TransformerMixin):
    """
    Vectorized range-aware relational neighbor transformer.

    For each row, for each feature, computes:
    - First and last indices of other features with same or larger (or smaller) values
    - Distance to the first neighbor only (avoids redundancy)
    - Excludes self-comparisons
    """

    def __init__(self, direction='larger', include_distance=True, include_index=True):
        self.direction = direction
        self.include_distance = include_distance
        self.include_index = include_index

    def fit(self, X, y=None):
        X = np.asarray(X, dtype=float)
        self.n_features_in_ = X.shape[1]
        return self

    def transform(self, X):
        X = np.asarray(X, dtype=float)
        n_samples, n_features = X.shape
        results = [X]

        # Broadcasted difference matrix: diff[i,j,k] = X[i,k] - X[i,j]
        diff = X[:, None, :] - X[:, :, None]  # shape: (n_samples, n_features, n_features)

        if self.direction == 'larger':
            mask = diff >= 0
        else:
            mask = diff <= 0
            diff = np.abs(diff)

        # Exclude self-comparisons (set diagonal to False)
        for i in range(n_features):
            mask[:, i, i] = False

        # Set invalid entries to inf
        diff_masked = np.where(mask, diff, np.inf)

        # First index (minimum index with valid neighbor)
        first_idx = np.argmin(diff_masked, axis=2)

        # Mark as -1 where no valid neighbor exists (all were inf)
        no_neighbor = np.all(diff_masked == np.inf, axis=2)
        first_idx = np.where(no_neighbor, -1, first_idx)

        # Get first neighbor values
        first_val = np.where(
            first_idx >= 0,
            np.take_along_axis(X, np.maximum(first_idx, 0), axis=1),
            np.nan
        )

        # Last index (maximum index with valid neighbor)
        # Find all valid indices, take the max
        last_idx = np.full((n_samples, n_features), -1, dtype=int)
        for i in range(n_samples):
            for j in range(n_features):
                valid_indices = np.where(mask[i, j, :])[0]
                if len(valid_indices) > 0:
                    last_idx[i, j] = valid_indices[-1]

        # Distance to first neighbor
        dist_first = np.where(first_idx >= 0, first_val - X, np.nan)

        # Concatenate outputs
        if self.include_index:
            results.append(first_idx.astype(float))
            results.append(last_idx.astype(float))
        if self.include_distance:
            results.append(dist_first)

        return np.concatenate(results, axis=1)