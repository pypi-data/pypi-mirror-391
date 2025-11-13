---
title: 'svd_imputer: A Python Package for Time Series Imputation Using Singular Value Decomposition'
tags:
  - Python
  - time series
  - missing data
  - imputation
  - SVD
  - matrix completion
  - uncertainty quantification
authors:
  - name: Rui Hugman
    orcid: 0000-0003-0891-3886
    affiliation: 1
affiliations:
 - name: INTERA, Portugal
   index: 1
date: 7 October 2025
bibliography: paper.bib
---

# Summary

Time series data from environmental monitoring networks, sensor arrays, and scientific instruments frequently contain gaps due to equipment failures, maintenance periods, transmission errors, or adverse conditions. Accurate imputation of these missing values is critical for downstream analyses including trend detection, anomaly identification, and decision-support model development. `svd_imputer` is a Python package that uses Singular Value Decomposition (SVD) to impute missing values in multivariate time series by exploiting spatial and temporal correlations across multiple series. The package provides Monte Carlo validation methods for uncertainty quantification, automatic rank estimation, and a scikit-learn-compatible API, making it accessible for both researchers and practitioners.

# Statement of Need

Multivariate time series from environmental monitoring networks (e.g., groundwater levels, weather stations, air quality sensors) often exhibit strong spatial and temporal correlations. Traditional univariate imputation methods such as linear interpolation or mean substitution ignore these cross-series relationships and fail to provide uncertainty estimates [@hastie2009elements]. While sophisticated machine learning approaches like random forests [@stekhoven2012missforest] or deep learning methods exist, they often require large training datasets, extensive hyperparameter tuning, and substantial computational resources that may not be available in many practical applications.

Matrix completion methods based on low-rank approximations offer a principled middle ground: they exploit correlations between series while remaining computationally efficient and theoretically grounded [@candes2010matrix; @mazumder2010spectral]. The SVD-based approach is particularly well-suited for time series with moderate missingness (<30%) and structured correlations between variables. 

However, existing Python implementations require significant customization by the user or provide no framework for uncertainty quantification, which is essential for real-world applications.

`svd_imputer` addresses these limitations by providing:

1. **Scikit-learn-compatible API** [@pedregosa2011scikit] for seamless integration into existing machine learning workflows
2. **Automatic rank estimation** based on variance thresholds or cross-validation, eliminating manual parameter tuning
3. **Monte Carlo uncertainty quantification** with multiple masking strategies (random, temporal blocks) for assessing uncertainty in imputed values


The package is aimed at practitioners working with environmental monitoring data, where understanding uncertainty in imputed values is essential for downstream model development and risk assessment. Similar functionality exists in R packages like Amelia [@amelia] and mice [@buuren2011mice], but Python implementations with comparable features and uncertainty quantification have been lacking.

# Implementation and Methods

## Algorithmic Approach

`svd_imputer` implements the iterative SVD imputation algorithm for matrix completion [@troyanskaya2001missing; @mazumder2010spectral]. Consider a data matrix $\mathbf{X} \in \mathbb{R}^{n \times p}$ representing $n$ time points and $p$ monitoring sites, where some entries are missing. The algorithm assumes $\mathbf{X}$ can be well-approximated by a low-rank matrix:

$$\mathbf{X} \approx \mathbf{U}_r \mathbf{\Sigma}_r \mathbf{V}_r^T$$

where $\mathbf{U}_r \in \mathbb{R}^{n \times r}$, $\mathbf{\Sigma}_r \in \mathbb{R}^{r \times r}$, and $\mathbf{V}_r \in \mathbb{R}^{p \times r}$ are the truncated SVD components at rank $r$.

The iterative algorithm proceeds as:

1. **Initialize**: Replace missing values with column means (after standardization): $\mathbf{X}^{(0)}$
2. **Iterate** until convergence:
   - Compute full SVD: $\mathbf{X}^{(t-1)} = \mathbf{U} \mathbf{\Sigma} \mathbf{V}^T$
   - Compute rank-$r$ approximation: $\hat{\mathbf{X}}^{(t)} = \mathbf{U}_r \mathbf{\Sigma}_r \mathbf{V}_r^T$
   - Update only missing entries: $X^{(t)}_{ij} = \begin{cases} \hat{X}^{(t)}_{ij} & \text{if } X_{ij} \text{ missing} \\ X_{ij} & \text{otherwise} \end{cases}$
3. **Converge**: Stop when $\|\mathbf{X}^{(t)} - \mathbf{X}^{(t-1)}\|_F < \epsilon$ (default: $\epsilon = 10^{-4}$)

### Automatic Rank Selection

The rank $r$ controls model complexity. `svd_imputer` provides three methods for rank selection:

1. **Variance threshold** (default): Select minimum rank explaining 95% of variance in observed data
2. **Cross-validation**: Optimize rank by minimizing prediction error on held-out validation sets
3. **Fixed rank**: User-specified rank

### Uncertainty Quantification

The package implements Monte Carlo validation [@efron1979bootstrap] to estimate imputation uncertainty:

1. Randomly mask a fraction (default 10%) of observed values
2. Impute the artificially missing values
3. Compute error metrics (RMSE, MAE) against true values
4. Repeat $N$ times (default 100) to build error distributions
5. Report mean error and 95% confidence intervals

Two masking strategies are available:

