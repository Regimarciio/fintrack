import streamlit as st
import sqlite3
import pandas as pd

conn = sqlite3.connect("data/gastos.db")

df = pd.read_sql("SELECT * FROM gastos", conn)
itens = pd.read_sql("SELECT * FROM itens", conn)

st.title("Dashboard Financeiro")

if not df.empty:
    st.metric("Total", f"R$ {df['valor'].sum():.2f}")
    st.bar_chart(df.groupby("categoria")["valor"].sum())

if not itens.empty:
    st.subheader("Itens")
    st.dataframe(itens)
    st.bar_chart(itens.groupby("categoria")["valor"].sum())
