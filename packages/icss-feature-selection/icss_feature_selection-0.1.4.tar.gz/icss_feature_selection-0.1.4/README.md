# Interval Chi-Square Score (ICSS) Feature Selection

A Python implementation of the **Interval Chi-Square Score (ICSS)** feature selection algorithm for interval-valued data. This library provides a scikit-learn compatible feature selector that ranks and selects features based on their statistical independence from class labels.

## Overview

The Interval Chi-Square Score (ICSS) is a feature selection technique designed specifically for **interval-valued data**, where each feature is represented as an interval $[a_i, b_i]$ rather than a single continuous value. This approach is particularly useful in domains where data naturally comes as ranges or intervals, such as:

- Temperature ranges in climate studies
- Price ranges in e-commerce
- Uncertainty quantification in measurements
- Survey response ranges

The ICSS algorithm evaluates the degree of independence between each interval-valued feature and the target class label using a chi-square based approach adapted for interval data.

## Features

- ✨ Scikit-learn compatible API (`fit`, `transform`, `fit_transform`)
- 📊 Works with interval-valued features (shape: `(n_samples, n_features, 2)`)
- 🎯 Selects top-k features based on ICSS scores
- 📈 Integrates seamlessly with scikit-learn pipelines
- 🧬 Based on peer-reviewed research

## Installation

### Via PyPI (Recommended)

```bash
pip install icss-feature-selection
```

