import streamlit as st 

st.set_page_config(page_title="Analyse IRVE France", page_icon="⚡️")

st.title("⚡️ Analyse du Déploiement des Infrastructures de Recharge pour Véhicules Électriques en France")

st.markdown("""
Ce projet vise à analyser si la répartition et l'évolution des infrastructures de recharge pour véhicules électriques (IRVE) en France sont en adéquation avec la croissance du parc automobile électrique, les objectifs réglementaires et les besoins spécifiques de chaque territoire.

L'analyse s'appuie sur des données publiques pour fournir un état des lieux, identifier les disparités territoriales et temporelles, et proposer des recommandations stratégiques.
""")

st.markdown("---")

st.header("🎯 Problématique")
st.markdown("""
La répartition et l’évolution des infrastructures de recharge pour véhicules électriques en France sont-elles adaptées à la croissance du parc, aux objectifs du règlement AFI (Infrastructure pour Carburants Alternatifs) et aux besoins territoriaux ?
""")

st.header("🗺️ Démarche Analytique")
st.markdown("""
Notre analyse se décompose en **quatre étapes clés** pour répondre à la problématique centrale :

1. **État des Lieux de la Croissance**  
   - Évolution annuelle du nombre de points de recharge installés  
   - Croissance annuelle du parc de véhicules électriques  
   - Calcul du ratio points de recharge / véhicules électriques vs recommandation européenne (1 pour 10)

2. **Analyse Géographique**  
   - Corrélation entre densité de points de recharge et densité de population  
   - Identification des zones sous-équipées (bornes/1000 habitants, bornes/TMJA)  
   - Cartographie des clusters géographiques

3. **Analyse Temporelle**  
   - Détection des tendances, pics d’installation et retards régionaux  
   - Suivi par rapport aux objectifs de la Loi d’Orientation des Mobilités (LOM)

4. **Recommandations et Scénarios**  
   - Identification des zones prioritaires pour le déploiement  
   - Modélisation des besoins futurs selon la croissance du parc VE
""")

st.markdown("---")

st.header("📊 Fichiers de Données Utilisés")
st.markdown("""
- **BornePropre.csv 📍**  
  Liste géolocalisée des points de recharge (puissance, opérateur, date de mise en service).  
  *Base pour état des lieux, analyse spatiale et temporelle.*

- **voiture_par_commune.csv 🚗**  
  Nombre de véhicules électriques et hybrides rechargeables par commune.  
  *Quantification de la demande et calcul du ratio bornes/véhicules.*

- **population_with_geopoint.csv 👨‍👩‍👧‍👦**  
  Nombre d’habitants par commune avec coordonnées géographiques.  
  *Contextualisation par rapport à la population.*

- **TMJA.csv 🛣️**  
  Trafic Moyen Journalier Annuel sur grands axes routiers.  
  *Analyse des besoins en mobilité longue distance.*
""")

st.markdown("---")

st.header("🛠️ Environnement Technique")
st.markdown("""
- **Langage :** Python 3.10  
- **Bibliothèques :** pandas, numpy, matplotlib, seaborn, plotly, geopandas  
- **Outils :** Dataiku, Visual Studio Code, Streamlit
""")

st.markdown("---")

st.header("🧩 Issue Tree Résumé")
st.markdown("""
**Problématique centrale :**  
La répartition et l’évolution des infrastructures de recharge sont-elles adaptées à la croissance du parc VE, aux objectifs AFI et aux besoins territoriaux ?

---

**I. Comprendre le niveau actuel de déploiement**  
- Évolution des bornes et parc VE  
- Ratio bornes / véhicules vs AFI

**II. Analyse Géographique**  
- Cohérence infrastructures / population / trafic  
- Zones sous-équipées et clusters

**III. Analyse Temporelle**  
- Tendances, pics, retards  
- Conformité aux objectifs LOM

**IV. Recommandations**  
- Zones prioritaires  
- Renforcement selon trafic et prévisions  
- Scénarios de croissance
""")
