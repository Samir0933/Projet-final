import streamlit as st 

st.set_page_config(page_title="Analyse IRVE France", page_icon="⚡️")

st.title("Analyse du Déploiement des Infrastructures de Recharge pour Véhicules Électriques en France")

st.markdown("""
Ce projet vise à analyser si la répartition et l'évolution des infrastructures de recharge pour véhicules électriques (IRVE) en France sont en adéquation avec la croissance du parc automobile électrique, les objectifs réglementaires et les besoins spécifiques de chaque territoire.

L'analyse s'appuie sur des données publiques pour fournir un état des lieux, identifier les disparités territoriales et temporelles, et proposer des recommandations stratégiques.
""")

st.markdown("---")

st.header("Problématique")
st.markdown("""
La répartition et l’évolution des infrastructures de recharge pour véhicules électriques en France sont-elles adaptées à la croissance du parc, aux objectifs du règlement AFI (Infrastructure pour Carburants Alternatifs) et aux besoins territoriaux ?
""")

st.header("Démarche Analytique")
st.markdown("""
Notre analyse se décompose en **quatre étapes clés** pour répondre à la problématique centrale :

1. **État des Lieux de la Croissance**  
  

2. **Analyse Géographique**  

3. **Analyse Temporelle**  
   


""")

st.markdown("---")

st.header("Fichiers de Données Utilisés")
st.markdown("""
- **BornesPropres_with_depart_light.csv et BornesPropresLight.csv  **  
  Liste géolocalisée des points de recharge (puissance, opérateur, date de mise en service).  
  *Base pour état des lieux, analyse spatiale et temporelle.*

- **voiture_par_commune.csv **  
  Nombre de véhicules électriques et hybrides rechargeables par commune.  
  *Quantification de la demande et calcul du ratio bornes/véhicules.*

- **population_with_geopoint.csv et population_densite.csv.csv **  
  Nombre d’habitants par commune avec coordonnées géographiques.  
  *Contextualisation par rapport à la population.*

- **TMJA2016_2019_Propre.csv  **  
  Trafic Moyen Journalier Annuel sur grands axes routiers.  
  *Analyse des besoins en mobilité longue distance.*
""")

st.markdown("---")
