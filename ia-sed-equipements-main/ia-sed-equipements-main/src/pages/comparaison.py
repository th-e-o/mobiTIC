import streamlit as st

st.set_page_config(page_title="Comparaison", page_icon="📈", layout="wide")

st.title("📈 Comparaison de dates")

st.info("🚧 Page en construction - Comparaison entre deux dates, évolution, etc.")

col1, col2 = st.columns(2)

with col1:
    st.date_input("Date 1")
    st.write("Carte 1 ici")

with col2:
    st.date_input("Date 2")
    st.write("Carte 2 ici")