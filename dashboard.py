import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import sqlite3
from pathlib import Path

st.set_page_config(page_title="Crypto Bot Dashboard", layout="wide")
st.title("🤖 Crypto Trading Bot Dashboard")

# Sidebar
st.sidebar.header("Controls")
refresh = st.sidebar.button("Refresh")
symbol = st.sidebar.selectbox("Symbol", ["BTCUSDT", "ETHUSDT"])

# Load orders from database
db_path = Path("orders.db")
if db_path.exists():
    conn = sqlite3.connect(db_path)
    df = pd.read_sql("SELECT * FROM orders ORDER BY created_at DESC", conn)
    conn.close()
else:
    df = pd.DataFrame()

# Metrics
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Trades", len(df))
with col2:
    winning = len(df[df["status"] == "FILLED"]) if len(df) > 0 else 0
    st.metric("Filled Orders", winning)
with col3:
    st.metric("Last Update", datetime.now().strftime("%H:%M:%S"))

# Orders table
if len(df) > 0:
    st.subheader("📊 Recent Orders")
    st.dataframe(
        df[["symbol", "side", "quantity", "price", "status", "created_at"]],
        use_container_width=True,
    )
else:
    st.info("No orders yet")

# PnL (если есть данные)
st.subheader("💰 PnL")
st.info("PnL tracking coming soon")

# Footer
st.markdown("---")
st.caption("Auto-refresh every 30 seconds")
