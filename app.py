import math

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(
    page_title="Tech & Software Screener",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Safely load and process CSS styles using single-quote formatting to avoid nested parser issues
css_style = '''<style>
[data-testid="stAppViewContainer"] {background-color: #0B0F19; color: #F3F4F6;}
[data-testid="stSidebar"] {background-color: #111827; border-right: 1px solid #1F2937;}
h1, h2, h3 {font-family: 'Inter', sans-serif; font-weight: 700; color: #F3F4F6; letter-spacing: -0.025em;}
div[data-testid="stMarkdownContainer"] h1 {color: #60A5FA; margin-bottom: 5px;}
div[data-testid="stMarkdownContainer"] h2 {color: #38BDF8; border-bottom: 2px solid #1F2937; padding-bottom: 8px;}
div[data-testid="metric-container"] {background-color: #1F2937; padding: 20px; border-radius: 12px; border: 1px solid #374151;}
.insight-box {background-color: #1F2937; padding: 20px 22px; border-radius: 12px; border-left: 5px solid #3B82F6; margin: 14px 0 25px 0;}
.insight-box h4 {margin-top: 0; color: #60A5FA; font-size: 1.1rem;}
.insight-box p {margin-bottom: 0; color: #D1D5DB; font-size: 0.95rem; line-height: 1.6;}
.app-footer {color: #9CA3AF; font-size: 0.82rem; text-align: center; margin-top: 10px;}
</style>'''

st.markdown(css_style, unsafe_allow_html=True)

# --- App Headers ---
st.title("📊 Tech & Software Screener")
st.caption("ACCT 3343 · Financial Accounting Analysis")
st.write("Screen 100 technology and software companies with quantitative filters for quality, value, and risk — and build a Buy or Sell list in seconds.")

@st.cache_data
def load_data():
    df = pd.read_csv('universe.csv')
    df = df.rename(columns={
        'Metric_1_STA': 'STA',
        'Metric_2_Z_Score': 'Altman Z-Score',
        'Metric_3_SNOA': 'SNOA',
        'Metric_4_GPA': 'Gross Profitability (GPA)',
        'Metric_5_BM': 'Book-to-Market (B/M)',
        'Metric_6_DE': 'Debt-to-Equity (D/E)',
        'Metric_7_PS': 'Price-to-Sales (P/S)'
    })
    return df

try:
    df = load_data()
except FileNotFoundError:
    st.error("universe.csv was not found. Please make sure universe.csv is in the same folder as this app.")
    st.stop()

# --- Intro Panel ---
st.markdown('<div class="insight-box"><h4>How This Screener Works</h4><p>Technology and software companies grow by investing in intangible assets, so this screener uses benchmarks calibrated for the sector rather than one-size-fits-all cut-offs. The filters start at sensible defaults that surface companies with strong profit generation, solid balance sheets, and reasonable valuations — and flag firms showing warning signs such as high accruals or financial distress. Move any slider in the sidebar and both lists update instantly.</p></div>', unsafe_allow_html=True)

# --- Metric Guide & Methodology ---
with st.expander("📖 Metric Guide & How Recommendations Work"):
    st.markdown(
        "**Long (Buy) and short (Sell) recommendations are kept separate by design:** a company that triggers any risk flag "
        "can never appear as a Buy Candidate, even if it passes the value and quality filters.\n\n"
        "- 🟢 **Buy Candidate (Long):** passes all four Buy thresholds **and** triggers no risk flags.\n"
        "- 🔴 **Sell Flag (Short / Avoid):** triggers at least one risk flag — high accruals, a weak Altman Z-Score, or balance-sheet bloat.\n"
        "- ⚪ **Hold / Watchlist:** triggers no risk flag, but does not pass every Buy threshold.\n\n"
        "**Ranking:** Buy Candidates are ranked by a Quality–Value Score (0–100) that combines each firm's percentile rank for "
        "profitability and book-to-market with its percentile rank for low price-to-sales and low leverage. Sell Flags are ranked "
        "by a Risk Score (0–100) built the same way from accruals, Z-Score, and SNOA. Use the ranking controls in the sidebar to re-rank either list by any single metric instead."
    )
    guide = pd.DataFrame([
        {"Metric": "Accruals (STA)", "Side": "Sell", "What it measures": "Non-cash earnings. High accruals can signal aggressive accounting.", "Calculated as": "(Net income − Operating cash flow) ÷ Total assets", "Flag / Pass": "Flagged when above the Max Accruals slider"},
        {"Metric": "Altman Z-Score", "Side": "Sell", "What it measures": "Composite financial-distress score combining liquidity, profitability, leverage, and market value. Lower means higher bankruptcy risk.", "Calculated as": "Altman composite of working capital, retained earnings, EBIT, market value of equity, and sales", "Flag / Pass": "Flagged when below the Min Z-Score slider"},
        {"Metric": "SNOA", "Side": "Sell", "What it measures": "Scaled net operating assets. A bloated balance sheet relative to assets is linked to weaker future performance.", "Calculated as": "(Total assets − Total liabilities) ÷ Total assets", "Flag / Pass": "Flagged when above the Max SNOA slider"},
        {"Metric": "Gross Profitability (GPA)", "Side": "Buy", "What it measures": "How productively a firm turns its asset base into profit.", "Calculated as": "Gross profit ÷ Total assets", "Flag / Pass": "Must be at or above the Min GPA slider"},
        {"Metric": "Book-to-Market (B/M)", "Side": "Buy", "What it measures": "Book value of equity relative to market value. Higher suggests the shares are cheaper relative to accounting value.", "Calculated as": "Shareholders' equity ÷ Market cap", "Flag / Pass": "Must be at or above the Min B/M slider"},
        {"Metric": "Price-to-Sales (P/S)", "Side": "Buy", "What it measures": "The valuation multiple being paid for each dollar of sales.", "Calculated as": "Market cap ÷ Revenue", "Flag / Pass": "Must be at or below the Max P/S slider"},
        {"Metric": "Debt-to-Equity (D/E)", "Side": "Buy", "What it measures": "Financial leverage and balance-sheet risk.", "Calculated as": "Total liabilities ÷ Shareholders' equity", "Flag / Pass": "Must be at or below the Max D/E slider"},
    ])
    st.dataframe(guide, use_container_width=True, hide_index=True)
    st.caption("Data note: Alphabet (GOOGL), NVIDIA (NVDA), Accenture (ACN), and Silicon Laboratories (SLAB) have missing values for one or more metrics in the source data. They are screened on the metrics available, and the Company Lookup below marks their data as incomplete.")

# --- Sidebar Controls ---
st.sidebar.header("Filter Adjustments")
st.sidebar.caption("Slider ranges are rounded to whole numbers. Defaults are pre-set for a balanced starting list.")

def whole_bounds(series):
    """Round a slider's range outward to whole numbers (floor the min, ceil the max)."""
    return float(math.floor(series.dropna().min())), float(math.ceil(series.dropna().max()))

# --- SELL SIDE FILTERS ---
st.sidebar.markdown("### 🔴 SELL Side (Risk Flags)")
sta_lo, sta_hi = whole_bounds(df['STA'])
sta_max = st.sidebar.slider("Max Accruals (STA)", min_value=sta_lo, max_value=sta_hi, value=0.15, help="Flags companies with excessive non-cash earnings.")
st.sidebar.caption("Filters out firms with suspicious non-cash adjustments.")

z_lo, z_hi = whole_bounds(df['Altman Z-Score'])
z_min = st.sidebar.slider("Min Altman Z-Score", min_value=z_lo, max_value=z_hi, value=1.5, help="Bankruptcy proxy.")
st.sidebar.caption("Flags companies under significant distress.")

snoa_lo, snoa_hi = whole_bounds(df['SNOA'])
snoa_max = st.sidebar.slider("Max SNOA", min_value=snoa_lo, max_value=snoa_hi, value=0.90, help="Balance sheet asset bloating.")

# --- BUY SIDE FILTERS ---
st.sidebar.markdown("### 🟢 BUY Side (Value & Quality)")
gpa_lo, gpa_hi = whole_bounds(df['Gross Profitability (GPA)'])
gpa_min = st.sidebar.slider("Min Gross Profitability (GPA)", min_value=gpa_lo, max_value=gpa_hi, value=0.20)
st.sidebar.caption("Ensures business actively generates profit.")

bm_lo, bm_hi = whole_bounds(df['Book-to-Market (B/M)'])
bm_min = st.sidebar.slider("Min Book-to-Market (B/M)", min_value=bm_lo, max_value=bm_hi, value=0.03)
st.sidebar.caption("Value factor adjustment for tech multiple levels.")

ps_lo, ps_hi = whole_bounds(df['Price-to-Sales (P/S)'])
max_ps = st.sidebar.slider("Max Price-to-Sales (P/S)", min_value=ps_lo, max_value=ps_hi, value=25.0)

de_lo, de_hi = whole_bounds(df['Debt-to-Equity (D/E)'])
max_de = st.sidebar.slider("Max Debt-to-Equity (D/E)", min_value=de_lo, max_value=de_hi, value=2.0)

# --- RANKING CONTROLS ---
st.sidebar.markdown("### 🏆 Ranking")
buy_rank = st.sidebar.selectbox(
    "Rank Buy Candidates by",
    ["Quality–Value Score", "Gross Profitability (GPA)", "Book-to-Market (B/M)", "Lowest Price-to-Sales (P/S)", "Lowest Debt-to-Equity (D/E)"],
)
sell_rank = st.sidebar.selectbox(
    "Rank Sell Flags by",
    ["Risk Score", "Highest Accruals (STA)", "Lowest Altman Z-Score", "Highest SNOA"],
)

# --- Screening Logic ---
# Sell side: ANY risk flag triggers a Sell Flag.
flag_sta = df['STA'] > sta_max
flag_z = df['Altman Z-Score'] < z_min
flag_snoa = df['SNOA'] > snoa_max
sell_mask = flag_sta | flag_z | flag_snoa

# Buy side: ALL quality/value thresholds must pass, AND no risk flag may be triggered.
buy_pass = (
    (df['Gross Profitability (GPA)'] >= gpa_min)
    & (df['Book-to-Market (B/M)'] >= bm_min)
    & (df['Price-to-Sales (P/S)'] <= max_ps)
    & (df['Debt-to-Equity (D/E)'] <= max_de)
)
buy_mask = buy_pass & ~sell_mask

df['Category'] = np.where(sell_mask, "🔴 Sell Flag", np.where(buy_mask, "🟢 Buy Candidate", "⚪ Hold / Watchlist"))

# --- Ranking Scores (percentile-based, 0-100, transparent and comparable across metrics) ---
def pct(series):
    return series.rank(pct=True)

df['Quality–Value Score'] = 100 * pd.concat([
    pct(df['Gross Profitability (GPA)']),
    pct(df['Book-to-Market (B/M)']),
    1 - pct(df['Price-to-Sales (P/S)']),
    1 - pct(df['Debt-to-Equity (D/E)']),
], axis=1).mean(axis=1)

df['Risk Score'] = 100 * pd.concat([
    pct(df['STA']),
    1 - pct(df['Altman Z-Score']),
    pct(df['SNOA']),
], axis=1).mean(axis=1)

def risk_flags(row):
    flags = []
    if pd.notna(row['STA']) and row['STA'] > sta_max:
        flags.append("High accruals")
    if pd.notna(row['Altman Z-Score']) and row['Altman Z-Score'] < z_min:
        flags.append("Low Z-Score (distress risk)")
    if pd.notna(row['SNOA']) and row['SNOA'] > snoa_max:
        flags.append("Balance-sheet bloat (SNOA)")
    return " · ".join(flags)

df['Risk Flags'] = df.apply(risk_flags, axis=1)

sell_candidates = df[df['Category'] == "🔴 Sell Flag"].copy()
buy_candidates = df[df['Category'] == "🟢 Buy Candidate"].copy()
hold_count = int((df['Category'] == "⚪ Hold / Watchlist").sum())

# Apply the chosen ranking
buy_sort = {
    "Quality–Value Score": ('Quality–Value Score', False),
    "Gross Profitability (GPA)": ('Gross Profitability (GPA)', False),
    "Book-to-Market (B/M)": ('Book-to-Market (B/M)', False),
    "Lowest Price-to-Sales (P/S)": ('Price-to-Sales (P/S)', True),
    "Lowest Debt-to-Equity (D/E)": ('Debt-to-Equity (D/E)', True),
}[buy_rank]
buy_candidates = buy_candidates.sort_values(buy_sort[0], ascending=buy_sort[1]).reset_index(drop=True)
buy_candidates.insert(0, 'Rank', range(1, len(buy_candidates) + 1))

sell_sort = {
    "Risk Score": ('Risk Score', False),
    "Highest Accruals (STA)": ('STA', False),
    "Lowest Altman Z-Score": ('Altman Z-Score', True),
    "Highest SNOA": ('SNOA', False),
}[sell_rank]
sell_candidates = sell_candidates.sort_values(sell_sort[0], ascending=sell_sort[1]).reset_index(drop=True)
sell_candidates.insert(0, 'Rank', range(1, len(sell_candidates) + 1))

# --- Headline Metrics ---
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Universe", f"{len(df)} Firms")
col2.metric("🔴 Sell Flags", f"{len(sell_candidates)} Firms")
col3.metric("🟢 Buy Candidates", f"{len(buy_candidates)} Firms")
col4.metric("⚪ Hold / Watchlist", f"{hold_count} Firms")

# --- Top Picks Summary ---
st.markdown("--- ")
st.header("⭐ Top Picks at Current Settings")
st.caption("The five strongest long and short recommendations right now, using the ranking selected in the sidebar. Change any filter and this list rebuilds itself.")
pick_col1, pick_col2 = st.columns(2)

with pick_col1:
    st.subheader("🟢 Top 5 Long Picks")
    if not buy_candidates.empty:
        for _, row in buy_candidates.head(5).iterrows():
            st.markdown(
                f"**{int(row['Rank'])}. {row['Ticker']} — {row['Company_Name']}**  \n"
                f"Quality–Value Score {row['Quality–Value Score']:.0f}/100 · GPA {row['Gross Profitability (GPA)']:.2f} · "
                f"B/M {row['Book-to-Market (B/M)']:.2f} · P/S {row['Price-to-Sales (P/S)']:.2f} · D/E {row['Debt-to-Equity (D/E)']:.2f} · No risk flags"
            )
    else:
        st.warning("No Buy Candidates at the current settings.")

with pick_col2:
    st.subheader("🔴 Top 5 Short / Avoid Picks")
    if not sell_candidates.empty:
        for _, row in sell_candidates.head(5).iterrows():
            st.markdown(
                f"**{int(row['Rank'])}. {row['Ticker']} — {row['Company_Name']}**  \n"
                f"Risk Score {row['Risk Score']:.0f}/100 · {row['Risk Flags']} · "
                f"STA {row['STA']:.2f} · Z-Score {row['Altman Z-Score']:.2f} · SNOA {row['SNOA']:.2f}"
            )
    else:
        st.success("No Sell Flags at the current settings.")

# --- Visual Analysis ---
st.markdown("--- ")
st.header("📈 Visual Analysis")
chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    st.subheader("Quality vs. Value")
    st.caption("Gross profitability against book-to-market. Bubble size is market cap — top-right firms combine strong profitability with cheaper valuations.")
    scatter_df = df.dropna(subset=['Book-to-Market (B/M)', 'Gross Profitability (GPA)', 'Market_Cap'])
    fig_scatter = px.scatter(
        scatter_df,
        x='Book-to-Market (B/M)',
        y='Gross Profitability (GPA)',
        color='Category',
        size='Market_Cap',
        hover_name='Ticker',
        hover_data={'Company_Name': True, 'Market_Cap': False, 'Category': False},
        color_discrete_map={"🔴 Sell Flag": "#EF4444", "🟢 Buy Candidate": "#22C55E", "⚪ Hold / Watchlist": "#9CA3AF"},
        template="plotly_dark",
        height=420,
    )
    fig_scatter.update_layout(paper_bgcolor="#111827", plot_bgcolor="#111827", legend_title_text="", margin=dict(l=10, r=10, t=10, b=10))
    st.plotly_chart(fig_scatter, use_container_width=True)

with chart_col2:
    st.subheader("Financial Distress Distribution")
    st.caption(f"Altman Z-Scores across the universe. The dashed line is the current Min Z-Score threshold ({z_min:.2f}) — firms to its left are flagged for distress risk.")
    z_df = df.dropna(subset=['Altman Z-Score'])
    fig_z = px.histogram(
        z_df,
        x='Altman Z-Score',
        color='Category',
        nbins=20,
        color_discrete_map={"🔴 Sell Flag": "#EF4444", "🟢 Buy Candidate": "#22C55E", "⚪ Hold / Watchlist": "#9CA3AF"},
        template="plotly_dark",
        height=420,
    )
    fig_z.add_vline(x=z_min, line_dash="dash", line_color="#FACC15")
    fig_z.update_layout(paper_bgcolor="#111827", plot_bgcolor="#111827", legend_title_text="", margin=dict(l=10, r=10, t=10, b=10), bargap=0.05)
    st.plotly_chart(fig_z, use_container_width=True)

# --- Sell Portfolio ---
st.markdown("--- ")
st.header("🔴 Sell Candidate Portfolio")
st.caption(f"Ranked by {sell_rank}. Short / avoid recommendations — each firm triggered at least one risk flag, listed beside its metrics.")
if not sell_candidates.empty:
    display_sell = sell_candidates[['Rank', 'Ticker', 'Company_Name', 'Risk Score', 'Risk Flags', 'STA', 'Altman Z-Score', 'SNOA']]
    st.dataframe(display_sell.style.background_gradient(cmap='Reds', subset=['STA', 'SNOA']).format({'Risk Score': '{:.0f}', 'STA': '{:.4f}', 'Altman Z-Score': '{:.2f}', 'SNOA': '{:.4f}'}), use_container_width=True)
    st.download_button("⬇️ Download Sell Flags as CSV", data=display_sell.to_csv(index=False), file_name="sell_flags.csv", mime="text/csv")
else:
    st.success("No companies meet high-risk flags.")

# --- Buy Portfolio ---
st.markdown("--- ")
st.header("🟢 Buy Candidate Portfolio")
st.caption(f"Ranked by {buy_rank}. Long recommendations — each firm passes every quality and value threshold and triggers no risk flags.")
if not buy_candidates.empty:
    display_buy = buy_candidates[['Rank', 'Ticker', 'Company_Name', 'Quality–Value Score', 'Gross Profitability (GPA)', 'Book-to-Market (B/M)', 'Debt-to-Equity (D/E)', 'Price-to-Sales (P/S)']]
    st.dataframe(display_buy.style.background_gradient(cmap='Greens', subset=['Gross Profitability (GPA)', 'Book-to-Market (B/M)']).format({'Quality–Value Score': '{:.0f}', 'Gross Profitability (GPA)': '{:.4f}', 'Book-to-Market (B/M)': '{:.4f}', 'Debt-to-Equity (D/E)': '{:.2f}', 'Price-to-Sales (P/S)': '{:.2f}'}), use_container_width=True)
    st.download_button("⬇️ Download Buy Candidates as CSV", data=display_buy.to_csv(index=False), file_name="buy_candidates.csv", mime="text/csv")
else:
    st.warning("No buy candidates found. Try loosening your sidebar sliders.")

# --- Company Lookup ---
st.markdown("--- ")
st.header("🔎 Company Lookup")
st.caption("Pick any company in the universe to see its recommendation and the evidence behind it, at the current slider settings.")
lookup_options = df.sort_values('Ticker')
lookup_labels = {f"{row.Ticker} — {row.Company_Name}": row.Ticker for row in lookup_options.itertuples()}
chosen_label = st.selectbox("Company", list(lookup_labels.keys()))
company = df[df['Ticker'] == lookup_labels[chosen_label]].iloc[0]

metric_cols = ['STA', 'Altman Z-Score', 'SNOA', 'Gross Profitability (GPA)', 'Book-to-Market (B/M)', 'Debt-to-Equity (D/E)', 'Price-to-Sales (P/S)']
has_gaps = company[metric_cols].isna().any()

if company['Category'] == "🟢 Buy Candidate":
    st.success(f"🟢 **{company['Company_Name']} ({company['Ticker']}) — Buy Candidate (Long)** · Quality–Value Score: {company['Quality–Value Score']:.0f}/100")
    st.markdown(
        f"Passes all four Buy thresholds at the current settings — GPA {company['Gross Profitability (GPA)']:.2f} (min {gpa_min:.2f}), "
        f"B/M {company['Book-to-Market (B/M)']:.2f} (min {bm_min:.2f}), P/S {company['Price-to-Sales (P/S)']:.2f} (max {max_ps:.0f}), "
        f"D/E {company['Debt-to-Equity (D/E)']:.2f} (max {max_de:.2f}) — and triggers no risk flags."
    )
elif company['Category'] == "🔴 Sell Flag":
    st.error(f"🔴 **{company['Company_Name']} ({company['Ticker']}) — Sell Flag (Short / Avoid)** · Risk Score: {company['Risk Score']:.0f}/100")
    st.markdown(f"Risk flags triggered: **{company['Risk Flags']}**.")
else:
    st.info(f"⚪ **{company['Company_Name']} ({company['Ticker']}) — Hold / Watchlist**")
    st.markdown("Triggers no risk flags, but does not pass every Buy threshold at the current slider settings.")

lookup_display = company[metric_cols].to_frame(name='Value').T
lookup_display.insert(0, 'Market Cap ($B)', round(company['Market_Cap'] / 1e9, 2))
st.dataframe(lookup_display.style.format('{:.4f}', subset=metric_cols), use_container_width=True)
if has_gaps:
    st.caption("⚠️ This company has missing data for one or more metrics in the source filings, shown as blank above. It is screened on the metrics available.")

st.markdown("--- ")
st.markdown('<p class="app-footer">Tech &amp; Software Screener · Universe of 100 companies · For informational and educational purposes only — not investment advice.</p>', unsafe_allow_html=True)
