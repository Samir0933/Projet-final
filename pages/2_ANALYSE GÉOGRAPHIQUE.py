import streamlit as st
import pandas as pd
import geopandas as gpd
from scipy.spatial import cKDTree
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from shapely import wkt

# =======================================================
# TITRE PRINCIPAL - II. ANALYSE GÉOGRAPHIQUE
# =======================================================
st.title("II. ANALYSE GÉOGRAPHIQUE")

st.markdown("""
**Objectif :** Évaluer la cohérence entre infrastructures, population et trafic routier.

**Points d'analyse :**
- 🔹 La répartition des bornes suit-elle la densité de population ?
- 🔹 Le déploiement des bornes suit-il les axes à fort trafic (TMJA) ?
- 🔹 Quelles zones sont sous-équipées (ratio bornes/population ou bornes/TMJA faible) ?
- 🔹 Corrélations : bornes vs trafic, bornes vs nombre de véhicules, bornes vs densité démographique
- 🔹 Existe-t-il des clusters géographiques par usage ou intensité ?
""")

# =======================================================
# 1. FONCTIONS UTILITAIRES
# =======================================================
def to_gdf(df, lon_col, lat_col, crs="EPSG:4326"):
    """Convertit un DataFrame en GeoDataFrame avec points géométriques."""
    return gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df[lon_col], df[lat_col]), crs=crs)

# =======================================================
# 2. CHARGEMENT DES DONNÉES
# =======================================================
@st.cache_data
def load_data():
    try:
        pop = pd.read_csv("data_prod/population_densite.csv", delimiter=",", encoding='utf-8')
        pop['Niv_densité'] = pop['Niv_densité'].astype(int)
        gdf_pop = to_gdf(pop, "longitude_decimal", "latitude_decimal")

        bornes = pd.read_csv("data_prod/BornesPropresLight.csv", delimiter=",", encoding='utf-8')
        bornes = bornes.dropna(subset=['consolidated_latitude', 'consolidated_longitude'])
        gdf_bornes = to_gdf(bornes, "consolidated_longitude", "consolidated_latitude")
    except FileNotFoundError:
        st.error("Fichiers CSV non trouvés. Vérifiez les chemins.")
        st.stop()

    # Association bornes-population via KDTree
    pop_coords = np.column_stack((gdf_pop.geometry.x, gdf_pop.geometry.y))
    bornes_coords = np.column_stack((gdf_bornes.geometry.x, gdf_bornes.geometry.y))
    tree = cKDTree(pop_coords)
    _, indices = tree.query(bornes_coords)
    gdf_bornes['index_pop'] = indices

    # Attribution du département
    dep_col = 'Libellé du département' if 'Libellé du département' in gdf_pop.columns else gdf_pop.columns[0]
    gdf_bornes['departement_proche'] = gdf_bornes['index_pop'].map(gdf_pop[dep_col])

    # Comptage bornes par département
    bornes_count = gdf_bornes.groupby('departement_proche').size().reset_index(name='nb_bornes')
    df = gdf_pop.merge(bornes_count, left_on=dep_col, right_on='departement_proche', how='left')
    df['nb_bornes'] = df['nb_bornes'].fillna(0).astype(int)

    # Palette uniforme
    colors = {1: '#00B894', 2: '#0984E3', 3: '#0652DD'}
    df['color'] = df['Niv_densité'].map(colors)
    return df, dep_col

@st.cache_data
def load_tmja_data():
    try:
        return pd.read_csv("data_prod/TMJA2016_2019_Propre.csv")
    except FileNotFoundError:
        st.error("Fichier TMJA non trouvé.")
        st.stop()

@st.cache_data
def load_bornes_with_dept():
    try:
        return pd.read_csv("data_prod/BornesPropres_with_depart_light.csv")
    except FileNotFoundError:
        st.warning("Fichier BornesPropres_with_depart_v2.csv manquant.")
        return None

def simple_linear_regression(x, y):
    """Régression linéaire simple + R²."""
    x = np.array(x)
    y = np.array(y)
    slope = np.cov(x, y, bias=True)[0, 1] / np.var(x) if np.var(x) != 0 else 0
    intercept = np.mean(y) - slope * np.mean(x)
    y_pred = slope * x + intercept
    r2 = 1 - (np.sum((y - y_pred)**2) / np.sum((y - np.mean(y))**2)) if np.var(y) != 0 else 0
    return slope, intercept, y_pred, r2

# =======================================================
# CHARGEMENT
# =======================================================
df, dep_col = load_data()
tmja_df = load_tmja_data()

# =======================================================
# 3. ANALYSE BORNES VS DENSITÉ
# =======================================================
st.header("Bornes vs Densité de population")
st.markdown("Commençons par vérifier si **la répartition des bornes suit la densité de population**.")

summary = df.groupby('Niv_densité', as_index=False)['nb_bornes'].sum()
fig1 = px.bar(summary, x='Niv_densité', y='nb_bornes',
              color='Niv_densité',
              color_discrete_sequence=['#00B894', '#0984E3', '#0652DD'],
              labels={'Niv_densité': 'Niveau de densité', 'nb_bornes': 'Nombre de bornes'})
st.plotly_chart(fig1)

st.markdown("On observe ainsi les zones les mieux équipées selon leur densité démographique.")

# =======================================================
# 4. ANALYSE TRAFIC TMJA
# =======================================================
st.header("Axes à fort trafic")
st.markdown("Top 10 de la somme annuelle du TMJA par route.")

