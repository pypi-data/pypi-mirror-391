import numpy as np
from sklearn.base import BaseEstimator, TransformerMixin


class RelationalFeaturesTransformer(BaseEstimator, TransformerMixin):
    """
    Vectorized range-aware relational neighbor transformer.

    For each row, for each feature, computes:
    - First and last indices of the next larger (or smaller) features
    - Distance to the first neighbor only (avoids redundancy)
    """

    def __init__(self, direction='larger', include_distance=True, include_index=True):
        self.direction = direction
        self.include_distance = include_distance
        self.include_index = include_index

    def fit(self, X, y=None):
        X = self._validate_data(X, dtype=np.float64, force_all_finite=True)
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
            diff = -diff  # distances for smaller

        # Set invalid entries to inf
        diff_masked = np.where(mask, diff, np.inf)

        # First index (next neighbor)
        first_idx = np.argmin(diff_masked, axis=2)
        first_val = np.take_along_axis(X, first_idx, axis=1)

        # Last index (range neighbor)
        reversed_order = np.arange(n_features)[::-1]
        X_rev = X[:, reversed_order]
        diff_rev = X_rev[:, None, :] - X_rev[:, :, None]
        if self.direction == 'larger':
            mask_rev = diff_rev >= 0
        else:
            mask_rev = diff_rev <= 0
            diff_rev = -diff_rev

        diff_rev_masked = np.where(mask_rev, diff_rev, np.inf)
        last_idx_rev = np.argmin(diff_rev_masked, axis=2)
        last_idx = reversed_order[last_idx_rev]

        # Distance only to first neighbor
        dist_first = np.where(first_idx != -1, first_val - X, np.nan)

        # Concatenate outputs
        if self.include_index:
            results.append(first_idx.astype(float))
            results.append(last_idx.astype(float))
        if self.include_distance:
            results.append(dist_first)

        return np.concatenate(results, axis=1)


if __name__ == '__main__':
    import numpy as np

    # Example data: rows with obvious next-larger neighbors
    X = np.array([
        [2, 5, 5, 8],
        [4, 2, 6, 1]
    ])

    rnt = RelationalFeaturesTransformer(direction='larger', include_distance=True, include_index=True)
    X_transformed = rnt.fit_transform(X)

    print("Original X:\n", X)
    print("\nTransformed X (first row breakdown):")
    n_features = X.shape[1]

    # Slice outputs for clarity
    original = X_transformed[:, :n_features]
    first_idx = X_transformed[:, n_features:n_features * 2].astype(int)
    last_idx = X_transformed[:, n_features * 2:n_features * 3].astype(int)
    dist_first = X_transformed[:, n_features * 3:n_features * 4]

    print("Original features:\n", original)
    print("First neighbor indices:\n", first_idx)
    print("Last neighbor indices:\n", last_idx)
    print("Distance to first neighbor:\n", dist_first)
