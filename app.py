
import io
import os

import streamlit as st
from google import genai
from gtts import gTTS
from PIL import Image


# ----------------------------------------
# CONFIGURACION GENERAL
# ----------------------------------------

st.set_page_config(
    page_title="Asistente Visual por Voz",
    page_icon="🔊",
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    .stApp {
        background-color: #171717;
        color: #FFFFFF;
    }

    h1, h2, h3, p, label, span {
        color: #FFFFFF;
    }

    .stButton > button {
        width: 100%;
        min-height: 75px;
        font-size: 24px;
        font-weight: bold;
        background-color: #B91C1C;
        color: white;
        border: 3px solid white;
        border-radius: 12px;
    }

    .stButton > button:focus {
        outline: 4px solid #FFFF00;
        outline-offset: 3px;
    }

    .stFileUploader, [data-testid="stCameraInput"] {
        border: 2px solid white;
        border-radius: 10px;
        padding: 10px;
    }

    [data-testid="stAlert"] {
        font-size: 20px;
    }

    footer {
        visibility: hidden;
    }
</style>
""", unsafe_allow_html=True)


# ----------------------------------------
# FUNCION: ANALIZAR LA IMAGEN CON IA
# ----------------------------------------


import os
import io
from PIL import Image
from google import genai


def analizar_imagen(imagen_bytes):
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise RuntimeError(
            "Falta configurar GEMINI_API_KEY."
        )

    cliente = genai.Client(api_key=api_key)

    imagen = Image.open(
        io.BytesIO(imagen_bytes)
    ).convert("RGB")

    respuesta = cliente.models.generate_content(
        model="gemini-3.5-flash",
        contents=[
            """
            Eres un asistente visual para una persona ciega.
            Describe en español claro los objetos de la imagen.
            Explica qué objeto es y dónde está situado.
            Usa frases breves y naturales para leer en voz alta.
            No inventes detalles si no estás seguro.
            No afirmes que algo es seguro para tocar o consumir.
            """,
            imagen
        ]
    )

    return respuesta.text.strip()



# ----------------------------------------
# FUNCION: CONVERTIR TEXTO A VOZ
# ----------------------------------------

def convertir_a_voz(texto):
    """
    Genera audio en español a partir de un texto.
    """

    audio_buffer = io.BytesIO()

    tts = gTTS(
        text=texto,
        lang="es",
        slow=False
    )

    tts.write_to_fp(audio_buffer)
    audio_buffer.seek(0)

    return audio_buffer.getvalue()


# ----------------------------------------
# INTERFAZ PRINCIPAL
# ----------------------------------------

st.title("ASISTENTE VISUAL POR VOZ")

st.markdown("""
### Una ayuda para reconocer objetos

Toma una fotografía o carga una imagen.
La inteligencia artificial describirá lo que ve
y podrás escuchar la respuesta en español.

**Importante:** pulsa el botón de captura de la cámara
cuando hayas orientado el dispositivo hacia el objeto.
""")

st.divider()

st.subheader("OPCION 1: USAR LA CAMARA")

foto = st.camera_input(
    "Pulsa aquí para tomar una fotografía",
    key="camara"
)

st.subheader("OPCION 2: CARGAR UNA FOTOGRAFIA")

archivo = st.file_uploader(
    "Selecciona una fotografía",
    type=["jpg", "jpeg", "png", "webp"],
    help="Puedes utilizar una imagen de tu dispositivo."
)

imagen_seleccionada = archivo if archivo is not None else foto

if "descripcion" not in st.session_state:
    st.session_state.descripcion = ""

if "audio" not in st.session_state:
    st.session_state.audio = None


# ----------------------------------------
# BOTON DE ANALISIS
# ----------------------------------------

if st.button(
    "IDENTIFICAR OBJETO Y HABLAR",
    type="primary",
    use_container_width=True
):
    if imagen_seleccionada is None:
        st.warning(
            "Primero debes tomar una fotografía "
            "o seleccionar una imagen."
        )
        st.session_state.descripcion = ""
        st.session_state.audio = None

    else:
        try:
            with st.spinner(
                "Estoy analizando la imagen. Espera un momento."
            ):
                imagen_bytes = imagen_seleccionada.getvalue()

                descripcion = analizar_imagen(imagen_bytes)

                audio = convertir_a_voz(descripcion)

                st.session_state.descripcion = descripcion
                st.session_state.audio = audio

        except Exception as error:
            st.session_state.descripcion = ""
            st.session_state.audio = None

            st.error(
                "No pude completar el análisis. "
                "Comprueba tu conexión a internet, "
                "la configuración de la API y los créditos "
                "disponibles. Detalle: "
                + str(error)
            )


# ----------------------------------------
# MOSTRAR Y REPRODUCIR EL RESULTADO
# ----------------------------------------

if st.session_state.descripcion:
    st.divider()

    st.header("RESULTADO")

    st.markdown(
        st.session_state.descripcion
    )

    if st.session_state.audio:
        st.audio(
            st.session_state.audio,
            format="audio/mp3",
            autoplay=True
        )

        st.caption(
            "Si el audio no comienza automáticamente, "
            "pulsa el reproductor para escucharlo."
        )

    if st.button(
        "VOLVER A ESCUCHAR",
        use_container_width=True
    ):
        if st.session_state.audio:
            st.audio(
                st.session_state.audio,
                format="audio/mp3"
            )

st.divider()

st.caption(
    "Asistente experimental de accesibilidad. "
    "Puede equivocarse al identificar objetos. "
    "No lo utilices como único medio para evitar peligros."
)
