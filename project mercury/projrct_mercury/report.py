import os
from datetime import date
import matplotlib.pyplot as plt
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet
from .config import OUTPUT_DIR, DISCLAIMER

def ensure_out():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR, exist_ok=True)

def plot_save_chart(df, name, support=None, resistance=None, fname=None):
    if df is None or df.empty:
        return None
    if fname is None:
        fname = f"{name.replace(' ', '_')}_chart.png"
    plt.figure(figsize=(10,4))
    plt.plot(df.index, df['Close'], label='Close')
    if 'ema20' in df: plt.plot(df.index, df['ema20'], label='EMA20', linewidth=0.8)
    if 'ema50' in df: plt.plot(df.index, df['ema50'], label='EMA50', linewidth=0.8)
    if support: plt.axhline(support, linestyle='--', label='Support')
    if resistance: plt.axhline(resistance, linestyle='--', label='Resistance', color='r')
    plt.title(name)
    plt.legend(fontsize='small')
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, fname), dpi=150)
    plt.close()
    return os.path.join(OUTPUT_DIR, fname)

def build_pdf(path, sections):
    ensure_out()
    doc = SimpleDocTemplate(path, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    # Title
    story.append(Paragraph("<b>Project Mercury — Daily Commodity Outlook</b>", styles['Title']))
    story.append(Spacer(1,12))
    story.append(Paragraph(f"Date: {date.today().strftime('%d-%b-%Y')}", styles['Normal']))
    story.append(Spacer(1,12))
    story.append(Paragraph("<b>Disclaimer</b>", styles['Heading3']))
    story.append(Paragraph(DISCLAIMER, styles['Normal']))
    story.append(PageBreak())

    for sec in sections:
        story.append(Paragraph(f"<b>{sec.get('title','')}</b>", styles['Heading2']))
        story.append(Spacer(1,6))
        for p in sec.get('paragraphs', []):
            story.append(Paragraph(p, styles['Normal']))
            story.append(Spacer(1,4))
        if sec.get('image'):
            try:
                img = Image(sec['image'], width=450, height=220)
                story.append(Spacer(1,8))
                story.append(img)
                story.append(Spacer(1,12))
            except Exception as e:
                story.append(Paragraph(f"[Could not attach image: {e}]", styles['Normal']))
        story.append(Paragraph("<i>Disclaimer:</i> " + DISCLAIMER, styles['Italic']))
        story.append(PageBreak())

    doc.build(story)
    return path