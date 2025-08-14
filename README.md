Analyse du Déploiement des Infrastructures de Recharge pour Véhicules Électriques en France ⚡️
Ce projet vise à analyser si la répartition et l'évolution des infrastructures de recharge pour véhicules électriques (IRVE) en France sont en adéquation avec la croissance du parc automobile électrique, les objectifs réglementaires et les besoins spécifiques de chaque territoire.

L'analyse s'appuie sur des données publiques pour fournir un état des lieux, identifier les disparités territoriales et temporelles, et proposer des recommandations stratégiques.

__________________________________________________________________________________________________________

🎯 Problématique
La répartition et l’évolution des infrastructures de recharge pour véhicules électriques en France sont-elles adaptées à la croissance du parc, aux objectifs du règlement AFI (Infrastructure pour Carburants Alternatifs) et aux besoins territoriaux ?

🗺️ Démarche Analytique
Notre analyse se décompose en quatre étapes clés pour répondre à la problématique centrale.

1. État des Lieux de la Croissance
L'objectif est de quantifier le déploiement actuel des véhicules électriques (VE) et des infrastructures de recharge.

Évolution annuelle du nombre de points de recharge installés.

Croissance annuelle du parc de véhicules électriques en circulation.

Calcul du ratio national points de recharge / véhicules électriques et comparaison avec la préconisation européenne (1 point de recharge pour 10 VE).

2. Analyse Géographique
Cette partie évalue la cohérence spatiale entre les infrastructures, la population et l'usage des routes.

Analyse de la corrélation entre la densité de points de recharge et la densité de population.

Identification des zones sous-équipées en se basant sur des ratios clés (ex: bornes pour 1000 habitants, bornes par rapport au Trafic Moyen Journalier Annuel - TMJA).

Cartographie des clusters géographiques pour visualiser les dynamiques de déploiement.

3. Analyse Temporelle
Il s'agit ici de détecter les tendances, les saisonnalités et les décalages dans le temps.

Identification des pics d'installation de bornes et analyse des retards d'équipement entre régions.

Suivi de la trajectoire de déploiement par rapport aux objectifs fixés par la Loi d'Orientation des Mobilités (LOM).



__________________________________________________________________________________________________________

📊 Fichiers de Données Utilisés
L'analyse s'appuie sur quatre jeux de données principaux qui ont été nettoyés et préparés. Voici le détail de chaque fichier et son intérêt stratégique :

BornePropre.csv 📍

Contenu : Notre référence pour les infrastructures. Il contient la liste géolocalisée de chaque point de recharge en France, avec sa puissance, son opérateur et sa date de mise en service.

Intérêt : Ce fichier est la base de l'offre d'infrastructures. Il permet de répondre aux questions de l'état des lieux (combien ?), de l'analyse géographique (où ?) et de l'analyse temporelle (quand ?).

voiture_par_commune.csv 🚗

Contenu : Recense le nombre de véhicules électriques et hybrides rechargeables par commune.

Intérêt : Essentiel pour quantifier la demande. Il permet de calculer le ratio bornes/véhicules, un indicateur clé, et de vérifier si les bornes sont là où se trouvent les voitures.

population_with_geopoint.csv 👨‍👩‍👧‍👦

Contenu : Le nombre d'habitants pour chaque commune, enrichi de coordonnées géographiques.

Intérêt : Permet de contextualiser le déploiement par rapport aux besoins résidentiels. Il est crucial pour calculer le nombre de bornes pour 1000 habitants et évaluer la pertinence de la couverture.

TMJA.csv 🛣️

Contenu : Le Trafic Moyen Journalier Annuel sur les grands axes routiers français.

Intérêt : Apporte une vision des besoins en mobilité longue distance. Il est indispensable pour identifier si les axes à fort trafic sont suffisamment équipés et pour renforcer le réseau sur les corridors de transit.

__________________________________________________________________________________________________________

🛠️ Environnement Technique
Langage : Python 3.10

Analyse de données : pandas, numpy, matplotlib, seaborn, plotly

Visualisation : matplotlib, seaborn

Analyse géospatiale : geopandas

Environnement : Dataiku, Visual Studio Code, Streamlit


__________________________________________________________________________________________________________

Issue Tree :

Problématique :  

La répartition et l’évolution des infrastructures de recharge pour véhicules électriques en France sont-elles adaptées à la croissance du parc, aux objectifs AFI et aux besoins territoriaux ? 

 

I. Comprendre le niveau actuel de déploiement des véhicules électriques et des infrastructures 


Quelle est l’évolution du nombre de bornes de recharge par an ? (graphborne) (voiture_commune olli)

Quelle est l’évolution du parc de véhicules électriques ? (voiture_commune olli)


Quel est le ratio bornes / véhicules (vs préconisation AFI = 1 borne pour 10 VE) ? (graphborne) (voiture_commune olli)



II. ANALYSE GÉOGRAPHIQUE 

 

Objectif : Évaluer la cohérence entre infrastructures, population et trafic routier 

La répartition des bornes suit-elle la densité de population ? (voiture_commune olli)


Quelles zones sont sous-équipées (ratio bornes/population ou bornes/TMJA faible) ? (TMJA olli partiel) (voiture_commune olli)


Corrélations : 

bornes vs nombre de véhicules 

bornes vs densité démographique 

Existe-t-il des clusters géographiques par usage ou intensité ? 



III. ANALYSE TEMPORELLE 

 

Objectif : Détecter les tendances, pics et retards 

À quelle période observe-t-on les pics d’installation de bornes ? (graphborne)

Y a-t-il des retards d’équipement selon les régions ? 

Les évolutions suivent-elles les objectifs de la loi d’orientation des mobilités ? 

Analyse des opérateurs et leur évolution (graphborne)

 

 

IV. RECOMMANDATIONS 

 

Objectif : Identifier les leviers d’action et zones prioritaires pour l’avenir  (graphborne)

Quelles régions / communes doivent être ciblées en priorité ? (voiture_commune olli)


Où renforcer le réseau selon le trafic et les prévisions d’immatriculation ? (TMJA olli partiel)

Quels opérateurs pourraient être mobilisés selon leurs performances passées ? 

Scénarios : que se passe-t-il si les VE augmentent de X% par an ? (graphborne)