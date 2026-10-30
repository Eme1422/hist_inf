import os
import streamlit as st
import base64
from openai import OpenAI
import openai
from PIL import Image
import numpy as np
import pandas as pd
from streamlit_drawable_canvas import st_canvas

# Configuración de la página
st.set_page_config(
    page_title='Cuentacuentos Mágico con IA 📖✨',
    page_icon='📚',
    layout='centered',
    initial_sidebar_state='expanded'
)

# Estilos CSS personalizados con paleta de tonos morados / infantiles elegantes
st.markdown("""
    <style>
    .stApp {
        background-color: #F8F5FC;
        color: #2D2342;
    }
    h1, h2, h3 {
        color: #512DA8 !important;
        font-family: 'Inter', sans-serif;
    }
    [data-testid="stSidebar"] {
        background-color: #2D2342;
        color: #FFFFFF;
    }
    [data-testid="stSidebar"] h3, [data-testid="stSidebar"] span, [data-testid="stSidebar"] p, [data-testid="stSidebar"] label {
        color: #E2DFEC !important;
    }
    .stTextInput input {
        background-color: #FFFFFF !important;
        color: #2D2342 !important;
        border: 1px solid #D1C4E9 !important;
        border-radius: 8px !important;
    }
    .stButton button {
        background-color: #7B1FA2 !important;
        color: #FFFFFF !important;
        border-radius: 8px !important;
        border: none !important;
        font-weight: 600 !important;
        transition: background-color 0.3s ease;
    }
    .stButton button:hover {
        background-color: #6A1B9A !important;
    }
    .response-box {
        background-color: #FFFFFF;
        padding: 20px;
        border-radius: 12px;
        border-left: 6px solid #7B1FA2;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        margin-top: 15px;
        margin-bottom: 15px;
    }
    .story-box {
        background-color: #FFF8E1;
        padding: 25px;
        border-radius: 12px;
        border-left: 6px solid #FFA000;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        margin-top: 15px;
    }
    </style>
""", unsafe_allow_html=True)

# Inicializar session_state
if 'analysis_done' not in st.session_state:
    st.session_state.analysis_done = False
if 'full_response' not in st.session_state:
    st.session_state.full_response = ""

def encode_image_to_base64(image_path):
    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")
    except FileNotFoundError:
        return "Error: La imagen no se encontró."

# Panel Lateral de Configuración
with st.sidebar:
    st.subheader("📚 Magia Educativa")
    st.markdown("¡Convierte tus dibujos en el personaje principal de una aventura literaria mágica gracias a la Inteligencia Artificial!")
    
    st.markdown("---")
    st.subheader("⚙️ Opciones del Cuento")
    
    # Propiedades del tablero configurables
    stroke_width = st.slider('Grosor del Pincel', 1, 30, 6)
    stroke_color = st.color_picker('Color del Pincel', '#000000')
    bg_color = st.color_picker('Color de Fondo', '#FFFFFF')
    
    # Opciones de la historia
    story_genre = st.selectbox(
        "Género de la historia",
        ["Aventura", "Fantasía y Magia", "Fábula con Moraleja", "Espacial / Ciencia Ficción"]
    )
    target_age = st.selectbox("Edad del lector", ["3 a 5 años", "6 a 8 años", "9 a 12 años"])

# Título Principal
st.title("📖 Cuentacuentos Mágico: Dibuja y Crea")
st.markdown("#### *Haz un boceto de un personaje u objeto, y deja que la IA cree un cuento único basado en él.*")
st.markdown("---")

# Lienzo interactivo
st.subheader("🎨 Lienzo de Dibujo")
canvas_result = st_canvas(
    fill_color="rgba(123, 31, 162, 0.3)",
    stroke_width=stroke_width,
    stroke_color=stroke_color,
    background_color=bg_color,
    height=280,
    width=400,
    drawing_mode="freedraw",
    key="canvas",
)

st.markdown("---")

# Configuración de OpenAI
st.subheader("🔑 Credenciales de Acceso")
ke = st.text_input('Ingresa tu Clave de OpenAI', type="password", help="Tu clave se mantiene segura durante la sesión.")
if ke:
    os.environ['OPENAI_API_KEY'] = ke

api_key = os.environ.get('OPENAI_API_KEY', '')
client = OpenAI(api_key=api_key) if api_key else None

analyze_button = st.button("✨ Interpretar Dibujo y Crear Cuento", type="secondary")

# Lógica principal cuando se presiona el botón
if canvas_result.image_data is not None and api_key and analyze_button:
    if np.max(canvas_result.image_data) == 0 and bg_color == '#000000':
        st.warning("⚠️ Por favor, dibuja algo en el lienzo antes de continuar.", icon="⚠️")
    else:
        with st.spinner("🔮 Analizando tu dibujo y tejiendo la historia..."):
            # Procesar y guardar imagen temporal
            input_numpy_array = np.array(canvas_result.image_data)
            input_image = Image.fromarray(input_numpy_array.astype('uint8')).convert('RGBA')
            input_image.save('img.png')
            
            base64_image = encode_image_to_base64("img.png")
            prompt_text = "Describe in spanish briefly what is drawn in this image, identifying clearly the main character or object."
            
            try:
                # 1. Analizar la imagen con OpenAI
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": prompt_text},
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:image/png;base64,{base64_image}"
                                    },
                                },
                            ],
                        }
                    ],
                    max_tokens=300,
                )
                
                full_response = response.choices[0].message.content
                st.session_state.full_response = full_response
                st.session_state.analysis_done = True
                
                # Mostrar interpretación del dibujo
                st.markdown("### 🔍 Interpretación de la IA:")
                st.markdown(f'<div class="response-box"><b>Esto es lo que vio la máquina en tu dibujo:</b><br>{full_response}</div>', unsafe_allow_html=True)
                
                # 2. Generar automáticamente la historia infantil contextualizada
                with st.spinner("✍️ Escribiendo el cuento mágico..."):
                    story_prompt = (
                        f"Basándote en este elemento dibujado: '{full_response}', escribe un cuento infantil original y entretenido. "
                        f"El género debe ser '{story_genre}' dirigido a niños de '{target_age}'. "
                        f"Usa un tono tierno, alegre, con párrafos cortos y un vocabulario adecuado. Incluye un título llamativo."
                    )
                    
                    story_response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[{"role": "user", "content": story_prompt}],
                        max_tokens=600,
                    )
                    
                    story_content = story_response.choices[0].message.content
                    
                    st.markdown("### 📚 Cuento Mágico Creado:")
                    st.markdown(f'<div class="story-box">{story_content}</div>', unsafe_allow_html=True)

            except Exception as e:
                st.error(f"Ocurrió un error al procesar la solicitud: {e}")

else:
    if analyze_button:
        if not api_key:
            st.warning("🔒 Por favor ingresa tu Clave de OpenAI.", icon="⚠️")
        elif not canvas_result.image_data is not None:
            st.warning("⚠️ Dibuja algo en el tablero primero.", icon="⚠️")
