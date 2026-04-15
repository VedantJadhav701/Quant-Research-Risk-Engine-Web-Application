import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import requests
from datetime import datetime, timedelta

# Page config
st.set_page_config(
    page_title="Quant Research & Risk Engine",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
<style>
    .reportview-container {
        background: #0e1117;
    }
    .metric-card {
        background-color: #1e2130;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        border: 1px solid #3e4150;
    }
</style>
""", unsafe_allow_html=True)

import os

# API Base URL (Live Vercel Backend)
API_URL = os.getenv("API_URL", "https://quant-research-risk-engine-web-appl-gules.vercel.app")

# If using Streamlit Secrets (priority)
try:
    if "API_URL" in st.secrets:
        API_URL = st.secrets["API_URL"]
except:
    pass

# Sidebar Inputs
st.sidebar.title("🛠️ Project Controls")
ticker = st.sidebar.text_input("Ticker Symbol", value="SPY")
start_date = st.sidebar.date_input("Start Date", datetime.now() - timedelta(days=730))
end_date = st.sidebar.date_input("End Date", datetime.now())
simulations = st.sidebar.slider("Monte Carlo Paths", 5000, 20000, 10000)

run_button = st.sidebar.button("🚀 Run Full Pipeline")

st.title("🛡️ Quant Research & Risk Engine")
st.markdown("---")

if run_button:
    with st.spinner("Executing Pipeline... (Regime Detection -> Volatility Modeling -> Simulation)"):
        try:
            # Call Backend API
            payload = {
                "ticker": ticker,
                "start_date": start_date.strftime('%Y-%m-%d'),
                "end_date": end_date.strftime('%Y-%m-%d'),
                "simulations": simulations
            }
            
            response = requests.post(f"{API_URL}/analyze", json=payload)
            if response.status_code == 200:
                data = response.json()['result']
                
                # --- Metrics Section ---
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Detected Regime", data['metadata']['regime'])
                with col2:
                    st.metric("VaR (95%)", f"{data['risk']['metrics']['VaR_95']:.2%}")
                with col3:
                    st.metric("CVaR (95%)", f"{data['risk']['metrics']['CVaR_95']:.2%}")
                with col4:
                    st.metric("Max Drawdown", f"{data['risk']['metrics']['Max_Drawdown']:.2%}")
                
                st.markdown("---")
                
                # --- Plots Section ---
                tab1, tab2, tab3 = st.tabs(["🌪️ Volatility Surface", "🧠 Regime Analysis", "🎲 Risk Simulation"])
                
                with tab1:
                    st.subheader("3D Volatility Surface (Term Structure + Skew)")
                    vol_data = data['volatility']['surface']
                    fig_surface = go.Figure(data=[go.Surface(
                        x=vol_data['x'],
                        y=vol_data['y'],
                        z=vol_data['z'],
                        colorscale='Viridis'
                    )])
                    fig_surface.update_layout(
                        scene=dict(
                            xaxis_title='Strike',
                            yaxis_title='Expiry (Years)',
                            zaxis_title='Implied Vol'
                        ),
                        margin=dict(l=0, r=0, b=0, t=0)
                    )
                    st.plotly_chart(fig_surface, use_container_width=True)
                
                with tab2:
                    st.subheader("Market Regime Over Time")
                    regime_df = pd.DataFrame({
                        'Date': data['regime_data']['dates'],
                        'Price': data['regime_data']['prices'],
                        'Regime': data['regime_data']['regimes']
                    })
                    fig_regime = px.line(regime_df, x='Date', y='Price', color='Regime',
                                        title=f"{ticker} Price Colored by Risk Regime",
                                        color_discrete_map={
                                            'Low Volatility': '#00cc96',
                                            'Trending': '#636efa',
                                            'High Volatility': '#ef553b'
                                        })
                    st.plotly_chart(fig_regime, use_container_width=True)
                
                with tab3:
                    st.subheader("Monte Carlo Path Simulation (Student-t)")
                    paths = np.array(data['risk']['simulation']['paths']).T
                    horizon = data['risk']['simulation']['horizon']
                    
                    fig_paths = go.Figure()
                    # Plot subset of paths
                    for i in range(min(50, paths.shape[0])):
                        fig_paths.add_trace(go.Scatter(y=paths[i], mode='lines', 
                                                    line=dict(width=1), opacity=0.3, 
                                                    showlegend=False))
                    
                    fig_paths.update_layout(
                        title=f"Next 252 Trading Days Simulation (Starting Price: ${data['metadata']['current_price']})",
                        xaxis_title="Days",
                        yaxis_title="Price"
                    )
                    st.plotly_chart(fig_paths, use_container_width=True)

            else:
                st.error(f"API Error: {response.text}")
        except Exception as e:
            st.error(f"Failed to connect to backend: {str(e)}")
else:
    st.info("👈 Set parameters in the sidebar and click 'Run Full Pipeline' to begin.")
    
    # Hero/Welcome area
    st.subheader("Advanced Quantitative Risk Engine")
    
    st.markdown("""
    ### System Capabilities:
    1. **Real-time Data Fetching**: Integration with Yahoo Finance for global markets.
    2. **Adaptive Simulation**: Monte Carlo paths using Student-t distributions that adjust based on the current regime.
    3. **Volatility Surface**: 3D surface construction modeling both term structure and equity skew.
    4. **ML Regime Detection**: SVD-based dimensionality reduction followed by KMeans clustering to identify hidden market states.
    """)
