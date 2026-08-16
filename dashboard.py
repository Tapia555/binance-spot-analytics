import streamlit as st
import pandas as pd
from datetime import datetime
import sqlite3
from pathlib import Path

st.set_page_config(page_title="Crypto Bot", layout="wide")
st.title("🤖 Crypto Trading Bot Dashboard")

# Sidebar
st.sidebar.header("Controls")
if st.sidebar.button("Refresh"):
    st.rerun()

symbol = st.sidebar.selectbox("Symbol", ["BTCUSDT", "ETHUSDT"])

# Load orders
db_path = Path("orders.db")
if db_path.exists():
    conn = sqlite3.connect(db_path)
    df = pd.read_sql("SELECT * FROM orders ORDER BY created_at DESC", conn)
    conn.close()
else:
    df = pd.DataFrame()

# Metrics
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Orders", len(df))
with col2:
    filled = len(df[df["status"] == "FILLED"]) if len(df) > 0 else 0
    st.metric("Filled", filled)
with col3:
    buys = len(df[df["side"] == "BUY"]) if len(df) > 0 else 0
    st.metric("Buys", buys)
with col4:
    sells = len(df[df["side"] == "SELL"]) if len(df) > 0 else 0
    st.metric("Sells", sells)

# PnL estimate
if len(df) > 0:
    filled_df = df[df["status"] == "FILLED"]
    if len(filled_df) >= 2:
        buys = filled_df[filled_df["side"] == "BUY"]["price"].sum()
        sells = filled_df[filled_df["side"] == "SELL"]["price"].sum()
        pnl = sells - buys
        st.metric("Est. PnL", f"${pnl:.2f}")

# Table
if len(df) > 0:
    st.subheader("📊 Recent Orders")
    display_cols = ["symbol", "side", "quantity", "price", "status", "created_at"]
    st.dataframe(df[display_cols], use_container_width=True)
else:
    st.info("No orders yet")

# Footer
st.markdown("---")
st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
