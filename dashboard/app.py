import os
import sys
import streamlit as st
import pandas as pd
import subprocess

# Add the parent directory to sys.path so we can import components
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from components.kpi_cards import render_kpi_cards
from components.charts import render_sector_growth_chart, render_top_performers, render_ticker_explorer, render_pipeline_monitor

# Define the local data path
DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'sector_growth_data.parquet')

st.set_page_config(
    page_title="AIIMIN Market Intelligence | The Arena.",
    page_icon="📈",
    layout="wide"
)

# Custom premium CSS styling matching 'The Arena'
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&family=Playfair+Display:ital,wght@0,500;0,700;1,500&display=swap');

/* Main application background and font */
.stApp {
    background-color: #F4F3EF !important;
    font-family: 'Outfit', sans-serif !important;
    color: #1c1a17 !important;
}

/* Hide Streamlit default sidebar and collapse button */
[data-testid="collapsedControl"] {
    display: none !important;
}
section[data-testid="stSidebar"] {
    display: none !important;
}
div.stSidebarCollapseButton {
    display: none !important;
}

/* Custom Headers */
.arena-tag {
    font-size: 11px !important;
    text-transform: uppercase !important;
    letter-spacing: 2px !important;
    color: #1a4329 !important;
    font-weight: 700 !important;
    margin-bottom: 2px !important;
}

.arena-title {
    font-family: 'Playfair Display', serif !important;
    font-size: 52px !important;
    font-weight: 700 !important;
    color: #1c1a17 !important;
    margin-bottom: 25px !important;
    line-height: 1.1 !important;
}

/* Radio buttons container (Toggling Exchanges) */
div[role="radiogroup"] {
    display: flex !important;
    flex-direction: row !important;
    gap: 12px !important;
    margin-bottom: 30px !important;
    flex-wrap: wrap !important;
}

/* Radio items (Pills) */
div[role="radiogroup"] label {
    background-color: #ffffff !important;
    border: 1px solid #e1e0db !important;
    border-radius: 24px !important;
    padding: 10px 24px !important;
    color: #1c1a17 !important;
    font-weight: 600 !important;
    font-size: 14px !important;
    box-shadow: 0 2px 4px rgba(0,0,0,0.02) !important;
    cursor: pointer !important;
    transition: all 0.2s ease !important;
    display: flex !important;
    align-items: center !important;
}

div[role="radiogroup"] label:hover {
    border-color: #1a4329 !important;
    color: #1a4329 !important;
}

/* Selected state styling */
div[role="radiogroup"] label[data-baseweb="radio"] div:first-child {
    display: none !important;
}

div[role="radiogroup"] label:has(input:checked) {
    background-color: #1a4329 !important;
    color: #ffffff !important;
    border-color: #1a4329 !important;
}

div[role="radiogroup"] label:has(input:checked) * {
    color: #ffffff !important;
}

div[role="radiogroup"] label span {
    display: none !important;
}

/* Custom styled headers for sections */
h3 {
    font-family: 'Playfair Display', serif !important;
    font-size: 28px !important;
    font-weight: 700 !important;
    color: #1c1a17 !important;
    margin-top: 30px !important;
    margin-bottom: 15px !important;
}

/* Line Chart & Bar Chart container */
div[data-testid="stLineChart"], div[data-testid="stBarChart"] {
    background: #ffffff !important;
    border-radius: 18px !important;
    border: 1px solid #e1e0db !important;
    padding: 20px !important;
    box-shadow: 0 4px 12px rgba(0,0,0,0.02) !important;
}

/* Style the Tab List Container */
div[data-baseweb="tab-list"] {
    background-color: transparent !important;
    gap: 10px !important;
    border-bottom: 2px solid #e1e0db !important;
    margin-bottom: 25px !important;
}

/* Style each Tab Button */
div[data-baseweb="tab-list"] button {
    font-family: 'Outfit', sans-serif !important;
    font-weight: 600 !important;
    font-size: 15px !important;
    color: #7a7872 !important;
    background-color: transparent !important;
    border: none !important;
    padding: 10px 20px !important;
    transition: all 0.2s ease !important;
}

/* Hover and active states */
div[data-baseweb="tab-list"] button:hover {
    color: #1a4329 !important;
}
div[data-baseweb="tab-list"] button[aria-selected="true"] {
    color: #1a4329 !important;
    border-bottom: 3px solid #1a4329 !important;
}

/* Sync feed styling */
.live-status {
    display: inline-flex;
    align-items: center;
    background: #e2f0d9;
    color: #385723;
    font-size: 12px;
    font-weight: bold;
    border-radius: 20px;
    padding: 6px 14px;
    margin-right: 10px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.02);
}
.live-status::before {
    content: "";
    display: inline-block;
    width: 8px;
    height: 8px;
    background-color: #385723;
    border-radius: 50px;
    margin-right: 8px;
    animation: blinker 1.5s linear infinite;
}

