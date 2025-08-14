import streamlit as st
from PIL import Image

# Titre de l'application
st.set_page_config(layout="wide")  # Utiliser toute la largeur
st.title("Diagramme de Gantt")

# Charger l'image
image_path = "data_prod/Gantt projet.png" 
image = Image.open(image_path)

# Afficher l'image en grand
st.image(image, use_container_width=True)

# Titre de l'application
st.set_page_config(layout="wide")  # Utiliser toute la largeur
st.title("Héritage TMJA")

# Charger l'image
image_path = "data_prod/Héritage_TMJA_Dataiku.png" 
image = Image.open(image_path)

# Afficher l'image en grand
st.image(image, use_container_width=True)

# Titre de l'application
st.set_page_config(layout="wide")  # Utiliser toute la largeur
st.title("Héritage Voiture")

# Charger l'image
image_path = "data_prod/Héritage_voiture_Dataiku.png" 
image = Image.open(image_path)

# Afficher l'image en grand
st.image(image, use_container_width=True)
