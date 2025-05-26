# RUN COMMAND: python -m streamlit run main.py

import time as time_module
from datetime import datetime

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import yfinance as yf

# Cache the stock data to prevent unnecessary reloads
TIMER = 900 # Need to be 900
@st.cache_data(ttl=TIMER)  # 15 minutes in seconds
def get_stock_data(ticker):
    stock = Stock(ticker)
    return stock


class Stock:
    def __init__(self, ticker):
        self.ticker = ticker
        self.df_daily = yf.download(ticker, interval="1d", period="6mo", auto_adjust=True)
        self.df_inner_daily = yf.download(ticker, interval="30m", period="21d", auto_adjust=True)

        for df in [self.df_daily, self.df_inner_daily]:
            Stock.add_sma(df, 6)
            Stock.add_sma(df, 50)
            Stock.add_sma(df, 200)
            df.reset_index(inplace=True)
        
        self.df_inner_daily = self.df_inner_daily.rename(columns={"Datetime": "Date"})

    @staticmethod
    def add_sma(dataframe: pd.DataFrame, num_periods: int):
        col_name = f"SMA{num_periods}"
        dataframe[col_name] = dataframe["Close"].rolling(window=num_periods).mean()

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



