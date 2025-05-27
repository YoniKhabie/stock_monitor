# RUN COMMAND: python -m streamlit run gui.py

import time as time_module
from datetime import datetime

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from stock import Stock

TIMER = 900 # Need to be 900

def get_stock_data(ticker):
    stock = Stock(ticker)
    return stock


def plot_stock_chart(df: pd.DataFrame, title: str):
    fig = go.Figure()
    fig.add_trace(go.Candlestick(
        x=df["Date"],
        open=df["Open"][ticker],
        high=df["High"][ticker],
        low=df["Low"][ticker],
        close=df["Close"][ticker],
        name="Candlestick"
    ))

    for period, color in zip([6, 50, 200], ["blue", "green", "red"]):
        sma_col = f"SMA{period}"
        if sma_col in df.columns:
            fig.add_trace(go.Scatter(
                x=df["Date"], y=df[sma_col],
                mode="lines", name=sma_col,
                line=dict(color=color, dash="dot")
            ))

    if "Support" in df.columns:
        fig.add_trace(go.Scatter(
            x=df["Date"], y=df["Support"],
            mode="lines", name="Support",
            line=dict(color="orange", dash="dash")
        ))
    if "Resistance" in df.columns:
        fig.add_trace(go.Scatter(
            x=df["Date"], y=df["Resistance"],
            mode="lines", name="Resistance",
            line=dict(color="purple", dash="dash")
        ))

    fig.update_layout(
        title=title,
        xaxis_title="Date",
        yaxis_title="Price (USD)",
        xaxis_rangeslider_visible=False,
        template="plotly_white",
        xaxis=dict(
            type='category',
            tickangle=-45,
            tickfont=dict(size=12)
        )
    )
    return fig

# --- Streamlit App ---
st.set_page_config(layout="wide")

# Create placeholders for dynamic content
title_placeholder = st.empty()

stock_input = st.text_input(
    "Enter stock ticker",
    placeholder="e.g., AAPL, TSLA, MSFT, GOOGL, SPY",
    key="stock_input"
)
ticker = stock_input if stock_input else "SPY"
chart_placeholder_daily = st.empty()
chart_placeholder_intraday = st.empty()
status_placeholder = st.empty()



while True:
    # Get fresh data (will use cached version if <15 minutes old)
    stock = get_stock_data(ticker)
    
    # Update the UI components
    with title_placeholder.container():
        st.title(f"{ticker} Stock Charts")
    
    with chart_placeholder_daily.container():
        st.subheader("Daily Chart 1d")
        st.plotly_chart(plot_stock_chart(stock.df_daily, f"{ticker} - Daily Chart"), 
                       use_container_width=True)
    
    with chart_placeholder_intraday.container():
        st.subheader("Intraday Chart 30m")
        st.plotly_chart(plot_stock_chart(stock.df_inner_daily, f"{ticker} - Intraday Chart"), 
                       use_container_width=True)
    
    # Show last update time
    status_placeholder.write(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Wait 15 minutes before next update
    time_module.sleep(TIMER)



