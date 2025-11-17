import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

st.set_page_config(page_title="Statistiques", page_icon="📊", layout="wide")

st.title("📊 Statistiques globales")

st.info("🚧 Page en construction - Évolutions temporelles, analyses comparatives, etc.")

# Exemple de contenu
st.subheader("Distribution des volumes")

# Mock data pour exemple
import numpy as np
data = pd.DataFrame({
    'date': pd.date_range('2022-01-01', periods=100),
    'volume': np.random.randint(1000, 5000, 100)
})

fig = px.line(data, x='date', y='volume', title="Évolution du volume dans le temps")
st.plotly_chart(fig, use_container_width=True)