# DConfusion
A Python package for working with confusion matrices - now with a web UI!

## Overview
`dconfusion` is a comprehensive Python package for working with confusion matrices, supporting both binary and multi-class classification. It now includes a beautiful Streamlit web interface for comparing multiple models side-by-side.

## ✨ New: Web Interface!

**Features:**
- 📊 Compare multiple models side-by-side
- 📈 Interactive visualizations and metrics
- 📊 Statistical testing with bootstrap CIs and McNemar's test
- 📥 Export comparisons as CSV
- 🎯 Identify best-performing models instantly

[See QUICKSTART.md for detailed instructions](QUICKSTART.md)

## Features
* **Binary & Multi-class Support** - Works with 2+ classes
* **Comprehensive Metrics** - Accuracy, Precision, Recall, F1, MCC, Cohen's Kappa, and more
* **Flexible Input** - From values, matrix, or prediction lists
* **Visualization** - Beautiful matplotlib plots with metrics panels
* **Import/Export** - CSV, JSON, dict formats
* **Web UI** - Streamlit app for easy comparison
* **⚠️ Warning System** - Research-based warnings for common pitfalls (sample size, class imbalance, metric reliability)
* **📊 NEW: Statistical Testing** - Bootstrap confidence intervals, McNemar's test, metric consistency checks
* **Modular Design** - Clean separation: core, metrics, visualization, I/O, statistics

## Installation
You can install `dconfusion` using pip:

```bash
pip install dconfusion
```

Usage
Here's an example of how to use dconfusion:

# Binary classification (existing usage)
``` python
binary_cm = DConfusion(80, 70, 10, 20)
```

# Multi-class from matrix
``` python
multiclass_cm = DConfusion(
    confusion_matrix=[[50, 3, 2], [8, 45, 1], [4, 2, 48]], 
    labels=['Cat', 'Dog', 'Bird']
)
```

# Multi-class from predictions
``` python
y_true = ['Cat', 'Dog', 'Bird', 'Cat', 'Dog']
y_pred = ['Cat', 'Dog', 'Cat', 'Cat', 'Dog']  
cm = DConfusion.from_predictions(y_true, y_pred)
```

# Get class-specific metrics
``` python
# Get metrics for a specific class
cat_metrics = multiclass_cm.get_class_metrics(class_label='Cat')
# Returns: {'precision': 0.91, 'recall': 0.83, 'f1_score': 0.87, 'specificity': 0.95}
```

# Get overall metrics
```
overall_metrics = multiclass_cm.get_all_metrics()
```

# Plot confusion matrix
```python
cm = DConfusion(80, 70, 10, 20)
fig = cm.plot()

# Normalized with custom styling
fig2 = cm.plot(normalize=True, cmap='Blues', figsize=(10, 8))

# With metrics panel (binary only)
fig3 = cm.plot(show_metrics=True)

multiclass_cm = DConfusion(
    confusion_matrix=[[50, 3, 2], [8, 45, 1], [4, 2, 48]],
    labels=['Cat', 'Dog', 'Bird']
)

fig4 = multiclass_cm.plot(normalize=True, cmap='cool') # If we show metrics, only accuracy is displayed
fig4.show()
```

## ⚠️ Warning System (NEW!)

DConfusion now includes a comprehensive warning system based on peer-reviewed research on binary classification metrics. It automatically detects common pitfalls like:

- **Small sample sizes** that lead to high metric uncertainty
- **Class imbalance** with insufficient samples per class
- **Misleading accuracy** when it's close to majority class proportion
- **Perfect classification** that might indicate data leakage
- **Zero cells** (TP, TN, FP, or FN = 0) that make metrics undefined
- **Poor basic rates** hidden by high accuracy or ROC AUC
- **Unreliable comparisons** due to sample size or uncertainty issues

### Quick Start

```python
from dconfusion import DConfusion

# Create a confusion matrix
cm = DConfusion(true_positive=10, false_negative=5,
                false_positive=3, true_negative=12)

# Print warnings
cm.print_warnings()

# Or access warnings programmatically
warnings = cm.check_warnings()
for warning in warnings:
    print(warning.severity, warning.category, warning.message)

# Compare two models with warnings
model_a = DConfusion(true_positive=48, false_negative=7, false_positive=5, true_negative=40)
model_b = DConfusion(true_positive=50, false_negative=5, false_positive=8, true_negative=37)
result = model_a.compare_with(model_b, metric='accuracy')

if result['has_warnings']:
    print("Comparison may not be reliable:")
    for w in result['warnings']:
        print(f"  - {w}")
```

### Example Output

```
================================================================================
CONFUSION MATRIX ANALYSIS WARNINGS
================================================================================

WARNING (2):
--------------------------------------------------------------------------------
[WARNING] Sample Size: Total sample size (30) is small. Metric uncertainty
is approximately 1.8x higher than with 100 samples.
  → Recommendation: Collect 70 more samples to reduce uncertainty, or report
    confidence intervals with all metrics.

[WARNING] High Metric Uncertainty: Metric uncertainty is high (±9.1% for
accuracy). With n=30, differences smaller than ~18.2% may not be meaningful.
  → Recommendation: Need 120 samples to halve the uncertainty, or always
    report confidence intervals when comparing models.
================================================================================
```

