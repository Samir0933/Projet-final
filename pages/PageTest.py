import streamlit as st
import pandas as pd
import plotly.express as px

# ==============================
# CONFIGURATION DE L'APPLICATION
# ==============================
st.set_page_config(page_title="Analyse démographique", layout="wide")

# Palette de couleurs thématique (voitures électriques : vert & bleu)
color_scale_main = 'Tealgrn'  # Teal/Green
color_scale_secondary = 'Blues'

# ==============================
# CHARGEMENT ET PRÉPARATION DES DONNÉES
# ==============================
file_path = 'data/clean/population_with_geopoint.csv'
df = pd.read_csv(file_path)

# Séparer latitude et longitude depuis la colonne geopoint
df[['lat', 'lon']] = df['geopoint'].str.split(',', expand=True)
df['lat'] = df['lat'].astype(float)
df['lon'] = df['lon'].astype(float)

# Nettoyage des colonnes numériques
df['Total'] = df['Total'].astype(str).str.replace(' ', '').str.replace('\u202f', '').str.replace('\xa0', '').astype(int)
age_columns = ['0 à 19 ans', '20 à 39 ans', '40 à 59 ans', '60 à 74 ans', '75 ans et plus']
for col in age_columns:
    df[col] = df[col].astype(str).str.replace(' ', '').str.replace('\u202f', '').str.replace('\xa0', '').astype(int)

# ==============================
# TITRE PRINCIPAL
# ==============================
st.markdown("<h1 style='text-align:center; color:#00796B;'>Analyse démographique en France</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; font-size:18px;'>Une exploration visuelle des structures d’âge et de la répartition de la population par département.</p>", unsafe_allow_html=True)

# ==============================
# 1. PYRAMIDE DES ÂGES - FRANCE ENTIÈRE
# ==============================
st.header("1. Pyramide des âges - France entière")
st.write("Commençons par une vue d’ensemble : cette pyramide horizontale représente la population totale par tranche d’âge, pour toute la France.")

age_totals = [df[col].sum() for col in age_columns]
age_labels = ['0-19 ans', '20-39 ans', '40-59 ans', '60-74 ans', '75+ ans']

fig_pyramid = px.bar(
    x=age_totals,
    y=age_labels,
    orientation='h',
    title='Répartition par tranche d’âge - France entière',
    labels={'x': 'Population', 'y': 'Tranche d’âge'},
    color=age_totals,
    color_continuous_scale=color_scale_main
)
st.plotly_chart(fig_pyramid, use_container_width=True)

# ==============================
# 2. ANALYSE DU VIEILLISSEMENT PAR DÉPARTEMENT
# ==============================
st.header("2. Analyse du vieillissement par département")
st.write("Après la vue globale, zoomons sur le vieillissement de la population : "
         "plus un département est rouge sur la carte, plus la proportion de seniors (75 ans et plus) est élevée.")

df['ratio_vieux_jeunes'] = df['75 ans et plus'] / df['0 à 19 ans']
df['pourcentage_seniors'] = (df['75 ans et plus'] / df['Total']) * 100

fig_vieillissement = px.scatter_mapbox(
    df,
    lat='lat',
    lon='lon',
    size='Total',
    color='pourcentage_seniors',
    hover_name='Département',
    hover_data={'pourcentage_seniors': ':.1f', 'ratio_vieux_jeunes': ':.2f', 'lat': False, 'lon': False},
    color_continuous_scale='RdPu',
    size_max=40,
    zoom=5,
    center={'lat': 46.5, 'lon': 2},
    mapbox_style='open-street-map',
    labels={'pourcentage_seniors': '% 75+ ans'}
)
fig_vieillissement.update_layout(height=700)
st.plotly_chart(fig_vieillissement, use_container_width=True)

# ==============================
# 3. TOP 10 JEUNES VS PLUS VIEUX
# ==============================
st.header("3. Top 10 départements les plus jeunes vs plus vieux")
st.write("Regardons maintenant les départements qui comptent le plus grand nombre de jeunes, "
         "et ceux où les seniors sont les plus nombreux.")

df_sorted_young = df.nlargest(10, '0 à 19 ans')
df_sorted_old = df.nlargest(10, '75 ans et plus')

col1, col2 = st.columns(2)

with col1:
    fig_young = px.bar(
        df_sorted_young,
        x='Département',
        y='0 à 19 ans',
        title='Top 10 - Jeunes (0-19 ans)',
        color='0 à 19 ans',
        color_continuous_scale=color_scale_secondary
    )
    fig_young.update_xaxes(tickangle=45)
    st.plotly_chart(fig_young, use_container_width=True)

with col2:
    fig_old = px.bar(
        df_sorted_old,
        x='Département',
        y='75 ans et plus',
        title='Top 10 - Seniors (75+ ans)',
        color='75 ans et plus',
        color_continuous_scale=color_scale_main
    )
    fig_old.update_xaxes(tickangle=45)
    st.plotly_chart(fig_old, use_container_width=True)

# ==============================
# 4. ANALYSE DES ACTIFS (20-59 ans)
# ==============================
st.header("4. Analyse des actifs (20-59 ans)")
st.write("Les actifs représentent une part essentielle de la population : cette carte montre leur répartition en France, "
         "avec la taille des cercles proportionnelle au nombre d’actifs.")

df['actifs'] = df['20 à 39 ans'] + df['40 à 59 ans']
df['pourcentage_actifs'] = (df['actifs'] / df['Total']) * 100

fig_actifs = px.scatter_mapbox(
    df,
    lat='lat',
    lon='lon',
    size='actifs',
    color='pourcentage_actifs',
    hover_name='Département',
    hover_data={'actifs': ':,', 'pourcentage_actifs': ':.1f', 'lat': False, 'lon': False},
    color_continuous_scale=color_scale_secondary,
    size_max=45,
    zoom=5,
    center={'lat': 46.5, 'lon': 2},
    mapbox_style='open-street-map',
    labels={'pourcentage_actifs': '% Actifs'}
)
fig_actifs.update_layout(height=700)
st.plotly_chart(fig_actifs, use_container_width=True)

# ==============================
# 5. RELATION JEUNES VS SENIORS
# ==============================
st.header("5. Relation entre population jeune et senior par département")
st.write("Enfin, ce nuage de points permet de visualiser la relation entre le nombre de jeunes (0-19 ans) "
         "et celui des seniors (75+ ans) dans chaque département.")

fig_scatter = px.scatter(
    df,
    x='0 à 19 ans',
    y='75 ans et plus',
    size='Total',
    hover_name='Département',
    labels={'0 à 19 ans': 'Population 0-19 ans', '75 ans et plus': 'Population 75+ ans'},
    color='Total',
    color_continuous_scale=color_scale_main
)
st.plotly_chart(fig_scatter, use_container_width=True)