See the [PyPI package page](https://pypi.org/project/icss-feature-selection/0.1.0/) for more information.

### From Source

```bash
git clone https://github.com/vinaykumarngitub/icss-feature-selection.git
cd icss-feature-selection
pip install -e .
```

### Requirements

- Python >= 3.8
- NumPy
- scikit-learn

## Quick Start

### Basic Usage

```python
import numpy as np
from icss_feature_selection import ICSSFeatureSelector

# Create dummy interval data: (n_samples, n_features, 2)
# Each feature is represented as [lower_bound, upper_bound]
n_samples = 100
X = np.random.rand(n_samples, 4, 2)
X = np.sort(X, axis=2)  # Ensure [min, max] order

# Create labels correlated with some features
y = np.zeros(n_samples)
y[(X[:, 0, 0] > 0.1) & (X[:, 0, 1] < 0.2)] = 1
y[(X[:, 2, 0] > 0.7) & (X[:, 2, 1] < 0.9)] = 1

# Select top 2 features
selector = ICSSFeatureSelector(k=2)
selector.fit(X, y)

# Check ICSS scores for each feature
print("ICSS Scores:", selector.scores_)

# Transform data to keep only selected features
X_selected = selector.transform(X)
print("Selected features shape:", X_selected.shape)  # (100, 2, 2)
```

### Using with Scikit-learn Pipelines

```python
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

# Create a pipeline
pipeline = Pipeline([
    ('icss_select', ICSSFeatureSelector(k=2)),
    # Add your own preprocessing/classification steps here
])

# Fit and use the pipeline
pipeline.fit(X, y)
X_transformed = pipeline.transform(X)
```

## Input Format

The feature selector expects input in the following format:

- **X**: 3D NumPy array of shape `(n_samples, n_features, 2)`
  - `n_samples`: Number of samples in the dataset
  - `n_features`: Number of interval-valued features
  - `2`: Each feature is represented as `[lower_bound, upper_bound]`
  
- **y**: 1D NumPy array of shape `(n_samples,)`
  - Target class labels (discrete values for classification)

### Example Data Creation

```python
import numpy as np

# Method 1: Random intervals
n_samples, n_features = 100, 5
X = np.random.rand(n_samples, n_features, 2)
X = np.sort(X, axis=2)  # Ensure min <= max

# Method 2: From existing data with uncertainty
lower_bounds = np.random.rand(n_samples, n_features)
upper_bounds = lower_bounds + np.random.rand(n_samples, n_features) * 0.5
X = np.stack([lower_bounds, upper_bounds], axis=2)

# Class labels
y = np.random.randint(0, 3, n_samples)  # 3 classes
```

## API Reference

### ICSSFeatureSelector

```python
class ICSSFeatureSelector(BaseEstimator, SelectorMixin)
```

#### Parameters

- **k** (`int`, default=10): Number of top features to select based on ICSS scores.

#### Attributes

- **scores_** (`ndarray` of shape `(n_features,)`): ICSS score for each feature after fitting.

#### Methods

- **fit(X, y)**: Compute ICSS scores for all features.
- **transform(X)**: Select features with highest ICSS scores.
- **fit_transform(X, y)**: Fit and transform in one step.
- **get_support(indices=False)**: Get a boolean mask or indices of selected features.

## Complete Example

Here's a complete example demonstrating the feature selection workflow:

```python
import numpy as np
from icss_feature_selection import ICSSFeatureSelector

# 1. Create dummy interval data
n_samples = 100
X = np.random.rand(n_samples, 4, 2)
X = np.sort(X, axis=2)  # Ensure [min, max] order

# 2. Create labels correlated with features 0 and 2
y = np.zeros(n_samples)
y[(X[:, 0, 0] > 0.1) & (X[:, 0, 1] < 0.2)] = 1
y[(X[:, 2, 0] > 0.7) & (X[:, 2, 1] < 0.9)] = 1

print(f"Original X shape: {X.shape}")  # (100, 4, 2)

# 3. Use the ICSSFeatureSelector to select top 2 features
selector = ICSSFeatureSelector(k=2)

# 4. Fit the selector
selector.fit(X, y)

# 5. Check the scores (higher is better)
print(f"ICSS Scores: {selector.scores_}")

# 6. Transform the data
X_selected = selector.transform(X)
print(f"Transformed X shape: {X_selected.shape}")  # (100, 2, 2)

# 7. Get selected feature indices
support_indices = selector.get_support(indices=True)
print(f"Selected feature indices: {support_indices}")

print("\n✓ Successfully performed ICSS feature selection!")
```

## Algorithm Details

The ICSS algorithm works as follows:

1. **Reference Intervals**: For each feature, extract all unique interval values from the dataset.

2. **Similarity Kernel**: Define a similarity measure between intervals:
   $$\text{sim}(I^q, I^r) = \begin{cases} 1 & \text{if } I^q \text{ contains } I^r \\ 0 & \text{otherwise} \end{cases}$$

3. **Contingency Table**: Build a contingency table using the similarity kernel to count occurrences of each reference interval in each class.

4. **Chi-Square Calculation**: Compute the chi-square statistic adapted for interval data:
   $$I\chi^2 = \sum_{i,j} \frac{(O_{ij} - E_{ij})^2}{E_{ij}}$$
   where $O_{ij}$ are observed frequencies and $E_{ij}$ are expected frequencies.

5. **Feature Ranking**: Rank features by their ICSS scores and select the top-k.

For more details, please refer to the research paper.

## Research Paper

This implementation is based on the following peer-reviewed research:

**Interval Chi-Square Score (ICSS): Feature Selection of Interval Valued Data**

- **Authors**: Guru, D.S.; Vinay Kumar, N.
- **Conference**: Intelligent Systems Design and Applications (ISDA 2018)
- **Published**: April 14, 2019
- **Publisher**: Springer, Cham
- **Book**: Advances in Intelligent Systems and Computing, Vol. 941
- **Pages**: 579–590
- **Print ISBN**: 978-3-030-16659-5
- **Online ISBN**: 978-3-030-16660-1
- **DOI**: https://doi.org/10.1007/978-3-030-16660-1_67

### Links

- 📄 **Springer**: https://link.springer.com/chapter/10.1007/978-3-030-16660-1_67
- 🔬 **ResearchGate**: https://www.researchgate.net/publication/332410223_Interval_Chi-Square_Score_ICSS_Feature_Selection_of_Interval_Valued_Data

## Citation

If you use this implementation in your research, please cite the original paper:

```bibtex
@incollection{guru2020interval,
  title={Interval Chi-Square Score (ICSS): Feature Selection of Interval Valued Data},
  author={Guru, D.S. and Vinay Kumar, N.},
  booktitle={Intelligent Systems Design and Applications},
  pages={579--590},
  year={2020},
  publisher={Springer, Cham},
  isbn={978-3-030-16660-1},
  doi={10.1007/978-3-030-16660-1_67}
}
```

## Testing

Run the test example to verify the installation:

```bash
python tests/test.py
```

Expected output:
```
Original X shape: (100, 4, 2)
ICSS Scores: [...]
Transformed X shape: (100, 2, 2)

✓ Successfully created and tested ICSSFeatureSelector!
```

## Use Cases

- **Climate Data**: Select important temperature/humidity ranges for weather prediction
- **Medical Data**: Identify key biometric ranges that correlate with disease diagnosis
- **Financial Data**: Select relevant price ranges for stock trading systems
- **Sensor Data**: Choose important measurement ranges from multi-sensor systems
- **Survey Analysis**: Identify key response ranges in survey data

## Implementation Notes

- The algorithm uses a similarity kernel where an interval $I^q$ "contains" interval $I^r$ if $q_- \leq r_- \text{ and } q_+ \geq r_+$
- ICSS scores are computed using the chi-square formula adapted for interval data
- Features with higher ICSS scores have stronger association with the class label
- The implementation is compatible with scikit-learn's feature selection interface

## License

This project is licensed under the Apache License Version 2.0 - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

- ## Related Work

For other feature selection techniques and interval data methods, see:
- scikit-learn's [feature selection module](https://scikit-learn.org/stable/modules/feature_selection.html)
- Symbolic Data Analysis literature on interval-valued data

---

**Last Updated**: November 2025
