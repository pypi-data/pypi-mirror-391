import numpy as np
from icss_feature_selection import ICSSFeatureSelector
from sklearn.pipeline import Pipeline
from sklearn.svm import SVC

# 1. Create dummy interval data
# (n_samples, n_features, 2)
# 100 samples, 4 features. Features 0 and 2 are good, 1 and 3 are bad.
n_samples = 100
X = np.random.rand(n_samples, 4, 2)
X = np.sort(X, axis=2)  # Ensure [min, max] order

# Create labels 'y' correlated with features 0 and 2
y = np.zeros(n_samples)
# Samples where feature 0's interval is "small" [0.1, 0.2] get class 1
y[(X[:, 0, 0] > 0.1) & (X[:, 0, 1] < 0.2)] = 1
# Samples where feature 2's interval is "large" [0.7, 0.9] get class 1
y[(X[:, 2, 0] > 0.7) & (X[:, 2, 1] < 0.9)] = 1


print(f"Original X shape: {X.shape}")

# 2. Use the ICSSFeatureSelector
# We want to select the top 2 features
icss_selector = ICSSFeatureSelector(k=2)

# 3. Fit the selector
icss_selector.fit(X, y)

# 4. Check the scores
# (Higher is better)
print(f"ICSS Scores: {icss_selector.scores_}")
# Expected output: Features 0 and 2 will have much higher scores

# 5. Transform the data
X_new = icss_selector.transform(X)
print(f"Transformed X shape: {X_new.shape}")
# Expected output: (100, 2, 2)

# 6. Use in a Pipeline
pipeline = Pipeline([
    ('icss_select', ICSSFeatureSelector(k=2)),
    # We can't use SVC directly on interval data.
    # This example shows selection. A real pipeline would need
    # a step to flatten or featurize the intervals.
    # e.g., ('flatten', MyIntervalFlattener()),
    # ('clf', SVC())
])

print("\nSuccessfully created and tested ICSSFeatureSelector!")