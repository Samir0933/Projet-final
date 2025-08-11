import streamlit as st
import pandas as pd
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

        self.df['annee'] = self.df['date_mise_en_service'].dt.year.astype('Int64')
        self.df['mois'] = self.df['date_mise_en_service'].dt.month.astype('Int64')
        self.df['trimestre'] = self.df['date_mise_en_service'].dt.quarter.astype('Int64')

        current_year = datetime.now().year
        self.df = self.df[(self.df['annee'] >= 2010) & (self.df['annee'] <= current_year)]

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


# Dans ta page 3 Streamlit

def page_3_saisonnalite():
    st.title(" À quelle période observe-t-on les pics d’installation de bornes ?")
    file_path = 'data/raw/BornesPropres.csv'
    df = pd.read_csv(file_path)

    analyzer = VEChargingAnalyzer(df)
    fig = analyzer.plot_saisonnalite_installations()
    st.plotly_chart(fig, use_container_width=True)


# Pour lancer la page 3 (dans ton app Streamlit principale, tu appelles page_3_saisonnalite())
if __name__ == "__main__":
    page_3_saisonnalite()
