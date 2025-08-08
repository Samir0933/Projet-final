import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

class VEChargingAnalyzer:
    def __init__(self, df):
        self.df = df.copy()
        self.prepare_data()

    def prepare_data(self):
        self.df['date_mise_en_service'] = pd.to_datetime(self.df['date_mise_en_service'], errors='coerce')
        self.df['date_maj'] = pd.to_datetime(self.df['date_maj'], errors='coerce')

        if 'coordonneesXY' in self.df.columns:
            coords = self.df['coordonneesXY'].str.strip('[]').str.split(',', expand=True)
            if coords.shape[1] >= 2:
                self.df['longitude'] = pd.to_numeric(coords[0], errors='coerce')
                self.df['latitude'] = pd.to_numeric(coords[1], errors='coerce')

        self.df['annee'] = self.df['date_mise_en_service'].dt.year.astype('Int64')
        self.df['mois'] = self.df['date_mise_en_service'].dt.month.astype('Int64')
        self.df['trimestre'] = self.df['date_mise_en_service'].dt.quarter.astype('Int64')

        current_year = datetime.now().year
        self.df = self.df[(self.df['annee'] >= 2010) & (self.df['annee'] <= current_year)]

        self.df['puissance_nominale'] = pd.to_numeric(self.df['puissance_nominale'], errors='coerce')

        if 'adresse_station' in self.df.columns:
            self.df['code_postal'] = self.df['adresse_station'].str.extract(r'(\d{5})')
            self.df['departement'] = self.df['code_postal'].str[:2]
        else:
            np.random.seed(42)
            self.df['departement'] = np.random.choice(
                ['75', '13', '69', '59', '31', '44', '33', '34', '06', '67'], size=len(self.df)
            )

        self.df['puissance_nominale'] = self.df['puissance_nominale'].fillna(22)
        self.df['categorie_puissance'] = pd.cut(
            self.df['puissance_nominale'],
            bins=[0, 7, 22, 50, 150, float('inf')],
            labels=['Lente (≤7kW)', 'Normale (7-22kW)', 'Semi-rapide (22-50kW)',
                    'Rapide (50-150kW)', 'Ultra-rapide (>150kW)']
        ).astype(str)

        self.df['nom_operateur'] = self.df['nom_operateur'].fillna('Inconnu').astype(str)
        self.df['nom_station'] = self.df['nom_station'].fillna('Station sans nom').astype(str)

        years = list(range(2015, 2026))
        ve_data = {
            'annee': years,
            'nb_ve': [8000, 15000, 25000, 42000, 68000, 185000, 295000,
                      400000, 520000, 680000, 900000]
        }
        self.ve_df = pd.DataFrame(ve_data)

    def plot_evolution_bornes(self):
        df_valid = self.df.dropna(subset=['annee'])
        if len(df_valid) == 0:
            return None

        bornes_par_an = df_valid.groupby('annee').size().reset_index(name='total_bornes')
        bornes_par_an['cumul'] = bornes_par_an['total_bornes'].cumsum()

        fig = make_subplots(rows=1, cols=2, subplot_titles=["Cumul bornes", "Nouvelles installations"])

        fig.add_trace(go.Scatter(
            x=bornes_par_an['annee'], y=bornes_par_an['cumul'],
            mode='lines+markers', name="Cumul bornes"), row=1, col=1)

        fig.add_trace(go.Bar(
            x=bornes_par_an['annee'], y=bornes_par_an['total_bornes'],
            name="Installations annuelles"), row=1, col=2)

        fig.update_layout(title_text="Évolution des bornes", height=500)
        return fig

    def plot_ratio_bornes_ve(self):
        df_clean = self.df.dropna(subset=['annee'])
        bornes_cumul = df_clean.groupby('annee').size().cumsum()
        bornes_reset = bornes_cumul.reset_index()
        bornes_reset.columns = ['annee', 'nb_bornes']
        bornes_reset['annee'] = bornes_reset['annee'].astype(int)

        ratio_data = pd.merge(bornes_reset, self.ve_df, on='annee', how='inner')
        ratio_data['ratio_actual'] = ratio_data['nb_ve'] / ratio_data['nb_bornes']
        ratio_data['objectif_afi'] = 10
        ratio_data['ecart'] = ratio_data['ratio_actual'] - 10

        fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                            subplot_titles=["Ratio VE/bornes", "Écart à l’objectif"])

        fig.add_trace(go.Scatter(
            x=ratio_data['annee'], y=ratio_data['ratio_actual'],
            mode='lines+markers', name="Ratio actuel"), row=1, col=1)

        fig.add_trace(go.Scatter(
            x=ratio_data['annee'], y=[10]*len(ratio_data),
            mode='lines', name="Objectif AFI", line=dict(dash='dash')), row=1, col=1)

        fig.add_trace(go.Bar(
            x=ratio_data['annee'], y=ratio_data['ecart'],
            name="Écart à l’objectif",
            marker_color=['red' if x > 0 else 'green' for x in ratio_data['ecart']]
        ), row=2, col=1)

        fig.update_layout(title_text="Ratio Bornes / Véhicules Électriques", height=600)
        return fig

    def plot_saisonnalite_installations(self):
        df_valid = self.df.dropna(subset=['mois', 'annee', 'trimestre'])
        mois_order = list(range(1, 13))
        mois_labels = ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Jun',
                       'Jul', 'Aoû', 'Sep', 'Oct', 'Nov', 'Déc']

        installs_par_mois = df_valid.groupby('mois').size().reindex(mois_order, fill_value=0)

        heatmap_data = df_valid.groupby(['annee', 'trimestre']).size().unstack(fill_value=0)

        fig = make_subplots(rows=1, cols=2, subplot_titles=["Installations par mois", "Heatmap Annuelle"])

        fig.add_trace(go.Bar(x=mois_labels, y=installs_par_mois.values), row=1, col=1)

        fig.add_trace(go.Heatmap(
            z=heatmap_data.values,
            x=[f'T{col}' for col in heatmap_data.columns],
            y=heatmap_data.index,
            colorscale='YlOrRd'
        ), row=1, col=2)

        fig.update_layout(title="Saisonnalité des installations", height=500)
        return fig

    def plot_operateurs_analysis(self):
        top_operateurs = self.df['nom_operateur'].value_counts().head(10)

        fig = make_subplots(rows=1, cols=2, subplot_titles=["Top opérateurs", "Évolution cumulée"])

        fig.add_trace(go.Bar(
            x=top_operateurs.values, y=top_operateurs.index,
            orientation='h'), row=1, col=1)

        top5_ops = top_operateurs.head(5).index
        for op in top5_ops:
            op_data = self.df[self.df['nom_operateur'] == op]
            install_cumul = op_data.groupby('annee').size().cumsum()
            fig.add_trace(go.Scatter(
                x=install_cumul.index, y=install_cumul.values,
                mode='lines+markers', name=op), row=1, col=2)

        fig.update_layout(title="Analyse des opérateurs", height=500)
        return fig

    def plot_scenarios_futurs(self):
        derniere_annee = self.df['annee'].max()
        bornes_actuelles = len(self.df)

        annees_futures = list(range(derniere_annee + 1, derniere_annee + 6))
        scenarios = {
            'Conservateur': [680000 * (1.2 ** i) for i in range(1, 6)],
            'Modéré': [680000 * (1.35 ** i) for i in range(1, 6)],
            'Ambitieux': [680000 * (1.5 ** i) for i in range(1, 6)]
        }

        fig = make_subplots(rows=1, cols=2, subplot_titles=["Projection VE", "Besoins en bornes"])

        for label, data in scenarios.items():
            fig.add_trace(go.Scatter(
                x=annees_futures, y=data, mode='lines+markers', name=f'VE - {label}'
            ), row=1, col=1)

            bornes_requises = [x / 10 for x in data]
            fig.add_trace(go.Scatter(
                x=annees_futures, y=bornes_requises, mode='lines+markers', name=f'Bornes - {label}'
            ), row=1, col=2)

        fig.add_hline(y=bornes_actuelles, line_dash='dash', row=1, col=2)

        fig.update_layout(title="Scénarios futurs", height=500)
        return fig

    # Supprimé plot_repartition_geographique car Folium non utilisé

    def generer_tous_graphiques(self):
        figs = []
        figs.append(('Évolution des bornes', self.plot_evolution_bornes()))
        figs.append(('Ratio Bornes / Véhicules Électriques', self.plot_ratio_bornes_ve()))
        figs.append(('Saisonnalité des installations', self.plot_saisonnalite_installations()))
        figs.append(('Analyse des opérateurs', self.plot_operateurs_analysis()))
        figs.append(('Scénarios futurs', self.plot_scenarios_futurs()))
        return figs


#graphiques ICI

file_path = 'data/raw/BornesPropres.csv'
df = pd.read_csv(file_path)

analyzer = VEChargingAnalyzer(df)

st.title("Analyse des bornes de recharge VE")

for title, fig in analyzer.generer_tous_graphiques():
    st.header(title)
    if fig:
        st.plotly_chart(fig)
    else:
        st.write("Pas de données à afficher.")