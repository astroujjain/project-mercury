import os
import math
from .data_fetch import fetch_all, fetch_ohlc
from .indicators import add_indicators, compute_key_levels
from .sentiment import fetch_headlines_from_newsapi, load_headlines_csv, score_headlines
from .ensemble import ta_probability, combine_prob, map_to_signal
from .report import plot_save_chart, build_pdf
from .config import OUTPUT_DIR
import pandas as pd

def run(out_dir=OUTPUT_DIR):
    os.makedirs(out_dir, exist_ok=True)
    print("[*] Fetching market data...")
    data = fetch_all()

    results = {}
    # simple macro: use DXY and WTI returns
    dxy = data.get('dxy')
    wti = data.get('wti')

    # Sentiment: try NewsAPI_KEY then fallback
    import os
    key = os.environ.get('NEWSAPI_KEY')
    heads = []
    if key:
        heads = fetch_headlines_from_newsapi(key)
    if not heads:
        heads = load_headlines_csv()
    if not heads:
        heads = [
            "Markets watch inflation and Fed comments",
            "Oil prices rise on supply concerns",
            "Safe-haven demand supports gold"
        ]

    sent_norm, scored = score_headlines(heads)
    print(f"[*] Sentiment norm: {sent_norm:.3f} (based on {len(heads)} headlines)")

    # Process each asset: gold, silver
    for asset in ['gold','silver']:
        df = data.get(asset, pd.DataFrame())
        df = add_indicators(df)
        support, resistance = compute_key_levels(df)
        chart = plot_save_chart(df, asset.capitalize(), support, resistance, fname=f"{asset}_chart.png")
        ta_prob = ta_probability(df)
        # macro_norm: use simple heuristic: DXY down => positive for metals
        macro_norm = 0.0
        try:
            if dxy is not None and not dxy.empty:
                # compute last pct change
                macro_norm += - (dxy['Close'].pct_change().dropna().iloc[-1])
            if wti is not None and not wti.empty:
                macro_norm += (wti['Close'].pct_change().dropna().iloc[-1])
            # average
            macro_norm = max(-1.0, min(1.0, macro_norm))
        except Exception:
            macro_norm = 0.0

        final_prob = combine_prob(ta_prob, sent_norm, macro_norm)
        rec, strength = map_to_signal(final_prob)

        results[asset] = {
            'rec': rec,
            'strength': strength,
            'confidence': int(round(final_prob*100)),
            'support': support,
            'resistance': resistance,
            'chart': chart,
            'ta_prob': ta_prob,
            'macro_norm': macro_norm
        }

    # Build PDF
    sections = []
    today = pd.Timestamp.now().strftime('%d-%b-%Y')
    summary = [f"Date: {today}"]
    for k,v in results.items():
        summary.append(f"{k.capitalize()}: {v['rec']} | Strength: {v['strength']} | Confidence: {v['confidence']}%")
        summary.append(f"Key Support: {v['support']} | Key Resistance: {v['resistance']}")
    sections.append({'title':'Summary', 'paragraphs': summary, 'image': None})

    for k,v in results.items():
        paras = [
            f"Recommendation: {v['rec']}",
            f"Strength: {v['strength']}",
            f"Confidence: {v['confidence']}%",
            f"TA probability: {v['ta_prob']:.3f}",
            f"Macro norm: {v['macro_norm']:.3f}"
        ]
        sections.append({'title': f"{k.capitalize()} Details", 'paragraphs': paras, 'image': v['chart']})

    out_path = os.path.join(out_dir, "Project_Mercury_Report.pdf")
    build_pdf(out_path, sections)
    print(f"[OK] Report generated: {out_path}")
    return out_path

if _name_ == "_main_":
    run()