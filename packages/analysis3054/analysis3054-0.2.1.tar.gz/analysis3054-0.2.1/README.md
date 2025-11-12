# EIA Band Plot & Time Series Forecasting

This package provides two primary utilities:

* **`five_year_plot`** – Generate interactive 5‑year band plots using
  Plotly.  These plots mirror the charts used by the U.S. Energy
  Information Administration (EIA) to contextualize recent values
  against the range, minimum, maximum and average of the last five
  years.  Multiple numeric columns within a DataFrame can be plotted
  simultaneously as separate subplots.

* **`ml_forecast`** – Train individual AutoGluon time series models
  for each numeric column in a DataFrame and forecast future values.
  The function returns a DataFrame with point forecasts and, if
  requested, prediction intervals.  Each series is trained
  independently using the specified presets (default: `best_quality`).

## Installation

Install the package with:


```bash
pip install analysis3054
```

To enable the optional machine‑learning forecasting features, also
install the AutoGluon time series dependency:

```bash
pip install analysis3054[ml]
```

## Usage

### Five‑Year Band Plot

```python
import pandas as pd
from analysis3054 import five_year_plot

# Example DataFrame with a 'date' column and one or more numeric columns
df = pd.read_csv("my_timeseries_data.csv")

# Create the plot
fig = five_year_plot(date='date', df=df, prior_year_lines=1)
fig.show()
```

### Machine Learning Forecasting

```python
import pandas as pd
from analysis3054 import ml_forecast

df = pd.read_csv("my_timeseries_data.csv")

# Forecast the next 12 periods for each numeric column
result = ml_forecast(date='date', df=df, periods=12)

# Access point forecasts
forecasts = result.forecasts

# Access confidence intervals (if requested)
conf_ints = result.conf_intervals
```

See the docstrings of each function for detailed parameter descriptions.

## User Guide

For a complete overview of all available functions, advanced
forecasting methods, statistical analyses and plotting utilities,
consult the **USER_GUIDE.md** file included with the package.  It
provides step‑by‑step examples, explains optional parameters such as
confidence interval computation and plotting, and offers best
practices for combining models and interpreting results.
