import streamlit as st
from openai import OpenAI
import os
import json

# Configuración de la página de Streamlit
st.set_page_config(page_title="Talkie Chatbot", page_icon="🤖")

st.title("🎭 Chat con Personajes (Grok)")

# --- VERIFICACIÓN DE SEGURIDAD PARA QUE NO SE CAIGA EL SERVIDOR ---
api_key = os.environ.get("XAI_API_KEY")

if not api_key:
    st.error("⚠️ Falta configurar la variable de entorno `XAI_API_KEY` en el panel de Render.")
    st.info("Por favor, ve a tu panel de Render -> Environment y añade tu clave API de xAI.")
    st.stop() # Detiene la ejecución amablemente sin crashear el servidor

# Inicializar cliente de manera segura
try:
    cliente = OpenAI(
        api_key=api_key,
        base_url="https://api.xai.com/v1",
    )
except Exception as e:
    st.error(f"Error al inicializar el cliente de IA: {e}")
    st.stop()

# Personalidad del personaje
PERSONALIDAD = "Eres un guerrero medieval gruñón pero leal. Respondes de forma ruda pero siempre intentas proteger al usuario."

if "mensajes" not in st.session_state:
    st.session_state.mensajes = [
        {"role": "system", "content": PERSONALIDAD}
    ]

# Mostrar historial en pantalla
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
        except Exception as e:
            st.error(f"Error comunicándose con la API de Grok: {e}")
