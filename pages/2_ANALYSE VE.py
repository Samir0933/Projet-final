import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import geopandas as gpd
import numpy as np

# Configuration de la page
st.set_page_config(
    page_title="Parc Véhicules Électriques France",
    page_icon="🚗",
    layout="wide"
)

# Configuration matplotlib pour Streamlit
plt.style.use('default')
sns.set_style("whitegrid")

# Fonction de chargement des données avec cache
@st.cache_data
def load_data():
    """Charge et prépare toutes les données"""
    # Chargement des données
    bornes = pd.read_csv("data_prod/BornesPropreFloLight.csv", low_memory=False) 
    vehicules = pd.read_csv("data_prod/voitures_par_commune_cleaned.csv", low_memory=False)
    population = pd.read_csv("data_prod/population_with_geopoint.csv", low_memory=False)

    # Préparation des données - dates et types
    bornes["date_mise_en_service"] = pd.to_datetime(bornes["date_mise_en_service"], errors="coerce")

    vehicules["code_commune"] = vehicules["code_commune"].astype(str).str.zfill(5)
    vehicules["date_recensement"] = pd.to_datetime(vehicules["date_recensement"], errors="coerce")
    vehicules["departement"] = vehicules["departement"].astype(str).str.strip().str.upper()
    vehicules["nb_voit_elec"] = pd.to_numeric(vehicules["nb_voit_elec"], errors="coerce")
    vehicules["nb_voit_total"] = pd.to_numeric(vehicules["nb_voit_total"], errors="coerce")

    # Population
    population["departement"] = population["Département"].astype(str).str.strip().str.upper()

    cols_to_num = ["0 à 19 ans", "20 à 39 ans", "40 à 59 ans", "60 à 74 ans", "75 ans et plus", "Total"]
    for col in cols_to_num:
        population[col] = (
            population[col]
            .astype(str)
            .str.replace(r"\s", "", regex=True)
            .str.replace(",", ".", regex=False)
            .replace({"-": None, "nc": None})
            .astype(float)
        )

    # Fonction pour extraire dates
    def extraire_date_datetime(df, colonne_date, prefix=""):
        col_prefix = f"_{prefix}" if prefix else ""
        df[f'annee{col_prefix}'] = pd.to_datetime(df[colonne_date]).dt.year.astype('Int64')
        df[f'mois{col_prefix}'] = pd.to_datetime(df[colonne_date]).dt.month.astype('Int64')
        df[f'jour{col_prefix}'] = pd.to_datetime(df[colonne_date]).dt.day.astype('Int64')
        df[f'date{col_prefix}'] = pd.to_datetime(df[colonne_date]).dt.date
        return df

    bornes = extraire_date_datetime(bornes, 'date_mise_en_service', prefix='mes')
    vehicules = extraire_date_datetime(vehicules, 'date_recensement', prefix='recensement')

    # Jointures
    vehicule_pop = vehicules.merge(population, on='departement', how='inner')

    return bornes, vehicules, population, vehicule_pop

@st.cache_data
def calculate_kpis(vehicule_pop):
    """Calcule les KPIs principaux"""
    vehicule_pop['date_recensement'] = pd.to_datetime(vehicule_pop['date_recensement'])
    vehicule_pop['annee'] = vehicule_pop['date_recensement'].dt.year

    # Données 2025 les plus récentes
    dernieres_dates_2025 = vehicule_pop[vehicule_pop['annee'] == 2025].groupby('departement')['date_recensement'].max().reset_index()
    vehicule_2025_latest = vehicule_pop.merge(dernieres_dates_2025, on=['departement','date_recensement'], how='inner')

    nb_vt_total = vehicule_2025_latest['nb_voit_total'].sum()
    nb_ve_total = vehicule_2025_latest['nb_voit_elec'].sum()
    pct_ve_vs_vt = (nb_ve_total / nb_vt_total * 100) if nb_vt_total else 0

    # Évolution annuelle
    dernieres_dates_dep = vehicule_pop.groupby(['annee', 'departement'])['date_recensement'].max().reset_index()
    vehicule_latest = vehicule_pop.merge(dernieres_dates_dep, on=['annee','departement','date_recensement'], how='inner')
    cumul_vehicules_annuel = vehicule_latest.groupby('annee').agg(
        total_ve=('nb_voit_elec', 'sum'),
        total_vt=('nb_voit_total', 'sum')
    ).reset_index()

    if len(cumul_vehicules_annuel) > 1:
        croissance_ve = (cumul_vehicules_annuel['total_ve'].iloc[-1] - cumul_vehicules_annuel['total_ve'].iloc[0]) / cumul_vehicules_annuel['total_ve'].iloc[0] * 100
    else:
        croissance_ve = 0

    return {
        'nb_vt_total': nb_vt_total,
        'nb_ve_total': nb_ve_total,
        'pct_ve_vs_vt': pct_ve_vs_vt,
        'croissance_ve': croissance_ve,
        'vehicule_latest': vehicule_latest
    }

