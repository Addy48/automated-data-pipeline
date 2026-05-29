import streamlit as st
import pandas as pd

def render_sector_growth_chart(df):
    """Render a line chart of sector cumulative returns over time."""
    st.markdown("### Sector Cumulative Returns Over 12 Months")
    
    if df.empty:
        st.info("Insufficient data for sector growth chart.")
        return

    # Handle columns correctly
    sector_col = 'GICS_Sector' if 'GICS_Sector' in df.columns else 'GICS Sector'
    
    if sector_col not in df.columns:
        st.warning("GICS Sector column not found in data.")
        return

    # Group by Date and Sector to get average cumulative return
    sector_growth = df.groupby(['Date', sector_col])['Cumulative_Return'].mean().reset_index()
    
    # Pivot for charting
    chart_data = sector_growth.pivot(index='Date', columns=sector_col, values='Cumulative_Return')
    
    # Fill NaN values to ensure a continuous line chart
    chart_data = chart_data.ffill().bfill().fillna(0.0)
    
    st.line_chart(chart_data * 100, height=400, use_container_width=True)

def render_top_performers(df, selected_sector):
    """Render top performing stocks as beautiful cards styled like The Arena."""
    if not selected_sector:
        return

    st.markdown(f"### Top Performers in {selected_sector}")
    
    sector_col = 'GICS_Sector' if 'GICS_Sector' in df.columns else 'GICS Sector'
    
    sector_df = df[df[sector_col] == selected_sector]
    if sector_df.empty:
        st.info("No data for this sector.")
        return

    # Get latest data
    latest_date = sector_df['Date'].max()
    latest_data = sector_df[sector_df['Date'] == latest_date]
    
    # Sort by best performers
    top_data = latest_data.sort_values(by='Cumulative_Return', ascending=False).head(6)
    
    if top_data.empty:
        st.info("No stocks found in this sector.")
        return

    # Render as CSS grid
    cards_html = "<div style='display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 20px; margin-top: 15px;'>"
    
    for idx, row in top_data.iterrows():
        symbol = row.get('Symbol', row.get('Ticker', 'N/A'))
        security = row.get('Security', symbol)
        close_price = row.get('Close', 0.0)
        cum_return = row.get('Cumulative_Return', 0.0) * 100
        volatility = row.get('Volatility_30D', row.get('Volatility_30d', 0.0)) * 100
        drawdown = row.get('Max_Drawdown', 0.0) * 100
        exchange = row.get('Exchange', 'Market')
        
        # Format exchange flag/badge
        exch_badge = "🇮🇳 NSE" if "Nifty" in exchange else "🇺🇸 NYSE" if "S&P" in exchange else f"📈 {exchange}"
        
        # Color for returns
        ret_color = "#385723" if cum_return >= 0 else "#c00000"
        ret_bg = "#e2f0d9" if cum_return >= 0 else "#fce4d6"
        ret_sign = "+" if cum_return > 0 else ""
        
        # Status badge like "FINISHED" or "LIVE"
        status_text = "BULLISH" if cum_return > 5 else "BEARISH" if cum_return < -5 else "STABLE"
        status_color = "#385723" if cum_return > 5 else "#c00000" if cum_return < -5 else "#7f7f7f"
        status_bg = "#e2f0d9" if cum_return > 5 else "#fce4d6" if cum_return < -5 else "#f2f2f2"
        
        cards_html += f"""
        <div style="background: #ffffff; border-radius: 18px; border: 1px solid #e1e0db; padding: 20px; box-shadow: 0 4px 12px rgba(0,0,0,0.02); display: flex; flex-direction: column; justify-content: space-between; transition: transform 0.2s ease, box-shadow 0.2s ease;">
            <div>
                <!-- Card Header -->
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                    <span style="font-size: 11px; font-weight: 600; color: #7a7872; letter-spacing: 0.5px;">{exch_badge}</span>
                    <span style="background: {status_bg}; color: {status_color}; font-size: 9px; font-weight: bold; border-radius: 4px; padding: 3px 8px; letter-spacing: 0.5px;">{status_text}</span>
                </div>
                
                <!-- Card Body -->
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                    <div>
                        <div style="font-size: 22px; font-weight: 700; color: #1c1a17; font-family: 'Outfit', sans-serif;">{symbol}</div>
                        <div style="font-size: 12px; color: #7a7872; max-width: 180px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;" title="{security}">{security}</div>
                    </div>
                    <div style="text-align: right;">
                        <div style="font-size: 20px; font-weight: 700; color: #1c1a17;">{"$" if "S&P" in exchange else "₹"}{close_price:,.2f}</div>
                        <div style="background: {ret_bg}; color: {ret_color}; font-size: 11px; font-weight: bold; border-radius: 4px; padding: 2px 6px; display: inline-block; margin-top: 4px;">
                            {ret_sign}{cum_return:.2f}%
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Divider -->
            <div style="height: 1px; background: #e1e0db; margin: 10px 0;"></div>
            
            <!-- Card Footer -->
            <div style="display: flex; justify-content: space-between; font-size: 11px; color: #7a7872;">
                <div>⚡ Volatility: <strong style="color: #1c1a17;">{volatility:.1f}%</strong></div>
                <div>📉 Max DD: <strong style="color: #1c1a17;">{drawdown:.1f}%</strong></div>
            </div>
        </div>
        """
        
    cards_html += "</div>"
    st.markdown(cards_html, unsafe_allow_html=True)
