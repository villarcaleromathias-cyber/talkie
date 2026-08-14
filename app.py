import streamlit as st
from openai import OpenAI
import os
import json
import tempfile
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
import io

# --- 1. CONFIGURACIÓN DE LA API (Grok / xAI) ---
# La clave se leerá desde las variables de entorno de Render
XAI_API_KEY = os.environ.get("XAI_API_KEY")
cliente = OpenAI(
    api_key=XAI_API_KEY,
    base_url="https://api.xai.com/v1",
)

# --- 2. CONFIGURACIÓN DE GOOGLE DRIVE ---
SCOPES = ['https://www.googleapis.com/auth/drive.file']

def obtener_servicio_drive():
    creds_json = os.environ.get("DRIVE_CREDENTIALS")
    if creds_json:
        try:
            creds_dict = json.loads(creds_json)
            creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
            return build('drive', 'v3', credentials=creds)
        except Exception as e:
            st.error(f"Error al leer credenciales de Drive: {e}")
    return None

def guardar_memoria(servicio_drive, file_id, historial):
    try:
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as temp:
            json.dump(historial, temp)
            temp_path = temp.name
            
        media = MediaFileUpload(temp_path, mimetype='application/json', resumable=True)
        servicio_drive.files().update(fileId=file_id, media_body=media).execute()
        os.remove(temp_path)
    except Exception as e:
        st.error(f"Error guardando memoria en Drive: {e}")

# --- 3. INTERFAZ DE STREAMLIT (Estilo Talkie) ---
st.title("🎭 Chat con Personajes")

# Personalidad del personaje (Prompt del sistema)
# Aquí defines cómo actúa el personaje
PERSONALIDAD = "Eres un guerrero medieval gruñón pero leal. Respondes de forma ruda pero siempre intentas proteger al usuario."

if "mensajes" not in st.session_state:
    st.session_state.mensajes = [
        {"role": "system", "content": PERSONALIDAD}
    ]

# Mostrar historial en pantalla (ocultando las instrucciones del sistema)
for msg in st.session_state.mensajes:
    if msg["role"] != "system":
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

# Capturar nuevo mensaje del usuario
if prompt := st.chat_input("Escribe tu mensaje..."):
    st.session_state.mensajes.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generar respuesta de Grok
    with st.chat_message("assistant"):
        try:
            respuesta = cliente.chat.completions.create(
                model="grok-beta", 
                messages=st.session_state.mensajes
            )
            mensaje_ia = respuesta.choices[0].message.content
            st.markdown(mensaje_ia)
            
            st.session_state.mensajes.append({"role": "assistant", "content": mensaje_ia})
            
            # (Opcional) Aquí llamas a la función para guardar en Drive si tienes el ID del archivo
            # servicio = obtener_servicio_drive()
            # si servicio:
            #     guardar_memoria(servicio, "AQUI_PONES_EL_ID_DEL_ARCHIVO", st.session_state.mensajes)
            
        except Exception as e:
            st.error(f"Error comunicándose con la API: {e}")
