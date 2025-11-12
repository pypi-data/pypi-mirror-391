
# Monte Carlo Singular Spectrum Analysis (MCSSA)

**A Python implementation of Monte Carlo Singular Spectrum Analysis (MCSSA)**, a rigorous spectral-decomposition and hypothesis-testing toolkit for researchers working in the **climate and geophysical sciences**.
It builds upon the foundational work of **Myles R. Allen** and **Leonard A. Smith**, and has been further extended by **Andreas Groth** and **Michael Ghil**.

---
## Status

This package is **experimental**.  
- Features may be incomplete  
- No guarantees of backward compatibility  
- Not actively maintained


## Overview

**Singular Spectrum Analysis (SSA)** decomposes a univariate time series into interpretable components, trend, oscillations, and noise without requiring a predefined model.

**Monte Carlo SSA (MCSSA)** extends SSA by generating an ensemble of surrogate datasets based on a **red-noise (AR(1)) null hypothesis**, which is the *standard statistical null model in climate dynamics and geophysical signal analysis*.  

By comparing the eigenspectrum of the observed data to that of AR(1) surrogate series, MCSSA identifies oscillatory components that are **statistically significant** beyond what would be expected from background red noise.

> ⚠️ **Note:** MCSSA assumes that the null hypothesis of the data follows an **AR(1)** process. A valid and widely used assumption in **climate, atmospheric, and oceanic** time series analysis.
> It may not be suitable for processes with fundamentally different stochastic structures.


This package provides:

- SSA decomposition and reconstruction  
- MCSSA hypothesis testing with three approaches:
  1. **Data-basis** testing (`mcssa_basic`)  
  2. **Ensemble-basis** testing (`mcssa_ensemble`)  
  3. **Procrustes-aligned** testing (`mcssa_procrustes`)
- AR(1) parameter estimation and surrogate generation  
- Publication-ready statistical output
## Theoretical Background

### 1. Trajectory Matrix (Embedding)
Given a time series xₜ of length n and embedding dimension m:

**X** = [ [x₁, x₂, …, xₘ], [x₂, x₃, …, xₘ₊₁], …, [xₙ₋ₘ₊₁, xₙ₋ₘ₊₂, …, xₙ] ]


This (n–m+1) × m matrix represents overlapping windows of the time series.

---

### 2. Covariance Matrix and Eigen-Decomposition

The covariance matrix summarizes how lagged versions of the time series co-vary:

**C** = (1 / (n − m + 1)) **X**ᵀ **X**


Each element Cᵢⱼ measures the covariance between time-lagged copies of the signal, separated by ( |i-j| ) timesteps.



### Why Eigen-Decomposition?

To extract dominant and independent patterns of variability, we solve the eigenvalue problem:

**C** **eₖ** = λₖ **eₖ**

This operation identifies orthogonal directions — called **Empirical Orthogonal Functions (EOFs)** — that **maximize variance** of the lagged trajectories while maintaining mutual orthogonality.

Formally, each EOF eₖ is obtained by solving:

max₍ₑₖ₎  **eₖ**ᵀ **C** **eₖ**,  subject to **eₖ**ᵀ.**eₖ** = 1

The solution yields:
- λₖ: the **variance explained** by mode k  
- eₖ: the **orthogonal spatial (temporal-lag) pattern** of that mode  



Hence, SSA performs a **variance-maximizing decomposition** in the space of time-delayed embeddings,  
analogous to Principal Component Analysis (PCA) — but applied to lagged copies of the original time series.  

This allows one to separate:
- Slowly varying trends  
- Quasi-periodic oscillations  
- High-frequency (noise-like) components  


### 3. AR(1) Null Model

Under the red-noise null hypothesis, the process is modeled as:

xₜ = γ xₜ₋₁ + α wₜ, wₜ ~ 𝒩(0, 1)

where:  
- γ = lag-1 autocorrelation coefficient  
- α= noise scaling parameter
---

### 4. Monte Carlo Testing

Generate Nₛ surrogate realizations, apply SSA to each, and collect their eigenvalues λₖ⁽ⁱ⁾. For each SSA mode k, estimate confidence bounds:

