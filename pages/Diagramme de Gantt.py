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
