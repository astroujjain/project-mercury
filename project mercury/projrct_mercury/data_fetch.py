import os
import pandas as pd
import yfinance as yf
from .config import DEFAULT_TICKERS, PERIOD, INTERVAL

def fetch_ohlc(ticker, period=PERIOD, interval=INTERVAL):
    try:
        df = yf.download(ticker, period=period, interval=interval, progress=False)
        if df.empty:
            print(f"[WARN] No data for {ticker}")
        return df[['Open','High','Low','Close','Volume']].dropna(how='all')
    except Exception as e:
        print(f"[ERROR] fetch_ohlc {ticker}: {e}")
        return pd.DataFrame()

def fetch_all():
    out = {}
    for key, tk in DEFAULT_TICKERS.items():
        out[key] = fetch_ohlc(tk)
    return out

if _name_ == "_main_":
    d = fetch_all()
    for k,df in d.items():
        print(k, df.shape)