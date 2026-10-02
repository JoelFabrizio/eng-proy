import streamlit as st
import requests
import os
import uuid  # 👈 Genera IDs únicos para cada sesión de chat (ej: chat_a1b2c3)
import base64
import re
import asyncio

import socket
import subprocess
import sys
import time

try:
    import edge_tts
    HAS_EDGE_TTS = True
except ImportError:
    HAS_EDGE_TTS = False

import io

def generar_audio_bytes(texto: str, language: str = "Español") -> bytes:
    """Genera un archivo MP3 en memoria (bytes) para Streamlit st.audio y st.download_button."""
    if not texto:
        return None
    try:
        texto_limpio = re.sub(r'\[NIVEL_FINAL:\s*[A-C][1-2]\]', '', texto, flags=re.IGNORECASE)
        patron_disc = r"^(Como|Aunque|Dado que|En esta)\s+.*?(interfaz|asistente|modelo|texto|sonido|audio).*?([:\n]|\.\s*)"
        texto_limpio = re.sub(patron_disc, "", texto_limpio, flags=re.IGNORECASE)
        texto_limpio = re.sub(r'[*#_`]', '', texto_limpio).strip()
        
        if not texto_limpio:
            return None

        from gtts import gTTS
        lang_code = "es" if language == "Español" else "en"
        fp = io.BytesIO()
        tts = gTTS(text=texto_limpio[:1000], lang=lang_code)
        tts.write_to_fp(fp)
        fp.seek(0)
        return fp.read()
    except Exception as e:
        print(f"⚠️ Error generando audio: {e}")
        return None


def asegurar_db_vectorial():
    """Descarga automáticamente la base vectorial desde Google Drive si no existe o está vacía en la nube."""
    db_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "db_vectorial")
    if not os.path.exists(db_dir) or not os.listdir(db_dir):
        print("⏳ Descargando base vectorial desde Google Drive...")
        try:
            import gdown
            folder_url = "https://drive.google.com/drive/folders/1zAqmuqyhpHtbZFwet3It-HF00oPXe2ok?usp=drive_link"
            gdown.download_folder(url=folder_url, output=db_dir, quiet=False, remaining_ok=True)
            print("✅ Base vectorial descargada con éxito.")
        except Exception as e:
            print(f"⚠️ Error al descargar la base vectorial de Google Drive: {e}")

# Asegurar que la base vectorial esté descargada antes de iniciar el backend
asegurar_db_vectorial()

# Sincronizar secretos de Streamlit Cloud con las variables de entorno del sistema
try:
    if hasattr(st, "secrets"):
        for key, val in st.secrets.items():
            if isinstance(val, str) and key not in os.environ:
                os.environ[key] = val
except Exception as e:
    pass

