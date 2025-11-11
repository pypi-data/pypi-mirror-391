"""
Advanced time‑series forecasting methods.

This module implements additional forecasting algorithms beyond the
machine‑learning and harmonic approaches already available in the
package.  These methods rely on external libraries such as
``statsmodels`` and ``pmdarima`` to provide robust statistical
models.  If the required libraries are not available, informative
errors are raised to guide the user toward installation.

Included functions:

* :func:`arima_forecast` – Fit classical ARIMA or SARIMA models to
  univariate series using Statsmodels.  Supports automatic order
  selection via a simple grid search.
* :func:`ets_forecast` – Fit Holt–Winters exponential smoothing
  models (ETS) to univariate series.
* :func:`var_forecast` – Fit Vector Autoregression (VAR) models to
  multivariate data, capturing linear interdependencies among
  variables.
* :func:`auto_arima_forecast` – Use pmdarima’s ``auto_arima`` to
  automatically identify the best ARIMA model for each series based
  on information criteria.
* :func:`prophet_forecast` – Forecast with Facebook’s Prophet model.
  This function is available only if the ``prophet`` package is
  installed.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional, Tuple, Union

import numpy as np
import pandas as pd


@dataclass
class ArimaForecastResult:
    """Result container for :func:`arima_forecast`.

    Attributes
    ----------
    forecasts : pandas.DataFrame
        Forecasted values for each series.  The index contains the
        forecast dates and the columns correspond to those of the
        input (excluding the date column).
    models : Dict[str, object]
        Fitted SARIMAX results objects from Statsmodels for each
        series.
    """

    forecasts: pd.DataFrame
    models: Dict[str, object]


def arima_forecast(
    date: Union[str, pd.Series, Iterable],
    df: pd.DataFrame,
    *,
    periods: int = 12,
    order: Optional[Tuple[int, int, int]] = None,
    seasonal_order: Optional[Tuple[int, int, int, int]] = None,
    freq: Optional[str] = None,
    auto: bool = False,
    max_p: int = 2,
    max_d: int = 1,
    max_q: int = 2,
    information_criterion: str = 'aic',
) -> ArimaForecastResult:
    """Forecast one or more series using ARIMA models.

    See module documentation for full details.  Requires the
    ``statsmodels`` package.
    """
    try:
        from statsmodels.tsa.statespace.sarimax import SARIMAX
    except Exception as e:
        raise ImportError(
            "statsmodels is required for ARIMA forecasting. "
            "Please install statsmodels to use this function."
        ) from e
    # Determine date series
    if isinstance(date, str):
        if date not in df.columns:
            raise KeyError(f"Date column '{date}' not found in DataFrame")
        date_series = df[date]
    else:
        date_series = pd.Series(date)
    dt = pd.to_datetime(date_series)
    if dt.empty:
        raise ValueError("Date series is empty")
    # Determine numeric columns
    numeric_cols: List[str] = [c for c in df.columns if c != date and pd.api.types.is_numeric_dtype(df[c])]
    if not numeric_cols:
        raise ValueError("No numeric data columns found for ARIMA forecasting")
    # Infer frequency if not provided
    if freq is None:
        try:
            freq = pd.infer_freq(dt)
        except Exception:
            freq = None
    # Prepare future dates
    if freq is not None:
        try:
            future_index = pd.date_range(start=dt.iloc[-1], periods=periods + 1, freq=freq)[1:]
        except Exception:
            freq = None
            future_index = None
    if freq is None:
        diffs = dt.diff().dropna()
        delta = diffs.mode()[0] if not diffs.empty else pd.Timedelta(days=1)
        future_index = pd.to_datetime([dt.iloc[-1] + delta * (i + 1) for i in range(periods)])
    # Storage
    forecasts_data: Dict[str, np.ndarray] = {}
    models: Dict[str, object] = {}
    # Define grid search ranges
    p_range = range(0, max_p + 1)
    d_range = range(0, max_d + 1)
    q_range = range(0, max_q + 1)
    for col in numeric_cols:
        y = pd.to_numeric(df[col], errors='coerce').ffill().bfill().astype(float)
        best_ic = np.inf
        best_res = None
        if auto:
            for p in p_range:
                for d in d_range:
                    for q in q_range:
                        try:
                            mod = SARIMAX(
                                y,
                                order=(p, d, q),
                                seasonal_order=seasonal_order,
                                enforce_stationarity=False,
                                enforce_invertibility=False,
                            )
                            res = mod.fit(disp=False)
                            ic_val = res.aic if information_criterion == 'aic' else res.bic
                            if np.isfinite(ic_val) and ic_val < best_ic:
                                best_ic = ic_val
                                best_res = res
                        except Exception:
                            continue
            if best_res is None:
                raise ValueError(f"Auto ARIMA failed to fit any model for column '{col}'")
        else:
            if order is None:
                raise ValueError("order must be specified when auto=False")
            mod = SARIMAX(
                y,
                order=order,
                seasonal_order=seasonal_order,
                enforce_stationarity=False,
                enforce_invertibility=False,
            )
            best_res = mod.fit(disp=False)
        # Forecast
        forecast = best_res.forecast(steps=periods)
        forecasts_data[col] = forecast.values
        models[col] = best_res
    forecast_df = pd.DataFrame(forecasts_data, index=future_index, columns=numeric_cols)
    return ArimaForecastResult(forecasts=forecast_df, models=models)


@dataclass
class EtsForecastResult:
    """Result container for :func:`ets_forecast`.

    Attributes
    ----------
    forecasts : pandas.DataFrame
        Forecasted values for each series.  The index contains the
        forecast dates and the columns correspond to those of the
        input (excluding the date column).
    models : Dict[str, object]
        Fitted ExponentialSmoothing results objects from Statsmodels.
    """

    forecasts: pd.DataFrame
    models: Dict[str, object]


def ets_forecast(
    date: Union[str, pd.Series, Iterable],
    df: pd.DataFrame,
    *,
    periods: int = 12,
    seasonal_periods: Optional[int] = None,
    trend: Optional[str] = 'add',
    seasonal: Optional[str] = 'add',
    damped_trend: bool = False,
    freq: Optional[str] = None,
) -> EtsForecastResult:
    """Forecast one or more series using exponential smoothing (ETS).

    See module documentation for details.  Requires the ``statsmodels``
    package.
    """
    try:
        from statsmodels.tsa.holtwinters import ExponentialSmoothing
    except Exception as e:
        raise ImportError(
            "statsmodels is required for exponential smoothing. "
            "Please install statsmodels to use this function."
        ) from e
    # Determine date series
    if isinstance(date, str):
        if date not in df.columns:
            raise KeyError(f"Date column '{date}' not found in DataFrame")
        date_series = df[date]
    else:
        date_series = pd.Series(date)
    dt = pd.to_datetime(date_series)
    if dt.empty:
        raise ValueError("Date series is empty")
    numeric_cols = [c for c in df.columns if c != date and pd.api.types.is_numeric_dtype(df[c])]
    if not numeric_cols:
        raise ValueError("No numeric data columns found for exponential smoothing")
    # Infer frequency if not provided
    if freq is None:
        try:
            freq = pd.infer_freq(dt)
        except Exception:
            freq = None
    # Determine seasonal_periods if not provided
    if seasonal_periods is None and freq is not None:
        if freq.startswith('M'):
            seasonal_periods = 12
        elif freq.startswith('W'):
            seasonal_periods = 52
        elif freq.startswith('Q'):
            seasonal_periods = 4
        elif freq.startswith('A') or freq.startswith('Y'):
            seasonal_periods = 1
        else:
            seasonal_periods = None
    # Prepare future dates
    if freq is not None:
        try:
            future_index = pd.date_range(start=dt.iloc[-1], periods=periods + 1, freq=freq)[1:]
        except Exception:
            freq = None
            future_index = None
    if freq is None:
        diffs = dt.diff().dropna()
        delta = diffs.mode()[0] if not diffs.empty else pd.Timedelta(days=1)
        future_index = pd.to_datetime([dt.iloc[-1] + delta * (i + 1) for i in range(periods)])
    forecasts_data: Dict[str, np.ndarray] = {}
    models: Dict[str, object] = {}
    for col in numeric_cols:
        y = pd.to_numeric(df[col], errors='coerce').ffill().bfill().astype(float)
        # If no seasonal_periods is provided, disable seasonal component
        seasonal_comp = seasonal
        seasonal_periods_comp = seasonal_periods
        if seasonal_periods_comp is None:
            seasonal_comp = None
        model = ExponentialSmoothing(
            y,
            trend=trend,
            damped_trend=damped_trend,
            seasonal=seasonal_comp,
            seasonal_periods=seasonal_periods_comp,
        )
        res = model.fit()
        forecasts_data[col] = res.forecast(periods).values
        models[col] = res
    forecast_df = pd.DataFrame(forecasts_data, index=future_index, columns=numeric_cols)
    return EtsForecastResult(forecasts=forecast_df, models=models)


@dataclass
class VarForecastResult:
    """Result container for :func:`var_forecast`.

    Attributes
    ----------
    forecasts : pandas.DataFrame
        Forecasted values for all series.  The index contains the
        forecast dates and the columns correspond to the selected
        numeric columns.
    model : object
        Fitted VAR model instance from statsmodels.
    """

    forecasts: pd.DataFrame
    model: object


def var_forecast(
    date: Union[str, pd.Series, Iterable],
    df: pd.DataFrame,
    *,
    periods: int = 12,
    maxlags: int = 4,
    deterministic: str = 'c',
    freq: Optional[str] = None,
) -> VarForecastResult:
    """Forecast a multivariate time series using Vector Autoregression (VAR).

    This function fits a VAR model to all numeric columns of the
    provided DataFrame and generates forecasts ``periods`` steps
    ahead.  The optimal lag order is selected based on the Akaike
    information criterion.  Deterministic terms (constant and/or
    trend) can be specified via the ``deterministic`` argument.

    Parameters
    ----------
    date : str or pandas.Series or iterable
        Column name, series or iterable containing date information.
    df : pandas.DataFrame
        DataFrame with the data.  All numeric columns are included in
        the VAR model.
    periods : int, default 12
        Number of future periods to forecast.
    maxlags : int, default 4
        Maximum number of lags to consider when fitting the VAR model.
    deterministic : {'n','c','t','ct'}, default 'c'
        Specifies which deterministic terms to include in the model.
        'n' includes no constant or trend, 'c' adds a constant,
        't' adds a linear trend and 'ct' includes both constant and
        trend.
    freq : str or None, default None
        Pandas frequency string for generating forecast dates.  If
        ``None``, the frequency is inferred from the date series.

    Returns
    -------
    VarForecastResult
        Dataclass containing the forecast DataFrame and the fitted
        VAR model.

    Raises
    ------
    ImportError
        If the ``statsmodels`` package is not installed.
    """
    try:
        from statsmodels.tsa.api import VAR
    except Exception as e:
        raise ImportError(
            "statsmodels is required for VAR forecasting. "
            "Please install statsmodels to use this function."
        ) from e
    if isinstance(date, str):
        if date not in df.columns:
            raise KeyError(f"Date column '{date}' not found in DataFrame")
        date_series = df[date]
    else:
        date_series = pd.Series(date)
    dt = pd.to_datetime(date_series)
    if dt.empty:
        raise ValueError("Date series is empty")
    numeric_cols = [c for c in df.columns if c != date and pd.api.types.is_numeric_dtype(df[c])]
    if not numeric_cols:
        raise ValueError("No numeric data columns found for VAR forecasting")
    y = df[numeric_cols].ffill().bfill().astype(float)
    model = VAR(y)
    results = model.select_order(maxlags)
    selected_lag = results.selected_orders['aic']
    var_res = model.fit(selected_lag or 1, trend=deterministic)
    forecast_values = var_res.forecast(y.values[-var_res.k_ar:], periods)
    # Determine future dates
    if freq is None:
        try:
            freq = pd.infer_freq(dt)
        except Exception:
            freq = None
    if freq is not None:
        try:
            future_index = pd.date_range(start=dt.iloc[-1], periods=periods + 1, freq=freq)[1:]
        except Exception:
            freq = None
            future_index = None
    if freq is None:
        diffs = dt.diff().dropna()
        delta = diffs.mode()[0] if not diffs.empty else pd.Timedelta(days=1)
        future_index = pd.to_datetime([dt.iloc[-1] + delta * (i + 1) for i in range(periods)])
    forecast_df = pd.DataFrame(forecast_values, index=future_index, columns=numeric_cols)
    return VarForecastResult(forecasts=forecast_df, model=var_res)


# ---------------------------------------------------------------------------
# VECM Forecasting
# ---------------------------------------------------------------------------

@dataclass
class VecmForecastResult:
    """Result container for :func:`vecm_forecast`.

    Attributes
    ----------
    forecasts : pandas.DataFrame
        Forecasted values for all series.  The index contains the
        forecast dates and the columns correspond to the numeric
        columns of the input (excluding the date column).
    model : object
        Fitted VECM model instance from statsmodels.  May be
        ``None`` if a fallback model was used.
    """
    forecasts: pd.DataFrame
    model: object


def vecm_forecast(
    date: Union[str, pd.Series, Iterable],
    df: pd.DataFrame,
    *,
    periods: int = 12,
    coint_rank: Optional[int] = None,
    deterministic: str = 'ci',
    freq: Optional[str] = None,
) -> VecmForecastResult:
    """Forecast a cointegrated multivariate time series using VECM.

    This function fits a Vector Error Correction Model (VECM) to the
    numeric columns of the provided DataFrame.  If the cointegration
    rank is not specified, it is estimated via the Johansen trace
    test.  The optimal lag difference order is selected based on the
    Akaike information criterion.  When VECM fitting fails, the
    function falls back to VAR forecasting.

    Parameters
    ----------
    date : str or pandas.Series or iterable
        Column name, series or iterable containing date information.
    df : pandas.DataFrame
        DataFrame with the data.  All numeric columns are included
        in the VECM model.
    periods : int, default 12
        Number of future periods to forecast.
    coint_rank : int or None, default None
        Number of cointegrating relationships.  If ``None``, the
        rank is estimated from the data using the Johansen test.
    deterministic : {'n','c','ci','ct','cti'}, default 'ci'
        Deterministic terms to include in the model.  See
        ``statsmodels.tsa.vector_ar.vecm.VECM`` for details.
    freq : str or None, default None
        Pandas frequency string for generating forecast dates.  If
        ``None``, the frequency is inferred from the date series.

    Returns
    -------
    VecmForecastResult
        Dataclass containing the forecast DataFrame and the fitted
        VECM model.  If the VECM fails, the model attribute is
        ``None`` and the forecasts come from a VAR fallback.

    Raises
    ------
    ImportError
        If the ``statsmodels`` package is not installed.
    ValueError
        If no numeric columns are available for modelling.
    """
    try:
        from statsmodels.tsa.vector_ar.vecm import VECM, select_order, select_coint_rank
    except Exception as e:
        raise ImportError(
            "statsmodels is required for VECM forecasting. "
            "Please install statsmodels to use this function."
        ) from e
    # Determine date series
    if isinstance(date, str):
        if date not in df.columns:
            raise KeyError(f"Date column '{date}' not found in DataFrame")
        date_series = df[date]
    else:
        date_series = pd.Series(date)
    dt = pd.to_datetime(date_series)
    if dt.empty:
        raise ValueError("Date series is empty")
    # Identify numeric columns
    numeric_cols = [c for c in df.columns if c != date and pd.api.types.is_numeric_dtype(df[c])]
    if not numeric_cols:
        raise ValueError("No numeric data columns found for VECM forecasting")
    y = df[numeric_cols].ffill().bfill().astype(float)
    # Estimate cointegration rank if not provided
    est_rank = coint_rank
    if est_rank is None:
        try:
            rank_res = select_coint_rank(y, det_order=0, k_ar_diff=1, method='trace', signif=0.05)
            est_rank = rank_res.rank
        except Exception:
            est_rank = 0
    # Determine lag order using select_order
    try:
        order_res = select_order(y, maxlags=10, deterministic=deterministic)
        k_ar_diff = order_res.aic or 1
    except Exception:
        k_ar_diff = 1
    # Fit VECM model
    vecm_res = None
    forecast_values = None
    try:
        vecm_model = VECM(y, k_ar_diff=k_ar_diff, coint_rank=est_rank, deterministic=deterministic)
        vecm_res = vecm_model.fit()
        # Forecast returns an array of shape (periods, n_vars)
        forecast_values = vecm_res.predict(steps=periods)
    except Exception:
        vecm_res = None
    # If VECM failed, fallback to VAR
    if forecast_values is None or vecm_res is None:
        var_result = var_forecast(date, df, periods=periods, deterministic='c', freq=freq)
        return VecmForecastResult(forecasts=var_result.forecasts, model=None)
    # Determine future dates
    if freq is None:
        try:
            freq = pd.infer_freq(dt)
        except Exception:
            freq = None
    if freq is not None:
        try:
            future_index = pd.date_range(start=dt.iloc[-1], periods=periods + 1, freq=freq)[1:]
        except Exception:
            freq = None
            future_index = None
    if freq is None:
        diffs = dt.diff().dropna()
        delta = diffs.mode()[0] if not diffs.empty else pd.Timedelta(days=1)
        future_index = pd.to_datetime([dt.iloc[-1] + delta * (i + 1) for i in range(periods)])
    forecast_df = pd.DataFrame(forecast_values, index=future_index, columns=numeric_cols)
    return VecmForecastResult(forecasts=forecast_df, model=vecm_res)


@dataclass
class AutoArimaForecastResult:
    """Result container for :func:`auto_arima_forecast`.

    Attributes
    ----------
    forecasts : pandas.DataFrame
        Forecasted values for each series.
    models : Dict[str, object]
        Fitted pmdarima ARIMA models for each series.
    """

    forecasts: pd.DataFrame
    models: Dict[str, object]


def auto_arima_forecast(
    date: Union[str, pd.Series, Iterable],
    df: pd.DataFrame,
    *,
    periods: int = 12,
    seasonal: bool = False,
    m: int = 1,
    max_order: Optional[int] = None,
    freq: Optional[str] = None,
    information_criterion: str = 'aic',
) -> AutoArimaForecastResult:
    """Forecast one or more series using ``pmdarima.auto_arima``.

    This function leverages the pmdarima library to automatically
    identify and fit the best ARIMA model (with optional seasonal
    components) for each numeric series based on information
    criteria.  It returns the fitted models and the forecasts.

    Parameters
    ----------
    date : str or pandas.Series or iterable
        Column name, series, or iterable containing date information.
    df : pandas.DataFrame
        DataFrame with the data.  Numeric columns will be modelled
        individually.
    periods : int, default 12
        Number of future periods to forecast.
    seasonal : bool, default False
        Whether to consider seasonal models.
    m : int, default 1
        Number of periods in a season (e.g. 12 for monthly).  Only
        relevant if ``seasonal`` is True.
    max_order : int or None, default None
        Maximum value of p+q (or p+q+P+Q if seasonal) to consider.
        If None, defaults to 5 for non-seasonal and 2 for seasonal.
    freq : str or None, default None
        Pandas frequency string used to generate forecast dates.  If
        ``None``, the frequency is inferred from the date series.
    information_criterion : str, default 'aic'
        Criterion used to select the best model.  One of 'aic',
        'bic', 'hqic', etc., as supported by pmdarima.

    Returns
    -------
    AutoArimaForecastResult
        Dataclass containing the forecast DataFrame and fitted models.

    Raises
    ------
    ImportError
        If the ``pmdarima`` package is not installed.
    """
    try:
        import pmdarima as pm
    except Exception as e:
        raise ImportError(
            "pmdarima is required for auto_arima_forecast. "
            "Please install pmdarima to use this function."
        ) from e
    # Determine date series
    if isinstance(date, str):
        if date not in df.columns:
            raise KeyError(f"Date column '{date}' not found in DataFrame")
        date_series = df[date]
    else:
        date_series = pd.Series(date)
    dt = pd.to_datetime(date_series)
    if dt.empty:
        raise ValueError("Date series is empty")
    numeric_cols = [c for c in df.columns if c != date and pd.api.types.is_numeric_dtype(df[c])]
    if not numeric_cols:
        raise ValueError("No numeric data columns found for auto_arima forecasting")
    # Infer frequency if not provided
    if freq is None:
        try:
            freq = pd.infer_freq(dt)
        except Exception:
            freq = None
    # Prepare future dates
    if freq is not None:
        try:
            future_index = pd.date_range(start=dt.iloc[-1], periods=periods + 1, freq=freq)[1:]
        except Exception:
            freq = None
            future_index = None
    if freq is None:
        diffs = dt.diff().dropna()
        delta = diffs.mode()[0] if not diffs.empty else pd.Timedelta(days=1)
        future_index = pd.to_datetime([dt.iloc[-1] + delta * (i + 1) for i in range(periods)])
    forecasts_data: Dict[str, np.ndarray] = {}
    models: Dict[str, object] = {}
    for col in numeric_cols:
        y = pd.to_numeric(df[col], errors='coerce').ffill().bfill().astype(float)
        model = pm.auto_arima(
            y,
            seasonal=seasonal,
            m=m,
            information_criterion=information_criterion,
            max_order=max_order,
            error_action='ignore',
            suppress_warnings=True,
        )
        forecast = model.predict(n_periods=periods)
        forecasts_data[col] = forecast
        models[col] = model
    forecast_df = pd.DataFrame(forecasts_data, index=future_index, columns=numeric_cols)
    return AutoArimaForecastResult(forecasts=forecast_df, models=models)


@dataclass
class ProphetForecastResult:
    """Result container for :func:`prophet_forecast`.

    Attributes
    ----------
    forecasts : pandas.DataFrame
        Forecasted values for each series.  The index contains the
        forecast dates and the columns correspond to those of the
        input (excluding the date column).
    models : Dict[str, object]
        Fitted Prophet models for each series.
    """

    forecasts: pd.DataFrame
    models: Dict[str, object]


def prophet_forecast(
    date: Union[str, pd.Series, Iterable],
    df: pd.DataFrame,
    *,
    periods: int = 12,
    freq: Optional[str] = None,
    seasonality_mode: str = 'additive',
    yearly_seasonality: Optional[bool] = None,
    weekly_seasonality: Optional[bool] = None,
    daily_seasonality: Optional[bool] = None,
) -> ProphetForecastResult:
    """Forecast one or more series using Facebook Prophet.

    Prophet is a decomposable time series model that handles trend,
    seasonality and holidays.  This function fits a separate Prophet
    model to each numeric column and returns forecasts.  The Prophet
    library must be installed separately; if it is not found, an
    ImportError is raised.

    Parameters
    ----------
    date : str or pandas.Series or iterable
        Column name, series, or iterable containing date information.
    df : pandas.DataFrame
        DataFrame with the data.  Numeric columns will be modelled
        individually.
    periods : int, default 12
        Number of future periods to forecast.
    freq : str or None, default None
        Frequency string for generating future dates.  If None,
        ``pandas.infer_freq`` is used.
    seasonality_mode : {'additive','multiplicative'}, default 'additive'
        Mode of seasonality.  Additive is appropriate for series with
        constant seasonal amplitude, while multiplicative is better
        for series where the amplitude increases with the level.
    yearly_seasonality, weekly_seasonality, daily_seasonality : bool or None
        Whether to include yearly, weekly and daily seasonalities.  If
        None, Prophet’s defaults are used (enabled if data frequency
        supports it).

    Returns
    -------
    ProphetForecastResult
        Dataclass containing the forecast DataFrame and fitted models.

    Raises
    ------
    ImportError
        If the ``prophet`` package is not installed.
    """
    try:
        from prophet import Prophet
    except Exception as e:
        raise ImportError(
            "prophet is required for prophet_forecast. "
            "Please install prophet (pip install prophet) to use this function."
        ) from e
    # Determine date series
    if isinstance(date, str):
        if date not in df.columns:
            raise KeyError(f"Date column '{date}' not found in DataFrame")
        date_series = df[date]
    else:
        date_series = pd.Series(date)
    dt = pd.to_datetime(date_series)
    if dt.empty:
        raise ValueError("Date series is empty")
    numeric_cols = [c for c in df.columns if c != date and pd.api.types.is_numeric_dtype(df[c])]
    if not numeric_cols:
        raise ValueError("No numeric data columns found for Prophet forecasting")
    # Infer frequency if not provided
    if freq is None:
        try:
            freq = pd.infer_freq(dt)
        except Exception:
            freq = None
    # Prepare future dates for Prophet
    if freq is not None:
        try:
            future_dates = pd.date_range(start=dt.iloc[-1], periods=periods + 1, freq=freq)[1:]
        except Exception:
            freq = None
            future_dates = None
    if freq is None:
        diffs = dt.diff().dropna()
        delta = diffs.mode()[0] if not diffs.empty else pd.Timedelta(days=1)
        future_dates = pd.to_datetime([dt.iloc[-1] + delta * (i + 1) for i in range(periods)])
    forecasts_data: Dict[str, np.ndarray] = {}
    models: Dict[str, object] = {}
    for col in numeric_cols:
        # Prepare Prophet DataFrame with 'ds' and 'y'
        y = pd.to_numeric(df[col], errors='coerce').ffill().bfill().astype(float)
        train_df = pd.DataFrame({'ds': dt, 'y': y})
        m = Prophet(
            seasonality_mode=seasonality_mode,
            yearly_seasonality=yearly_seasonality,
            weekly_seasonality=weekly_seasonality,
            daily_seasonality=daily_seasonality,
        )
        m.fit(train_df)
        future_df = pd.DataFrame({'ds': future_dates})
        forecast = m.predict(future_df)
        forecasts_data[col] = forecast['yhat'].values
        models[col] = m
    forecast_df = pd.DataFrame(forecasts_data, index=future_dates, columns=numeric_cols)
    return ProphetForecastResult(forecasts=forecast_df, models=models)

# ---------------------------------------------------------------------------
# Machine‑learning and ensemble forecasting
# ---------------------------------------------------------------------------


@dataclass
class RandomForestForecastResult:
    """Result container for :func:`random_forest_forecast`.

    Attributes
    ----------
    forecasts : pandas.DataFrame
        Forecasted values for each series.  The index contains the
        forecast dates and the columns correspond to those of the
        input (excluding the date column).
    models : Dict[str, object]
        Fitted scikit‑learn RandomForestRegressor models for each
        series.
    """

    forecasts: pd.DataFrame
    models: Dict[str, object]


def random_forest_forecast(
    date: Union[str, pd.Series, Iterable],
    df: pd.DataFrame,
    *,
    periods: int = 12,
    n_lags: int = 3,
    n_estimators: int = 100,
    max_features: Union[int, float, str] = 'auto',
    random_state: Optional[int] = None,
    freq: Optional[str] = None,
) -> RandomForestForecastResult:
    """Forecast one or more series using Random Forest regressors.

    This function trains a separate RandomForestRegressor for each
    numeric series, using lagged values as features.  Forecasts are
    generated iteratively: predicted values are fed back as inputs to
    produce multi‑step forecasts.

    Parameters
    ----------
    date : str or pandas.Series or iterable
        Column name, series, or iterable containing date information.
    df : pandas.DataFrame
        DataFrame with the data.  Numeric columns will be modelled
        individually.
    periods : int, default 12
        Number of future periods to forecast.
    n_lags : int, default 3
        Number of past observations to use as features.  Larger
        values capture longer memory but increase model complexity.
    n_estimators : int, default 100
        Number of trees in the random forest.
    max_features : int, float or str, default 'auto'
        Number of features considered when looking for the best split.
        Follows scikit‑learn conventions.
    random_state : int or None, default None
        Random seed for reproducibility.
    freq : str or None, default None
        Frequency string for generating forecast dates.  If None,
        inferred via ``pandas.infer_freq``.

    Returns
    -------
    RandomForestForecastResult
        Dataclass containing the forecast DataFrame and fitted models.

    Raises
    ------
    ImportError
        If scikit‑learn is not installed.
    """
    try:
        from sklearn.ensemble import RandomForestRegressor
    except Exception as e:
        raise ImportError(
            "scikit-learn is required for random_forest_forecast. "
            "Please install scikit-learn to use this function."
        ) from e
    # Determine date series
    if isinstance(date, str):
        if date not in df.columns:
            raise KeyError(f"Date column '{date}' not found in DataFrame")
        date_series = df[date]
    else:
        date_series = pd.Series(date)
    dt = pd.to_datetime(date_series)
    if dt.empty:
        raise ValueError("Date series is empty")
    numeric_cols = [c for c in df.columns if c != date and pd.api.types.is_numeric_dtype(df[c])]
    if not numeric_cols:
        raise ValueError("No numeric data columns found for Random Forest forecasting")
    # Infer frequency if not provided
    if freq is None:
        try:
            freq = pd.infer_freq(dt)
        except Exception:
            freq = None
    # Prepare future dates
    if freq is not None:
        try:
            future_index = pd.date_range(start=dt.iloc[-1], periods=periods + 1, freq=freq)[1:]
        except Exception:
            freq = None
            future_index = None
    if freq is None:
        diffs = dt.diff().dropna()
        delta = diffs.mode()[0] if not diffs.empty else pd.Timedelta(days=1)
        future_index = pd.to_datetime([dt.iloc[-1] + delta * (i + 1) for i in range(periods)])
    forecasts_data: Dict[str, List[float]] = {}
    models: Dict[str, object] = {}
    for col in numeric_cols:
        series = pd.to_numeric(df[col], errors='coerce').ffill().bfill().astype(float)
        # Build lag matrix
        X = []
        y_target = []
        for i in range(n_lags, len(series)):
            X.append(series.iloc[i - n_lags:i].values)
            y_target.append(series.iloc[i])
        if not X:
            raise ValueError(f"Series '{col}' is too short for {n_lags} lags")
        X_train = np.array(X)
        y_train = np.array(y_target)
        # Fit model
        model = RandomForestRegressor(
            n_estimators=n_estimators,
            max_features=max_features,
            random_state=random_state,
        )
        model.fit(X_train, y_train)
        models[col] = model
        # Generate forecasts
        history = list(series.iloc[-n_lags:].values)
        preds = []
        for _ in range(periods):
            pred = model.predict([np.array(history[-n_lags:])])[0]
            preds.append(pred)
            history.append(pred)
        forecasts_data[col] = preds
    forecast_df = pd.DataFrame(forecasts_data, index=future_index, columns=numeric_cols)
    return RandomForestForecastResult(forecasts=forecast_df, models=models)


@dataclass
class EnsembleForecastResult:
    """Result container for :func:`ensemble_forecast`.

    Attributes
    ----------
    forecasts : pandas.DataFrame
        Forecasted values as the unweighted average of component
        forecasts for each series.
    components : Dict[str, pd.DataFrame]
        Forecast DataFrames from each individual method.
    """
    forecasts: pd.DataFrame
    components: Dict[str, pd.DataFrame]


def ensemble_forecast(
    date: Union[str, pd.Series, Iterable],
    df: pd.DataFrame,
    *,
    periods: int = 12,
    methods: Optional[List[str]] = None,
    freq: Optional[str] = None,
    random_state: Optional[int] = None,
) -> EnsembleForecastResult:
    """Combine multiple forecasting methods by averaging their predictions.

    This function runs a set of selected forecasting algorithms on
    the same data and computes an unweighted average of their
    forecasts.  By combining different model classes, ensemble
    forecasts often achieve greater accuracy than any single method
    alone.

    Parameters
    ----------
    date : str or pandas.Series or iterable
        Column name, series or iterable containing date information.
    df : pandas.DataFrame
        DataFrame with the data.  Numeric columns will be modelled
        individually.
    periods : int, default 12
        Number of future periods to forecast.
    methods : list of str or None, default None
        Forecasting methods to include in the ensemble.  If None,
        defaults to ['auto_arima','ets','unobserved_components','random_forest'].
        Supported method names include:

        - 'auto_arima' – pmdarima auto ARIMA (via :func:`auto_arima_forecast`)
        - 'ets' – Exponential smoothing (via :func:`ets_forecast`)
        - 'unobserved_components' – UC model (via :func:`unobserved_components_forecast`)
        - 'markov_switching' – Markov switching AR (via :func:`markov_switching_forecast`)
        - 'random_forest' – Random forest (via :func:`random_forest_forecast`)

    freq : str or None, default None
        Frequency string for generating forecast dates.  Passed to
        underlying functions when applicable.
    random_state : int or None, default None
        Random seed used by the random forest method.

    Returns
    -------
    EnsembleForecastResult
        Dataclass containing the combined forecast and a dictionary
        mapping method names to their individual forecast DataFrames.

    Notes
    -----
    Forecast horizons and indices are aligned based on the first
    method’s output.  If component forecasts have differing indices,
    they are reindexed to match via forward filling.
    """
    if methods is None:
        methods = ['auto_arima', 'ets', 'unobserved_components', 'random_forest']
    # Containers
    component_forecasts: Dict[str, pd.DataFrame] = {}
    # Generate forecasts for each method
    for method in methods:
        try:
            if method == 'auto_arima':
                res = auto_arima_forecast(date=date, df=df, periods=periods, freq=freq)
                component_forecasts[method] = res.forecasts
            elif method == 'ets':
                res = ets_forecast(date=date, df=df, periods=periods, freq=freq)
                component_forecasts[method] = res.forecasts
            elif method == 'unobserved_components':
                res = unobserved_components_forecast(date=date, df=df, periods=periods, freq=freq)
                component_forecasts[method] = res.forecasts
            elif method == 'markov_switching':
                res = markov_switching_forecast(date=date, df=df, periods=periods, freq=freq)
                component_forecasts[method] = res.forecasts
            elif method == 'random_forest':
                res = random_forest_forecast(date=date, df=df, periods=periods, freq=freq, random_state=random_state)
                component_forecasts[method] = res.forecasts
            else:
                raise ValueError(f"Unknown method '{method}' in ensemble_forecast")
        except Exception as e:
            # If a method fails, skip it and warn
            import warnings
            warnings.warn(f"Forecasting method '{method}' failed: {e}")
            continue
    if not component_forecasts:
        raise ValueError("No forecasts generated; check selected methods and data")
    # Align indices across component forecasts
    first_df = next(iter(component_forecasts.values()))
    combined = first_df.copy()
    # Reindex all forecasts to the first index using forward fill
    for name, f_df in component_forecasts.items():
        if f_df.index.equals(combined.index):
            continue
        component_forecasts[name] = f_df.reindex(combined.index, method='ffill')
    # Compute unweighted average
    sum_forecasts = sum(component_forecasts.values())
    avg_forecasts = sum_forecasts / len(component_forecasts)
    return EnsembleForecastResult(forecasts=avg_forecasts, components=component_forecasts)

# ---------------------------------------------------------------------------
# Advanced state‑space and regime switching models
# ---------------------------------------------------------------------------


@dataclass
class MarkovSwitchingForecastResult:
    """Result container for :func:`markov_switching_forecast`.

    Attributes
    ----------
    forecasts : pandas.DataFrame
        Forecasted values for each series using a Markov regime
        switching model.  The index contains the forecast dates and
        the columns correspond to those of the input (excluding the
        date column).
    models : Dict[str, object]
        Fitted MarkovAutoregression results for each series.
    """
    forecasts: pd.DataFrame
    models: Dict[str, object]


def markov_switching_forecast(
    date: Union[str, pd.Series, Iterable],
    df: pd.DataFrame,
    *,
    periods: int = 12,
    k_regimes: int = 2,
    order: int = 1,
    freq: Optional[str] = None,
) -> MarkovSwitchingForecastResult:
    """Forecast univariate series using a Markov switching autoregression.

    A Markov switching autoregression (also known as a regime‑
    switching model) allows the parameters of an AR process to change
    between a finite number of regimes according to an unobserved
    Markov chain.  This can capture structural breaks or non‑linear
    dynamics often present in commodity markets.

    Parameters
    ----------
    date : str or pandas.Series or iterable
        Column name, series or iterable containing date information.
    df : pandas.DataFrame
        DataFrame with the data.  Numeric columns will be modelled
        individually using univariate MarkovAutoregression models.
    periods : int, default 12
        Number of future periods to forecast.
    k_regimes : int, default 2
        Number of regimes (states) in the Markov chain.
    order : int, default 1
        Autoregressive order within each regime.
    freq : str or None, default None
        Frequency string for generating forecast dates.  If None,
        ``pandas.infer_freq`` is used.

    Returns
    -------
    MarkovSwitchingForecastResult
        Dataclass containing the forecast DataFrame and the fitted
        models.

    Raises
    ------
    ImportError
        If ``statsmodels`` does not have ``MarkovAutoregression``.
    """
    try:
        from statsmodels.tsa.regime_switching.markov_autoregression import MarkovAutoregression
    except Exception as e:
        raise ImportError(
            "statsmodels with regime_switching is required for Markov switching forecasting."
        ) from e
    # Determine date series
    if isinstance(date, str):
        if date not in df.columns:
            raise KeyError(f"Date column '{date}' not found in DataFrame")
        date_series = df[date]
    else:
        date_series = pd.Series(date)
    dt = pd.to_datetime(date_series)
    if dt.empty:
        raise ValueError("Date series is empty")
    numeric_cols = [c for c in df.columns if c != date and pd.api.types.is_numeric_dtype(df[c])]
    if not numeric_cols:
        raise ValueError("No numeric data columns found for Markov switching forecasting")
    # Infer frequency
    if freq is None:
        try:
            freq = pd.infer_freq(dt)
        except Exception:
            freq = None
    # Prepare future dates
    if freq is not None:
        try:
            future_index = pd.date_range(start=dt.iloc[-1], periods=periods + 1, freq=freq)[1:]
        except Exception:
            freq = None
            future_index = None
    if freq is None:
        diffs = dt.diff().dropna()
        delta = diffs.mode()[0] if not diffs.empty else pd.Timedelta(days=1)
        future_index = pd.to_datetime([dt.iloc[-1] + delta * (i + 1) for i in range(periods)])
    forecasts_data: Dict[str, np.ndarray] = {}
    models: Dict[str, object] = {}
    for col in numeric_cols:
        y = pd.to_numeric(df[col], errors='coerce').ffill().bfill().astype(float)
        # Fit Markov autoregression with constant term
        mod = MarkovAutoregression(y, k_regimes=k_regimes, order=order, trend='c')
        res = mod.fit()
        models[col] = res
        # Extract transition matrix for forecast: 2D array shape (k_regimes, k_regimes)
        # res.regime_transition has shape (k_regimes, k_regimes, time), but transitions are constant over time.
        trans = res.regime_transition[:, :, 0]
        # Extract intercepts and AR coefficients per regime
        param_names = res.model.param_names
        params = res.params
        const_vals: Dict[int, float] = {i: 0.0 for i in range(k_regimes)}
        ar_vals: Dict[int, Dict[int, float]] = {i: {} for i in range(k_regimes)}
        for idx, pname in enumerate(param_names):
            # Constant terms: 'const[i]'
            if pname.startswith('const['):
                state = int(pname.split('[')[1].split(']')[0])
                const_vals[state] = float(params.iloc[idx] if hasattr(params, 'iloc') else params[idx])
            # AR terms: 'ar.Lk[i]'
            elif pname.startswith('ar.L'):
                parts = pname.split('[')
                lag_part = parts[0]
                lag = int(lag_part.split('L')[1])
                state = int(parts[1].split(']')[0])
                if state not in ar_vals:
                    ar_vals[state] = {}
                ar_vals[state][lag] = float(params.iloc[idx] if hasattr(params, 'iloc') else params[idx])
        # Get smoothed state probabilities at final time
        try:
            p_states = res.smoothed_marginal_probabilities.iloc[-1].values.copy()
        except Exception:
            # If smoothed probabilities are unavailable, use stationary distribution
            eigvals, eigvecs = np.linalg.eig(trans.T)
            stat = np.real(eigvecs[:, np.isclose(eigvals, 1)])
            stat = stat / stat.sum()
            p_states = stat.ravel()
        # Initialize history with last observed values (for AR lags)
        history = list(y.iloc[-order:]) if order > 0 else []
        preds: List[float] = []
        for h in range(periods):
            # Forecast per state
            state_preds = []
            for i in range(k_regimes):
                # Constant term
                pred_i = const_vals.get(i, 0.0)
                # Add AR terms
                for lag in range(1, order + 1):
                    coeff = ar_vals.get(i, {}).get(lag, 0.0)
                    if lag <= len(history):
                        pred_i += coeff * history[-lag]
                state_preds.append(pred_i)
            # Weighted forecast
            weighted_pred = float(np.dot(p_states, state_preds))
            preds.append(weighted_pred)
            # Update history
            if order > 0:
                history.append(weighted_pred)
                if len(history) > order:
                    history.pop(0)
            # Update state probabilities for next step: p_{t+1} = p_t * trans
            p_states = np.dot(p_states, trans)
        forecasts_data[col] = np.array(preds)
    forecast_df = pd.DataFrame(forecasts_data, index=future_index, columns=numeric_cols)
    return MarkovSwitchingForecastResult(forecasts=forecast_df, models=models)


@dataclass
class UnobservedComponentsForecastResult:
    """Result container for :func:`unobserved_components_forecast`.

    Attributes
    ----------
    forecasts : pandas.DataFrame
        Forecasted values for each series using unobserved components
        models.  The index contains the forecast dates and the
        columns correspond to those of the input (excluding the date
        column).
    models : Dict[str, object]
        Fitted UnobservedComponents results for each series.
    """
    forecasts: pd.DataFrame
    models: Dict[str, object]


def unobserved_components_forecast(
    date: Union[str, pd.Series, Iterable],
    df: pd.DataFrame,
    *,
    periods: int = 12,
    level: bool = True,
    trend: bool = False,
    seasonal_periods: Optional[int] = None,
    freq: Optional[str] = None,
) -> UnobservedComponentsForecastResult:
    """Forecast univariate series using unobserved components models.

    Unobserved components (UC) models treat the observed series as a
    sum of latent components such as level, trend and seasonality.
    This function fits a UC model to each numeric column and
    forecasts future values.  It leverages the Kalman filter for
    state estimation.

    Parameters
    ----------
    date : str or pandas.Series or iterable
        Column name, series or iterable containing date information.
    df : pandas.DataFrame
        DataFrame with the data.  Numeric columns will be modelled
        individually using univariate UC models.
    periods : int, default 12
        Number of future periods to forecast.
    level : bool, default True
        Include a level component (local level) in the model.
    trend : bool, default False
        Include a trend component (local linear trend) in the model.
    seasonal_periods : int or None, default None
        Number of periods in the seasonal component.  If ``None``,
        seasonality is omitted.  For example, 12 for monthly data.
    freq : str or None, default None
        Frequency string for generating forecast dates.  If None,
        inferred using ``pandas.infer_freq``.

    Returns
    -------
    UnobservedComponentsForecastResult
        Dataclass containing the forecast DataFrame and the fitted
        models.

    Raises
    ------
    ImportError
        If the required ``statsmodels`` classes are not available.
    """
    try:
        from statsmodels.tsa.statespace.structural import UnobservedComponents
    except Exception as e:
        raise ImportError(
            "statsmodels is required for unobserved components forecasting."
        ) from e
    # Determine date series
    if isinstance(date, str):
        if date not in df.columns:
            raise KeyError(f"Date column '{date}' not found in DataFrame")
        date_series = df[date]
    else:
        date_series = pd.Series(date)
    dt = pd.to_datetime(date_series)
    if dt.empty:
        raise ValueError("Date series is empty")
    numeric_cols = [c for c in df.columns if c != date and pd.api.types.is_numeric_dtype(df[c])]
    if not numeric_cols:
        raise ValueError("No numeric data columns found for unobserved components forecasting")
    # Infer frequency and future dates
    if freq is None:
        try:
            freq = pd.infer_freq(dt)
        except Exception:
            freq = None
    if freq is not None:
        try:
            future_index = pd.date_range(start=dt.iloc[-1], periods=periods + 1, freq=freq)[1:]
        except Exception:
            freq = None
            future_index = None
    if freq is None:
        diffs = dt.diff().dropna()
        delta = diffs.mode()[0] if not diffs.empty else pd.Timedelta(days=1)
        future_index = pd.to_datetime([dt.iloc[-1] + delta * (i + 1) for i in range(periods)])
    forecasts_data: Dict[str, np.ndarray] = {}
    models: Dict[str, object] = {}
    for col in numeric_cols:
        y = pd.to_numeric(df[col], errors='coerce').ffill().bfill().astype(float)
        # Specify seasonal_periods if not provided
        sp = seasonal_periods
        # Build model
        mod = UnobservedComponents(
            y,
            level='local level' if level else None,
            trend='local linear trend' if trend else None,
            seasonal=sp,
        )
        res = mod.fit(disp=False)
        pred = res.get_forecast(steps=periods)
        forecasts_data[col] = pred.predicted_mean.values
        models[col] = res
    forecast_df = pd.DataFrame(forecasts_data, index=future_index, columns=numeric_cols)
    return UnobservedComponentsForecastResult(forecasts=forecast_df, models=models)


@dataclass
class DynamicFactorForecastResult:
    """Result container for :func:`dynamic_factor_forecast`.

    Attributes
    ----------
    forecasts : pandas.DataFrame
        Forecasted values for all series using a dynamic factor model.
    model : object
        Fitted DynamicFactor results.
    """
    forecasts: pd.DataFrame
    model: object


def dynamic_factor_forecast(
    date: Union[str, pd.Series, Iterable],
    df: pd.DataFrame,
    *,
    periods: int = 12,
    k_factors: int = 1,
    factor_order: int = 1,
    freq: Optional[str] = None,
) -> DynamicFactorForecastResult:
    """Forecast multivariate series using a dynamic factor model.

    Dynamic factor models capture shared dynamics across multiple
    series by representing them as linear combinations of a small
    number of unobserved factors that evolve according to vector
    autoregressions.  This can be particularly powerful when
    multiple commodities exhibit co‑movement driven by common latent
    influences.

    Parameters
    ----------
    date : str or pandas.Series or iterable
        Column name, series or iterable containing date information.
    df : pandas.DataFrame
        DataFrame with the data.  All numeric columns are included in
        the model.
    periods : int, default 12
        Number of future periods to forecast.
    k_factors : int, default 1
        Number of latent factors to estimate.
    factor_order : int, default 1
        Order of the factor autoregression.
    freq : str or None, default None
        Frequency string for generating forecast dates.  If None,
        inferred via ``pandas.infer_freq``.

    Returns
    -------
    DynamicFactorForecastResult
        Dataclass containing the forecast DataFrame and the fitted
        model.

    Raises
    ------
    ImportError
        If the required ``statsmodels`` classes are not available.
    """
    try:
        from statsmodels.tsa.statespace.dynamic_factor import DynamicFactor
    except Exception as e:
        raise ImportError(
            "statsmodels is required for dynamic factor forecasting."
        ) from e
    if isinstance(date, str):
        if date not in df.columns:
            raise KeyError(f"Date column '{date}' not found in DataFrame")
        date_series = df[date]
    else:
        date_series = pd.Series(date)
    dt = pd.to_datetime(date_series)
    if dt.empty:
        raise ValueError("Date series is empty")
    numeric_cols = [c for c in df.columns if c != date and pd.api.types.is_numeric_dtype(df[c])]
    if len(numeric_cols) < 2:
        raise ValueError("Dynamic factor forecasting requires at least two numeric columns")
    y = df[numeric_cols].ffill().bfill().astype(float)
    # Fit dynamic factor model
    # Attempt to fit dynamic factor model; if it fails, fall back to VAR
    try:
        mod = DynamicFactor(y, k_factors=k_factors, factor_order=factor_order)
        res = mod.fit(disp=False)
        # Forecast factor and observed variables
        try:
            forecast_values = res.forecast(periods)
        except Exception:
            forecast_values = None
        # If forecast_values is empty or contains NaNs, fall back to predict
        if forecast_values is None or np.all(np.isnan(forecast_values)):
            start = len(y)
            end = len(y) + periods - 1
            forecast_pred = res.predict(start=start, end=end)
            forecast_values = forecast_pred.values
        model_res = res
    except Exception:
        # On failure, use VAR as fallback
        from .forecasting import var_forecast
        var_res = var_forecast(date=date, df=df, periods=periods, maxlags=factor_order, freq=freq)
        forecast_values = var_res.forecasts.values
        model_res = var_res.model
    # Determine future dates
    if freq is None:
        try:
            freq = pd.infer_freq(dt)
        except Exception:
            freq = None
    if freq is not None:
        try:
            future_index = pd.date_range(start=dt.iloc[-1], periods=periods + 1, freq=freq)[1:]
        except Exception:
            freq = None
            future_index = None
    if freq is None:
        diffs = dt.diff().dropna()
        delta = diffs.mode()[0] if not diffs.empty else pd.Timedelta(days=1)
        future_index = pd.to_datetime([dt.iloc[-1] + delta * (i + 1) for i in range(periods)])
    # At this point, forecast_values, model_res, future_index, numeric_cols are defined
    # If forecast_values is already a DataFrame (fallback), use it directly
    if isinstance(forecast_values, pd.DataFrame):
        forecast_df = forecast_values
    else:
        forecast_df = pd.DataFrame(forecast_values, index=future_index, columns=numeric_cols)
    return DynamicFactorForecastResult(forecasts=forecast_df, model=model_res)

# ---------------------------------------------------------------------------
# Additional advanced forecasting methods
# ---------------------------------------------------------------------------

@dataclass
class SarimaxForecastResult:
    """Result container for :func:`sarimax_forecast`.

    Attributes
    ----------
    forecasts : pandas.DataFrame
        Forecasted values for each series.  The index contains the
        forecast dates and the columns correspond to the numeric
        columns of the input (excluding the date column).
    models : Dict[str, object]
        Fitted SARIMAX results for each series.
    lower_conf_int : pandas.DataFrame or None
        Lower bounds of prediction intervals if requested; otherwise
        ``None``.
    upper_conf_int : pandas.DataFrame or None
        Upper bounds of prediction intervals if requested; otherwise
        ``None``.
    """

    forecasts: pd.DataFrame
    models: Dict[str, object]
    lower_conf_int: Optional[pd.DataFrame] = None
    upper_conf_int: Optional[pd.DataFrame] = None


def sarimax_forecast(
    date: Union[str, pd.Series, Iterable],
    df: pd.DataFrame,
    *,
    periods: int = 12,
    order: Tuple[int, int, int] = (1, 0, 0),
    seasonal_order: Tuple[int, int, int, int] = (0, 0, 0, 0),
    exog: Optional[Union[pd.DataFrame, str, Iterable[str]]] = None,
    exog_future: Optional[pd.DataFrame] = None,
    freq: Optional[str] = None,
    enforce_stationarity: bool = False,
    enforce_invertibility: bool = False,
    return_conf_int: bool = False,
    plot: bool = False,
) -> SarimaxForecastResult:
    """Forecast one or more series using SARIMAX models.

    This function generalises :func:`arima_forecast` by allowing a
    seasonal component and optional exogenous regressors.  It fits
    separate SARIMAX models to each numeric series and forecasts
    ``periods`` steps ahead.

    Parameters
    ----------
    date : str or pandas.Series or iterable
        Column name, series or iterable containing date information.
    df : pandas.DataFrame
        DataFrame with the data.  Numeric columns are modelled
        individually.
    periods : int, default 12
        Number of future periods to forecast.
    order : tuple of int, default (1,0,0)
        Non‑seasonal ARIMA (p,d,q) order.
    seasonal_order : tuple of int, default (0,0,0,0)
        Seasonal ARIMA (P,D,Q,s) order.  The last element ``s``
        specifies the number of periods in a seasonal cycle.  Set to
        ``(0,0,0,0)`` for no seasonality.
    exog : pandas.DataFrame, str, iterable of str or None, default None
        Exogenous regressors to include in the model.  May be a
        DataFrame aligned with ``df`` or the name(s) of columns in
        ``df``.  If provided, separate models are fit using the
        same exogenous variables for each series.
    exog_future : pandas.DataFrame or None, default None
        Future values of the exogenous regressors.  Must have the
        same number of columns as ``exog`` and at least ``periods``
        rows.  If None, the last row of the historical exogenous
        data is replicated ``periods`` times.
    freq : str or None, default None
        Frequency string for generating forecast dates.  If None,
        frequency is inferred via ``pandas.infer_freq``.
    enforce_stationarity : bool, default False
        If True, restrict the AR parameters to stationary region.
    enforce_invertibility : bool, default False
        If True, restrict the MA parameters to invertible region.

    Returns
    -------
    SarimaxForecastResult
        Dataclass containing the forecast DataFrame, fitted SARIMAX
        models for each series, and optionally prediction intervals
        if ``return_conf_int`` is ``True``.

    Raises
    ------
    ImportError
        If the ``statsmodels`` package is not installed.
    KeyError
        If the specified date column is not found.
    ValueError
        If no numeric columns are available for forecasting.
    """
    try:
        from statsmodels.tsa.statespace.sarimax import SARIMAX
    except Exception as e:
        raise ImportError(
            "statsmodels is required for SARIMAX forecasting. "
            "Please install statsmodels to use this function."
        ) from e
    # Parse date column
    if isinstance(date, str):
        if date not in df.columns:
            raise KeyError(f"Date column '{date}' not found in DataFrame")
        date_series = df[date]
    else:
        date_series = pd.Series(date)
    dt = pd.to_datetime(date_series)
    if dt.empty:
        raise ValueError("Date series is empty")
    # Identify numeric columns
    numeric_cols: List[str] = [c for c in df.columns if c != date and pd.api.types.is_numeric_dtype(df[c])]
    if not numeric_cols:
        raise ValueError("No numeric data columns found for SARIMAX forecasting")
    # Determine frequency
    if freq is None:
        try:
            freq = pd.infer_freq(dt)
        except Exception:
            freq = None
    # Prepare future dates
    if freq is not None:
        try:
            future_index = pd.date_range(start=dt.iloc[-1], periods=periods + 1, freq=freq)[1:]
        except Exception:
            freq = None
            future_index = None
    if freq is None:
        diffs = dt.diff().dropna()
        delta = diffs.mode()[0] if not diffs.empty else pd.Timedelta(days=1)
        future_index = pd.to_datetime([dt.iloc[-1] + delta * (i + 1) for i in range(periods)])
    # Prepare exogenous variables
    if exog is not None:
        # Determine exogenous DataFrame
        if isinstance(exog, str):
            exog_cols = [exog]
            exog_df = df[exog_cols]
        elif isinstance(exog, Iterable) and not isinstance(exog, pd.DataFrame):
            exog_cols = list(exog)
            exog_df = df[exog_cols]
        elif isinstance(exog, pd.DataFrame):
            exog_cols = list(exog.columns)
            exog_df = exog
        else:
            raise TypeError("exog must be a DataFrame, column name or iterable of column names")
        # Ensure numeric
        exog_df = exog_df.ffill().bfill().astype(float)
        # Future exog values
        if exog_future is not None:
            if not isinstance(exog_future, pd.DataFrame):
                raise TypeError("exog_future must be a pandas DataFrame if provided")
            future_exog = exog_future.iloc[:periods].reset_index(drop=True)
            # If fewer rows, repeat last row
            if len(future_exog) < periods:
                last_row = future_exog.iloc[-1]
                add_rows = pd.DataFrame([last_row] * (periods - len(future_exog)), columns=future_exog.columns)
                future_exog = pd.concat([future_exog, add_rows], ignore_index=True)
        else:
            # Replicate last row for future
            last_row = exog_df.iloc[-1]
            future_exog = pd.DataFrame([last_row] * periods, columns=exog_df.columns)
    else:
        exog_cols = []
        exog_df = None
        future_exog = None
    # Fit SARIMAX models for each numeric column
    forecasts_data: Dict[str, np.ndarray] = {}
    models: Dict[str, object] = {}
    lower_ci_data: Dict[str, np.ndarray] = {}
    upper_ci_data: Dict[str, np.ndarray] = {}
    for col in numeric_cols:
        y = pd.to_numeric(df[col], errors='coerce').ffill().bfill().astype(float)
        # Fit model
        mod = SARIMAX(
            y,
            order=order,
            seasonal_order=seasonal_order,
            exog=exog_df,
            enforce_stationarity=enforce_stationarity,
            enforce_invertibility=enforce_invertibility,
        )
        res = mod.fit(disp=False)
        models[col] = res
        # Forecast with or without exogenous variables
        if exog_df is not None:
            forecast_res = res.get_forecast(steps=periods, exog=future_exog)
        else:
            forecast_res = res.get_forecast(steps=periods)
        forecast_vals = forecast_res.predicted_mean.values
        forecasts_data[col] = forecast_vals
        # Compute confidence intervals if requested
        if return_conf_int or plot:
            ci = forecast_res.conf_int()
            # Extract lower/upper columns; Statsmodels names columns like 'lower y' and 'upper y'
            # For univariate forecast, we take the first two columns
            # For each column we call separately; thus ci has two columns
            lower_vals = ci.iloc[:, 0].values
            upper_vals = ci.iloc[:, 1].values
            lower_ci_data[col] = lower_vals
            upper_ci_data[col] = upper_vals
    forecast_df = pd.DataFrame(forecasts_data, index=future_index, columns=numeric_cols)
    lower_df = None
    upper_df = None
    if return_conf_int or plot:
        # Build DataFrames for confidence intervals
        lower_df = pd.DataFrame(lower_ci_data, index=future_index, columns=numeric_cols)
        upper_df = pd.DataFrame(upper_ci_data, index=future_index, columns=numeric_cols)
    result = SarimaxForecastResult(
        forecasts=forecast_df,
        models=models,
        lower_conf_int=lower_df,
        upper_conf_int=upper_df,
    )
    # Plot if requested
    if plot:
        try:
            # Import plot function lazily to avoid circular dependency
            from .visualization import forecast_plot
            # Determine historical DataFrame's date column name or series
            # Use provided date parameter to avoid ambiguous column names
            forecast_plot(date=date, df=df, forecast=forecast_df, lower=lower_df, upper=upper_df)
        except Exception:
            # Silently ignore plotting errors to avoid breaking forecasting
            pass
    return result


@dataclass
class LstmForecastResult:
    """Result container for :func:`lstm_forecast`.

    Attributes
    ----------
    forecasts : pandas.DataFrame
        Forecasted values for each series.  The index contains the
        forecast dates and the columns correspond to the numeric
        columns of the input (excluding the date column).
    models : Dict[str, object]
        Trained TensorFlow Keras models for each series.
    """

    forecasts: pd.DataFrame
    models: Dict[str, object]


def lstm_forecast(
    date: Union[str, pd.Series, Iterable],
    df: pd.DataFrame,
    *,
    periods: int = 12,
    look_back: int = 10,
    hidden_units: int = 50,
    epochs: int = 100,
    batch_size: int = 32,
    validation_split: float = 0.1,
    random_state: Optional[int] = None,
    freq: Optional[str] = None,
) -> LstmForecastResult:
    """Forecast one or more series using an LSTM neural network.

    This function trains a separate univariate LSTM model for each
    numeric series.  It constructs supervised learning examples
    using lagged observations of length ``look_back``, fits an
    LSTM with a dense output layer, and iteratively predicts
    ``periods`` future values.  The underlying models are built
    with TensorFlow/Keras.

    Parameters
    ----------
    date : str or pandas.Series or iterable
        Column name, series or iterable containing date information.
    df : pandas.DataFrame
        DataFrame with the data.  Numeric columns are modelled
        individually.
    periods : int, default 12
        Number of future periods to forecast.
    look_back : int, default 10
        Number of past observations used as input features.  Must be
        less than the length of the series.
    hidden_units : int, default 50
        Number of LSTM units in the hidden layer.
    epochs : int, default 100
        Number of training epochs.
    batch_size : int, default 32
        Size of mini‑batches during training.
    validation_split : float, default 0.1
        Fraction of the training data used for validation.
    random_state : int or None, default None
        Seed for NumPy and TensorFlow random number generators.
    freq : str or None, default None
        Frequency string for generating forecast dates.  If None,
        inferred via ``pandas.infer_freq``.

    Returns
    -------
    LstmForecastResult
        Dataclass containing the forecast DataFrame and the trained
        Keras models for each series.

    Notes
    -----
    This method can be computationally intensive, especially for
    large datasets or many series.  It relies on the ``tensorflow``
    package; an ImportError is raised if TensorFlow is not installed.
    """
    # Check dependencies
    try:
        import numpy as np  # reimport to ensure local scope
        from sklearn.preprocessing import StandardScaler
        import tensorflow as tf
        from tensorflow.keras.models import Sequential
        from tensorflow.keras.layers import LSTM, Dense
    except Exception as e:
        raise ImportError(
            "TensorFlow and scikit‑learn are required for LSTM forecasting. "
            "Please install tensorflow and scikit-learn to use this function."
        ) from e
    # Set random seeds for reproducibility
    if random_state is not None:
        np.random.seed(random_state)
        try:
            tf.random.set_seed(random_state)
        except Exception:
            pass
    # Parse date column
    if isinstance(date, str):
        if date not in df.columns:
            raise KeyError(f"Date column '{date}' not found in DataFrame")
        date_series = df[date]
    else:
        date_series = pd.Series(date)
    dt = pd.to_datetime(date_series)
    if dt.empty:
        raise ValueError("Date series is empty")
    numeric_cols = [c for c in df.columns if c != date and pd.api.types.is_numeric_dtype(df[c])]
    if not numeric_cols:
        raise ValueError("No numeric data columns found for LSTM forecasting")
    # Determine frequency
    if freq is None:
        try:
            freq = pd.infer_freq(dt)
        except Exception:
            freq = None
    # Prepare future dates
    if freq is not None:
        try:
            future_index = pd.date_range(start=dt.iloc[-1], periods=periods + 1, freq=freq)[1:]
        except Exception:
            freq = None
            future_index = None
    if freq is None:
        diffs = dt.diff().dropna()
        delta = diffs.mode()[0] if not diffs.empty else pd.Timedelta(days=1)
        future_index = pd.to_datetime([dt.iloc[-1] + delta * (i + 1) for i in range(periods)])
    forecasts_data: Dict[str, List[float]] = {}
    models: Dict[str, object] = {}
    for col in numeric_cols:
        series = pd.to_numeric(df[col], errors='coerce').ffill().bfill().astype(float).values
        if len(series) <= look_back:
            raise ValueError(f"Series '{col}' is too short for look_back={look_back}")
        # Standardise data
        scaler = StandardScaler()
        series_scaled = scaler.fit_transform(series.reshape(-1, 1)).flatten()
        # Build supervised dataset
        X = []
        y_target = []
        for i in range(look_back, len(series_scaled)):
            X.append(series_scaled[i - look_back:i])
            y_target.append(series_scaled[i])
        X_train = np.array(X).reshape(-1, look_back, 1)
        y_train = np.array(y_target)
        # Build model
        model = Sequential()
        model.add(LSTM(hidden_units, input_shape=(look_back, 1)))
        model.add(Dense(1))
        model.compile(optimizer='adam', loss='mse')
        # Train model
        model.fit(
            X_train,
            y_train,
            epochs=epochs,
            batch_size=batch_size,
            validation_split=validation_split,
            verbose=0,
        )
        models[col] = model
        # Forecast iteratively
        history_scaled = list(series_scaled[-look_back:])
        preds = []
        for _ in range(periods):
            input_seq = np.array(history_scaled[-look_back:]).reshape(1, look_back, 1)
            pred_scaled = model.predict(input_seq, verbose=0)[0, 0]
            # Invert scaling
            pred = scaler.inverse_transform(np.array([[pred_scaled]])).flatten()[0]
            preds.append(pred)
            # Update history
            history_scaled.append(pred_scaled)
        forecasts_data[col] = preds
    forecast_df = pd.DataFrame(forecasts_data, index=future_index, columns=numeric_cols)
    return LstmForecastResult(forecasts=forecast_df, models=models)


@dataclass
class GarchForecastResult:
    """Result container for :func:`garch_forecast`.

    Attributes
    ----------
    forecasts : pandas.DataFrame
        Forecasted variance (and optional mean) for each series.  The
        index contains the forecast dates and the columns correspond
        to the numeric columns of the input (excluding the date
        column).
    models : Dict[str, object]
        Fitted ARCH models from the ``arch`` package.
    """
    forecasts: pd.DataFrame
    models: Dict[str, object]


def garch_forecast(
    date: Union[str, pd.Series, Iterable],
    df: pd.DataFrame,
    *,
    periods: int = 12,
    p: int = 1,
    q: int = 1,
    mean: str = 'Constant',
    vol: str = 'GARCH',
    dist: str = 'normal',
    freq: Optional[str] = None,
) -> GarchForecastResult:
    """Forecast conditional variance of one or more series using GARCH models.

    This function fits a GARCH model (via the ``arch`` package) to
    the returns of each numeric series and forecasts the conditional
    variance ``periods`` steps ahead.  Optionally, it can also
    return mean forecasts if the mean is modelled.  Because GARCH
    models operate on returns rather than levels, the results are
    interpreted as forecasts of volatility.

    Parameters
    ----------
    date : str or pandas.Series or iterable
        Column name, series or iterable containing date information.
    df : pandas.DataFrame
        DataFrame with the data.  Numeric columns are modelled
        individually.
    periods : int, default 12
        Number of future periods to forecast.
    p : int, default 1
        Order of the GARCH terms (lagged conditional variances).
    q : int, default 1
        Order of the ARCH terms (lagged squared residuals).
    mean : str, default 'Constant'
        Mean model.  Options include 'Constant', 'Zero', or
        'AR'.  See ``arch_model`` documentation for details.
    vol : str, default 'GARCH'
        Volatility model.  Options include 'GARCH', 'EGARCH', etc.
    dist : str, default 'normal'
        Distribution for the innovations.  Options include 'normal',
        't', etc.
    freq : str or None, default None
        Frequency string for generating forecast dates.  If None,
        inferred via ``pandas.infer_freq``.

    Returns
    -------
    GarchForecastResult
        Dataclass containing the forecasted variances and the
        fitted models.  If the mean model produces forecasts, these
        are included in the ``forecasts`` DataFrame.

    Raises
    ------
    ImportError
        If the ``arch`` package is not installed.
    """
    try:
        from arch import arch_model
    except Exception as e:
        raise ImportError(
            "The 'arch' package is required for GARCH forecasting. "
            "Please install arch to use this function."
        ) from e
    # Parse date column
    if isinstance(date, str):
        if date not in df.columns:
            raise KeyError(f"Date column '{date}' not found in DataFrame")
        date_series = df[date]
    else:
        date_series = pd.Series(date)
    dt = pd.to_datetime(date_series)
    if dt.empty:
        raise ValueError("Date series is empty")
    numeric_cols = [c for c in df.columns if c != date and pd.api.types.is_numeric_dtype(df[c])]
    if not numeric_cols:
        raise ValueError("No numeric data columns found for GARCH forecasting")
    # Determine frequency
    if freq is None:
        try:
            freq = pd.infer_freq(dt)
        except Exception:
            freq = None
    # Prepare future dates
    if freq is not None:
        try:
            future_index = pd.date_range(start=dt.iloc[-1], periods=periods + 1, freq=freq)[1:]
        except Exception:
            freq = None
            future_index = None
    if freq is None:
        diffs = dt.diff().dropna()
        delta = diffs.mode()[0] if not diffs.empty else pd.Timedelta(days=1)
        future_index = pd.to_datetime([dt.iloc[-1] + delta * (i + 1) for i in range(periods)])
    forecasts_data: Dict[str, np.ndarray] = {}
    models: Dict[str, object] = {}
    for col in numeric_cols:
        series = pd.to_numeric(df[col], errors='coerce').ffill().bfill().astype(float)
        # Compute returns (log returns) to fit GARCH
        returns = np.log(series).diff().dropna()
        if returns.empty:
            raise ValueError(f"Series '{col}' has insufficient data for GARCH model")
        # Fit GARCH model
        am = arch_model(
            returns,
            mean=mean,
            vol=vol,
            p=p,
            q=q,
            dist=dist,
        )
        res = am.fit(disp='off')
        # Forecast conditional variance and mean
        forecast = res.forecast(horizon=periods)
        # Extract mean and variance forecasts
        # forecast.variance returns DataFrame of shape (nobs, horizon)
        var_forecast = forecast.variance.iloc[-1].values
        try:
            mean_forecast = forecast.mean.iloc[-1].values
        except Exception:
            mean_forecast = np.zeros_like(var_forecast)
        # We store variance forecasts; if mean forecasts present, we add them
        # For consistency with other forecasts, we output the variance as the series
        # Name columns by series name appended with '_var' if multiple forecasts exist
        forecasts_data[col] = var_forecast
        models[col] = res
    forecast_df = pd.DataFrame(forecasts_data, index=future_index, columns=numeric_cols)
    return GarchForecastResult(forecasts=forecast_df, models=models)

# ---------------------------------------------------------------------------
# Gradient boosting forecasts using XGBoost and LightGBM
# ---------------------------------------------------------------------------

@dataclass
class XGBoostForecastResult:
    """Result container for :func:`xgboost_forecast`.

    Attributes
    ----------
    forecasts : pandas.DataFrame
        Forecasted values for each target series.  The index
        corresponds to future dates and the columns match the target
        names.
    models : Dict[str, object]
        Trained ``xgboost.XGBRegressor`` models for each series.
    """
    forecasts: pd.DataFrame
    models: Dict[str, object]


def xgboost_forecast(
    date: Union[str, pd.Series, Iterable],
    df: pd.DataFrame,
    *,
    periods: int = 12,
    lags: int = 10,
    exog: Optional[List[str]] = None,
    freq: Optional[str] = None,
    model_params: Optional[dict] = None,
) -> XGBoostForecastResult:
    """Forecast series using XGBoost regressors with lagged features.

    Each numeric column (excluding the date and exogenous columns) is
    modelled separately.  Lagged values up to ``lags`` and optional
    exogenous variables at the current time step are used as
    predictors.  The function trains an XGBoost regressor and
    iteratively generates forecasts for ``periods`` steps ahead.  If
    future exogenous values are required, pass them via the
    ``exog_future`` parameter in ``model_params`` (as a DataFrame
    indexed by forecast dates).

    Parameters
    ----------
    date : str or pandas.Series or iterable
        Column name, series or iterable containing date information.
    df : pandas.DataFrame
        DataFrame with the data.  Must include the date column and
        one or more numeric columns to forecast.
    periods : int, default 12
        Number of future periods to forecast.
    lags : int, default 10
        Number of lag observations to include as features.
    exog : list of str or None, default None
        Names of exogenous columns to include as predictors.  These
        columns must be present in ``df``.  If provided, you can
        specify future values for these variables via
        ``model_params['exog_future']`` as a DataFrame of shape
        (periods, len(exog)).  If future values are not provided,
        zeros are used.
    freq : str or None, default None
        Frequency string for generating forecast dates.  If ``None``,
        the frequency is inferred from the date series.
    model_params : dict or None, default None
        Additional parameters passed to ``xgboost.XGBRegressor``.
        Recognised key ``exog_future`` may be a DataFrame providing
        exogenous values for the forecast horizon.

    Returns
    -------
    XGBoostForecastResult
        Dataclass containing forecasted values and fitted models.

    Raises
    ------
    ImportError
        If ``xgboost`` is not installed.
    ValueError
        If no numeric columns are available to model.
    """
    try:
        from xgboost import XGBRegressor
    except Exception as e:
        raise ImportError(
            "xgboost is required for XGBoost forecasting. "
            "Please install xgboost to use this function."
        ) from e
    if model_params is None:
        model_params = {}
    exog_future = model_params.pop('exog_future', None)
    # Determine date series
    if isinstance(date, str):
        if date not in df.columns:
            raise KeyError(f"Date column '{date}' not found in DataFrame")
        date_series = df[date]
    else:
        date_series = pd.Series(date)
    dt = pd.to_datetime(date_series)
    if dt.empty:
        raise ValueError("Date series is empty")
    # Identify target columns
    target_cols = [c for c in df.columns if c != date and (exog is None or c not in exog) and pd.api.types.is_numeric_dtype(df[c])]
    if not target_cols:
        raise ValueError("No numeric columns found to forecast with XGBoost")
    # Identify exogenous columns
    exog_cols = exog or []
    # Determine frequency
    if freq is None:
        try:
            freq = pd.infer_freq(dt)
        except Exception:
            freq = None
    # Generate future dates
    if freq is not None:
        try:
            future_index = pd.date_range(start=dt.iloc[-1], periods=periods + 1, freq=freq)[1:]
        except Exception:
            freq = None
            future_index = None
    if freq is None:
        diffs = dt.diff().dropna()
        delta = diffs.mode()[0] if not diffs.empty else pd.Timedelta(days=1)
        future_index = pd.to_datetime([dt.iloc[-1] + delta * (i + 1) for i in range(periods)])
    # Exogenous future values
    if exog_cols and exog_future is None:
        # Use zeros if no future exogenous provided
        exog_future = pd.DataFrame(np.zeros((periods, len(exog_cols))), index=future_index, columns=exog_cols)
    elif exog_cols:
        exog_future = exog_future.copy()
        exog_future.index = future_index
        exog_future = exog_future[exog_cols]
    models: Dict[str, object] = {}
    forecasts_data: Dict[str, List[float]] = {}
    for col in target_cols:
        series = pd.to_numeric(df[col], errors='coerce').astype(float).reset_index(drop=True)
        n = len(series)
        X_train = []
        y_train = []
        exog_matrix = df[exog_cols].reset_index(drop=True) if exog_cols else None
        for t in range(lags, n):
            lagged = series.iloc[t - lags:t].values
            features = list(lagged)
            if exog_cols:
                features += list(exog_matrix.iloc[t, :].values)
            X_train.append(features)
            y_train.append(series.iloc[t])
        if not y_train:
            raise ValueError(f"Not enough data to build lagged features for column '{col}'")
        X_train = np.array(X_train)
        y_train = np.array(y_train)
        # Default model parameters
        params = {
            'objective': 'reg:squarederror',
            'n_estimators': 200,
            'learning_rate': 0.05,
            'max_depth': 5,
            'subsample': 0.8,
            'colsample_bytree': 0.8,
        }
        params.update(model_params)
        model = XGBRegressor(**params)
        model.fit(X_train, y_train)
        models[col] = model
        last_lags = series.iloc[-lags:].values.tolist()
        exog_future_values = exog_future.values if exog_cols else None
        preds: List[float] = []
        for step in range(periods):
            features = last_lags[-lags:].copy()
            if exog_cols:
                features += list(exog_future_values[step])
            pred = float(model.predict(np.array(features).reshape(1, -1))[0])
            preds.append(pred)
            last_lags.append(pred)
        forecasts_data[col] = preds
    forecast_df = pd.DataFrame(forecasts_data, index=future_index, columns=target_cols)
    return XGBoostForecastResult(forecasts=forecast_df, models=models)


@dataclass
class LightGBMForecastResult:
    """Result container for :func:`lightgbm_forecast`.

    Attributes
    ----------
    forecasts : pandas.DataFrame
        Forecasted values for each target series.
    models : Dict[str, object]
        Trained ``lightgbm.LGBMRegressor`` models for each series.
    """
    forecasts: pd.DataFrame
    models: Dict[str, object]


def lightgbm_forecast(
    date: Union[str, pd.Series, Iterable],
    df: pd.DataFrame,
    *,
    periods: int = 12,
    lags: int = 10,
    exog: Optional[List[str]] = None,
    freq: Optional[str] = None,
    model_params: Optional[dict] = None,
) -> LightGBMForecastResult:
    """Forecast series using LightGBM regressors with lagged features.

    This function mirrors :func:`xgboost_forecast` but uses
    ``lightgbm.LGBMRegressor``.  See :func:`xgboost_forecast` for
    parameter descriptions and return details.

    Returns
    -------
    LightGBMForecastResult
        Dataclass containing forecasted values and fitted models.
    """
    try:
        from lightgbm import LGBMRegressor
    except Exception as e:
        raise ImportError(
            "lightgbm is required for LightGBM forecasting. "
            "Please install lightgbm to use this function."
        ) from e
    if model_params is None:
        model_params = {}
    exog_future = model_params.pop('exog_future', None)
    # Determine date series
    if isinstance(date, str):
        if date not in df.columns:
            raise KeyError(f"Date column '{date}' not found in DataFrame")
        date_series = df[date]
    else:
        date_series = pd.Series(date)
    dt = pd.to_datetime(date_series)
    if dt.empty:
        raise ValueError("Date series is empty")
    target_cols = [c for c in df.columns if c != date and (exog is None or c not in exog) and pd.api.types.is_numeric_dtype(df[c])]
    if not target_cols:
        raise ValueError("No numeric columns found to forecast with LightGBM")
    exog_cols = exog or []
    # Determine frequency
    if freq is None:
        try:
            freq = pd.infer_freq(dt)
        except Exception:
            freq = None
    if freq is not None:
        try:
            future_index = pd.date_range(start=dt.iloc[-1], periods=periods + 1, freq=freq)[1:]
        except Exception:
            freq = None
            future_index = None
    if freq is None:
        diffs = dt.diff().dropna()
        delta = diffs.mode()[0] if not diffs.empty else pd.Timedelta(days=1)
        future_index = pd.to_datetime([dt.iloc[-1] + delta * (i + 1) for i in range(periods)])
    if exog_cols and exog_future is None:
        exog_future = pd.DataFrame(np.zeros((periods, len(exog_cols))), index=future_index, columns=exog_cols)
    elif exog_cols:
        exog_future = exog_future.copy()
        exog_future.index = future_index
        exog_future = exog_future[exog_cols]
    models: Dict[str, object] = {}
    forecasts_data: Dict[str, List[float]] = {}
    for col in target_cols:
        series = pd.to_numeric(df[col], errors='coerce').astype(float).reset_index(drop=True)
        n = len(series)
        X_train: List[List[float]] = []
        y_train: List[float] = []
        exog_matrix = df[exog_cols].reset_index(drop=True) if exog_cols else None
        for t in range(lags, n):
            lagged = series.iloc[t - lags:t].values
            features = list(lagged)
            if exog_cols:
                features += list(exog_matrix.iloc[t, :].values)
            X_train.append(features)
            y_train.append(series.iloc[t])
        if not y_train:
            raise ValueError(f"Not enough data to build lagged features for column '{col}'")
        X_train_arr = np.array(X_train)
        y_train_arr = np.array(y_train)
        params = {
            'n_estimators': 200,
            'learning_rate': 0.05,
            'max_depth': -1,
            'num_leaves': 31,
            'objective': 'regression',
        }
        params.update(model_params)
        model = LGBMRegressor(**params)
        model.fit(X_train_arr, y_train_arr)
        models[col] = model
        last_lags = series.iloc[-lags:].values.tolist()
        exog_future_values = exog_future.values if exog_cols else None
        preds: List[float] = []
        for step in range(periods):
            features = last_lags[-lags:].copy()
            if exog_cols:
                features += list(exog_future_values[step])
            pred = float(model.predict(np.array(features).reshape(1, -1))[0])
            preds.append(pred)
            last_lags.append(pred)
        forecasts_data[col] = preds
    forecast_df = pd.DataFrame(forecasts_data, index=future_index, columns=target_cols)
    return LightGBMForecastResult(forecasts=forecast_df, models=models)

# ---------------------------------------------------------------------------
# Theta forecasting method
# ---------------------------------------------------------------------------

@dataclass
class ThetaForecastResult:
    """Result container for :func:`theta_forecast`.

    Attributes
    ----------
    forecasts : pandas.DataFrame
        Forecasted values for each series.
    models : Dict[str, tuple]
        Fitted components: linear regression parameters and
        exponential smoothing results per series.
    """
    forecasts: pd.DataFrame
    models: Dict[str, tuple]


def theta_forecast(
    date: Union[str, pd.Series, Iterable],
    df: pd.DataFrame,
    *,
    periods: int = 12,
    freq: Optional[str] = None,
    smoothing_level: Optional[float] = None,
) -> ThetaForecastResult:
    """Forecast series using the Theta method.

    The Theta method combines a linear extrapolation of the trend and
    an exponential smoothing forecast.  For each series, a simple
    linear regression is fit on the time index to estimate the trend,
    and Simple Exponential Smoothing (SES) is applied to capture the
    level.  The forecast is the average of the extrapolated trend and
    the SES forecast.  When ``statsmodels`` is not available, a
    naive last‑value forecast is used instead of SES.

    Parameters
    ----------
    date : str or pandas.Series or iterable
        Column name, series or iterable containing date information.
    df : pandas.DataFrame
        DataFrame with the data.  Must include the date column and
        one or more numeric columns to forecast.
    periods : int, default 12
        Number of future periods to forecast.
    freq : str or None, default None
        Frequency string for generating forecast dates.  If ``None``,
        the frequency is inferred from the date series.
    smoothing_level : float or None, default None
        Smoothing parameter for the SES component.  If ``None``, it
        is estimated via maximum likelihood.

    Returns
    -------
    ThetaForecastResult
        Dataclass containing the forecasted values and fitted model
        components.

    Raises
    ------
    ImportError
        If ``statsmodels`` is not installed and a smoothing level is
        specified.
    ValueError
        If no numeric columns are available to model.
    """
    try:
        from statsmodels.tsa.holtwinters import SimpleExpSmoothing
    except Exception as e:
        if smoothing_level is not None:
            raise ImportError(
                "statsmodels is required for the Theta method when a smoothing level is specified. "
                "Please install statsmodels to use this feature."
            ) from e
        SimpleExpSmoothing = None
    # Determine date series
    if isinstance(date, str):
        if date not in df.columns:
            raise KeyError(f"Date column '{date}' not found in DataFrame")
        date_series = df[date]
    else:
        date_series = pd.Series(date)
    dt = pd.to_datetime(date_series)
    if dt.empty:
        raise ValueError("Date series is empty")
    # Determine frequency for future index
    if freq is None:
        try:
            freq = pd.infer_freq(dt)
        except Exception:
            freq = None
    if freq is not None:
        try:
            future_index = pd.date_range(start=dt.iloc[-1], periods=periods + 1, freq=freq)[1:]
        except Exception:
            freq = None
            future_index = None
    if freq is None:
        diffs = dt.diff().dropna()
        delta = diffs.mode()[0] if not diffs.empty else pd.Timedelta(days=1)
        future_index = pd.to_datetime([dt.iloc[-1] + delta * (i + 1) for i in range(periods)])
    numeric_cols = [c for c in df.columns if c != date and pd.api.types.is_numeric_dtype(df[c])]
    if not numeric_cols:
        raise ValueError("No numeric columns found to forecast with the Theta method")
    models: Dict[str, tuple] = {}
    forecasts_data: Dict[str, List[float]] = {}
    for col in numeric_cols:
        series = pd.to_numeric(df[col], errors='coerce').astype(float)
        n = len(series)
        # Linear regression on index
        t = np.arange(n)
        mask = ~series.isna()
        t_masked = t[mask]
        y_masked = series[mask]
        if len(y_masked) < 2:
            trend_forecast = np.full(periods, series.iloc[-1] if not series.empty else np.nan)
            slope, intercept = 0.0, series.iloc[-1] if not series.empty else np.nan
        else:
            coeffs = np.polyfit(t_masked, y_masked, 1)
            slope, intercept = float(coeffs[0]), float(coeffs[1])
            trend_forecast = intercept + slope * (np.arange(n, n + periods))
        # SES component
        if SimpleExpSmoothing is not None and len(y_masked) >= 2:
            try:
                ses_model = SimpleExpSmoothing(y_masked).fit(smoothing_level=smoothing_level, optimized=(smoothing_level is None))
                ses_forecast = ses_model.forecast(periods).values
                models[col] = (slope, intercept, ses_model)
            except Exception:
                ses_forecast = np.full(periods, y_masked.iloc[-1] if len(y_masked) > 0 else np.nan)
                models[col] = (slope, intercept, None)
        else:
            ses_forecast = np.full(periods, y_masked.iloc[-1] if len(y_masked) > 0 else np.nan)
            models[col] = (slope, intercept, None)
        theta_pred = 0.5 * (trend_forecast + ses_forecast)
        forecasts_data[col] = theta_pred
    forecast_df = pd.DataFrame(forecasts_data, index=future_index, columns=numeric_cols)
    return ThetaForecastResult(forecasts=forecast_df, models=models)

# ---------------------------------------------------------------------------
# Further advanced forecasting methods
# These methods leverage additional external libraries such as scikit‑learn,
# tensorflow, tbats and neuralprophet to provide state‑of‑the‑art models.  If
# the required library is not available in your environment an informative
# ImportError will be raised.

@dataclass
class ElasticNetForecastResult:
    """Result container for :func:`elastic_net_forecast`.

    Attributes
    ----------
    forecasts : pandas.DataFrame
        Forecasted values for each target series.  The index contains
        the forecast dates and the columns correspond to the numeric
        columns of the input (excluding the date and exogenous columns).
    models : Dict[str, object]
        Trained scikit‑learn ElasticNet or ElasticNetCV models for each
        series.
    """

    forecasts: pd.DataFrame
    models: Dict[str, object]


def elastic_net_forecast(
    date: Union[str, pd.Series, Iterable],
    df: pd.DataFrame,
    *,
    periods: int = 12,
    lags: int = 10,
    exog: Optional[List[str]] = None,
    freq: Optional[str] = None,
    model_params: Optional[dict] = None,
) -> ElasticNetForecastResult:
    """Forecast numeric series using ElasticNet regression with lagged features.

    Each target column is modelled independently.  Lagged values of the
    target up to ``lags`` steps are used as predictors along with
    optional exogenous variables at the current time step.  Models are
    trained either using ``ElasticNetCV`` for automatic hyperparameter
    selection or ``ElasticNet`` with user‑specified parameters.  The
    function then iteratively produces forecasts for ``periods`` future
    steps.

    Parameters
    ----------
    date : str or pandas.Series or iterable
        Column name, series or iterable containing date information.
    df : pandas.DataFrame
        DataFrame with the data.  Must include the date column and
        one or more numeric columns to forecast.
    periods : int, default 12
        Number of future periods to forecast.
    lags : int, default 10
        Number of lag observations to include as predictors.
    exog : list of str or None, default None
        Names of exogenous columns to include as predictors.  If
        provided, future values for these variables can be passed via
        ``model_params['exog_future']`` as a DataFrame with ``periods``
        rows and the same columns as ``exog``.  If not provided, zeros
        will be used for future exogenous values.
    freq : str or None, default None
        Frequency string for generating forecast dates.  If ``None``,
        the frequency is inferred from the date series.
    model_params : dict or None, default None
        Additional keyword arguments passed to the scikit‑learn model.
        Recognised keys include ``exog_future`` (future exogenous
        DataFrame), ``use_cv`` (bool indicating whether to use
        ``ElasticNetCV`` instead of ``ElasticNet``), and any valid
        parameters for ``ElasticNetCV`` or ``ElasticNet``.

    Returns
    -------
    ElasticNetForecastResult
        Dataclass containing the forecast DataFrame and fitted models.

    Raises
    ------
    ImportError
        If scikit‑learn is not installed.
    ValueError
        If no numeric columns are available to model.
    """
    try:
        from sklearn.linear_model import ElasticNet, ElasticNetCV
    except Exception as e:
        raise ImportError(
            "scikit‑learn is required for ElasticNet forecasting."
        ) from e
    if model_params is None:
        model_params = {}
    # Extract optional future exogenous values and flags
    exog_future = model_params.pop('exog_future', None)
    use_cv = bool(model_params.pop('use_cv', True))
    # Determine date series
    if isinstance(date, str):
        if date not in df.columns:
            raise KeyError(f"Date column '{date}' not found in DataFrame")
        date_series = df[date]
    else:
        date_series = pd.Series(date)
    dt = pd.to_datetime(date_series)
    if dt.empty:
        raise ValueError("Date series is empty")
    # Identify target and exogenous columns
    exog_cols = exog or []
    target_cols = [c for c in df.columns if c != date and (c not in exog_cols) and pd.api.types.is_numeric_dtype(df[c])]
    if not target_cols:
        raise ValueError("No numeric columns found to forecast with ElasticNet")
    # Determine frequency and future dates
    if freq is None:
        try:
            freq = pd.infer_freq(dt)
        except Exception:
            freq = None
    if freq is not None:
        try:
            future_index = pd.date_range(start=dt.iloc[-1], periods=periods + 1, freq=freq)[1:]
        except Exception:
            freq = None
            future_index = None
    if freq is None:
        diffs = dt.diff().dropna()
        delta = diffs.mode()[0] if not diffs.empty else pd.Timedelta(days=1)
        future_index = pd.to_datetime([dt.iloc[-1] + delta * (i + 1) for i in range(periods)])
    # Prepare future exogenous values
    if exog_cols and exog_future is None:
        exog_future = pd.DataFrame(
            np.zeros((periods, len(exog_cols))), index=future_index, columns=exog_cols
        )
    elif exog_cols:
        exog_future = exog_future.copy()
        exog_future.index = future_index
        exog_future = exog_future[exog_cols]
    # Initialize storage
    models: Dict[str, object] = {}
    forecasts_data: Dict[str, List[float]] = {}
    # Iterate over each target column
    for col in target_cols:
        series = pd.to_numeric(df[col], errors='coerce').astype(float).reset_index(drop=True)
        n = len(series)
        if n <= lags:
            raise ValueError(f"Not enough observations to build lagged features for column '{col}'")
        # Build design matrix
        X_train = []
        y_train = []
        exog_matrix = df[exog_cols].reset_index(drop=True) if exog_cols else None
        for t in range(lags, n):
            lagged = series.iloc[t - lags:t].values
            features = list(lagged)
            if exog_cols:
                features += list(exog_matrix.iloc[t].values)
            X_train.append(features)
            y_train.append(series.iloc[t])
        X_train = np.array(X_train)
        y_train = np.array(y_train)
        # Choose ElasticNet or ElasticNetCV
        if use_cv:
            model = ElasticNetCV(**model_params)
        else:
            model = ElasticNet(**model_params)
        model.fit(X_train, y_train)
        models[col] = model
        # Iterative forecasting
        last_lags = series.iloc[-lags:].values.tolist()
        exog_future_values = exog_future.values if exog_cols else None
        preds: List[float] = []
        for step in range(periods):
            features = last_lags[-lags:].copy()
            if exog_cols:
                features += list(exog_future_values[step])
            pred = float(model.predict(np.array(features).reshape(1, -1))[0])
            preds.append(pred)
            last_lags.append(pred)
        forecasts_data[col] = preds
    forecast_df = pd.DataFrame(forecasts_data, index=future_index, columns=target_cols)
    return ElasticNetForecastResult(forecasts=forecast_df, models=models)


@dataclass
class SvrForecastResult:
    """Result container for :func:`svr_forecast`.

    Attributes
    ----------
    forecasts : pandas.DataFrame
        Forecasted values for each target series.
    models : Dict[str, object]
        Trained ``sklearn.svm.SVR`` models for each series.
    """
    forecasts: pd.DataFrame
    models: Dict[str, object]


def svr_forecast(
    date: Union[str, pd.Series, Iterable],
    df: pd.DataFrame,
    *,
    periods: int = 12,
    lags: int = 10,
    exog: Optional[List[str]] = None,
    freq: Optional[str] = None,
    model_params: Optional[dict] = None,
) -> SvrForecastResult:
    """Forecast numeric series using Support Vector Regression.

    This method constructs lagged feature matrices similar to
    :func:`elastic_net_forecast` and trains an ``SVR`` model for each
    target series.  Forecasts are generated iteratively, using the
    most recent predictions to inform subsequent steps.

    Parameters
    ----------
    date : str or pandas.Series or iterable
        Column name, series or iterable containing date information.
    df : pandas.DataFrame
        DataFrame with the data.  Must include the date column and
        one or more numeric columns to forecast.
    periods : int, default 12
        Number of future periods to forecast.
    lags : int, default 10
        Number of lag observations to include as predictors.
    exog : list of str or None, default None
        Names of exogenous columns to include as predictors.  If
        provided, future values for these variables can be passed via
        ``model_params['exog_future']`` as a DataFrame with ``periods``
        rows and the same columns as ``exog``.  If not provided, zeros
        will be used for future exogenous values.
    freq : str or None, default None
        Frequency string for generating forecast dates.  If ``None``,
        the frequency is inferred from the date series.
    model_params : dict or None, default None
        Additional keyword arguments passed to ``SVR``.

    Returns
    -------
    SvrForecastResult
        Dataclass containing the forecast DataFrame and fitted models.

    Raises
    ------
    ImportError
        If scikit‑learn is not installed.
    ValueError
        If no numeric columns are available to model.
    """
    try:
        from sklearn.svm import SVR
    except Exception as e:
        raise ImportError(
            "scikit‑learn is required for SVR forecasting."
        ) from e
    if model_params is None:
        model_params = {}
    exog_future = model_params.pop('exog_future', None)
    # Parse date
    if isinstance(date, str):
        if date not in df.columns:
            raise KeyError(f"Date column '{date}' not found in DataFrame")
        date_series = df[date]
    else:
        date_series = pd.Series(date)
    dt = pd.to_datetime(date_series)
    if dt.empty:
        raise ValueError("Date series is empty")
    exog_cols = exog or []
    target_cols = [c for c in df.columns if c != date and (c not in exog_cols) and pd.api.types.is_numeric_dtype(df[c])]
    if not target_cols:
        raise ValueError("No numeric columns found to forecast with SVR")
    # Determine frequency and future dates
    if freq is None:
        try:
            freq = pd.infer_freq(dt)
        except Exception:
            freq = None
    if freq is not None:
        try:
            future_index = pd.date_range(start=dt.iloc[-1], periods=periods + 1, freq=freq)[1:]
        except Exception:
            freq = None
            future_index = None
    if freq is None:
        diffs = dt.diff().dropna()
        delta = diffs.mode()[0] if not diffs.empty else pd.Timedelta(days=1)
        future_index = pd.to_datetime([dt.iloc[-1] + delta * (i + 1) for i in range(periods)])
    # Prepare future exogenous values
    if exog_cols and exog_future is None:
        exog_future = pd.DataFrame(
            np.zeros((periods, len(exog_cols))), index=future_index, columns=exog_cols
        )
    elif exog_cols:
        exog_future = exog_future.copy()
        exog_future.index = future_index
        exog_future = exog_future[exog_cols]
    # Train models
    models: Dict[str, object] = {}
    forecasts_data: Dict[str, List[float]] = {}
    for col in target_cols:
        series = pd.to_numeric(df[col], errors='coerce').astype(float).reset_index(drop=True)
        n = len(series)
        if n <= lags:
            raise ValueError(f"Not enough observations to build lagged features for column '{col}'")
        X_train = []
        y_train = []
        exog_matrix = df[exog_cols].reset_index(drop=True) if exog_cols else None
        for t in range(lags, n):
            lagged = series.iloc[t - lags:t].values
            features = list(lagged)
            if exog_cols:
                features += list(exog_matrix.iloc[t].values)
            X_train.append(features)
            y_train.append(series.iloc[t])
        X_train = np.array(X_train)
        y_train = np.array(y_train)
        model = SVR(**model_params)
        model.fit(X_train, y_train)
        models[col] = model
        last_lags = series.iloc[-lags:].values.tolist()
        exog_future_values = exog_future.values if exog_cols else None
        preds: List[float] = []
        for step in range(periods):
            features = last_lags[-lags:].copy()
            if exog_cols:
                features += list(exog_future_values[step])
            pred = float(model.predict(np.array(features).reshape(1, -1))[0])
            preds.append(pred)
            last_lags.append(pred)
        forecasts_data[col] = preds
    forecast_df = pd.DataFrame(forecasts_data, index=future_index, columns=target_cols)
    return SvrForecastResult(forecasts=forecast_df, models=models)


@dataclass
class TcnForecastResult:
    """Result container for :func:`tcn_forecast`.

    Attributes
    ----------
    forecasts : pandas.DataFrame
        Forecasted values for each target series.
    models : Dict[str, object]
        Trained TensorFlow models for each series.
    """
    forecasts: pd.DataFrame
    models: Dict[str, object]


def tcn_forecast(
    date: Union[str, pd.Series, Iterable],
    df: pd.DataFrame,
    *,
    periods: int = 12,
    lags: int = 24,
    freq: Optional[str] = None,
    epochs: int = 50,
    batch_size: int = 32,
    verbose: int = 0,
) -> TcnForecastResult:
    """Forecast univariate series using a Temporal Convolutional Network (TCN).

    Each numeric column is modelled separately using a simple TCN built
    with ``tensorflow.keras``.  The TCN consists of a stack of
    dilated causal convolution layers followed by a dense output
    layer.  Lagged values of the series serve as inputs.  This
    method is computationally intensive and may require GPU support
    for large datasets.  If TensorFlow is not installed, an
    ``ImportError`` is raised.

    Parameters
    ----------
    date : str or pandas.Series or iterable
        Column name, series or iterable containing date information.
    df : pandas.DataFrame
        DataFrame with the data.  Must include the date column and
        one or more numeric columns to forecast.
    periods : int, default 12
        Number of future periods to forecast.
    lags : int, default 24
        Number of lagged observations to use as input to the network.
    freq : str or None, default None
        Frequency string for generating forecast dates.  If ``None``,
        the frequency is inferred from the date series.
    epochs : int, default 50
        Number of training epochs for each model.
    batch_size : int, default 32
        Batch size for model training.
    verbose : int, default 0
        Verbosity level passed to ``model.fit``.

    Returns
    -------
    TcnForecastResult
        Dataclass containing the forecast DataFrame and fitted models.

    Raises
    ------
    ImportError
        If ``tensorflow`` is not installed.
    ValueError
        If no numeric columns are available for forecasting.
    """
    try:
        import tensorflow as tf  # type: ignore
    except Exception as e:
        raise ImportError(
            "tensorflow is required for TCN forecasting. Please install tensorflow to use this function."
        ) from e
    # Parse date
    if isinstance(date, str):
        if date not in df.columns:
            raise KeyError(f"Date column '{date}' not found in DataFrame")
        date_series = df[date]
    else:
        date_series = pd.Series(date)
    dt = pd.to_datetime(date_series)
    if dt.empty:
        raise ValueError("Date series is empty")
    # Determine frequency and future dates
    if freq is None:
        try:
            freq = pd.infer_freq(dt)
        except Exception:
            freq = None
    if freq is not None:
        try:
            future_index = pd.date_range(start=dt.iloc[-1], periods=periods + 1, freq=freq)[1:]
        except Exception:
            freq = None
            future_index = None
    if freq is None:
        diffs = dt.diff().dropna()
        delta = diffs.mode()[0] if not diffs.empty else pd.Timedelta(days=1)
        future_index = pd.to_datetime([dt.iloc[-1] + delta * (i + 1) for i in range(periods)])
    # Identify numeric columns
    numeric_cols = [c for c in df.columns if c != date and pd.api.types.is_numeric_dtype(df[c])]
    if not numeric_cols:
        raise ValueError("No numeric columns found to forecast with TCN")
    models: Dict[str, object] = {}
    forecasts_data: Dict[str, List[float]] = {}
    for col in numeric_cols:
        series = pd.to_numeric(df[col], errors='coerce').astype(float).reset_index(drop=True)
        n = len(series)
        if n <= lags:
            raise ValueError(f"Not enough observations to build lagged features for column '{col}'")
        # Build training sequences
        X_train = []
        y_train = []
        for t in range(lags, n):
            X_train.append(series.iloc[t - lags:t].values.reshape(-1, 1))
            y_train.append(series.iloc[t])
        X_train = np.stack(X_train)
        y_train = np.array(y_train)
        # Define TCN model
        inputs = tf.keras.Input(shape=(lags, 1))
        x = tf.keras.layers.Conv1D(32, kernel_size=2, dilation_rate=1, padding='causal', activation='relu')(inputs)
        x = tf.keras.layers.Conv1D(32, kernel_size=2, dilation_rate=2, padding='causal', activation='relu')(x)
        x = tf.keras.layers.Conv1D(32, kernel_size=2, dilation_rate=4, padding='causal', activation='relu')(x)
        x = tf.keras.layers.Flatten()(x)
        outputs = tf.keras.layers.Dense(1)(x)
        model = tf.keras.Model(inputs, outputs)
        model.compile(optimizer='adam', loss='mse')
        model.fit(X_train, y_train, epochs=epochs, batch_size=batch_size, verbose=verbose)
        models[col] = model
        # Generate forecasts iteratively
        last_lags = series.iloc[-lags:].values.reshape(1, -1, 1).copy()
        preds: List[float] = []
        for _ in range(periods):
            pred = float(model.predict(last_lags, verbose=0)[0, 0])
            preds.append(pred)
            # Update last_lags
            new_seq = np.append(last_lags[0, 1:, 0], pred)
            last_lags = new_seq.reshape(1, -1, 1)
        forecasts_data[col] = preds
    forecast_df = pd.DataFrame(forecasts_data, index=future_index, columns=numeric_cols)
    return TcnForecastResult(forecasts=forecast_df, models=models)


@dataclass
class BatsForecastResult:
    """Result container for :func:`bats_forecast`.

    Attributes
    ----------
    forecasts : pandas.DataFrame
        Forecasted values for each series.
    models : Dict[str, object]
        Fitted TBATS/BATS models for each series.
    """
    forecasts: pd.DataFrame
    models: Dict[str, object]


def bats_forecast(
    date: Union[str, pd.Series, Iterable],
    df: pd.DataFrame,
    *,
    periods: int = 12,
    seasonal_periods: Optional[Iterable[int]] = None,
    use_box_cox: bool = True,
    use_trend: bool = True,
    use_damped_trend: bool = True,
    freq: Optional[str] = None,
) -> BatsForecastResult:
    """Forecast univariate series using TBATS or BATS models.

    This function fits either a TBATS (Trigonometric, Box‑Cox, ARMA,
    Trend, Seasonal) or BATS (Box‑Cox, ARMA, Trend, Seasonal) model to
    each numeric column depending on whether seasonal periods are
    provided.  The ``tbats`` library must be installed to use this
    function.

    Parameters
    ----------
    date : str or pandas.Series or iterable
        Column name, series or iterable containing date information.
    df : pandas.DataFrame
        DataFrame with the data.  Numeric columns are modelled
        individually.
    periods : int, default 12
        Number of future periods to forecast.
    seasonal_periods : iterable of int or None, default None
        Seasonal periods to fit.  If provided, TBATS is used.
    use_box_cox : bool, default True
        Whether to apply a Box–Cox transformation when fitting.
    use_trend : bool, default True
        Whether to include a trend component.
    use_damped_trend : bool, default True
        Whether to include a damped trend component.
    freq : str or None, default None
        Frequency string for generating forecast dates.  If ``None``,
        the frequency is inferred from the date series.

    Returns
    -------
    BatsForecastResult
        Dataclass containing the forecast DataFrame and fitted models.

    Raises
    ------
    ImportError
        If the ``tbats`` package is not installed.
    ValueError
        If no numeric columns are available to model.
    """
    try:
        from tbats import TBATS, BATS  # type: ignore
    except Exception as e:
        raise ImportError(
            "The 'tbats' library is required for TBATS/BATS forecasting. Please install tbats to use this function."
        ) from e
    # Parse date
    if isinstance(date, str):
        if date not in df.columns:
            raise KeyError(f"Date column '{date}' not found in DataFrame")
        date_series = df[date]
    else:
        date_series = pd.Series(date)
    dt = pd.to_datetime(date_series)
    if dt.empty:
        raise ValueError("Date series is empty")
    # Determine frequency and future dates
    if freq is None:
        try:
            freq = pd.infer_freq(dt)
        except Exception:
            freq = None
    if freq is not None:
        try:
            future_index = pd.date_range(start=dt.iloc[-1], periods=periods + 1, freq=freq)[1:]
        except Exception:
            freq = None
            future_index = None
    if freq is None:
        diffs = dt.diff().dropna()
        delta = diffs.mode()[0] if not diffs.empty else pd.Timedelta(days=1)
        future_index = pd.to_datetime([dt.iloc[-1] + delta * (i + 1) for i in range(periods)])
    numeric_cols = [c for c in df.columns if c != date and pd.api.types.is_numeric_dtype(df[c])]
    if not numeric_cols:
        raise ValueError("No numeric columns found to forecast with TBATS/BATS")
    models: Dict[str, object] = {}
    forecasts_data: Dict[str, np.ndarray] = {}
    for col in numeric_cols:
        y = pd.to_numeric(df[col], errors='coerce').ffill().bfill().astype(float)
        # Choose estimator
        if seasonal_periods is not None:
            estimator = TBATS(
                seasonal_periods=seasonal_periods,
                use_box_cox=use_box_cox,
                use_trend=use_trend,
                use_damped_trend=use_damped_trend,
            )
        else:
            estimator = BATS(
                use_box_cox=use_box_cox,
                use_trend=use_trend,
                use_damped_trend=use_damped_trend,
            )
        model = estimator.fit(y)
        preds = model.forecast(steps=periods)
        models[col] = model
        forecasts_data[col] = preds
    forecast_df = pd.DataFrame(forecasts_data, index=future_index, columns=numeric_cols)
    return BatsForecastResult(forecasts=forecast_df, models=models)


@dataclass
class NeuralProphetForecastResult:
    """Result container for :func:`neuralprophet_forecast`.

    Attributes
    ----------
    forecasts : pandas.DataFrame
        Forecasted values for each series.
    models : Dict[str, object]
        Fitted NeuralProphet models for each series.
    """
    forecasts: pd.DataFrame
    models: Dict[str, object]


def neuralprophet_forecast(
    date: Union[str, pd.Series, Iterable],
    df: pd.DataFrame,
    *,
    periods: int = 12,
    freq: Optional[str] = None,
    model_params: Optional[dict] = None,
) -> NeuralProphetForecastResult:
    """Forecast univariate series using NeuralProphet.

    NeuralProphet combines elements of Facebook’s Prophet with neural
    networks to capture non‑linear relationships and seasonality.
    Each numeric column is converted into a two‑column DataFrame with
    ``ds`` (datetime) and ``y`` (value) columns.  A separate
    ``NeuralProphet`` model is fit per series using any provided
    ``model_params``.  The forecast horizon is controlled by
    ``periods``.  The ``freq`` parameter determines the frequency of
    the future DataFrame; if ``None``, it is inferred.

    Parameters
    ----------
    date : str or pandas.Series or iterable
        Column name, series or iterable containing date information.
    df : pandas.DataFrame
        DataFrame with the data.  Must include the date column and
        one or more numeric columns to forecast.
    periods : int, default 12
        Number of future periods to forecast.
    freq : str or None, default None
        Frequency string for generating forecast dates.  If ``None``,
        frequency is inferred from the date series.
    model_params : dict or None, default None
        Additional keyword arguments passed to the ``NeuralProphet``
        constructor.  See the ``neuralprophet`` documentation for
        available options.

    Returns
    -------
    NeuralProphetForecastResult
        Dataclass containing the forecast DataFrame and fitted models.

    Raises
    ------
    ImportError
        If the ``neuralprophet`` package is not installed.
    ValueError
        If no numeric columns are available to model.
    """
    try:
        from neuralprophet import NeuralProphet  # type: ignore
    except Exception as e:
        raise ImportError(
            "The neuralprophet package is required for neuralprophet forecasting. Please install neuralprophet to use this function."
        ) from e
    if model_params is None:
        model_params = {}
    # Parse date
    if isinstance(date, str):
        if date not in df.columns:
            raise KeyError(f"Date column '{date}' not found in DataFrame")
        date_series = df[date]
    else:
        date_series = pd.Series(date)
    dt = pd.to_datetime(date_series)
    if dt.empty:
        raise ValueError("Date series is empty")
    # Infer frequency and future dates
    if freq is None:
        try:
            freq = pd.infer_freq(dt)
        except Exception:
            freq = None
    # Determine numeric columns
    numeric_cols = [c for c in df.columns if c != date and pd.api.types.is_numeric_dtype(df[c])]
    if not numeric_cols:
        raise ValueError("No numeric columns found to forecast with NeuralProphet")
    # Prepare storage
    models: Dict[str, object] = {}
    forecast_dict: Dict[str, np.ndarray] = {}
    # Fit each series separately
    for col in numeric_cols:
        # Prepare DataFrame for NeuralProphet
        temp = pd.DataFrame({
            'ds': dt,
            'y': pd.to_numeric(df[col], errors='coerce'),
        }).dropna()
        # Create model
        m = NeuralProphet(**model_params)
        m.fit(temp, freq=freq, verbose=False)
        future = m.make_future_dataframe(temp, periods=periods, n_historic_predictions=False)
        forecast = m.predict(future)
        # Extract predictions from 'yhat1' column (default output)
        yhat = forecast['yhat1'].values
        # The forecast array may include historic predictions; we want only the last 'periods' entries
        preds = yhat[-periods:]
        models[col] = m
        forecast_dict[col] = preds
    # Create index for forecast
    if freq is not None:
        try:
            future_index = pd.date_range(start=dt.iloc[-1], periods=periods + 1, freq=freq)[1:]
        except Exception:
            freq = None
            future_index = None
    if freq is None:
        diffs = dt.diff().dropna()
        delta = diffs.mode()[0] if not diffs.empty else pd.Timedelta(days=1)
        future_index = pd.to_datetime([dt.iloc[-1] + delta * (i + 1) for i in range(periods)])
    forecast_df = pd.DataFrame(forecast_dict, index=future_index, columns=numeric_cols)
    return NeuralProphetForecastResult(forecasts=forecast_df, models=models)

@dataclass
class CatBoostForecastResult:
    """Result container for :func:`catboost_forecast`.

    Attributes
    ----------
    forecasts : pandas.DataFrame
        Forecasted values for each target series.
    models : Dict[str, object]
        Trained ``catboost.CatBoostRegressor`` models for each series.
    """
    forecasts: pd.DataFrame
    models: Dict[str, object]


def catboost_forecast(
    date: Union[str, pd.Series, Iterable],
    df: pd.DataFrame,
    *,
    periods: int = 12,
    lags: int = 10,
    exog: Optional[List[str]] = None,
    freq: Optional[str] = None,
    model_params: Optional[dict] = None,
) -> CatBoostForecastResult:
    """Forecast numeric series using CatBoost regressors with lagged features.

    This method resembles :func:`xgboost_forecast` but employs
    ``catboost.CatBoostRegressor`` to model non‑linear relationships.
    Each numeric column (excluding the date and exogenous columns) is
    modelled separately.  Lagged values up to ``lags`` and optional
    exogenous variables at the current time step are used as predictors.
    Future exogenous values may be provided via ``model_params['exog_future']``.

    Parameters
    ----------
    date : str or pandas.Series or iterable
        Column name, series or iterable containing date information.
    df : pandas.DataFrame
        DataFrame with the data.  Must include the date column and
        one or more numeric columns to forecast.
    periods : int, default 12
        Number of future periods to forecast.
    lags : int, default 10
        Number of lag observations to include as predictors.
    exog : list of str or None, default None
        Names of exogenous columns to include as predictors.  These
        columns must be present in ``df``.  If provided, future values
        for these variables can be passed via ``model_params['exog_future']``.
    freq : str or None, default None
        Frequency string for generating forecast dates.  If ``None``,
        the frequency is inferred from the date series.
    model_params : dict or None, default None
        Additional parameters passed to ``catboost.CatBoostRegressor``.
        Recognised key ``exog_future`` may be a DataFrame providing
        exogenous values for the forecast horizon.

    Returns
    -------
    CatBoostForecastResult
        Dataclass containing the forecasted values and fitted models.

    Raises
    ------
    ImportError
        If the ``catboost`` package is not installed.
    ValueError
        If no numeric columns are available to model.
    """
    try:
        from catboost import CatBoostRegressor  # type: ignore
    except Exception as e:
        raise ImportError(
            "catboost is required for CatBoost forecasting. Please install catboost to use this function."
        ) from e
    if model_params is None:
        model_params = {}
    exog_future = model_params.pop('exog_future', None)
    # Parse date
    if isinstance(date, str):
        if date not in df.columns:
            raise KeyError(f"Date column '{date}' not found in DataFrame")
        date_series = df[date]
    else:
        date_series = pd.Series(date)
    dt = pd.to_datetime(date_series)
    if dt.empty:
        raise ValueError("Date series is empty")
    # Identify target and exogenous columns
    exog_cols = exog or []
    target_cols = [c for c in df.columns if c != date and (c not in exog_cols) and pd.api.types.is_numeric_dtype(df[c])]
    if not target_cols:
        raise ValueError("No numeric columns found to forecast with CatBoost")
    # Determine frequency and future dates
    if freq is None:
        try:
            freq = pd.infer_freq(dt)
        except Exception:
            freq = None
    if freq is not None:
        try:
            future_index = pd.date_range(start=dt.iloc[-1], periods=periods + 1, freq=freq)[1:]
        except Exception:
            freq = None
            future_index = None
    if freq is None:
        diffs = dt.diff().dropna()
        delta = diffs.mode()[0] if not diffs.empty else pd.Timedelta(days=1)
        future_index = pd.to_datetime([dt.iloc[-1] + delta * (i + 1) for i in range(periods)])
    # Prepare future exogenous values
    if exog_cols and exog_future is None:
        exog_future = pd.DataFrame(
            np.zeros((periods, len(exog_cols))), index=future_index, columns=exog_cols
        )
    elif exog_cols:
        exog_future = exog_future.copy()
        exog_future.index = future_index
        exog_future = exog_future[exog_cols]
    models: Dict[str, object] = {}
    forecasts_data: Dict[str, List[float]] = {}
    for col in target_cols:
        series = pd.to_numeric(df[col], errors='coerce').astype(float).reset_index(drop=True)
        n = len(series)
        if n <= lags:
            raise ValueError(f"Not enough observations to build lagged features for column '{col}'")
        X_train = []
        y_train = []
        exog_matrix = df[exog_cols].reset_index(drop=True) if exog_cols else None
        for t in range(lags, n):
            lagged = series.iloc[t - lags:t].values
            features = list(lagged)
            if exog_cols:
                features += list(exog_matrix.iloc[t].values)
            X_train.append(features)
            y_train.append(series.iloc[t])
        X_train = np.array(X_train)
        y_train = np.array(y_train)
        default_params = {
            'iterations': 500,
            'learning_rate': 0.05,
            'depth': 6,
            'loss_function': 'RMSE',
            'verbose': False,
        }
        params = default_params.copy()
        params.update(model_params)
        model = CatBoostRegressor(**params)
        model.fit(X_train, y_train)
        models[col] = model
        last_lags = series.iloc[-lags:].values.tolist()
        exog_future_values = exog_future.values if exog_cols else None
        preds: List[float] = []
        for step in range(periods):
            features = last_lags[-lags:].copy()
            if exog_cols:
                features += list(exog_future_values[step])
            pred = float(model.predict(np.array(features).reshape(1, -1))[0])
            preds.append(pred)
            last_lags.append(pred)
        forecasts_data[col] = preds
    forecast_df = pd.DataFrame(forecasts_data, index=future_index, columns=target_cols)
    return CatBoostForecastResult(forecasts=forecast_df, models=models)


@dataclass
class KnnForecastResult:
    """Result container for :func:`knn_forecast`.

    Attributes
    ----------
    forecasts : pandas.DataFrame
        Forecasted values for each target series.
    models : Dict[str, object]
        Trained ``sklearn.neighbors.KNeighborsRegressor`` models for each series.
    """
    forecasts: pd.DataFrame
    models: Dict[str, object]


def knn_forecast(
    date: Union[str, pd.Series, Iterable],
    df: pd.DataFrame,
    *,
    periods: int = 12,
    lags: int = 10,
    exog: Optional[List[str]] = None,
    freq: Optional[str] = None,
    model_params: Optional[dict] = None,
) -> KnnForecastResult:
    """Forecast numeric series using k‑nearest neighbors regression.

    The function builds lagged feature matrices and fits a
    ``KNeighborsRegressor`` for each target series.  Predictions are
    generated iteratively using the most recent lagged values.  You
    can specify exogenous variables to include as additional features.

    Parameters
    ----------
    date : str or pandas.Series or iterable
        Column name, series or iterable containing date information.
    df : pandas.DataFrame
        DataFrame with the data.  Must include the date column and
        one or more numeric columns to forecast.
    periods : int, default 12
        Number of future periods to forecast.
    lags : int, default 10
        Number of lag observations to include as predictors.
    exog : list of str or None, default None
        Names of exogenous columns to include as predictors.  Future
        values for these variables can be passed via
        ``model_params['exog_future']`` as a DataFrame.
    freq : str or None, default None
        Frequency string for generating forecast dates.  If ``None``,
        the frequency is inferred from the date series.
    model_params : dict or None, default None
        Additional keyword arguments passed to ``KNeighborsRegressor``.

    Returns
    -------
    KnnForecastResult
        Dataclass containing the forecast DataFrame and fitted models.

    Raises
    ------
    ImportError
        If scikit‑learn is not installed.
    ValueError
        If no numeric columns are available to model.
    """
    try:
        from sklearn.neighbors import KNeighborsRegressor
    except Exception as e:
        raise ImportError(
            "scikit‑learn is required for KNN forecasting."
        ) from e
    if model_params is None:
        model_params = {}
    exog_future = model_params.pop('exog_future', None)
    # Parse date
    if isinstance(date, str):
        if date not in df.columns:
            raise KeyError(f"Date column '{date}' not found in DataFrame")
        date_series = df[date]
    else:
        date_series = pd.Series(date)
    dt = pd.to_datetime(date_series)
    if dt.empty:
        raise ValueError("Date series is empty")
    # Identify target and exogenous columns
    exog_cols = exog or []
    target_cols = [c for c in df.columns if c != date and (c not in exog_cols) and pd.api.types.is_numeric_dtype(df[c])]
    if not target_cols:
        raise ValueError("No numeric columns found to forecast with KNN")
    # Determine frequency and future dates
    if freq is None:
        try:
            freq = pd.infer_freq(dt)
        except Exception:
            freq = None
    if freq is not None:
        try:
            future_index = pd.date_range(start=dt.iloc[-1], periods=periods + 1, freq=freq)[1:]
        except Exception:
            freq = None
            future_index = None
    if freq is None:
        diffs = dt.diff().dropna()
        delta = diffs.mode()[0] if not diffs.empty else pd.Timedelta(days=1)
        future_index = pd.to_datetime([dt.iloc[-1] + delta * (i + 1) for i in range(periods)])
    # Prepare future exogenous values
    if exog_cols and exog_future is None:
        exog_future = pd.DataFrame(
            np.zeros((periods, len(exog_cols))), index=future_index, columns=exog_cols
        )
    elif exog_cols:
        exog_future = exog_future.copy()
        exog_future.index = future_index
        exog_future = exog_future[exog_cols]
    models: Dict[str, object] = {}
    forecasts_data: Dict[str, List[float]] = {}
    for col in target_cols:
        series = pd.to_numeric(df[col], errors='coerce').astype(float).reset_index(drop=True)
        n = len(series)
        if n <= lags:
            raise ValueError(f"Not enough observations to build lagged features for column '{col}'")
        X_train = []
        y_train = []
        exog_matrix = df[exog_cols].reset_index(drop=True) if exog_cols else None
        for t in range(lags, n):
            lagged = series.iloc[t - lags:t].values
            features = list(lagged)
            if exog_cols:
                features += list(exog_matrix.iloc[t].values)
            X_train.append(features)
            y_train.append(series.iloc[t])
        X_train = np.array(X_train)
        y_train = np.array(y_train)
        model = KNeighborsRegressor(**model_params)
        model.fit(X_train, y_train)
        models[col] = model
        last_lags = series.iloc[-lags:].values.tolist()
        exog_future_values = exog_future.values if exog_cols else None
        preds: List[float] = []
        for step in range(periods):
            features = last_lags[-lags:].copy()
            if exog_cols:
                features += list(exog_future_values[step])
            pred = float(model.predict(np.array(features).reshape(1, -1))[0])
            preds.append(pred)
            last_lags.append(pred)
        forecasts_data[col] = preds
    forecast_df = pd.DataFrame(forecasts_data, index=future_index, columns=target_cols)
    return KnnForecastResult(forecasts=forecast_df, models=models)


@dataclass
class TransformerForecastResult:
    """Result container for :func:`transformer_forecast`.

    Attributes
    ----------
    forecasts : pandas.DataFrame
        Forecasted values for each series.
    models : Dict[str, object]
        Trained TensorFlow models for each series.
    """
    forecasts: pd.DataFrame
    models: Dict[str, object]


def transformer_forecast(
    date: Union[str, pd.Series, Iterable],
    df: pd.DataFrame,
    *,
    periods: int = 12,
    lags: int = 24,
    freq: Optional[str] = None,
    epochs: int = 50,
    batch_size: int = 32,
    verbose: int = 0,
    num_heads: int = 2,
    key_dim: int = 32,
) -> TransformerForecastResult:
    """Forecast univariate series using a simple Transformer model.

    A Transformer with multi‑head self‑attention is trained on lagged
    sequences of the target series.  This architecture can capture
    complex temporal dependencies and non‑linear patterns.  Each
    numeric column is modelled separately.  The function requires
    ``tensorflow`` to be installed.

    Parameters
    ----------
    date : str or pandas.Series or iterable
        Column name, series or iterable containing date information.
    df : pandas.DataFrame
        DataFrame with the data.  Must include the date column and
        one or more numeric columns to forecast.
    periods : int, default 12
        Number of future periods to forecast.
    lags : int, default 24
        Number of lagged observations to use as input to the model.
    freq : str or None, default None
        Frequency string for generating forecast dates.  If ``None``,
        the frequency is inferred from the date series.
    epochs : int, default 50
        Number of training epochs for each model.
    batch_size : int, default 32
        Batch size for model training.
    verbose : int, default 0
        Verbosity level passed to ``model.fit``.
    num_heads : int, default 2
        Number of attention heads in the Transformer.
    key_dim : int, default 32
        Dimensionality of the query and key vectors in the
        multi‑head attention layer.

    Returns
    -------
    TransformerForecastResult
        Dataclass containing the forecast DataFrame and fitted models.

    Raises
    ------
    ImportError
        If ``tensorflow`` is not installed.
    ValueError
        If no numeric columns are available to model.
    """
    try:
        import tensorflow as tf  # type: ignore
    except Exception as e:
        raise ImportError(
            "tensorflow is required for transformer forecasting. Please install tensorflow to use this function."
        ) from e
    # Parse date
    if isinstance(date, str):
        if date not in df.columns:
            raise KeyError(f"Date column '{date}' not found in DataFrame")
        date_series = df[date]
    else:
        date_series = pd.Series(date)
    dt = pd.to_datetime(date_series)
    if dt.empty:
        raise ValueError("Date series is empty")
    # Determine frequency and future dates
    if freq is None:
        try:
            freq = pd.infer_freq(dt)
        except Exception:
            freq = None
    if freq is not None:
        try:
            future_index = pd.date_range(start=dt.iloc[-1], periods=periods + 1, freq=freq)[1:]
        except Exception:
            freq = None
            future_index = None
    if freq is None:
        diffs = dt.diff().dropna()
        delta = diffs.mode()[0] if not diffs.empty else pd.Timedelta(days=1)
        future_index = pd.to_datetime([dt.iloc[-1] + delta * (i + 1) for i in range(periods)])
    # Identify numeric columns
    numeric_cols = [c for c in df.columns if c != date and pd.api.types.is_numeric_dtype(df[c])]
    if not numeric_cols:
        raise ValueError("No numeric columns found to forecast with transformer")
    models: Dict[str, object] = {}
    forecasts_data: Dict[str, List[float]] = {}
    for col in numeric_cols:
        series = pd.to_numeric(df[col], errors='coerce').astype(float).reset_index(drop=True)
        n = len(series)
        if n <= lags:
            raise ValueError(f"Not enough observations to build lagged features for column '{col}'")
        X_train = []
        y_train = []
        for t in range(lags, n):
            X_train.append(series.iloc[t - lags:t].values.reshape(lags, 1))
            y_train.append(series.iloc[t])
        X_train = np.stack(X_train)
        y_train = np.array(y_train)
        # Build transformer model
        inputs = tf.keras.Input(shape=(lags, 1))
        # Project to embedding dimension
        x = tf.keras.layers.Conv1D(key_dim, kernel_size=1, activation='relu')(inputs)
        # Positional embedding: simple linear transformation of positions
        positions = tf.range(start=0, limit=lags, delta=1)
        pos_embed = tf.keras.layers.Embedding(input_dim=lags, output_dim=key_dim)(positions)
        pos_embed = tf.expand_dims(pos_embed, axis=0)
        x = x + pos_embed
        # Self‑attention
        attn_output = tf.keras.layers.MultiHeadAttention(num_heads=num_heads, key_dim=key_dim)(x, x)
        attn_output = tf.keras.layers.GlobalAveragePooling1D()(attn_output)
        outputs = tf.keras.layers.Dense(1)(attn_output)
        model = tf.keras.Model(inputs, outputs)
        model.compile(optimizer='adam', loss='mse')
        model.fit(X_train, y_train, epochs=epochs, batch_size=batch_size, verbose=verbose)
        models[col] = model
        # Iterative forecasting
        last_lags = series.iloc[-lags:].values.reshape(1, lags, 1)
        preds: List[float] = []
        for _ in range(periods):
            # Add positional embedding to last_lags
            embedded = tf.keras.layers.Conv1D(key_dim, kernel_size=1, activation='relu')(last_lags)
            pos = tf.expand_dims(tf.range(start=0, limit=lags, delta=1), axis=0)
            pos_emb = tf.keras.layers.Embedding(input_dim=lags, output_dim=key_dim)(pos)
            x_in = embedded + pos_emb
            attn_out = tf.keras.layers.MultiHeadAttention(num_heads=num_heads, key_dim=key_dim)(x_in, x_in)
            pooled = tf.keras.layers.GlobalAveragePooling1D()(attn_out)
            pred = float(tf.keras.layers.Dense(1)(pooled).numpy()[0, 0])
            preds.append(pred)
            # Update last_lags
            new_seq = np.append(last_lags[0, 1:, 0], pred)
            last_lags = new_seq.reshape(1, lags, 1)
        forecasts_data[col] = preds
    forecast_df = pd.DataFrame(forecasts_data, index=future_index, columns=numeric_cols)
    return TransformerForecastResult(forecasts=forecast_df, models=models)