Upper(k) = Percentile₉₇.₅{λₖ⁽ⁱ⁾},  Lower(k) = Percentile₂.₅{λₖ⁽ⁱ⁾}


Modes of the real data whose eigenvalues exceed these bounds are considered significant.

## Installation

You can install the package in two ways, depending on your use case:

---

### Option 1 — Direct install from GitHub (recommended for users)

If you simply want to use the package without modifying the source:

```bash
pip install git+https://github.com/sayan-geoDL/pymcssa.git
```
This command will automatically fetch the latest version from GitHub and install all required dependencies.

### Option 2 — Local editable install (recommended for development)
If you plan to modify the code or contribute:
```bash
git clone git+https://github.com/sayan-geoDL/pymcssa.git
cd pymcssa
pip install -e .
```
The -e flag installs the package in editable mode, meaning any local code changes will take effect immediately without reinstalling.
### Optional: Verify the installation

After installation, open a Python terminal and run:
```python
import pymcssa
print(pymcssa.__version__)
```
If no errors appear, the package has been successfully installed!
### Quickstart Example

```python
import numpy as np
from pymcssa import MCSSA

# Generate synthetic AR(1) red noise
np.random.seed(0)
n = 500
gamma = 0.6
data = np.zeros(n)
for t in range(1, n):
    data[t] = gamma * data[t-1] + np.random.randn()

# Run Monte Carlo SSA
m = 40
mc = MCSSA(data, m)
results = mc.mcssa_basic(up_perc=97.5, down_perc=2.5, ns=500)

print("Data eigenvalues:", results["data_eigenvalues"][:5])
print("Upper 97.5% bounds:", results["upper_confidence"][:5])
```

---

###  Available Classes

### `AR1estimator`
Provides AR(1) parameter estimation and surrogate generation.

**Key methods:**
- `gambar(max_iter=1000)` → estimate lag-1 autocorrelation  <img src="https://latex.codecogs.com/svg.latex?\gamma" />
- `alph(max_iter=1000)` → estimate noise std. dev.  <img src="https://latex.codecogs.com/svg.latex?\alpha" />
- `ar1_model(alpha, gamma)` → generate AR(1) surrogate series


### `SSA`
Implements Singular Spectrum Analysis for time series decomposition into:
- Empirical Orthogonal Functions (EOFs)
- Principal Components (PCs)
- Reconstructed Components (RCs)

### `MCSSA`
Builds on `AR1estimator` to provide:
- `mcssa_basic()` → data-basis testing  
- `mcssa_ensemble()` → ensemble mean basis testing  
- `mcssa_procrustes()` → Procrustes-aligned testing
## Example Output

Each MCSSA method returns a dictionary, for example:

```python
{
  "data_eigenvalues": ndarray,
  "upper_confidence": list,
  "lower_confidence": list,
  "gamma": float,
  "alpha": float,
  "spreads": ndarray,
  "surrogates": ndarray  # optional
}
```

---

### Testing and Dependencies
## Dependencies

