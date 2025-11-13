import numpy as np
from sklearn.base import BaseEstimator
from sklearn.feature_selection._base import SelectorMixin

class ICSSFeatureSelector(BaseEstimator, SelectorMixin):
    """
    Implements the Interval Chi-Square Score (ICSS) for feature selection
    based on the provided academic paper.

    This selector ranks and selects features based on their ICSS score, which
    evaluates the degree of independence between a class label and an
    interval-valued feature.

    Parameters
    ----------
    k : int, default=10
        The number of top features to select.

    Attributes
    ----------
    scores_ : array-like of shape (n_features,)
        The ICSS scores for each feature.
    """
    def __init__(self, k=10):
        self.k = k
        self.scores_ = None

    def _sim(self, q_interval, r_interval):
        """
        Implements the similarity kernel sim(In^q, In^r).
        Returns 1 if interval q contains interval r, 0 otherwise.
        
        From the paper: sim = 1 if q_i_minus <= r_i_minus AND q_i_plus >= r_i_plus
        """
        q_minus, q_plus = q_interval
        r_minus, r_plus = r_interval
        
        if q_minus <= r_minus and q_plus >= r_plus:
            return 1
        return 0

    def _calculate_icss(self, X_feature, y):
        """
        Calculates the I-Chi-Square (I-Chi^2) score for a single feature.
        
        X_feature : np.array of shape (n_samples, 2)
            The interval values for one feature.
        y : np.array of shape (n_samples,)
            The target class labels.
        """
        
        # u = number of unique intervals (reference intervals)
        # We define reference intervals as the unique intervals present in the feature data
        reference_intervals = np.unique(X_feature, axis=0)
        u = len(reference_intervals)
        
        # m = number of different classes
        classes = np.unique(y)
        m = len(classes)
        
        # In = total number of interval samples
        In = len(y)
        
        if u == 0 or m == 0 or In == 0:
            return 0.0

        # Create a map for class labels to indices for efficient counting
        class_map = {label: idx for idx, label in enumerate(classes)}

        # --- Calculate Observed Frequencies (In_ij) ---
        # In_ij = frequency of samples with i-th interval value in class j
        # But, using the paper's similarity kernel
        
        # observed_counts (In_ij): shape (u, m)
        observed_counts = np.zeros((u, m))
        
        # row_totals (In_i*): shape (u,)
        # In_i* = number of samples with the i-th interval value
        row_totals = np.zeros(u)
        
        # col_totals (In_*j): shape (m,)
        # In_*j = number of samples in class j
        col_totals = np.array([np.sum(y == j) for j in classes])
        
        # This is the core O(n_samples * u) loop
        for i, r_interval in enumerate(reference_intervals):
            for k in range(In):
                q_interval = X_feature[k]
                
                # Check if sample interval Q_k "contains" reference interval R_i
                if self._sim(q_interval, r_interval) == 1:
                    # Increment row total for this reference interval
                    row_totals[i] += 1
                    
                    # Increment observed count for this (interval, class) pair
                    j_idx = class_map[y[k]]
                    observed_counts[i, j_idx] += 1

        # --- Calculate Expected Frequencies (Iμ_ij) ---
        # Iμ_ij = (In_*j * In_i*) / In
        
        # Use broadcasting to create the (u, m) matrix of expected counts
        # Add a small epsilon to In to avoid division by zero if In is 0 (though we check this)
        expected_counts = (row_totals[:, np.newaxis] * col_totals[np.newaxis, :]) / (In + 1e-9)
        
        # --- Calculate the I-Chi-Square Score ---
        # Iχ^2 = Σ Σ ( (In_ij - Iμ_ij)^2 / Iμ_ij )
        
        # We need to handle cases where expected_counts is 0 to avoid division by zero.
        # In a Chi-Square test, if expected is 0, the contribution is 0 (if observed is also 0)
        # or infinite (if observed is > 0). We'll set 0/0 to 0.
        
        with np.errstate(divide='ignore', invalid='ignore'):
            term = np.nan_to_num(
                ((observed_counts - expected_counts)**2) / expected_counts
            )
        
        icss_score = np.sum(term)
        return icss_score

    def fit(self, X, y):
        """
        Fit the ICSS feature selector.

        Parameters
        ----------
        X : array-like of shape (n_samples, n_features, 2)
            The training input samples. Each feature is an interval.
        y : array-like of shape (n_samples,)
            The target values.
        """
        if not isinstance(X, np.ndarray):
            X = np.asarray(X)
        
        if X.ndim != 3 or X.shape[2] != 2:
            raise ValueError(
                "Input X must be a 3D NumPy array with shape (n_samples, n_features, 2)."
            )
            
        n_features = X.shape[1]
        self.scores_ = np.zeros(n_features)
        
        for i in range(n_features):
            X_feature_i = X[:, i, :]
            self.scores_[i] = self._calculate_icss(X_feature_i, y)
            
        return self

    def _get_support_mask(self):
        """
        Get the mask of selected features.
        Assumes higher score is better, as per the paper.
        """
        if self.scores_ is None:
            raise RuntimeError("You must call 'fit' before calling 'transform'.")
            
        mask = np.zeros(len(self.scores_), dtype=bool)
        
        # Get indices of the top k scores (highest scores)
        if self.k >= len(self.scores_):
            top_indices = np.arange(len(self.scores_))
        else:
            top_indices = np.argsort(self.scores_)[-self.k:]
        
        mask[top_indices] = True
        return mask

    def transform(self, X):
        """
        Reduce X to the selected features.

        Parameters
        ----------
        X : array-like of shape (n_samples, n_features, 2)
            The input samples.

        Returns
        -------
        X_r : array-like of shape (n_samples, k, 2)
            The input samples with only the selected features.
        """
        if self.scores_ is None:
            raise RuntimeError("You must call 'fit' before calling 'transform'.")
            
        # Validate input X
        if not isinstance(X, np.ndarray):
            X = np.asarray(X)
        
        if X.ndim != 3 or X.shape[2] != 2:
            raise ValueError(
                "Input X must be a 3D NumPy array with shape (n_samples, n_features, 2)."
            )
            
        # Get the boolean mask of features to keep
        mask = self._get_support_mask()
        
        # Check if number of features in X matches the one used in fit
        if len(mask) != X.shape[1]:
            raise ValueError(
                f"X has {X.shape[1]} features, but ICSSFeatureSelector "
                f"was fitted with {len(mask)} features."
            )
            
        # Apply the mask to the 3D array
        # This selects all samples, the columns (features) in the mask, 
        # and all a-points of the interval
        return X[:, mask, :]