import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import date, timedelta

BASE_URL = "http://localhost:8006"
TICKERS  = ["AAPL", "MSFT", "GOOGL", "ABNB"]

st.set_page_config(
    page_title="Stock Dashboard",
    page_icon="📈",
    layout="wide",
)


st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=DM+Sans:wght@300;400;600&display=swap');

html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }

.stApp { background: #0d0f14; color: #e8e8e8; }

.metric-card {
    background: #161921;
    border: 1px solid #2a2d3a;
    border-radius: 12px;
    padding: 20px 24px;
    text-align: center;
}
.metric-label {
    font-size: 11px;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: #6b7280;
    margin-bottom: 8px;
    font-family: 'Space Mono', monospace;
}
.metric-value {
    font-size: 28px;
    font-weight: 600;
    color: #f0f0f0;
    font-family: 'Space Mono', monospace;
}
.metric-sub {
    font-size: 13px;
    color: #6b7280;
    margin-top: 4px;
}
.positive { color: #22c55e !important; }
.negative { color: #ef4444 !important; }

.section-title {
    font-family: 'Space Mono', monospace;
    font-size: 11px;
    letter-spacing: 3px;
    text-transform: uppercase;
    color: #4b5563;
    margin: 32px 0 16px 0;
    border-bottom: 1px solid #1f2330;
    padding-bottom: 8px;
}

div[data-testid="stSelectbox"] label,
div[data-testid="stDateInput"] label,
div[data-testid="stSlider"] label,
div[data-testid="stMultiSelect"] label {
    font-family: 'Space Mono', monospace;
    font-size: 11px;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: #6b7280;
}
</style>
""", unsafe_allow_html=True)


def fetch(endpoint: str, params: dict = None):
    try:
        r = requests.get(f"{BASE_URL}{endpoint}", params=params, timeout=10)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        st.error(f"Erreur API : {e}")
        return None

def color(val):
    return "positive" if val >= 0 else "negative"

def sign(val):
    return f"+{val}" if val >= 0 else str(val)


with st.sidebar:
    st.markdown("## 📈 Stock Dashboard")
    st.markdown("---")

    ticker = st.selectbox("Ticker", TICKERS)

    st.markdown("**Période**")
    end_date   = date.today()
    start_date = st.date_input("Début", value=end_date - timedelta(days=365))
    end_date   = st.date_input("Fin",   value=end_date)

    st.markdown("---")
    compare_tickers = st.multiselect(
        "Comparer avec",
        [t for t in TICKERS if t != ticker],
        default=[t for t in TICKERS if t != ticker][:2],
    )


latest  = fetch(f"/stocks/{ticker}/latest")
stats   = fetch(f"/stocks/{ticker}/stats")
history = fetch(f"/stocks/{ticker}/history", {"start": start_date, "end": end_date})

all_compare = [ticker] + compare_tickers
compare_data = fetch("/stocks/compare", {
    "tickers": ",".join(all_compare),
    "start": start_date,
    "end": end_date,
})


st.markdown(f"# {ticker}")
if latest:
    st.markdown(f"<span style='color:#6b7280;font-family:Space Mono,monospace;font-size:13px'>Dernière clôture : {latest['date']}</span>", unsafe_allow_html=True)

st.markdown("---")


if latest and stats:
    c1, c2, c3, c4, c5 = st.columns(5)

    with c1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Close</div>
            <div class="metric-value">${latest['close']:.2f}</div>
        </div>""", unsafe_allow_html=True)

    with c2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Plus haut</div>
            <div class="metric-value positive">${stats['close_max']}</div>
        </div>""", unsafe_allow_html=True)

    with c3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Plus bas</div>
            <div class="metric-value negative">${stats['close_min']}</div>
        </div>""", unsafe_allow_html=True)

    with c4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Volatilité</div>
            <div class="metric-value">{stats['volatility']}%</div>
            <div class="metric-sub">écart-type journalier</div>
        </div>""", unsafe_allow_html=True)

    with c5:
        bd = stats['best_day']
        wd = stats['worst_day']
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Best / Worst day</div>
            <div class="metric-value">
                <span class="positive">+{bd}%</span>
                <span style="color:#2a2d3a"> / </span>
                <span class="negative">{wd}%</span>
            </div>
        </div>""", unsafe_allow_html=True)

