import streamlit as st
import pandas as pd

from ton_module import VEChargingAnalyzer  # adapte selon où tu ranges ta classe

# Chargement des données (à adapter au chemin correct)
df = pd.read_csv('../data/clean/borneClean.csv')

analyzer = VEChargingAnalyzer(df)

st.title("I. Niveau actuel de déploiement des VE et infrastructures")

st.header("1. Évolution du nombre de bornes de recharge par an")
fig1 = analyzer.plot_evolution_bornes()
if fig1:
    st.plotly_chart(fig1, use_container_width=True)
else:
    st.write("Pas de données disponibles pour ce graphique.")

st.header("2. Évolution du parc de véhicules électriques")
# Ici tu peux ajouter un graphique similaire quand tu l'auras

st.header("3. Ratio bornes / véhicules (objectif AFI = 1 borne pour 10 VE)")
fig3 = analyzer.plot_ratio_bornes_ve()
if fig3:
    st.plotly_chart(fig3, use_container_width=True)
else:
    st.write("Pas de données disponibles pour ce graphique.")

st.header("4. Analyse des opérateurs")
fig4 = analyzer.plot_operateurs_analysis()
if fig4:
    st.plotly_chart(fig4, use_container_width=True)
else:
    st.write("Pas de données disponibles pour ce graphique.")