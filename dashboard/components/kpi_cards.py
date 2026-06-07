import streamlit as st

def render_kpi_cards(df):
    """Render top-level KPI cards."""
    st.markdown("### Executive Summary")
    if df.empty:
        st.warning("No data available.")
        return

    total_records = len(df)
    unique_tickers = df['Ticker'].nunique()
    unique_sectors = df['GICS Sector'].nunique()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Records Processed", f"{total_records:,}")
    with col2:
        st.metric("Tickers Tracked", unique_tickers)
    with col3:
        st.metric("Sectors Tracked", unique_sectors)
    
    st.markdown("---")
