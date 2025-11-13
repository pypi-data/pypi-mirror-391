
# test_dual_scaler.py
import numpy as np
import pandas as pd
from skboost.preprocessing import DualScalerTransformer


def test_dual_scaler_rel_abs_split():
    df = pd.DataFrame({
        'feature_rel': [1.0, 2.0, 3.0],
        'feature_abs': [10.0, 20.0, 30.0],
        'other': [100, 200, 300]
    })
    transformer = DualScalerTransformer()
    result = transformer.fit_transform(df)

    assert result.shape == df.shape
    assert 'feature_rel' in result.columns
    assert 'feature_abs' in result.columns
    # Check that scaling was applied (means should be ~0, stds ~1)
    assert abs(result['feature_rel'].mean()) < 0.1
    assert abs(result['feature_abs'].mean()) < 0.1


def test_dual_scaler_no_rel_columns():
    df = pd.DataFrame({
        'feature1': [1.0, 2.0, 3.0],
        'feature2': [10.0, 20.0, 30.0]
    })
    transformer = DualScalerTransformer()
    result = transformer.fit_transform(df)

    # Should still work with only 'abs' columns
    assert result.shape == df.shape
    assert 'abs' in transformer.scalers_