sum_route = tmja_df.groupby("route")["TMJA_actualise"].sum().reset_index()
top_10_route = sum_route.sort_values("TMJA_actualise", ascending=False).head(10)
fig2 = px.bar(top_10_route, x='route', y='TMJA_actualise',
              color='TMJA_actualise', color_continuous_scale='Viridis',
              labels={'route': 'Route', 'TMJA_actualise': 'TMJA total'})
fig2.update_layout(xaxis_tickangle=45)
st.plotly_chart(fig2)

st.markdown("Ces données permettront de montrer quelles sont les zones de trafic les plus utilisées entre 2016 et 2019.")

# =======================================================
# 5. MATRICE DE CORRÉLATION
# =======================================================
st.subheader("Corrélations TMJA")
numeric_cols = ['TMJA_actualise', 'anneeMesureTrafic', 'depPrD']
available_cols = [col for col in numeric_cols if col in tmja_df.columns]
if len(available_cols) >= 2:
    correlation_matrix = tmja_df[available_cols].corr()
     # Définition des labels personnalisés pour les axes
    custom_labels = ["TMJA", "Année mesure trafic", "Département"]
    fig4 = px.imshow(correlation_matrix, text_auto=True, aspect="auto",x=custom_labels, y=custom_labels,
                     color_continuous_scale='RdBu_r',
                     title="Matrice de corrélation TMJA")
    st.plotly_chart(fig4)

# =======================================================
# 6. CARTE BORNE + TRAFIC
# =======================================================
st.header("Carte : Bornes & axes routiers")
st.markdown("Localisation conjointe des **bornes** et des **axes routiers** pour identifier les zones sous-équipées.")

# Carte
try:
    tmja_df['geopoint_depart'] = tmja_df['geopoint_depart'].apply(wkt.loads)
    gdf_tmja = gpd.GeoDataFrame(tmja_df, geometry='geopoint_depart', crs="EPSG:4326")
    gdf_tmja['lat'] = gdf_tmja.geometry.y
    gdf_tmja['lon'] = gdf_tmja.geometry.x
    bornes_raw = pd.read_csv("data_prod/BornesPropresLight.csv", delimiter=",", encoding='utf-8')
    bornes_clean = bornes_raw.dropna(subset=['consolidated_latitude', 'consolidated_longitude'])

    fig5 = go.Figure()
    fig5.add_trace(go.Scattermapbox(
        lat=bornes_clean['consolidated_latitude'], lon=bornes_clean['consolidated_longitude'],
        mode='markers', marker=dict(size=5, color='#00B894'), name='Bornes'
    ))
    #tmja_sample = gdf_tmja.sample(min(1000, len(gdf_tmja)))
    fig5.add_trace(go.Scattermapbox(
    lat=gdf_tmja['lat'], lon=gdf_tmja['lon'],
    mode='markers', marker=dict(size=6, color='#0984E3'), name='Axes routiers'
))
    fig5.update_layout(mapbox=dict(style="open-street-map", center=dict(lat=46.5, lon=2.5), zoom=5),
                       height=600)
    st.plotly_chart(fig5)
except Exception as e:
    st.error(f"Erreur carte : {e}")


# =======================================================
# 7. CORRÉLATION TMJA vs BORNES
# =======================================================
st.header("Corrélation TMJA vs Bornes")
bornes_with_dept = load_bornes_with_dept()
if bornes_with_dept is not None:
    bornes_clean = bornes_with_dept.dropna(subset=["num_departement"])
    bornes_clean["num_departement"] = bornes_clean["num_departement"].astype(int).astype(str).str.zfill(2)
    tmja_df["depPrD"] = tmja_df["depPrD"].astype(int).astype(str).str.zfill(2)

    bornes_dept = bornes_clean.groupby("num_departement").size().reset_index(name="bornes_count")
    tmja_dept = tmja_df.groupby("depPrD")["TMJA_actualise"].mean().reset_index()
    df_merge = pd.merge(bornes_dept, tmja_dept, left_on="num_departement", right_on="depPrD", how="inner")



    slope, intercept, y_pred, r2 = simple_linear_regression(df_merge["TMJA_actualise"], df_merge["bornes_count"])
    df_merge["y_pred"] = y_pred

    fig6 = px.scatter(df_merge, x="TMJA_actualise", y="bornes_count",
                      title=f"Corrélation TMJA vs Bornes (R²={r2:.2f})",
                      labels={"TMJA_actualise": "TMJA moyen", "bornes_count": "Nombre de bornes"})
    fig6.add_trace(go.Scatter(x=df_merge["TMJA_actualise"], y=df_merge["y_pred"],
                              mode="lines", name="Régression", line=dict(color='red')))
    st.plotly_chart(fig6)
    # ➕ Calcul du coefficient de corrélation de Pearson
    corr = df_merge["TMJA_actualise"].corr(df_merge["bornes_count"])

    # ➕ Interprétation du coefficient
    abs_corr = abs(corr)
    if abs_corr < 0.2:
        interpretation = "très faible"
    elif abs_corr < 0.4:
        interpretation = "faible"
    elif abs_corr < 0.6:
        interpretation = "modérée"
    elif abs_corr < 0.8:
        interpretation = "forte"
    else:
        interpretation = "très forte"

    st.markdown(f"**Coefficient de corrélation de Pearson :** {corr:.3f} ({interpretation})")