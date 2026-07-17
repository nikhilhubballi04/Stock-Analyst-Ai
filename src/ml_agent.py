import pandas as pd
import numpy as np
from xgboost import XGBRegressor
from sklearn.metrics import mean_absolute_percentage_error
from database import load_data


def create_features(df: pd.DataFrame, lags: int = 5) -> pd.DataFrame:
    """Turn the raw indicator data into a supervised learning table using returns."""
    df = df.copy()
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date").reset_index(drop=True)

    # Daily return instead of raw price
    df["return"] = df["close"].pct_change()

    # Lag features: past returns instead of past raw prices
    for lag in range(1, lags + 1):
        df[f"return_lag_{lag}"] = df["return"].shift(lag)

    # Normalize volume-based/indicator features that scale with price
    df["rsi_norm"] = df["rsi"] / 100  # RSI is already 0-100, just scale to 0-1
    df["macd_norm"] = df["macd"] / df["close"]  # scale relative to price
    df["ma20_dist"] = (df["close"] - df["ma_20"]) / df["close"]  # % distance from MA
    df["ma50_dist"] = (df["close"] - df["ma_50"]) / df["close"]

    # Target: TOMORROW's return, not tomorrow's price
    df["target"] = df["return"].shift(-1)

    feature_cols = [f"return_lag_{i}" for i in range(1, lags + 1)] + [
        "rsi_norm", "macd_norm", "ma20_dist", "ma50_dist"
    ]

    df = df.dropna().reset_index(drop=True)
    return df, feature_cols


def backtest_naive(df: pd.DataFrame, test_days: int = 30) -> float:
    """Naive baseline: tomorrow's price = today's price (0% predicted return)."""
    df = df.copy().sort_values("date").reset_index(drop=True)
    test = df.iloc[-test_days:]

    actual_prices = test["close"].values[1:]
    naive_predicted_prices = test["close"].values[:-1]  # predict no change

    mape = mean_absolute_percentage_error(actual_prices, naive_predicted_prices) * 100
    return round(mape, 2)


def train_xgboost(df: pd.DataFrame, lags: int = 5):
    """Train XGBoost to predict next-day RETURN, then convert back to price for evaluation."""
    data, feature_cols = create_features(df, lags)

    train = data.iloc[:-30]
    test = data.iloc[-30:]

    X_train, y_train = train[feature_cols], train["target"]
    X_test, y_test = test[feature_cols], test["target"]

    model = XGBRegressor(
        n_estimators=100,
        max_depth=3,
        learning_rate=0.05,
        random_state=42
    )
    model.fit(X_train, y_train)

    predicted_returns = model.predict(X_test)

    # Convert predicted returns back into actual prices for a fair MAPE comparison
    actual_prices = test["close"].values
    predicted_prices = test["close"].shift(1).values * (1 + predicted_returns)

    # Drop first row (no previous price to base prediction on within test set)
    valid = ~np.isnan(predicted_prices)
    mape = mean_absolute_percentage_error(actual_prices[valid], predicted_prices[valid]) * 100

    return model, feature_cols, round(mape, 2)


def forecast_next_day(model, df: pd.DataFrame, feature_cols: list, lags: int = 5):
    """Predict tomorrow's price using the most recent available data."""
    data, _ = create_features(df, lags)
    latest_row = data.iloc[[-1]][feature_cols]
    predicted_return = model.predict(latest_row)[0]

    latest_close = df.sort_values("date").iloc[-1]["close"]
    predicted_price = latest_close * (1 + predicted_return)
    return round(float(predicted_price), 2), round(float(predicted_return) * 100, 3)


if __name__ == "__main__":
    ticker = "AAPL"
    df = load_data(ticker)

    print(f"Loaded {len(df)} rows for {ticker}\n")

    naive_mape = backtest_naive(df)
    print(f"Naive baseline MAPE (last 30 days): {naive_mape}%")

    model, feature_cols, xgb_mape = train_xgboost(df)
    print(f"XGBoost (returns-based) MAPE (last 30 days): {xgb_mape}%")

    if xgb_mape < naive_mape:
        print(f"\nXGBoost beats the naive baseline by {round(naive_mape - xgb_mape, 2)} points.")
    else:
        print(f"\nXGBoost did NOT beat the naive baseline by {round(xgb_mape - naive_mape, 2)} points.")

    next_price, predicted_return_pct = forecast_next_day(model, df, feature_cols)
    latest_close = df.sort_values("date").iloc[-1]["close"]
    print(f"\nMost recent close: {latest_close}")
    print(f"Predicted return: {predicted_return_pct}%")
    print(f"Predicted next close: {next_price}")