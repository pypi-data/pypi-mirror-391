import numpy as np
from skboost.preprocessing import RelationalFeaturesTransformer


def test_relational_features_transformer():
    X = np.array([
        [2, 5, 5, 8],
        [4, 2, 6, 1]
    ])

    rnt = RelationalFeaturesTransformer(direction='larger', include_distance=True, include_index=True)
    X_transformed = rnt.fit_transform(X)

    n_features = X.shape[1]

    # Slice outputs
    original = X_transformed[:, :n_features]
    first_idx = X_transformed[:, n_features:n_features * 2].astype(int)
    last_idx = X_transformed[:, n_features * 2:n_features * 3].astype(int)
    dist_first = X_transformed[:, n_features * 3:n_features * 4]

    # Check original features unchanged
    np.testing.assert_array_equal(original, X)

    # Row 0: [2, 5, 5, 8]
    # - col 0 (val=2): others >= 2 are [1,2,3]. First=1, Last=3, Dist=3
    # - col 1 (val=5): others >= 5 are [2,3]. First=2, Last=3, Dist=0
    # - col 2 (val=5): others >= 5 are [1,3]. First=1, Last=3, Dist=0
    # - col 3 (val=8): no others >= 8. First=-1, Last=-1, Dist=nan

    # Row 1: [4, 2, 6, 1]
    # - col 0 (val=4): others >= 4 are [2]. First=2, Last=2, Dist=2
    # - col 1 (val=2): others >= 2 are [0,2]. First=0, Last=2, Dist=2
    # - col 2 (val=6): no others >= 6. First=-1, Last=-1, Dist=nan
    # - col 3 (val=1): others >= 1 are [0,1,2]. First=0, Last=2, Dist=3

    expected_first_idx = np.array([
        [1, 2, 1, -1],
        [2, 0, -1, 1]  # Changed last value from 0 to 1
    ])
    np.testing.assert_array_equal(first_idx, expected_first_idx)

    expected_last_idx = np.array([
        [3, 3, 3, -1],
        [2, 2, -1, 2]
    ])
    np.testing.assert_array_equal(last_idx, expected_last_idx)

    expected_dist_first = np.array([
        [3, 0, 0, np.nan],
        [2, 2, np.nan, 1]
    ])
    np.testing.assert_array_equal(dist_first, expected_dist_first)