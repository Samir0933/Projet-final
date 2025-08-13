import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
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

    def prepare_data(self, min_year, max_year):
        self.df['date_mise_en_service'] = pd.to_datetime(self.df['date_mise_en_service'], errors='coerce')
        self.df['annee'] = self.df['date_mise_en_service'].dt.year.astype('Int64')
        self.df['mois'] = self.df['date_mise_en_service'].dt.month.astype('Int64')
        self.df['trimestre'] = self.df['date_mise_en_service'].dt.quarter.astype('Int64')
        # Filtrage selon la plage d'années choisie
        self.df = self.df[(self.df['annee'] >= min_year) & (self.df['annee'] <= max_year)]

    def plot_saisonnalite_installations(self):
        df_valid = self.df.dropna(subset=['mois', 'annee', 'trimestre'])
        mois_order = list(range(1, 13))
        mois_labels = ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Juin',
                       'Juil', 'Aoû', 'Sep', 'Oct', 'Nov', 'Déc']

        installs_par_mois = df_valid.groupby('mois').size().reindex(mois_order, fill_value=0)
        heatmap_data = df_valid.groupby(['annee', 'trimestre']).size().unstack(fill_value=0)

        fig = make_subplots(rows=1, cols=2, subplot_titles=["Installations par mois", "Heatmap Annuelle"])
        fig.add_trace(go.Bar(x=mois_labels, y=installs_par_mois.values, marker_color=PRIMARY_COLOR), row=1, col=1)
        fig.add_trace(go.Heatmap(
            z=heatmap_data.values,
            x=[f'T{col}' for col in heatmap_data.columns],
            y=heatmap_data.index,
            colorscale=[[0, SECONDARY_COLOR], [1, PRIMARY_COLOR]]
        ), row=1, col=2)

        fig.update_layout(title="Saisonnalité des installations", height=500, title_font=dict(size=20))
        return fig

# --- CLASSE : Analyse du trafic ---
class TrafficAnalyzer:
    def __init__(self, df_traffic):
        self.df_traffic = df_traffic.copy()

    def plot_evolution_trafic(self):
        trafic_moyen = self.df_traffic.groupby('anneeMesureTrafic')['TMJA_actualise'].mean().reset_index()
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

# Chargement des données trafic
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
except:
    df_traffic = None
    st.error("Erreur lors du chargement du fichier TMJA2016_2019_Propre.csv")

# --- FILTRE PLAGE D'ANNÉES ---
min_year = 2010
max_year = datetime.now().year
annees_selection = st.slider(
    "Filtrer par plage d'années",
    min_value=min_year,
    max_value=max_year,
    value=(min_year, max_year)
)

st.markdown("""
**Objectif** : Détecter les tendances, pics et retards dans l'équipement en bornes de recharge électrique et observer l'évolution du trafic routier.
""")

def page_3_saisonnalite():
    # SECTION 1 - Installations de bornes filtrées
    st.header("Saisonnalité des installations de bornes")
    df_bornes = pd.read_csv('data/raw/BornesPropres.csv')
    analyzer = VEChargingAnalyzer(df_bornes)
    analyzer.prepare_data(annees_selection[0], annees_selection[1])
    st.plotly_chart(analyzer.plot_saisonnalite_installations(), use_container_width=True)

    st.markdown("---")

    # SECTION 2 - Évolution du trafic filtré
    st.header("Évolution du trafic routier en France")
    if df_traffic is not None:
        df_traffic_filtered = df_traffic[
            (df_traffic['anneeMesureTrafic'] >= annees_selection[0]) &
            (df_traffic['anneeMesureTrafic'] <= annees_selection[1])
        ]
        traffic_analyzer = TrafficAnalyzer(df_traffic_filtered)
        st.plotly_chart(traffic_analyzer.plot_evolution_trafic(), use_container_width=True)

if __name__ == "__main__":
    page_3_saisonnalite()