def main():
    # Titre principal
    st.title("Parc Automobile Électrique en France")
    st.markdown("### Analyse de l'évolution des véhicules électriques")
    
    st.divider()

    # Chargement des données
    try:
        with st.spinner("Chargement des données..."):
            bornes, vehicules, population, vehicule_pop = load_data()
            kpis = calculate_kpis(vehicule_pop)
    
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="Total Véhicules 2025",
                value=f"{kpis['nb_vt_total']:,}".replace(',', ' ')
            )
        
        with col2:
            st.metric(
                label="Véhicules Électriques 2025",
                value=f"{kpis['nb_ve_total']:,}".replace(',', ' ')
            )
        
        with col3:
            st.metric(
                label="Part des VE",
                value=f"{kpis['pct_ve_vs_vt']:.1f}%"
            )
        
        with col4:
            st.metric(
                label="Croissance VE",
                value=f"+{kpis['croissance_ve']:.1f}%",
                delta=f"{kpis['croissance_ve']:.1f}%"
            )

        st.divider()

        # Section Graphiques
        st.header("Visualisations")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Évolution annuelle des véhicules électriques")
            
            # Préparation des données pour le graphique
            df_ve_annee = kpis['vehicule_latest'].groupby('annee')['nb_voit_elec'].sum().reset_index()
            
            fig, ax = plt.subplots(figsize=(10, 6))
            sns.lineplot(data=df_ve_annee, x='annee', y='nb_voit_elec', marker='o', color='#4CAF50', linewidth=3, markersize=8)
            ax.set_title("Évolution annuelle des véhicules électriques", fontsize=14, fontweight='bold')
            ax.set_ylabel("Nombre de VE", fontsize=12)
            ax.set_xlabel("Année", fontsize=12)
            ax.grid(True, alpha=0.3)
            
            # Format des nombres sur l'axe y
            ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{int(x/1000)}K' if x >= 1000 else str(int(x))))
            
            plt.tight_layout()
            st.pyplot(fig)
        
        with col2:
            st.subheader("Répartition VE vs VT en 2025")
            
            # Graphique en secteurs
            nb_ve = kpis['nb_ve_total']
            nb_vt_autres = kpis['nb_vt_total'] - nb_ve
            sizes = [nb_ve, nb_vt_autres]
            labels = ['Véhicules Électriques', 'Autres Véhicules']
            colors = ['#4CAF50', '#2196F3']
            
            fig, ax = plt.subplots(figsize=(10, 6))
            wedges, texts, autotexts = ax.pie(sizes, labels=labels, autopct='%1.1f%%', 
                                            startangle=90, colors=colors, 
                                            explode=(0.05, 0))
            
            # Améliorer l'apparence
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontweight('bold')
                autotext.set_fontsize(12)
            
            ax.set_title("Répartition VE vs VT en 2025", fontsize=14, fontweight='bold')
            plt.tight_layout()
            st.pyplot(fig)


    except Exception as e:
        st.error(f"Erreur lors du chargement des données : {str(e)}")
        st.info("Vérifiez que les fichiers de données sont présents dans les répertoires spécifiés.")


if __name__ == "__main__":
    main()

import streamlit as st
from PIL import Image        
# Titre de l'application
st.set_page_config(layout="wide")  # Utiliser toute la largeur
st.title("Nombre de VE par département en 2025")

# Charger l'image
image_path = "data_prod/carte.png" 
image = Image.open(image_path)

# Afficher l'image en grand
st.image(image, use_container_width=True)    