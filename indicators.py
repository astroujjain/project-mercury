import pandas as pd
import numpy as np

def compute_rsi(series, length=14):
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    # use EMA smoothing
    avg_gain = gain.ewm(alpha=1/length, min_periods=length).mean()
    avg_loss = loss.ewm(alpha=1/length, min_periods=length).mean()
    rs = avg_gain / (avg_loss.replace(0, np.nan))
    rsi = 100 - (100 / (1 + rs))
    return rsi.fillna(50)

def compute_macd(series):
    ema12 = series.ewm(span=12, adjust=False).mean()
    ema26 = series.ewm(span=26, adjust=False).mean()
    macd = ema12 - ema26
    signal = macd.ewm(span=9, adjust=False).mean()
    return macd, signal

def compute_ema(series, span):
    return series.ewm(span=span, adjust=False).mean()

def compute_atr(df, length=14):
    high = df['High']
    low = df['Low']
    close = df['Close']
    prev_close = close.shift(1)
    tr = pd.concat([
        (high - low).abs(),
        (high - prev_close).abs(),
        (low - prev_close).abs()
    ], axis=1).max(axis=1)
    atr = tr.rolling(length).mean().fillna(method='bfill')
    return atr

def add_indicators(df):
    if df.empty:
        return df
    df = df.copy()
    df['rsi'] = compute_rsi(df['Close'])
    macd, macd_sig = compute_macd(df['Close'])
    df['macd'] = macd
    df['macd_sig'] = macd_sig
    df['ema20'] = compute_ema(df['Close'], 20)
    df['ema50'] = compute_ema(df['Close'], 50)
    df['atr'] = compute_atr(df)
    # recent 30-day high/low
    df['hi30'] = df['High'].rolling(30, min_periods=1).max()
    df['lo30'] = df['Low'].rolling(30, min_periods=1).min()
    return df

def compute_key_levels(df):
    if df.empty:
        return (None, None)
    last = df.iloc[-1]
    support = last['lo30'] if 'lo30' in df.columns else df['Close'].min()
    resistance = last['hi30'] if 'hi30' in df.columns else df['Close'].max()
    return float(support), float(resistance)