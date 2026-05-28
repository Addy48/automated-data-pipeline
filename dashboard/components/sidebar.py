import streamlit as st

def render_sidebar(df):
    """Render the sidebar and return user selections."""
    st.sidebar.header("Dashboard Filters")
    
    st.sidebar.markdown("Use these filters to explore specific exchanges, sectors, or timeframes.")
    
    if df.empty:
        st.sidebar.warning("No data available to filter.")
        return None, None
        
    # Exchange Filter
    exchanges = ["All Exchanges"]
    if 'Exchange' in df.columns:
        exchanges.extend(df['Exchange'].dropna().unique().tolist())
    selected_exchange = st.sidebar.selectbox("Select Exchange", exchanges)
    exchange_filter = None if selected_exchange == "All Exchanges" else selected_exchange
    
    # Sector Filter
    sectors = df['GICS Sector'].dropna().unique().tolist()
    sectors.insert(0, "All Sectors")
    selected_sector = st.sidebar.selectbox("Select Sector", sectors)
    sector_filter = None if selected_sector == "All Sectors" else selected_sector
    
    st.sidebar.markdown("---")
    st.sidebar.caption("Data is updated nightly by the Automated Data Pipeline.")
    
    return exchange_filter, sector_filter