# ── Graphique prix ────────────────────────────────────────────────────────────
if history:
    df = pd.DataFrame(history)
    df["date"] = pd.to_datetime(df["date"])

    st.markdown('<div class="section-title">Historique des prix</div>', unsafe_allow_html=True)

    fig = go.Figure()
    fig.add_trace(go.Candlestick(
        x=df["date"],
        open=df["open"],
        high=df["high"],
        low=df["low"],
        close=df["close"],
        name=ticker,
        increasing_line_color="#22c55e",
        decreasing_line_color="#ef4444",
    ))
    fig.update_layout(
        paper_bgcolor="#0d0f14",
        plot_bgcolor="#0d0f14",
        font=dict(color="#6b7280", family="Space Mono"),
        xaxis=dict(gridcolor="#1f2330", showgrid=True),
        yaxis=dict(gridcolor="#1f2330", showgrid=True),
        margin=dict(l=0, r=0, t=10, b=0),
        height=400,
        xaxis_rangeslider_visible=False,
    )
    st.plotly_chart(fig, use_container_width=True)

# ── Volume ────────────────────────────────────────────────────────────────────
    st.markdown('<div class="section-title">Volume</div>', unsafe_allow_html=True)

    fig_vol = go.Figure()
    fig_vol.add_trace(go.Bar(
        x=df["date"],
        y=df["volume"],
        marker_color="#3b82f6",
        opacity=0.7,
        name="Volume",
    ))
    fig_vol.update_layout(
        paper_bgcolor="#0d0f14",
        plot_bgcolor="#0d0f14",
        font=dict(color="#6b7280", family="Space Mono"),
        xaxis=dict(gridcolor="#1f2330"),
        yaxis=dict(gridcolor="#1f2330"),
        margin=dict(l=0, r=0, t=10, b=0),
        height=200,
        showlegend=False,
    )
    st.plotly_chart(fig_vol, use_container_width=True)


if compare_data:
    st.markdown('<div class="section-title">Comparaison (base 100)</div>', unsafe_allow_html=True)

    COLORS = ["#3b82f6", "#22c55e", "#f59e0b", "#ec4899"]
    fig_cmp = go.Figure()

    for i, (t, d) in enumerate(compare_data.items()):
        fig_cmp.add_trace(go.Scatter(
            x=d["dates"],
            y=d["values"],
            name=t,
            line=dict(color=COLORS[i % len(COLORS)], width=2),
            mode="lines",
        ))

    fig_cmp.add_hline(y=100, line_dash="dot", line_color="#2a2d3a")
    fig_cmp.update_layout(
        paper_bgcolor="#0d0f14",
        plot_bgcolor="#0d0f14",
        font=dict(color="#6b7280", family="Space Mono"),
        xaxis=dict(gridcolor="#1f2330"),
        yaxis=dict(gridcolor="#1f2330"),
        margin=dict(l=0, r=0, t=10, b=0),
        height=350,
        legend=dict(bgcolor="#161921", bordercolor="#2a2d3a", borderwidth=1),
    )
    st.plotly_chart(fig_cmp, use_container_width=True)


if stats:
    st.markdown('<div class="section-title">Statistiques détaillées</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
        | Métrique | Valeur |
        |---|---|
        | Prix moyen | ${stats['close_mean']} |
        | Prix min | ${stats['close_min']} |
        | Prix max | ${stats['close_max']} |
        """)
    with col2:
        st.markdown(f"""
        | Métrique | Valeur |
        |---|---|
        | Volume moyen | {stats['volume_mean']:,} |
        | Volatilité | {stats['volatility']}% |
        | Meilleure journée | +{stats['best_day']}% |
        | Pire journée | {stats['worst_day']}% |
        """)