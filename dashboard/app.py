import os
import sys
import streamlit as st
import pandas as pd

# Add the parent directory to sys.path so we can import components
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from components.kpi_cards import render_kpi_cards
from components.charts import render_sector_growth_chart, render_top_performers
from components.sidebar import render_sidebar

# Define the local data path
DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'sector_growth_data.parquet')

st.set_page_config(
    page_title="Automated Data Pipeline & Dashboard",
    page_icon="📈",
    layout="wide"
)

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
    st.title("📈 12-Month Sector-Growth Trends Dashboard")
    st.markdown("This dashboard visualizes data extracted by our Automated ETL Pipeline, processing **50,000+** records from Yahoo Finance.")
    
    df = load_data()
    
    if df.empty:
        st.warning("No data found! Please run `python run_pipeline.py` first to generate the dataset.")
        return
        
    # Render Sidebar
    selected_sector = render_sidebar(df)
    
    # Render KPI Cards
    render_kpi_cards(df)
    
    # Filter df by sector if necessary
    chart_df = df if not selected_sector else df[df['GICS Sector'] == selected_sector]
    
    # Render Charts
    render_sector_growth_chart(chart_df)
    
    st.markdown("---")
    
    # Ensure selected_sector is passed to render_top_performers if it's set
    if selected_sector:
        render_top_performers(df, selected_sector)
    else:
        st.info("Select a specific sector from the sidebar to view top performing stocks.")

    st.markdown("---")
    st.caption("Built with Python, Pandas, Boto3, and Streamlit. Part of the Automated Data Pipeline Project.")

if __name__ == "__main__":
    main()
