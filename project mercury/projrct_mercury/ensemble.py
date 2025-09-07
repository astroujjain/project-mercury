import numpy as np

def ta_probability(df):
    """
    Heuristic: combine RSI, MACD direction, MA slope into 0..1 prob_up
    """
    if df is None or df.empty:
        return 0.5
    rsi = df['rsi'].iloc[-1] if 'rsi' in df else 50
    macd = df['macd'].iloc[-1] if 'macd' in df else 0
    macd_sig = df['macd_sig'].iloc[-1] if 'macd_sig' in df else 0
    ema20 = df['ema20'].iloc[-1] if 'ema20' in df else df['Close'].iloc[-1]
    ema50 = df['ema50'].iloc[-1] if 'ema50' in df else df['Close'].iloc[-1]

    score = 0.5
    # RSI
    if rsi < 35:
        score += 0.12
    elif rsi < 45:
        score += 0.06
    elif rsi > 70:
        score -= 0.15
    elif rsi > 60:
        score -= 0.08

    # MACD
    if macd > macd_sig:
        score += 0.12
    else:
        score -= 0.08

    # MA slope
    if ema20 > ema50:
        score += 0.08
    else:
        score -= 0.06

    return float(max(0.0, min(1.0, score)))

def combine_prob(ta_prob, sentiment_norm, macro_norm, weights=(0.55, 0.15, 0.30)):
    # sentiment_norm, macro_norm are -1..1 -> convert 0..1
    s = (sentiment_norm + 1.0) / 2.0
    m = (macro_norm + 1.0) / 2.0
    w_t, w_s, w_m = weights
    prob = w_t * ta_prob + w_s * s + w_m * m
    return float(max(0.0, min(1.0, prob)))

def map_to_signal(prob):
    if prob >= 0.8:
        return "BUY", "Strong"
    if prob >= 0.65:
        return "BUY", "Medium-Strong"
    if prob >= 0.6:
        return "BUY", "Medium"
    if prob <= 0.2:
        return "SELL", "Strong"
    if prob <= 0.35:
        return "SELL", "Medium-Strong"
    if prob <= 0.4:
        return "SELL", "Medium"
    return "NEUTRAL", "Weak"