@keyframes blinker {
    50% { opacity: 0; }
}
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    if os.path.exists(DATA_PATH):
        return pd.read_parquet(DATA_PATH)
    else:
        # Fallback to CSV if parquet doesn't exist
        csv_path = DATA_PATH.replace('.parquet', '.csv')
        if os.path.exists(csv_path):
            return pd.read_csv(csv_path)
        return pd.DataFrame()

def main():
    # 1. HEADER ROW (Title & Actions)
    col_left, col_right = st.columns([7, 3])
    with col_left:
        st.markdown('<div class="arena-tag">AIIMIN MARKET INTELLIGENCE</div>', unsafe_allow_html=True)
        st.markdown('<div class="arena-title">The Arena.</div>', unsafe_allow_html=True)
    with col_right:
        st.markdown('<div style="display: flex; justify-content: flex-end; align-items: center; margin-top: 15px;">', unsafe_allow_html=True)
        # Render a Live Status Tag
        st.markdown('<div class="live-status">Live Market Feed</div>', unsafe_allow_html=True)
        # Render Sync Scores Button
        if st.button("🔄 Sync Markets", key="sync_btn"):
            with st.spinner("Executing ETL Pipeline (Scraping Wikipedia + yfinance)..."):
                try:
                    # Execute the ETL pipeline
                    result = subprocess.run([sys.executable, "run_pipeline.py"], capture_output=True, text=True, check=True)
                    st.cache_data.clear() # Clear cache so new data is loaded
                    st.success("ETL Pipeline completed successfully! Rerunning...")
                    st.rerun()
                except Exception as e:
                    st.error(f"ETL pipeline run failed: {e}")
        st.markdown('</div>', unsafe_allow_html=True)

    df = load_data()
    
    if df.empty:
        st.warning("No market data found! Please click the '🔄 Sync Markets' button on the top right to execute the ETL pipeline and pull latest exchange data.")
        return
        
    # 2. FILTER ROW (Exchange Selector styled as horizontal radio pills)
    exchanges = ["🌐 All Markets"]
    if 'Exchange' in df.columns:
        exchanges.extend(sorted(df['Exchange'].dropna().unique().tolist()))
        
    selected_exchange_opt = st.radio("Exchange", exchanges, label_visibility="collapsed")
    selected_exchange = None if selected_exchange_opt == "🌐 All Markets" else selected_exchange_opt

    # Filter df by exchange if necessary
    if selected_exchange and 'Exchange' in df.columns:
        df_filtered = df[df['Exchange'] == selected_exchange]
    else:
        df_filtered = df.copy()

    # 3. TAB NAVIGATION
    tab1, tab2, tab3 = st.tabs(["🏟️ Market Overview", "🔍 Stock Explorer", "⚙️ Pipeline Monitor"])
    
    with tab1:
        # KPI SUMMARY CARDS
        render_kpi_cards(df_filtered)
        
        # CHART SECTION (Sector returns over time)
        render_sector_growth_chart(df_filtered)
        
        st.markdown("<br><br>", unsafe_allow_html=True)
        
        # SECTOR-SPECIFIC TOP PERFORMERS GRID
        st.markdown("---")
        col_sec_title, col_sec_select = st.columns([6, 4])
        with col_sec_title:
            st.markdown("### Top Performing Industry Stocks")
        with col_sec_select:
            # Sector Filter (Selectbox styled cleanly)
            sector_col = 'GICS_Sector' if 'GICS_Sector' in df_filtered.columns else 'GICS Sector'
            sectors = sorted(df_filtered[sector_col].dropna().unique().tolist())
            selected_sector = st.selectbox("Filter Industry Sector", sectors, label_visibility="collapsed")

        # Render top stock cards for the selected sector
        render_top_performers(df_filtered, selected_sector)

    with tab2:
        st.markdown("### 🔍 Historical Stock Explorer")
        st.markdown("Select an equity ticker below to examine daily price trends, trading volumes, and analytical indicators.")
        
        # Select symbol
        symbols = sorted(df_filtered['Symbol'].dropna().unique().tolist())
        selected_symbol = st.selectbox("Select Ticker Symbol", symbols, label_visibility="visible")
        
        render_ticker_explorer(df_filtered, selected_symbol)

    with tab3:
        render_pipeline_monitor()

    st.markdown("<br><br><br>", unsafe_allow_html=True)
    st.caption("AIIMIN Personal OS • Powered by Python, yfinance, Boto3, and Streamlit.")

if __name__ == "__main__":
    main()
