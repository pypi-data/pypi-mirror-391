import numpy as np
from skboost.preprocessing import RelationalFeaturesTransformer


def test_relational_neighbor_transformer():
    X = np.array([
        [2, 5, 5, 8],
        [4, 2, 6, 1]
    ])

    rnt = RelationalFeaturesTransformer(direction='larger', include_distance=True, include_index=True)
    X_transformed = rnt.fit_transform(X)

    n_features = X.shape[1]

    # Slice outputs
    original = X_transformed[:, :n_features]
    first_idx = X_transformed[:, n_features:n_features*2].astype(int)
    last_idx  = X_transformed[:, n_features*2:n_features*3].astype(int)
    dist_first = X_transformed[:, n_features*3:n_features*4]

    # Check original features unchanged
    np.testing.assert_array_equal(original, X)

    # Check first neighbor indices
    expected_first_idx = np.array([
        [1, 3, 3, -1],  # Row 0
        [2, 2, -1, -1]  # Row 1
    ])
    np.testing.assert_array_equal(first_idx, expected_first_idx)

    # Check last neighbor indices
    expected_last_idx = np.array([
        [2, 3, 3, -1],  # Row 0
        [2, 2, -1, -1]  # Row 1
    ])
    np.testing.assert_array_equal(last_idx, expected_last_idx)

    # Check distances to first neighbor
    expected_dist_first = np.array([
        [3, 3, 3, np.nan],
        [2, 4, np.nan, np.nan]
    ])
    np.testing.assert_array_equal(dist_first, expected_dist_first)

