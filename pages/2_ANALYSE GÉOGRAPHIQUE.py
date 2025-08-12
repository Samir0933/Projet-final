import streamlit as st
import pandas as pd
import geopandas as gpd
from scipy.spatial import cKDTree
import numpy as np
import plotly.express as px

st.title("II. ANALYSE GÉOGRAPHIQUE")

# -------------------------
# 1. Fonctions utilitaires
# -------------------------
def to_gdf(df, lon_col, lat_col, crs="EPSG:4326"):
    """Convertit un DataFrame en GeoDataFrame avec points géométriques."""
    return gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df[lon_col], df[lat_col]), crs=crs)

# -------------------------
# 2. Chargement des données
# -------------------------
@st.cache_data
def load_data():
    try:
        pop = pd.read_csv("data/raw/population_densite.csv", delimiter=",", encoding='utf-8')
        pop['Niv_densité'] = pop['Niv_densité'].astype(int)
        gdf_pop = to_gdf(pop, "longitude_decimal", "latitude_decimal")

        bornes = pd.read_csv("data/raw/BornesPropres.csv", delimiter=",", encoding='utf-8')
        bornes = bornes.dropna(subset=['consolidated_latitude', 'consolidated_longitude'])
        gdf_bornes = to_gdf(bornes, "consolidated_longitude", "consolidated_latitude")
    except FileNotFoundError:
        st.error("Fichiers CSV non trouvés. Vérifiez les chemins dans votre structure de projet.")
        st.stop()

    # -------------------------
    # 3. KDTree pour association
    # -------------------------
    pop_coords = np.column_stack((gdf_pop.geometry.x, gdf_pop.geometry.y))
    bornes_coords = np.column_stack((gdf_bornes.geometry.x, gdf_bornes.geometry.y))

    tree = cKDTree(pop_coords)
    _, indices = tree.query(bornes_coords)
    gdf_bornes['index_pop'] = indices

    # -------------------------
    # 4. Attribution du département
    # -------------------------
    possible_cols = ['Libellé du département', 'departement']
    dep_col = next((c for c in possible_cols if c in gdf_pop.columns), gdf_pop.columns[0])
    gdf_bornes['departement_proche'] = gdf_bornes['index_pop'].map(gdf_pop[dep_col])

    # -------------------------
    # 5. Comptage et fusion
    # -------------------------
    bornes_count = gdf_bornes.groupby('departement_proche').size().reset_index(name='nb_bornes')
    df = gdf_pop.merge(bornes_count, left_on=dep_col, right_on='departement_proche', how='left')
    df['nb_bornes'] = df['nb_bornes'].fillna(0).astype(int)
    
    # -------------------------
    # 6. Couleurs
    # -------------------------
    colors = {1: '#a6cee3', 2: '#1f78b4', 3: '#08306b'}
    df['color'] = df['Niv_densité'].map(colors)

    return df, dep_col

# Charger les données
df, dep_col = load_data()

# -------------------------
# 6. Graphiques avec Plotly
# -------------------------

# Graphique 1: Bornes totales par niveau de densité
st.subheader("Nombre total de bornes par niveau de densité")
summary = df.groupby('Niv_densité', as_index=False)['nb_bornes'].sum()
colors = ['#a6cee3', '#1f78b4', '#08306b']

fig1 = px.bar(summary, 
              x='Niv_densité', 
              y='nb_bornes',
              color='Niv_densité',
              color_discrete_sequence=colors,
              labels={'Niv_densité': 'Niveau de densité', 'nb_bornes': 'Nombre total de bornes'})

st.plotly_chart(fig1)