def iniciar_backend_si_no_existe():
    """Inicia el backend FastAPI en segundo plano en puerto 8000 si no está activo."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1)
            if s.connect_ex(("127.0.0.1", 8000)) == 0:
                return  # El backend ya está corriendo
    except Exception:
        pass

    try:
        env_vars = os.environ.copy()
        subprocess.Popen([
            sys.executable, "-m", "uvicorn", "main:app",
            "--host", "127.0.0.1", "--port", "8000"
        ], env=env_vars)
        time.sleep(3)
    except Exception as e:
        print(f"⚠️ Error intentando iniciar el backend: {e}")

# Asegurar backend iniciado
iniciar_backend_si_no_existe()

# 🌐 URLs de FastAPI
AUTH_API_URL = "http://127.0.0.1:8000/api/v1/auth"
CHAT_API_URL = "http://127.0.0.1:8000/api/v1/rag"

BACKEND_HOST = os.getenv("BACKEND_HOST", "http://127.0.0.1:8000")

# ---------------------------------------------------------
# 🌐 Diccionario de Traducciones Multilingüe para la UI (i18n)
# ---------------------------------------------------------
TEXTS = {
    "Español": {
        "app_title": "🎓 Asistente Académico RAG",
        "tab_login": "🔑 Iniciar Sesión",
        "tab_register": "📝 Registrarse",
        "login_sub": "Ingresa tus credenciales",
        "reg_sub": "Crear una nueva cuenta de usuario",
        "user_label": "Usuario",
        "pass_label": "Contraseña",
        "new_user_label": "Nuevo Usuario",
        "new_pass_label": "Nueva Contraseña",
        "btn_login": "Ingresar",
        "btn_register": "Crear cuenta",
        "select_role": "Selecciona tu rol",
        "role_student": "👨‍🎓 Alumno",
        "role_teacher": "👨‍🏫 Profesor",
        "mode_teacher": "👨‍🏫 **Modo Profesor**: Didáctica, Pedagogía y Planificación",
        "mode_student": "👨‍🎓 **Modo Alumno**: Aprendizaje y Práctica de Inglés",
        "level_none": "⚠️ **Nivel**: Sin evaluar",
        "level_prefix": "🎯 **Nivel de Inglés**:",
        "btn_test": "🎯 Hacer Test de Nivel",
        "btn_new_chat": "➕ Nuevo Chat",
        "history_caption": "📜 HISTORIAL DE CHATS",
        "no_chats": "*(Sin chats guardados aún)*",
        "btn_delete": "🗑️ Eliminar",
        "btn_logout": "🚪 Cerrar Sesión",
        "active_conv": "Conversación activa:",
        "input_placeholder": "Escribe tu consulta académica...",
        "spinner": "Procesando consulta en la base de datos...",
        "lang_selector": "🌐 Idioma de la Interfaz",
        "test_prompt": "Hola, me gustaría realizar mi Test de Diagnóstico de Nivel de Inglés. Por favor preséntame las preguntas iniciales para evaluarme.",
        "toast_level": "🎉 ¡Nivel asignado! Tu nuevo nivel es",
        "login_success": "¡Inicio de sesión exitoso!",
        "login_warn": "Por favor completa todos los campos.",
        "btn_gen_audio": "🔊 Generar Archivo de Audio (.mp3)",
        "btn_download_audio": "📥 Descargar Audio MP3",
        "audio_spinner": "Generando archivo de audio MP3..."
    },
    "English": {
        "app_title": "🎓 RAG Academic Assistant",
        "tab_login": "🔑 Log In",
        "tab_register": "📝 Register",
        "login_sub": "Enter your credentials",
        "reg_sub": "Create a new user account",
        "user_label": "Username",
        "pass_label": "Password",
        "new_user_label": "New Username",
        "new_pass_label": "New Password",
        "btn_login": "Log In",
        "btn_register": "Create Account",
        "select_role": "Select your role",
        "role_student": "👨‍🎓 Student",
        "role_teacher": "👨‍🏫 Teacher",
        "mode_teacher": "👨‍🏫 **Teacher Mode**: Didactics, Pedagogy & Lesson Planning",
        "mode_student": "👨‍🎓 **Student Mode**: English Learning & Practice",
        "level_none": "⚠️ **Level**: Not evaluated",
        "level_prefix": "🎯 **English Level**:",
        "btn_test": "🎯 Take Placement Test",
        "btn_new_chat": "➕ New Chat",
        "history_caption": "📜 CHAT HISTORY",
        "no_chats": "*(No saved chats yet)*",
        "btn_delete": "🗑️ Delete",
        "btn_logout": "🚪 Log Out",
        "active_conv": "Active conversation:",
        "input_placeholder": "Type your academic query...",
        "spinner": "Processing query in database...",
        "lang_selector": "🌐 Interface Language",
        "test_prompt": "Hello, I would like to take my English Placement Diagnostic Test. Please present the initial questions to evaluate me.",
        "toast_level": "🎉 Level assigned! Your new level is",
        "login_success": "Login successful!",
        "login_warn": "Please fill in all fields.",
        "btn_gen_audio": "🔊 Generate Audio File (.mp3)",
        "btn_download_audio": "📥 Download MP3 Audio",
        "audio_spinner": "Generating MP3 audio file..."
    }
}

def t(key: str) -> str:
    """Obtiene el texto traducido según el idioma seleccionado en session_state."""
    lang = st.session_state.get("language", "Español")
    return TEXTS.get(lang, TEXTS["Español"]).get(key, key)

# ---------------------------------------------------------
# 🔌 Funciones de Comunicación HTTP con FastAPI
# ---------------------------------------------------------

def login_usuario(username, password):
    """Envía las credenciales a FastAPI (OAuth2 / Login)."""
    payload = {"username": username, "password": password}
    try:
        response = requests.post(f"{AUTH_API_URL}/login", json=payload)
        if response.status_code == 200:
            try:
                return True, response.json()
            except Exception:
                return False, "Respuesta inválida del servidor."
        else:
            try:
                error_msg = response.json().get("detail", "Error de autenticación.")
            except Exception:
                error_msg = f"Error del servidor ({response.status_code})."
            return False, error_msg
    except requests.exceptions.ConnectionError:
        return False, "❌ No se pudo conectar con el servidor. ¿Está FastAPI encendido?"
    except Exception as e:
        return False, f"❌ Error inesperado: {str(e)}"

def registrar_usuario(username, password, role="alumno"):
    """Envía los datos al endpoint de Registro."""
    payload = {"username": username, "password": password, "role": role}
    try:
        response = requests.post(f"{AUTH_API_URL}/register", json=payload)
        if response.status_code in (200, 201):
            return True, f"¡Usuario ({role}) creado exitosamente! Ahora puedes iniciar sesión."
        else:
            try:
                error_msg = response.json().get("detail", "Error al registrar usuario.")
            except Exception:
                error_msg = f"Error del servidor ({response.status_code}). Verifique la conexión a la base de datos."
            return False, error_msg
    except requests.exceptions.ConnectionError:
        return False, "❌ No se pudo conectar con el servidor."
    except Exception as e:
        return False, f"❌ Error al registrar: {str(e)}"

def actualizar_nivel_ingles(token: str, level: str):
    """Actualiza el nivel de inglés del usuario en SQLite."""
    headers = {"Authorization": f"Bearer {token}"}
    try:
        res = requests.put(f"{AUTH_API_URL}/level", json={"level": level}, headers=headers)
        return res.status_code == 200
    except Exception:
        return False

def obtener_sesiones(token: str):
    """Obtiene la lista de diccionario sesiones {'id': ..., 'title': ...} guardadas."""
    headers = {"Authorization": f"Bearer {token}"}
    try:
        res = requests.get(f"{CHAT_API_URL}/sessions", headers=headers)
        if res.status_code == 200:
            return res.json().get("sessions", [])
    except Exception:
        pass
    return []

def cargar_historial_sesion(token: str, session_id: str):
    """Carga los mensajes anteriores almacenados en SQLite para una sesión específica."""
    headers = {"Authorization": f"Bearer {token}"}
    try:
        res = requests.get(f"{CHAT_API_URL}/history/{session_id}", headers=headers)
        if res.status_code == 200:
            return res.json().get("messages", [])
    except Exception:
        pass
    return []

def borrar_sesion_chat(token: str, session_id: str):
    """Elimina una sesión de chat específica de la base de datos SQLite."""
    headers = {"Authorization": f"Bearer {token}"}
    try:
        res = requests.delete(f"{CHAT_API_URL}/history/{session_id}", headers=headers)
        return res.status_code == 200
    except Exception:
        return False

def enviar_mensaje_chat(mensaje: str, session_id: str, token: str, language: str = "Español"):
    """Envía la consulta del usuario asociándola a la sesión activa y el idioma preferido."""
    payload = {"message": mensaje, "session_id": session_id, "language": language}
    headers = {"Authorization": f"Bearer {token}"}

    try:
        response = requests.post(f"{CHAT_API_URL}/chat", json=payload, headers=headers)
        if response.status_code == 200:
            try:
                return True, response.json().get("response", "Sin respuesta.")
            except Exception:
                return False, "Respuesta inválida del servidor."
        else:
            return False, f"Error {response.status_code}: No se pudo procesar la solicitud."
    except requests.exceptions.ConnectionError:
        return False, "❌ No se pudo conectar con el servidor."
    except Exception as e:
        return False, f"❌ Error: {str(e)}"

# ---------------------------------------------------------
# 💾 Manejo del Estado de la Sesión (st.session_state)
# ---------------------------------------------------------

if "token" not in st.session_state:
    st.session_state["token"] = None

if "role" not in st.session_state:
    st.session_state["role"] = "alumno"

if "english_level" not in st.session_state:
    st.session_state["english_level"] = "sin_evaluar"

if "active_session_id" not in st.session_state:
    st.session_state["active_session_id"] = f"chat_{uuid.uuid4().hex[:6]}"

if "messages" not in st.session_state:
    st.session_state["messages"] = []

if "language" not in st.session_state:
    st.session_state["language"] = "Español"

# ---------------------------------------------------------
# 🎨 Renderizado de la Interfaz Gráfica
# ---------------------------------------------------------

# Selector de Idioma en el Sidebar global
with st.sidebar:
    if os.path.exists("Varien.jpg"):
        with open("Varien.jpg", "rb") as f:
            img_b64 = base64.b64encode(f.read()).decode()
            
        st.markdown(
            f"""
            <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 10px;">
                <img src="data:image/jpeg;base64,{img_b64}" width="28" style="border-radius: 4px;">
                <h3 style="margin: 0; font-size: 22px; font-weight: 600;position:relative; top:3px">Varien</h3>
            </div>
            """,
            unsafe_allow_html=True
        )

    # 🌐 Selector de Idioma de Interfaz
    idiomas = ["Español", "English"]
    idx_id = 0 if st.session_state.get("language", "Español") == "Español" else 1
    sel_idioma = st.selectbox(t("lang_selector"), options=idiomas, index=idx_id)
    if sel_idioma != st.session_state["language"]:
        st.session_state["language"] = sel_idioma
        st.rerun()

# Pantalla de Autenticación (Login / Registro) 🔑
if st.session_state["token"] is None:
    st.title(t("app_title"))
    
    # Pestañas para alternar entre Login y Registro
    tab_login, tab_register = st.tabs([t("tab_login"), t("tab_register")])

    # 1. PESTAÑA DE LOGIN
    with tab_login:
        st.subheader(t("login_sub"))
        usuario = st.text_input(t("user_label"), key="login_user")
        clave = st.text_input(t("pass_label"), type="password", key="login_pass")
        
        if st.button(t("btn_login")):
            if usuario and clave:
                exito, resultado = login_usuario(usuario, clave)
                if exito:
                    st.session_state["token"] = resultado["access_token"]
                    st.session_state["role"] = resultado.get("role", "alumno")
                    st.session_state["english_level"] = resultado.get("english_level", "sin_evaluar")
                    st.session_state["active_session_id"] = f"chat_{uuid.uuid4().hex[:6]}"
                    st.session_state["messages"] = []
                    st.success(t("login_success"))
                    st.rerun()
                else:
                    st.error(f"Error: {resultado}")
            else:
                st.warning(t("login_warn"))

    # 2. PESTAÑA DE REGISTRO
    with tab_register:
        st.subheader(t("reg_sub"))
        nuevo_usuario = st.text_input(t("new_user_label"), key="reg_user")
        nueva_clave = st.text_input(t("new_pass_label"), type="password", key="reg_pass")
        
        # Rol
        rol_usuario = st.radio(
            t("select_role"),
            options=["alumno", "profesor"],
            format_func=lambda x: t("role_student") if x == "alumno" else t("role_teacher"),
            key="reg_role"
        )

        if st.button(t("btn_register")):
            if nuevo_usuario and nueva_clave:
                exito, mensaje = registrar_usuario(nuevo_usuario, nueva_clave, rol_usuario)
                if exito:
                    st.success(mensaje)
                else:
                    st.error(f"Error: {mensaje}")
            else:
                st.warning(t("login_warn"))

# Pantalla del Chat RAG 💬
else:
    with st.sidebar:
        rol_actual = st.session_state.get("role", "alumno")
        if rol_actual in ["profesor", "teacher"]:
            st.info(t("mode_teacher"))
        else:
            st.info(t("mode_student"))
            
            # 🎯 Insignia de Nivel de Inglés del Alumno
            nivel_actual = st.session_state.get("english_level", "sin_evaluar")
            if nivel_actual == "sin_evaluar" or not nivel_actual:
                st.warning(t("level_none"))
            else:
                st.success(f"{t('level_prefix')} {nivel_actual}")

            if st.button(t("btn_test"), use_container_width=True):
                nueva_sesion = f"chat_eval_{uuid.uuid4().hex[:6]}"
                st.session_state["active_session_id"] = nueva_sesion
                st.session_state["messages"] = []
                prompt_eval = t("test_prompt")
                st.session_state["messages"].append({"role": "user", "content": prompt_eval})
                exito, resp_eval = enviar_mensaje_chat(prompt_eval, nueva_sesion, st.session_state["token"], language=st.session_state["language"])
                if exito:
                    msg_eval = {"role": "assistant", "content": resp_eval}
                    if st.session_state.get("enable_tts", True):
                        audio_eval = generar_audio_tts(resp_eval)
                        if audio_eval:
                            msg_eval["audio_path"] = audio_eval
                    st.session_state["messages"].append(msg_eval)
                st.rerun()

        # 1. Buscamos solo las sesiones guardadas (que tienen al menos 1 respuesta del bot)
        lista_sesiones = obtener_sesiones(st.session_state["token"])

        # 2. Botón "Nuevo chat" para crear una nueva conversación
        if st.button(t("btn_new_chat"), use_container_width=True):
            nueva_sesion = f"chat_{uuid.uuid4().hex[:6]}"
            st.session_state["active_session_id"] = nueva_sesion
            st.session_state["messages"] = []
            st.rerun()

        # 3. Lista vertical de chats guardados
        st.divider()
        st.caption(t("history_caption"))

        if not lista_sesiones:
            st.caption(t("no_chats"))
        else:
            for sesion in lista_sesiones:
                s_id = sesion["id"]
                s_title = sesion["title"]
                es_activa = (s_id == st.session_state["active_session_id"])
                tipo_boton = "primary" if es_activa else "secondary"
                
                # Dividimos la fila: 85% para el título del chat, 15% para los 3 puntos (⋮)
                col_chat, col_menu = st.columns([0.85, 0.15], vertical_alignment="center")
                
                with col_chat:
                    if st.button(s_title, key=f"sess_{s_id}", type=tipo_boton, use_container_width=True):
                        if not es_activa:
                            st.session_state["active_session_id"] = s_id
                            st.session_state["messages"] = cargar_historial_sesion(st.session_state["token"], s_id)
                            st.rerun()
                
                with col_menu:
                    with st.popover("⋮"):
                        if st.button(t("btn_delete"), key=f"del_{s_id}", use_container_width=True):
                            borrar_sesion_chat(st.session_state["token"], s_id)
                            if es_activa:
                                st.session_state["active_session_id"] = f"chat_{uuid.uuid4().hex[:6]}"
                                st.session_state["messages"] = []
                            st.rerun()

        st.divider()
        if st.button(t("btn_logout"), use_container_width=True):
            st.session_state["token"] = None
            st.session_state["messages"] = []
            st.rerun()

    # 💬 Pantalla Principal del Chat
    st.title(t("app_title"))
    st.caption(f"{t('active_conv')} **{st.session_state['active_session_id']}**")

    # Renderizar el historial de mensajes de la sesión activa
    for idx, msg in enumerate(st.session_state["messages"]):
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
            if msg["role"] == "assistant":
                audio_bytes = msg.get("audio_bytes")
                
                # Si el usuario presiona el botón para generar el archivo de audio
                if not audio_bytes and st.button(t("btn_gen_audio"), key=f"btn_gen_{idx}"):
                    with st.spinner(t("audio_spinner")):
                        audio_bytes = generar_audio_bytes(msg["content"], language=st.session_state.get("language", "Español"))
                        if audio_bytes:
                            msg["audio_bytes"] = audio_bytes
                            st.rerun()

                # Si el audio ya existe, mostrar reproductor y botón de descarga
                if audio_bytes:
                    st.audio(audio_bytes, format="audio/mp3")
                    st.download_button(
                        label=t("btn_download_audio"),
                        data=audio_bytes,
                        file_name=f"audio_respuesta_{idx+1}.mp3",
                        mime="audio/mp3",
                        key=f"btn_dl_{idx}"
                    )

    # Caja de texto para enviar un mensaje
    if prompt := st.chat_input(t("input_placeholder")):
        # Guardar y mostrar el mensaje del usuario
        st.session_state["messages"].append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)

        # Consultar al backend asociándolo a la sesión activa
        with st.chat_message("assistant"):
            with st.spinner(t("spinner")):
                exito, respuesta = enviar_mensaje_chat(
                    prompt, 
                    st.session_state["active_session_id"], 
                    st.session_state["token"],
                    language=st.session_state.get("language", "Español")
                )
                
                # Filtrar cualquier disclaimer introductorio
                patron_disc = r"^(Como|Aunque|Dado que|En esta)\s+.*?(interfaz|asistente|modelo|texto|sonido|audio).*?([:\n]|\.\s*)"
                respuesta = re.sub(patron_disc, "", respuesta, flags=re.IGNORECASE).strip()
                respuesta = re.sub(r"^No puedo (generar|enviar|crear) (archivos de )?(audio|sonido|voz).*?([:\n]|\.\s*)", "", respuesta, flags=re.IGNORECASE).strip()
                
                st.write(respuesta)
                
                # Detectar si el usuario solicitó audio explícitamente en su consulta
                pide_audio_explicito = any(p in prompt.lower() for p in ["audio", "nota de voz", "escuchar", "voz", "hablada", "podcast", "speech"])

                audio_bytes = None
                if pide_audio_explicito:
                    audio_bytes = generar_audio_bytes(respuesta, language=st.session_state.get("language", "Español"))
                    if audio_bytes:
                        st.audio(audio_bytes, format="audio/mp3")

                # Detectar si la respuesta contiene la etiqueta final de evaluación [NIVEL_FINAL: XX]
                match = re.search(r"\[NIVEL_FINAL:\s*([A-C][1-2])\]", respuesta, re.IGNORECASE)
                if match:
                    nuevo_nivel = match.group(1).upper()
                    if actualizar_nivel_ingles(st.session_state["token"], nuevo_nivel):
                        st.session_state["english_level"] = nuevo_nivel
                        st.toast(f"{t('toast_level')} {nuevo_nivel}.", icon="🎯")

        # Guardar la respuesta del asistente y recargar para refrescar el historial del sidebar
        msg_data = {"role": "assistant", "content": respuesta}
        if audio_bytes:
            msg_data["audio_bytes"] = audio_bytes
        st.session_state["messages"].append(msg_data)
        st.rerun()
