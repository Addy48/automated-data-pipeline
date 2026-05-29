import streamlit as st

def render_kpi_cards(df):
    """Render top-level KPI cards styled like The Arena."""
    if df.empty:
        st.warning("No data available.")
        return

    total_records = len(df)
    unique_symbols = df['Symbol'].nunique() if 'Symbol' in df.columns else df['Ticker'].nunique()
    unique_sectors = df['GICS_Sector'].nunique() if 'GICS_Sector' in df.columns else df['GICS Sector'].nunique()
    
    # Custom HTML for beautiful, premium KPI cards
    html = f"""
    <div style="display: flex; gap: 20px; margin-bottom: 25px; flex-wrap: wrap;">
        <div style="flex: 1; min-width: 250px; background: #ffffff; padding: 24px; border-radius: 16px; border: 1px solid #e1e0db; box-shadow: 0 4px 12px rgba(0,0,0,0.03);">
            <div style="font-size: 11px; text-transform: uppercase; letter-spacing: 1.5px; color: #7a7872; font-weight: 600; margin-bottom: 8px;">📊 Total Datapoints</div>
            <div style="font-size: 32px; font-weight: 700; color: #1a4329; font-family: 'Outfit', sans-serif;">{total_records:,}</div>
            <div style="font-size: 12px; color: #8e8c84; margin-top: 4px;">Historical market records processed</div>
        </div>
        <div style="flex: 1; min-width: 250px; background: #ffffff; padding: 24px; border-radius: 16px; border: 1px solid #e1e0db; box-shadow: 0 4px 12px rgba(0,0,0,0.03);">
            <div style="font-size: 11px; text-transform: uppercase; letter-spacing: 1.5px; color: #7a7872; font-weight: 600; margin-bottom: 8px;">📈 Active Tickers</div>
            <div style="font-size: 32px; font-weight: 700; color: #1a4329; font-family: 'Outfit', sans-serif;">{unique_symbols}</div>
            <div style="font-size: 12px; color: #8e8c84; margin-top: 4px;">Equities actively monitored</div>
        </div>
        <div style="flex: 1; min-width: 250px; background: #ffffff; padding: 24px; border-radius: 16px; border: 1px solid #e1e0db; box-shadow: 0 4px 12px rgba(0,0,0,0.03);">
            <div style="font-size: 11px; text-transform: uppercase; letter-spacing: 1.5px; color: #7a7872; font-weight: 600; margin-bottom: 8px;">🏢 Sectors Covered</div>
            <div style="font-size: 32px; font-weight: 700; color: #1a4329; font-family: 'Outfit', sans-serif;">{unique_sectors}</div>
            <div style="font-size: 12px; color: #8e8c84; margin-top: 4px;">Industry classifications tracked</div>
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)
