import streamlit as st
import pandas as pd
import plotly.express as px

# Chargement du fichier CSV
file_path = 'data/clean/population_with_geopoint.csv'
df = pd.read_csv(file_path)

# Séparer latitude et longitude depuis la colonne geopoint
df[['lat', 'lon']] = df['geopoint'].str.split(',', expand=True)
df['lat'] = df['lat'].astype(float)
df['lon'] = df['lon'].astype(float)

# Nettoyage de la colonne Total
df['Total'] = df['Total'].astype(str).str.replace(' ', '').str.replace('\u202f', '').str.replace('\xa0', '').astype(int)

# Nettoyer les colonnes d'âge
age_columns = ['0 à 19 ans', '20 à 39 ans', '40 à 59 ans', '60 à 74 ans', '75 ans et plus']
for col in age_columns:
    df[col] = df[col].astype(str).str.replace(' ', '').str.replace('\u202f', '').str.replace('\xa0', '').astype(int)

st.title("POPULATION")
# 1. Pyramide des âges - France entière
st.header("1. Pyramide des âges - France entière")
age_totals = [df[col].sum() for col in age_columns]
age_labels = ['0-19 ans', '20-39 ans', '40-59 ans', '60-74 ans', '75+ ans']

fig_pyramid = px.bar(
    x=age_totals,
    y=age_labels,
    orientation='h',
    title='Pyramide des âges - France entière',
    labels={'x': 'Population', 'y': 'Tranches d\'âge'},
    color=age_totals,
    color_continuous_scale='Blues'
)
st.plotly_chart(fig_pyramid, use_container_width=True)

# 2. Analyse du vieillissement par département
st.header("2. Analyse du vieillissement par département")
df['ratio_vieux_jeunes'] = df['75 ans et plus'] / df['0 à 19 ans']
df['pourcentage_seniors'] = (df['75 ans et plus'] / df['Total']) * 100

fig_vieillissement = px.scatter_mapbox(
    df,
    lat='lat',
    lon='lon',
    size='Total',
    color='pourcentage_seniors',
    hover_name='Département',
    hover_data={
        'pourcentage_seniors': ':.1f',
        'ratio_vieux_jeunes': ':.2f',
        'lat': False,
        'lon': False
    },
    color_continuous_scale='Reds',
    size_max=40,
    zoom=5,
    center={'lat': 46.5, 'lon': 2},
    mapbox_style='open-street-map',
    title='Vieillissement de la population par département (% de 75+ ans)',
    labels={'pourcentage_seniors': '% 75+ ans'}
)
fig_vieillissement.update_layout(height=700, width=1000)
st.plotly_chart(fig_vieillissement, use_container_width=True)

# 3. Top 10 départements les plus jeunes vs plus vieux
st.header("3. Top 10 départements les plus jeunes vs plus vieux")

df_sorted_young = df.nlargest(10, '0 à 19 ans')
df_sorted_old = df.nlargest(10, '75 ans et plus')

fig_young = px.bar(
    df_sorted_young,
    x='Département',
    y='0 à 19 ans',
    title='Top 10 - Départements avec le plus de jeunes (0-19 ans)',
    color='0 à 19 ans',
    color_continuous_scale='Greens'
)
fig_young.update_xaxes(tickangle=45)
st.plotly_chart(fig_young, use_container_width=True)

fig_old = px.bar(
    df_sorted_old,
    x='Département',
    y='75 ans et plus',
    title='Top 10 - Départements avec le plus de seniors (75+ ans)',
    color='75 ans et plus',
    color_continuous_scale='Oranges'
)
fig_old.update_xaxes(tickangle=45)
st.plotly_chart(fig_old, use_container_width=True)

# 4. Analyse des actifs (20-59 ans)
st.header("4. Analyse des actifs (20-59 ans)")
df['actifs'] = df['20 à 39 ans'] + df['40 à 59 ans']
df['pourcentage_actifs'] = (df['actifs'] / df['Total']) * 100

fig_actifs = px.scatter_mapbox(
    df,
    lat='lat',
    lon='lon',
    size='actifs',
    color='pourcentage_actifs',
    hover_name='Département',
    hover_data={
        'actifs': ':,',
        'pourcentage_actifs': ':.1f',
        'lat': False,
        'lon': False
    },
    color_continuous_scale='Viridis',
    size_max=45,
    zoom=5,
    center={'lat': 46.5, 'lon': 2},
    mapbox_style='open-street-map',
    title='Répartition de la population active (20-59 ans)',
    labels={'pourcentage_actifs': '% Actifs'}
)
fig_actifs.update_layout(height=700, width=1000)
st.plotly_chart(fig_actifs, use_container_width=True)

# 5. Scatter plot - jeunes vs seniors
st.header("5. Relation entre population jeune et senior par département")
fig_scatter = px.scatter(
    df,
    x='0 à 19 ans',
    y='75 ans et plus',
    size='Total',
    hover_name='Département',
    title='Relation entre population jeune et senior par département',
    labels={'x': 'Population 0-19 ans', 'y': 'Population 75+ ans'},
    color='Total',
    color_continuous_scale='Rainbow'
)
st.plotly_chart(fig_scatter, use_container_width=True)

