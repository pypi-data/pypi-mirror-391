import numpy as np
from sklearn.model_selection import cross_val_score
import copy
import itertools

def zoom_search_cv(
    estimator, X, y, param_grid, param_types=None, scoring=None, cv=3,
    n_iter=3, zoom_factor=0.5, verbose=True
):
    """
    Adaptive zoom-in grid search for numeric + categorical hyperparameters.

    Parameters
    ----------
    estimator : sklearn estimator
        The model to tune.
    X, y : array-like
        Training data.
    param_grid : dict
        Parameters with lists of initial candidate values.
        Numeric: list of 3 numbers [low, mid, high]
        Categorical: list of discrete options
    param_types : dict, optional
        'numeric' or 'categorical' for each parameter. If None, numeric assumed.
    scoring : str or callable
        Metric for cross_val_score.
    cv : int
        Number of CV folds.
    n_iter : int
        Number of zoom iterations.
    zoom_factor : float
        Compression factor for numeric ranges.
    verbose : bool
        Print progress.
    """
    if param_types is None:
        param_types = {k: 'numeric' for k in param_grid.keys()}

    best_params = None
    best_score = -np.inf
    grid = copy.deepcopy(param_grid)

    for iteration in range(n_iter):
        if verbose:
            print(f"\nIteration {iteration+1}/{n_iter}")

        # Build all combinations
        keys = list(grid.keys())
        values = [grid[k] for k in keys]
        candidates = [dict(zip(keys, combo)) for combo in itertools.product(*values)]

        # Evaluate
        for params in candidates:
            model = copy.deepcopy(estimator).set_params(**params)
            s = np.mean(cross_val_score(model, X, y, scoring=scoring, cv=cv))
            if s > best_score:
                best_score = s
                best_params = params
            if verbose:
                print(f"{params} -> {s:.4f}")

        # Update numeric params
        for k in keys:
            if param_types.get(k, 'numeric') == 'numeric':
                lo, mid, hi = grid[k]
                best_val = best_params[k]

                if np.isclose(best_val, mid):
                    new_lo = (lo + mid) / 2
                    new_hi = (hi + mid) / 2
                elif np.isclose(best_val, lo):
                    offset = mid - lo
                    new_lo = mid
                    new_hi = mid + offset
                else:  # hi best
                    offset = hi - mid
                    new_lo = mid - offset
                    new_hi = mid

                # compress around center
                center = (new_lo + new_hi) / 2
                delta = (new_hi - new_lo) * zoom_factor / 2
                grid[k] = [center - delta, center, center + delta]

            else:  # categorical param, keep best option + neighbors if available
                options = list(grid[k])
                if best_params[k] not in options:
                    options.append(best_params[k])
                grid[k] = [best_params[k]]  # always pick the current best

        if verbose:
            print(f"New grid: {grid}")

    return best_params, best_score


if __name__ == "__main__":
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.datasets import load_iris

    X, y = load_iris(return_X_y=True)
    model = RandomForestClassifier(random_state=0)

    param_grid = {
        'n_estimators': [50, 100, 150],
        'max_depth': [3, 6, 9]
    }

    best_params, best_score = zoom_search_cv(model, X, y, param_grid, cv=3, n_iter=3)
    print("\nBest params:", best_params)
    print("Best CV score:", best_score)

