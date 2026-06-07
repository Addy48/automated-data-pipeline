import streamlit as st
import pandas as pd

def render_sector_growth_chart(df):
    """Render a line chart of sector cumulative returns over time."""
    st.subheader("Sector Cumulative Returns Over 12 Months")
    
    if df.empty:
        st.info("Insufficient data for sector growth chart.")
        return

    # Group by Date and Sector to get average cumulative return
    sector_growth = df.groupby(['Date', 'GICS Sector'])['Cumulative_Return'].mean().reset_index()
    
    # Pivot for charting
    chart_data = sector_growth.pivot(index='Date', columns='GICS Sector', values='Cumulative_Return')
    
    st.line_chart(chart_data, height=400, use_container_width=True)

def render_top_performers(df, selected_sector):
    """Render a table of top performing stocks in a selected sector."""
    if not selected_sector:
        return

    st.subheader(f"Top Performers in {selected_sector}")
    
    sector_df = df[df['GICS Sector'] == selected_sector]
    if sector_df.empty:
        st.info("No data for this sector.")
        return

    # Get latest data
    latest_date = sector_df['Date'].max()
    latest_data = sector_df[sector_df['Date'] == latest_date]
    
    # Sort by best performers
    if 'Volatility_30d' in latest_data.columns:
        cols_to_show = ['Ticker', 'Close', 'Cumulative_Return', 'Volatility_30d']
    else:
        cols_to_show = ['Ticker', 'Close', 'Cumulative_Return']
        
    top_performers = latest_data.sort_values(by='Cumulative_Return', ascending=False)[cols_to_show]
    
    st.write(f"**As of {pd.to_datetime(latest_date).strftime('%Y-%m-%d')}**")
    
    # Format the metrics
    top_performers['Cumulative_Return'] = (top_performers['Cumulative_Return'] * 100).map("{:.2f}%".format)
    if 'Volatility_30d' in top_performers.columns:
        top_performers['Volatility_30d'] = (top_performers['Volatility_30d'] * 100).map("{:.2f}%".format)
    
    st.dataframe(top_performers.reset_index(drop=True), use_container_width=True)
