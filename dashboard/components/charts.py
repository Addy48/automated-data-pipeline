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

def render_ticker_explorer(df, selected_symbol):
    """Render historical charts for a selected ticker."""
    if not selected_symbol:
        st.info("Please select a stock symbol to explore.")
        return

    ticker_df = df[df['Symbol'] == selected_symbol]
    if ticker_df.empty:
        st.warning(f"No historical data found for {selected_symbol}.")
        return

    # Sort sequentially
    ticker_df = ticker_df.sort_values('Date').reset_index(drop=True)
    latest_row = ticker_df.iloc[-1]
    
    close_price = latest_row.get('Close', 0.0)
    cum_return = latest_row.get('Cumulative_Return', 0.0) * 100
    volatility = latest_row.get('Volatility_30D', 0.0) * 100
    drawdown = latest_row.get('Max_Drawdown', 0.0) * 100
    exchange = latest_row.get('Exchange', '')
    security = latest_row.get('Security', selected_symbol)
    
    # Sign and color formatting
    ret_color = "#385723" if cum_return >= 0 else "#c00000"
    ret_bg = "#e2f0d9" if cum_return >= 0 else "#fce4d6"
    ret_sign = "+" if cum_return > 0 else ""
    currency = "$" if "S&P" in exchange else "₹"

    # Display KPI highlights for the stock
    st.markdown(f"""
    <div style="background: #ffffff; border-radius: 16px; border: 1px solid #e1e0db; padding: 24px; box-shadow: 0 4px 12px rgba(0,0,0,0.03); margin-bottom: 25px;">
        <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 15px;">
            <div>
                <span style="font-size: 11px; font-weight: 600; color: #7a7872; letter-spacing: 1px; text-transform: uppercase;">{exchange} • Stock Analytics</span>
                <h2 style="margin: 4px 0 0 0; font-family: 'Playfair Display', serif; font-size: 36px; color: #1c1a17;">{selected_symbol}</h2>
                <div style="font-size: 14px; color: #7a7872; margin-top: 2px;">{security}</div>
            </div>
            <div style="text-align: right;">
                <span style="font-size: 11px; font-weight: 600; color: #7a7872; letter-spacing: 1px; text-transform: uppercase;">Latest Close</span>
                <h2 style="margin: 4px 0 0 0; font-size: 36px; color: #1c1a17;">{currency}{close_price:,.2f}</h2>
                <span style="background: {ret_bg}; color: {ret_color}; font-size: 13px; font-weight: bold; border-radius: 4px; padding: 3px 8px; display: inline-block; margin-top: 4px;">
                    {ret_sign}{cum_return:.2f}% Cumulative Return
                </span>
            </div>
        </div>
        
        <div style="height: 1px; background: #e1e0db; margin: 20px 0;"></div>
        
        <div style="display: flex; gap: 40px; flex-wrap: wrap;">
            <div>
                <div style="font-size: 12px; color: #7a7872;">30-Day Annualized Volatility</div>
                <div style="font-size: 20px; font-weight: bold; color: #1c1a17; margin-top: 2px;">{volatility:.2f}%</div>
            </div>
            <div>
                <div style="font-size: 12px; color: #7a7872;">Max Historical Drawdown</div>
                <div style="font-size: 20px; font-weight: bold; color: #1c1a17; margin-top: 2px;">{drawdown:.2f}%</div>
            </div>
            <div>
                <div style="font-size: 12px; color: #7a7872;">20-Day Simple Moving Average</div>
                <div style="font-size: 20px; font-weight: bold; color: #1c1a17; margin-top: 2px;">{currency}{latest_row.get('MA_20', 0.0):,.2f}</div>
            </div>
            <div>
                <div style="font-size: 12px; color: #7a7872;">50-Day Simple Moving Average</div>
                <div style="font-size: 20px; font-weight: bold; color: #1c1a17; margin-top: 2px;">{currency}{latest_row.get('MA_50', 0.0):,.2f}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Plot Price Chart (Close vs MA_20 vs MA_50)
    st.markdown("#### Price History & Moving Averages")
    
    chart_data = ticker_df[['Date', 'Close', 'MA_20', 'MA_50']].copy()
    chart_data['Date'] = pd.to_datetime(chart_data['Date'])
    chart_data = chart_data.set_index('Date')
    
    st.line_chart(chart_data, height=350, use_container_width=True)

    # Plot Volume Chart
    st.markdown("#### Trading Volume History")
    
    volume_data = ticker_df[['Date', 'Volume']].copy()
    volume_data['Date'] = pd.to_datetime(volume_data['Date'])
    volume_data = volume_data.set_index('Date')
    
    st.bar_chart(volume_data, height=180, use_container_width=True)


def render_pipeline_monitor():
    """Render pipeline health metrics and run logs."""
    import glob
    import json
    
    st.markdown("### Pipeline Execution Monitor")
    st.markdown("This control center aggregates JSON metric files produced during each ETL execution.")
    
    # Gather logs
    log_files = glob.glob("logs/metrics_*.json")
    if not log_files:
        st.info("No pipeline execution logs found in the `logs/` directory.")
        return
        
    runs = []
    for f_path in log_files:
        try:
            with open(f_path, 'r') as f:
                run_data = json.load(f)
                runs.append(run_data)
        except Exception:
            pass
            
    if not runs:
        st.warning("Failed to parse any pipeline execution logs.")
        return
        
    runs_df = pd.DataFrame(runs)
    # Sort runs chronologically (newest first)
    runs_df = runs_df.sort_values('start_time', ascending=False).reset_index(drop=True)
    
    # Display overall metrics
    total_runs = len(runs_df)
    success_runs = len(runs_df[runs_df['status'] == 'SUCCESS'])
    fail_runs = len(runs_df[runs_df['status'] == 'FAILURE'])
    success_rate = (success_runs / total_runs) * 100 if total_runs > 0 else 0.0
    
    # Custom HTML Summary Cards
    st.markdown(f"""
    <div style="display: flex; gap: 20px; margin-bottom: 25px; flex-wrap: wrap;">
        <div style="flex: 1; min-width: 200px; background: #ffffff; padding: 20px; border-radius: 14px; border: 1px solid #e1e0db; box-shadow: 0 4px 12px rgba(0,0,0,0.02);">
            <div style="font-size: 11px; text-transform: uppercase; color: #7a7872; font-weight: 600; margin-bottom: 4px;">📅 Total ETL Runs</div>
            <div style="font-size: 26px; font-weight: 700; color: #1c1a17;">{total_runs}</div>
        </div>
        <div style="flex: 1; min-width: 200px; background: #ffffff; padding: 20px; border-radius: 14px; border: 1px solid #e1e0db; box-shadow: 0 4px 12px rgba(0,0,0,0.02);">
            <div style="font-size: 11px; text-transform: uppercase; color: #385723; font-weight: 600; margin-bottom: 4px;">🟢 Successful Runs</div>
            <div style="font-size: 26px; font-weight: 700; color: #385723;">{success_runs}</div>
        </div>
        <div style="flex: 1; min-width: 200px; background: #ffffff; padding: 20px; border-radius: 14px; border: 1px solid #e1e0db; box-shadow: 0 4px 12px rgba(0,0,0,0.02);">
            <div style="font-size: 11px; text-transform: uppercase; color: #c00000; font-weight: 600; margin-bottom: 4px;">🔴 Failed Runs</div>
            <div style="font-size: 26px; font-weight: 700; color: #c00000;">{fail_runs}</div>
        </div>
        <div style="flex: 1; min-width: 200px; background: #ffffff; padding: 20px; border-radius: 14px; border: 1px solid #e1e0db; box-shadow: 0 4px 12px rgba(0,0,0,0.02);">
            <div style="font-size: 11px; text-transform: uppercase; color: #1a4329; font-weight: 600; margin-bottom: 4px;">📈 Success Rate</div>
            <div style="font-size: 26px; font-weight: 700; color: #1a4329;">{success_rate:.1f}%</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("#### Historical Run Logs")
    
    # Format the table for neat display
    table_cols = ['run_id', 'status', 'start_time', 'duration_seconds', 'records_extracted', 'records_gold']
    # Add error if present
    if 'errors' in runs_df.columns:
        table_cols.append('errors')
        
    table_df = runs_df[table_cols].copy()
    
    # Rename columns for presentation
    rename_dict = {
        'run_id': 'Run ID',
        'status': 'Status',
        'start_time': 'Start Time (UTC)',
        'duration_seconds': 'Duration (s)',
        'records_extracted': 'Extracted Rows',
        'records_gold': 'Gold Rows',
        'errors': 'Errors'
    }
    table_df = table_df.rename(columns={k: v for k, v in rename_dict.items() if k in table_df.columns})
    
    # Format dates and times
    if 'Start Time (UTC)' in table_df.columns:
        table_df['Start Time (UTC)'] = pd.to_datetime(table_df['Start Time (UTC)']).dt.strftime('%Y-%m-%d %H:%M:%S')
    if 'Duration (s)' in table_df.columns:
        table_df['Duration (s)'] = table_df['Duration (s)'].round(2)
    
    # Render with Streamlit
    st.dataframe(table_df, use_container_width=True)