### Research Foundation

The warning system is based on:
- **Chicco et al.** - Studies on MCC advantages and metric limitations
- **Lovell et al.** - Research showing uncertainty scales as 1/√N
- **Fazekas & Kovács** - Work on numerical consistency in ML evaluation

## 📊 Statistical Testing (NEW!)

DConfusion now includes rigorous statistical methods to compare models and quantify uncertainty in your metrics.

### Bootstrap Confidence Intervals

Estimate the uncertainty in any metric using bootstrap resampling. Unlike traditional methods, bootstrap doesn't assume any particular distribution and works well for small samples and complex metrics like F1 score.

```python
from dconfusion import DConfusion

# Create a confusion matrix
cm = DConfusion(true_positive=85, false_negative=15,
                false_positive=10, true_negative=90)

# Calculate 95% confidence interval for accuracy
result = cm.get_bootstrap_confidence_interval(
    metric='accuracy',
    confidence_level=0.95,
    n_bootstrap=1000,
    random_state=42
)

print(f"Accuracy: {result['point_estimate']:.3f}")
print(f"95% CI: [{result['lower']:.3f}, {result['upper']:.3f}]")
print(f"Std Error: {result['std_error']:.3f}")
```

**Output:**
```
Accuracy: 0.875
95% CI: [0.825, 0.915]
Std Error: 0.023
```

**Supported metrics:** accuracy, precision, recall, specificity, f1_score, and more!

### McNemar's Test for Paired Comparison

Compare two models tested on the same dataset using McNemar's test. This is more powerful than simply comparing accuracies because it accounts for the paired nature of predictions.

```python
# Two models tested on the same data
model_a = DConfusion(true_positive=85, false_negative=15,
                     false_positive=10, true_negative=90)

model_b = DConfusion(true_positive=80, false_negative=20,
                     false_positive=8, true_negative=92)

# Run McNemar's test
result = model_a.mcnemar_test(model_b, alpha=0.05)

print(f"Test Statistic: {result['statistic']:.4f}")
print(f"P-value: {result['p_value']:.4f}")
print(f"Significant: {result['significant']}")
print(f"Interpretation: {result['interpretation']}")
```

**Output:**
```
Test Statistic: 1.3333
P-value: 0.2482
Significant: False
Interpretation: No significant difference between models (p=0.2482)
```

**Key advantages:**
- Specifically designed for paired classifier comparison
- More powerful than unpaired tests
- Accounts for cases where both models agree
- Provides effect size (odds ratio)

### Metric Consistency Check

Verify that reported metrics match what would be computed from a confusion matrix. Useful for validating results from papers or detecting reporting errors.

```python
cm = DConfusion(true_positive=85, false_negative=15,
                false_positive=10, true_negative=90)

# Check if metrics are consistent
result = cm.check_metric_consistency({
    'accuracy': 0.875,
    'precision': 0.8947,
    'recall': 0.85,
    'f1_score': 0.8718
})

print(f"All metrics consistent: {result['consistent']}")
if not result['consistent']:
    print(f"Mismatches: {result['mismatches']}")
    for metric, details in result['details'].items():
        if details['status'] == 'mismatch':
            print(f"  {metric}: Expected {details['expected']:.4f}, "
                  f"Got {details['actual']:.4f}")
```

### Statistical Testing in Web UI

The Streamlit app includes an interactive **Statistical Testing** tab where you can:
- Calculate bootstrap confidence intervals for any model and metric
- Run McNemar's test to compare two models
- Visualize results with clear interpretations
- Adjust parameters (confidence level, bootstrap samples, significance level)

```bash
streamlit run app/streamlit_app.py
```

### Research Foundation

The statistical methods are based on established research:
- **Efron & Tibshirani (1993)** - Bootstrap methods for standard errors and confidence intervals
- **McNemar (1947)** - Note on the sampling error of the difference between correlated proportions
- **Dietterich (1998)** - Approximate statistical tests for comparing supervised classification learning algorithms

# Roadmap
This is the initial release (v0.2.1) of dconfusion, and we plan to add more features in future releases. Some potential features include:
- Backtracing statistical metrics based on partial data
- Integration with popular machine learning libraries

# Contributing
We welcome contributions to dconfusion! If you'd like to contribute, please fork the repository and submit a pull request.

# License
dconfusion is released under the MIT License. See LICENSE for details.

# Changelog
- v0.1: Initial release with basic confusion matrix representation and frequency calculation
- v0.2: Added support for multi-class confusion matrices
- v0.2.1: Added support for plotting confusion matrices
- v0.2.2: Added more metrics and CSV functionality. QOL improvements. Began adding validation functionality.
- v1.0.0: Broke the file into multiple modules for better modularity. Added support for warnings.
- v1.0.1: Updated documentation. Added new statistical tests.