- [NumPy](https://numpy.org)
- [math](https://docs.python.org/3/library/math.html)
- (Optional) PyTest


## Testing and Validation (for developers)
This package includes a comprehensive test suite to ensure the numerical stability and correctness of all SSA and MCSSA methods.  
The tests validate decomposition accuracy, eigenvalue consistency, reconstruction fidelity, and statistical behavior of surrogate-based hypothesis testing.


### **Running All Tests**

From the package root directory:
```bash
pytest -v
```


### **Included Test Modules**
#### `tests/test_ssa.py`

Validates the **Singular Spectrum Analysis (SSA)** core functionality.

**Tests include:**
- ✅ `test_ssa_basic_run` — checks SSA output consistency and expected keys  
- ✅ `test_ssa_variance_explained_sum` — ensures eigenvalue variance sums to 100%  
- ✅ `test_ssa_reconstruction_dimensions` — verifies reconstructed matrix shape  
- ✅ `test_ssa_orthogonality_of_eofs` — confirms orthonormal EOF basis  
- ✅ `test_ssa_invalid_dimension_raises` — confirms error on non-1D data  
- ✅ `test_ssa_invalid_window_too_large` — raises error if `m > len(data)`
#### `tests/test_mcssa_methods.py`

Validates the **Monte Carlo SSA (MCSSA)** routines for red-noise significance testing.

**Tests include:**
- ✅ `test_mcssa_basic_output` — validates main output keys and shapes  
- ✅ `test_mcssa_ensemble_output` — ensures ensemble averaging returns consistent results  
- ✅ `test_mcssa_procrustes_output` — checks Procrustes-aligned variant  
- ✅ `test_invalid_parameters` — verifies input parameter error handling

### Example Output

Typical pytest output (abridged):
```bash
=========================================================================================== test session starts ============================================================================================
platform linux -- Python 3.12.7, pytest-7.4.4
collected 10 items                                                                                                                                                                             

tests/test_mcssa_methods.py::test_mcssa_basic_output PASSED                                                                                                                                          [ 10%]
tests/test_mcssa_methods.py::test_mcssa_ensemble_output PASSED                                                                                                                                       [ 20%]
tests/test_mcssa_methods.py::test_mcssa_procrustes_output PASSED                                                                                                                                     [ 30%]
tests/test_mcssa_methods.py::test_invalid_parameters PASSED                                                                                                                                          [ 40%]
tests/test_ssa.py::test_ssa_basic_run PASSED                                                                                                                                                         [ 50%]
tests/test_ssa.py::test_ssa_variance_explained_sum PASSED                                                                                                                                            [ 60%]
tests/test_ssa.py::test_ssa_reconstruction_dimensions PASSED                                                                                                                                         [ 70%]
tests/test_ssa.py::test_ssa_orthogonality_of_eofs PASSED                                                                                                                                             [ 80%]
tests/test_ssa.py::test_ssa_invalid_dimension_raises PASSED                                                                                                                                          [ 90%]
tests/test_ssa.py::test_ssa_invalid_window_too_large PASSED                                                                                                                                          [100%]

============================================================================================ 10 passed in 0.56s ============================================================================================

```
---

### References
- **Groth, A., & Ghil, M. (2015). *Monte Carlo Singular Spectrum Analysis (SSA) Revisited: Detecting Oscillator Clusters in Multivariate Datasets*. Journal of Climate, 28 (19), 7873‑7893. doi:[10.1175/JCLI‑D‑15‑0100.1](https://doi.org/10.1175/JCLI-D-15-0100.1)**  
[Publisher Link](https://journals.ametsoc.org/view/journals/clim/28/19/jcli-d-15-0100.1.xml) | [Google Scholar](https://scholar.google.com/scholar?q=Monte+Carlo+Singular+Spectrum+Analysis+(SSA)+Revisited:+Detecting+Oscillator+Clusters+in+Multivariate+Datasets)
- **Allen, M. R., & Smith, L. A. (1996). *Monte Carlo SSA: Detecting irregular oscillations in the presence of coloured noise.* Journal of Climate, 9(12), 3373‑3404. doi:[10.1175/1520‑0442(1996)009<3373:MCSDIO>2.0.CO;2](https://doi.org/10.1175/1520-0442(1996)009<3373:MCSDIO>2.0.CO;2)**
[Publisher Link](https://journals.ametsoc.org/view/journals/clim/9/12/1520-0442_1996_009_3373_mcsdio_2_0_co_2.xml)  
---
## 📖 Documentation

Full documentation for `pymcssa` is available online at:  
[![Documentation](https://img.shields.io/badge/docs-online-brightgreen)](https://sayan-geoDL.github.io/pymcssa/)

---
## 📄 License

Released under the **MIT License**.  
See `LICENSE` for details.

---

## 📬 Contact

**Sayan Jana**  
Affiliation: *PhD. Student IISC, CAOS*  
Email: *janasayan143@gmail.com*
GitHub: [https://github.com/sayan-geoDL](https://github.com/sayan-geoDL)


