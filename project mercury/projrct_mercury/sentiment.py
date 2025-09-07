import os
import requests
import pandas as pd

POS_WORDS = ['gain', 'rise', 'easing', 'support', 'surge', 'rally', 'bullish', 'strong']
NEG_WORDS = ['drop', 'fall', 'inflation', 'risk', 'cut', 'weak', 'bearish', 'sell']

def fetch_headlines_from_newsapi(api_key, q='gold OR silver OR commodities', days=2, page_size=50):
    if not api_key:
        return []
    url = "https://newsapi.org/v2/everything"
    params = {
        'q': q,
        'language': 'en',
        'pageSize': page_size,
        'sortBy': 'relevancy',
        # 'from': (pd.Timestamp.utcnow() - pd.Timedelta(days=days)).strftime('%Y-%m-%dT%H:%M:%SZ'),
        'apiKey': api_key
    }
    try:
        r = requests.get(url, params=params, timeout=10)
        j = r.json()
        return [a['title'] for a in j.get('articles', []) if a.get('title')]
    except Exception as e:
        print("[WARN] NewsAPI failed:", e)
        return []

def load_headlines_csv(path='headlines.csv'):
    if not os.path.exists(path):
        return []
    df = pd.read_csv(path)
    # try common columns
    for col in ['headline', 'title', 'text']:
        if col in df.columns:
            return df[col].dropna().astype(str).tolist()
    # fallback: any text column
    for c in df.columns:
        if df[c].dtype == object:
            return df[c].dropna().astype(str).tolist()
    return []

def score_headlines(headlines):
    if not headlines:
        return 0.0, []
    rows = []
    total = 0
    for h in headlines:
        h_l = h.lower()
        score = 0
        for w in POS_WORDS:
            if w in h_l:
                score += 1
        for w in NEG_WORDS:
            if w in h_l:
                score -= 1
        # clamp per headline between -3..+3
        score = max(-3, min(3, score))
        total += score
        rows.append((h, score))
    avg = total / len(headlines)
    # normalize to -1..1 roughly (3 -> 1)
    norm = max(-1.0, min(1.0, avg / 3.0))
    return norm, rows