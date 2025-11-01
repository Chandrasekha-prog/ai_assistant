import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.express as px
import plotly.graph_objects as go

# Dashboard Title and Layout
st.set_page_config(page_title="Attractive Portfolio Dashboard", layout="wide")
st.title("Interactive Investment Portfolio Dashboard")
st.markdown("Track your stock portfolio with real-time data. Customize assets below for an attractive, insightful view.")

# User Inputs for Interactivity
st.sidebar.header("Portfolio Settings")
assets = st.sidebar.multiselect("Select Stocks", ["AAPL", "GOOGL", "TSLA", "MSFT", "AMZN"], default=["AAPL", "GOOGL", "TSLA"])
weights = st.sidebar.slider("Equal Weight Allocation? (Or adjust manually)", 0, 100, 33)  # Simplified equal weighting
period = st.sidebar.select_slider("Historical Period (Days)", options=[30, 90, 180, 365], value=90)

# Fetch Data
@st.cache_data
def fetch_data(assets, period):
    data = yf.download(assets, period=f"{period}d")['Adj Close']
    returns = data.pct_change().dropna()
    portfolio_returns = (returns.mean(axis=1) * 100).cumsum()  # Cumulative returns
    latest_prices = data.iloc[-1]
    total_value = latest_prices.sum()  # Simplified total
    daily_changes = returns.iloc[-1] * 100
    return data, portfolio_returns, total_value, daily_changes, latest_prices

data, portfolio_returns, total_value, daily_changes, latest_prices = fetch_data(assets, period)

# Summary Metrics (Attractive KPI Cards)
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Portfolio Value", f"${total_value:.2f}")
with col2:
    st.metric("Cumulative Return", f"{portfolio_returns.iloc[-1]:.2f}%")
with col3:
    st.metric("Number of Assets", len(assets))

# Interactive Charts Section
st.header("Portfolio Visuals")

# Pie Chart for Allocation (Attractive with Hover Interactivity)
allocation = pd.DataFrame({"Asset": assets, "Allocation": [1/len(assets)] * len(assets)})  # Equal for simplicity
fig_pie = px.pie(allocation, values="Allocation", names="Asset", title="Portfolio Allocation",
                 color_discrete_sequence=px.colors.qualitative.Pastel)
fig_pie.update_traces(textposition='inside', textinfo='percent+label')
fig_pie.update_layout(margin=dict(t=30, b=0, l=0, r=0))
st.plotly_chart(fig_pie, use_container_width=True)

# Line Chart for Performance (Interactive Zoom/Pan)
fig_line = px.line(data, title="Stock Price Trends", color_discrete_sequence=px.colors.qualitative.Bold)
fig_line.update_layout(xaxis_title="Date", yaxis_title="Adjusted Close ($)", legend_title="Assets")
st.plotly_chart(fig_line, use_container_width=True)

# Bar Chart for Daily Changes (Color-Coded for Positive/Negative)
fig_bar = go.Figure(go.Bar(x=assets, y=daily_changes, marker_color=['green' if x > 0 else 'red' for x in daily_changes]))
fig_bar.update_layout(title="Daily % Change", xaxis_title="Assets", yaxis_title="% Change")
st.plotly_chart(fig_bar, use_container_width=True)

# Data Table for Details
st.header("Detailed Data")
st.dataframe(data.tail(10).style.background_gradient(cmap='viridis'))  # Attractive gradient styling

st.markdown("---")
st.caption("Data sourced from Yahoo Finance. For production, add error handling and more features.")