- **Random masking**: Randomly select individual values while preserving at least one observation per row to avoid bias
- **Block masking**: Mask contiguous temporal blocks to simulate realistic sensor outages

This validation approach provides realistic uncertainty estimates that reflect the algorithm's performance on similar data patterns.

# Example Usage

The following example demonstrates the core functionality of `svd_imputer` using groundwater monitoring data:

```python
import pandas as pd
import numpy as np
from svd_imputer import Imputer

# Load time series data with datetime index
df = pd.read_csv('groundwater_data.csv', index_col=0, parse_dates=True)

# Basic imputation with automatic rank estimation
imputer = Imputer(data=df, variance_threshold=0.95, verbose=True)
df_imputed = imputer.fit_transform()

# Imputation with uncertainty quantification
df_imputed, uncertainty = imputer.fit_transform(
    return_uncertainty=True,
    n_repeats=100,
    mask_strategy='block',
    block_len=5,
    seed=42
)

print(f"Imputation RMSE: {uncertainty['rmse']:.4f}")
print(f"95% CI: {uncertainty['rmse_ci']}")

# Cross-validation for optimal rank selection
imputer_cv = Imputer(data=df, rank='auto')
imputer_cv.fit()
print(f"Optimized rank: {imputer_cv.rank_}")

# Inspect optimization results
results = imputer_cv.get_optimization_results()
print(results['results_df'])
```

For datasets with multiple monitoring sites and scattered missing data, the SVD approach effectively leverages spatial correlations between sites to produce accurate imputations. The Monte Carlo validation provides realistic uncertainty estimates that can be propagated to downstream analyses. A complete example with visualization is available in the package documentation.

# Software Architecture and Performance

`svd_imputer` is implemented in pure Python using NumPy [@harris2020array] for numerical computations, pandas [@reback2020pandas] for time series handling, and scikit-learn [@pedregosa2011scikit] conventions for the API design. The package follows software engineering best practices:

- **Modular design**: Separation of concerns with distinct modules for imputation (`imputer.py`) and preprocessing (`preprocessing.py`)
- **Testing**: Test suite including unit tests, integration tests, and edge case handling
- **Documentation**: Descriptive docstrings and example notebooks

The core SVD computation leverages NumPy's `linalg.svd`, which uses optimized LAPACK routines. For a dataset with $n$ time points and $p$ variables, the computational complexity is approximately $O(k \cdot n \cdot p \cdot \min(n,p))$ where $k$ is the number of iterations (typically 10-50). Performance on a standard laptop (2020 MacBook Pro):

- Small dataset (100 time points, 5 variables): <1 second
- Medium dataset (1,000 time points, 10 variables): ~5 seconds  
- Large dataset (10,000 time points, 20 variables): ~2 minutes
- Monte Carlo validation (100 repeats): adds 2-5 minutes depending on dataset size

The package is suitable for datasets ranging from small sensor networks to moderate-scale environmental monitoring systems (up to ~50,000 time points and ~100 variables).

# Comparison with Existing Tools

Several Python and R packages provide missing data imputation:

- **scikit-learn** [@pedregosa2011scikit]: Provides `SimpleImputer` and `IterativeImputer`, but lacks  uncertainty quantification
- **fancyimpute** (Python): Implements various matrix completion algorithms but is no longer actively maintained
- **Amelia** [@amelia] (R): Provides multiple imputation with uncertainty but limited to specific model assumptions
- **mice** [@buuren2011mice] (R): Comprehensive multiple imputation framework but computationally intensive

`svd_imputer` fills a gap by combining efficient SVD-based imputation, time series-specific validation, Monte Carlo uncertainty quantification, and a modern Python API in a single, well-tested package.

# Conclusion and Future Work

`svd_imputer` provides a robust, well-documented solution for imputing missing values in multivariate time series with quantified uncertainty. By combining the theoretical foundation of low-rank matrix completion with practical considerations for time series data—including comprehensive validation, automatic rank selection, and Monte Carlo uncertainty estimation—the package addresses an important need in the Python scientific computing ecosystem.

The package is particularly valuable for environmental monitoring applications where data completeness and uncertainty quantification are essential for scientific inference and decision-making. The scikit-learn-compatible API ensures easy integration into existing machine learning  or modelling pipelines, while the focus on time series-specific validation and uncertainty quantification distinguishes it from general-purpose imputation tools.

Future enhancements may include:

- Point-wise uncertainty estimation using bootstrap or analytical approximations
- Support for seasonal decomposition and non-stationary time series
- Support for Bayesian uncertainy framework accounting for measurment error
- GPU acceleration for large-scale datasets
- Integration with probabilistic forecasting frameworks

The package is actively maintained and welcomes community contributions. Source code, documentation, and issue tracking are available on GitHub.

# Availability and Installation

The package is available via PyPI and can be installed using:

```bash
pip install svd-imputer
```

**Source code**: https://github.com/rhugman/ranger.svdtseries  
**Documentation**: https://svd-imputer.readthedocs.io/  
**License**: MIT

The package requires Python ≥3.8 and depends on NumPy (≥1.20), pandas (≥1.3), and scikit-learn (≥1.0).

# Acknowledgements

We thank the open-source community for valuable feedback on early versions of this package, and the developers of NumPy, pandas, and scikit-learn for providing the foundational tools that made this work possible.

# References
