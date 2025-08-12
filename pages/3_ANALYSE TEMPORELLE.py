import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# --- Thème de couleurs choisi : Vert électrique & Bleu cobalt ---
PRIMARY_COLOR = "#2ecc71"  # Vert électrique
SECONDARY_COLOR = "#2980b9"  # Bleu cobalt

# --- CLASSE : Analyse bornes de recharge ---
class VEChargingAnalyzer:
    def __init__(self, df):
        self.df = df.copy()
        self.prepare_data()

    def prepare_data(self):
        # Conversion et extraction des dates
        self.df['date_mise_en_service'] = pd.to_datetime(self.df['date_mise_en_service'], errors='coerce')
        self.df['annee'] = self.df['date_mise_en_service'].dt.year.astype('Int64')
        self.df['mois'] = self.df['date_mise_en_service'].dt.month.astype('Int64')
        self.df['trimestre'] = self.df['date_mise_en_service'].dt.quarter.astype('Int64')

        # Filtrage sur la période 2010 à aujourd'hui
        current_year = datetime.now().year
        self.df = self.df[(self.df['annee'] >= 2010) & (self.df['annee'] <= current_year)]

    def plot_saisonnalite_installations(self):
        df_valid = self.df.dropna(subset=['mois', 'annee', 'trimestre'])
        mois_order = list(range(1, 13))
        mois_labels = ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Juin',
                       'Juil', 'Aoû', 'Sep', 'Oct', 'Nov', 'Déc']

        installs_par_mois = df_valid.groupby('mois').size().reindex(mois_order, fill_value=0)
        heatmap_data = df_valid.groupby(['annee', 'trimestre']).size().unstack(fill_value=0)

        fig = make_subplots(rows=1, cols=2, subplot_titles=["Installations par mois", "Heatmap Annuelle"])

        # Graphique 1 : Barres par mois
        fig.add_trace(go.Bar(
            x=mois_labels, 
            y=installs_par_mois.values, 
            marker_color=PRIMARY_COLOR
        ), row=1, col=1)

        # Graphique 2 : Heatmap annuelle
        fig.add_trace(go.Heatmap(
            z=heatmap_data.values,
            x=[f'T{col}' for col in heatmap_data.columns],
            y=heatmap_data.index,
            colorscale=[[0, SECONDARY_COLOR], [1, PRIMARY_COLOR]]
        ), row=1, col=2)

        fig.update_layout(
            title="Saisonnalité des installations",
            height=500,
            title_font=dict(size=20)
        )
        return fig

# --- CLASSE : Analyse du trafic ---
class TrafficAnalyzer:
    def __init__(self, df_traffic):
        self.df_traffic = df_traffic.copy()

    def plot_evolution_trafic(self):
        # Calcul de la moyenne du TMJA par année
        trafic_moyen = self.df_traffic.groupby('anneeMesureTrafic')['TMJA_actualise'].mean().reset_index()

        # Forcer le type entier pour éviter les décimales dans l'axe X
        trafic_moyen['anneeMesureTrafic'] = trafic_moyen['anneeMesureTrafic'].astype(int)
    
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=trafic_moyen['anneeMesureTrafic'],
            y=trafic_moyen['TMJA_actualise'],
            mode='lines+markers',
            name='TMJA moyen',
            line=dict(width=3, color=SECONDARY_COLOR),
            marker=dict(size=8, color=PRIMARY_COLOR)
        ))
    
        # Format de l'axe X : ticks tous les ans et pas de décimales
        fig.update_xaxes(dtick=1, tickformat="d")
    
        fig.update_layout(
            title="Évolution du trafic moyen journalier en France",
            xaxis_title="Année",
            yaxis_title="TMJA moyen",
            height=500,
            title_font=dict(size=20)
        )
        return fig

# --- PAGE STREAMLIT ---
st.set_page_config(page_title="Analyse Temporelle", page_icon="⚡", layout="wide")

st.title("III. ANALYSE TEMPORELLE")

# Affichage des métriques juste après le titre principal
try:
    df_traffic = pd.read_csv('data/raw/TMJA2016_2019_Propre.csv')
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("TMJA moyen global", f"{df_traffic['TMJA_actualise'].mean():,.0f}")
    with col2:
        evol = df_traffic[df_traffic['anneeMesureTrafic'] == 2019]['TMJA_actualise'].mean() - \
               df_traffic[df_traffic['anneeMesureTrafic'] == 2016]['TMJA_actualise'].mean()
        st.metric("Évolution 2016-2019", f"{evol:+,.0f}")
    with col3:
        st.metric("Points de mesure", f"{len(df_traffic):,}")
except FileNotFoundError:
    st.error("Le fichier TMJA2016_2019_Propre.csv est introuvable.")
    df_traffic = None
except Exception as e:
    st.error(f"Erreur lors du chargement des données : {str(e)}")
    df_traffic = None

st.markdown("""
**Objectif** : Détecter les tendances, pics et retards dans l'équipement en bornes de recharge électrique et observer l'évolution du trafic routier.

:small_blue_diamond: **À quelle période observe-t-on les pics d’installation de bornes ?**  
:small_blue_diamond: **Comment évolue le trafic ou la population sur les mêmes périodes ?**  
:small_blue_diamond: **Y a-t-il des retards d’équipement selon les régions ?**
""")

def page_3_saisonnalite():
    # SECTION 1 - Installations de bornes
    st.header("Saisonnalité des installations de bornes")
    st.markdown("""
    Ce graphique montre les pics et creux d’installations de bornes au fil de l’année.  
    On peut identifier les saisons les plus actives et repérer les éventuels ralentissements.
    """)
    df_bornes = pd.read_csv('data/raw/BornesPropres.csv')
    analyzer = VEChargingAnalyzer(df_bornes)
    st.plotly_chart(analyzer.plot_saisonnalite_installations(), use_container_width=True)
    
    st.markdown("---")
    
    # SECTION 2 - Évolution du trafic
    st.header("Évolution du trafic routier en France")
    st.markdown("""
    Cette visualisation met en évidence l'évolution du trafic moyen journalier (TMJA).  
    En comparant avec la saisonnalité des bornes, on peut voir s'il existe un lien entre trafic et installation.
    """)
    if df_traffic is not None:
        traffic_analyzer = TrafficAnalyzer(df_traffic)
        st.plotly_chart(traffic_analyzer.plot_evolution_trafic(), use_container_width=True)

if __name__ == "__main__":
    page_3_saisonnalite()
