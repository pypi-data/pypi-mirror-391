import pandas as pd
from skboost.preprocessing import GroupDiffTransformer, GroupValueCountsTransformer


def test_group_diff_numeric():
    df = pd.DataFrame({
        'user_id': [1, 1, 1, 2, 2],
        'timestamp': [1, 2, 3, 1, 2],
        'value': [10, 12, 15, 5, 8]
    })
    transformer = GroupDiffTransformer(key_col='user_id', add_prev=True, add_first=True)
    result = transformer.fit_transform(df)

    assert 'value_diff_prev' in result.columns
    assert 'value_diff_first' in result.columns
    assert result['value_diff_prev'].iloc[0] == 0  # First row per group
    assert result['value_diff_prev'].iloc[1] == 2  # 12 - 10


def test_group_diff_categorical():
    df = pd.DataFrame({
        'user_id': [1, 1, 1, 2, 2],
        'category': ['A', 'A', 'B', 'C', 'C']
    })
    transformer = GroupDiffTransformer(key_col='user_id', add_prev=True)
    result = transformer.fit_transform(df)

    assert 'category_eq_prev' in result.columns
    assert result['category_eq_prev'].iloc[0] == 1  # First row
    assert result['category_eq_prev'].iloc[1] == 1  # A == A
    assert result['category_eq_prev'].iloc[2] == 0  # B != A


def test_group_value_counts():
    df = pd.DataFrame({
        'session_id': [1, 1, 1, 2, 2, 2],
        'action': ['click', 'click', 'buy', 'click', 'buy', 'buy']
    })
    transformer = GroupValueCountsTransformer(group_col='session_id', value_col='action')
    result = transformer.fit_transform(df)

    assert 'session_id_action_counts' in result.columns
    assert 'session_id_action_norm' in result.columns
    assert result['session_id_action_counts'].iloc[0] == 2  # 'click' appears 2x in session 1
    assert result['session_id_action_counts'].iloc[2] == 1  # 'buy' appears 1x in session 1
    assert result['session_id_action_norm'].iloc[0] == 1.0  # 2/2 (max in group)


def test_group_value_counts_custom_prefix():
    df = pd.DataFrame({
        'grp': [1, 1, 2, 2],
        'val': ['a', 'a', 'b', 'b']
    })
    transformer = GroupValueCountsTransformer(group_col='grp', value_col='val', prefix='custom')
    result = transformer.fit_transform(df)

    assert 'custom_counts' in result.columns
    assert 'custom_norm' in result.columns


