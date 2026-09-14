import os
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage

from app.providers.factory import get_provider
from app.core.logging import logger
from app.db.database import SessionLocal
from app.db.models import ChatMessage, User
from config import settings


class SQLChatMessageHistory(BaseChatMessageHistory):
    """Clase personalizada para manejar el historial de chat de LangChain en la BD SQLite/SQLAlchemy."""
    
    def __init__(self, user_id: int, session_id: str = "default"):
        self.user_id = user_id
        self.session_id = session_id

    @property
    def messages(self) -> list[BaseMessage]:
        """Obtiene las conversaciones filtradas estrictamente por user_id desde SQL."""
        db = SessionLocal()
        try:
            records = (
                db.query(ChatMessage)
                .filter(ChatMessage.user_id == self.user_id,
                ChatMessage.session_id == self.session_id
                )
                .order_by(ChatMessage.id.asc())
                .all()
            )
            
            chat_messages = []
            for record in records:
                if record.role == "user":
                    chat_messages.append(HumanMessage(content=record.content))
                elif record.role == "assistant":
                    chat_messages.append(AIMessage(content=record.content))
            return chat_messages
        finally:
            db.close()

    def add_message(self, message: BaseMessage) -> None:
        """Guarda un nuevo mensaje en la tabla chat_messages asignando el user_id correspondiente."""
        db = SessionLocal()
        try:
            role = "user" if isinstance(message, HumanMessage) else "assistant"
            new_record = ChatMessage(
                user_id=self.user_id,
                session_id=self.session_id,
                role=role,
                content=message.content
            )
            db.add(new_record)
            db.commit()
        finally:
            db.close()

    def clear(self) -> None:
        """Borra el historial de un usuario específico de la base de datos."""
        db = SessionLocal()
        try:
            db.query(ChatMessage).filter(ChatMessage.user_id == self.user_id,
            ChatMessage.session_id == self.session_id
            ).delete()
            db.commit()
        finally:
            db.close()


class RAGService:
    def __init__(self):
        logger.info("Initializing RAG Service...")
        
        # 1. Obtenemos el proveedor mediante la fábrica (Factory)
        self.provider = get_provider()
        self.llm = self.provider.get_llm()
        
        # Cargar el mismo modelo de embeddings utilizado para crear la base de datos (BAAI/bge-small-en-v1.5)
        try:
            try:
                from langchain_huggingface import HuggingFaceEmbeddings
            except ImportError:
                from langchain_community.embeddings import HuggingFaceEmbeddings
            
            self.embeddings = HuggingFaceEmbeddings(
                model_name="BAAI/bge-small-en-v1.5",
                encode_kwargs={"normalize_embeddings": True}
            )
            logger.info("⚡ RAGService usando Hugging Face Embeddings ('BAAI/bge-small-en-v1.5').")
        except Exception as e:
            logger.warning(f"⚠️ Fallback a proveedor de embeddings ({e}).")
            self.embeddings = self.provider.get_embeddings()

        # 2. Conexión a las bases vectoriales ChromaDB en subcarpetas de db_vectorial/
        self.vector_dbs = {}
        if os.path.exists(settings.CHROMA_DIR):
            for item in os.listdir(settings.CHROMA_DIR):
                cat_path = os.path.join(settings.CHROMA_DIR, item)
                if os.path.isdir(cat_path):
                    try:
                        col_name = item.lower()
                        self.vector_dbs[col_name] = Chroma(
                            persist_directory=cat_path,
                            embedding_function=self.embeddings,
                            collection_name=col_name
                        )
                        logger.info(f"📚 Base vectorial cargada para categoría: '{col_name}'")
                    except Exception as e:
                        logger.warning(f"⚠️ No se pudo cargar colección '{item}': {e}")

        # Fallback si no hay subcarpetas o para búsqueda global directa
        self.db = Chroma(
            persist_directory=settings.CHROMA_DIR, 
            embedding_function=self.embeddings
        )

        # 3. Prompts diferenciados por Rol con control estricto de Idioma
        prompt_alumno_str = (
            "Eres un Tutor Académico de Inglés amigable, claro y directo.\n"
            "Tu objetivo principal es ayudar a los ALUMNOS a aprender, practicar y comprender el idioma inglés.\n\n"
            "🌐 REGLA ESTRICTA DE IDIOMA:\n"
            "1. DEBES responder OBLIGATORIAMENTE en el idioma indicado: {language}.\n"
            "2. Si la preferencia es 'Español' o el usuario escribe en español, DEBES redactar tus explicaciones, saludos y comentarios EN ESPAÑOL (manteniendo solo los ejemplos o términos gramaticales en inglés si es necesario para la enseñanza).\n"
            "3. NUNCA respondas todo el mensaje enteramente en inglés a menos que el nivel sea C1/C2 o el idioma indicado sea 'English'.\n\n"
            "🎯 NIVEL DE INGLÉS REGISTRADO DEL ALUMNO: {english_level}\n\n"
            "⚠️ REGLAS ADAPTATIVAS SEGÚN EL NIVEL:\n"
            "- Si el nivel es A1 o A2 (Principiante): Explicaciones claras en español, oraciones sencillas en inglés y vocabulario básico.\n"
            "- Si el nivel es B1 o B2 (Intermedio): Explicaciones bilingües/español fluido, ejercicios de gramática intermedia y vocabulario cotidiano.\n"
            "- Si el nivel es C1 o C2 (Avanzado): Inmersión total en inglés.\n"
            "- Si el nivel es SIN_EVALUAR: Responde con tono amigable en español e invita al alumno a realizar su Test de Nivel.\n\n"
            "📝 MODO TEST DE DIAGNÓSTICO DE NIVEL:\n"
            "- Si el alumno solicita realizar o está en su Test de Nivel, preséntale o evalúa preguntas progresivas adaptativas.\n"
            "- Al finalizar el test y concluir la evaluación, DEBES INCLUIR OBLIGATORIAMENTE al final de tu mensaje la etiqueta exacta en su propia línea:\n"
            "  [NIVEL_FINAL: A1] o [NIVEL_FINAL: A2] o [NIVEL_FINAL: B1] o [NIVEL_FINAL: B2] o [NIVEL_FINAL: C1]\n\n"
            "⚠️ REGLAS EXCLUSIVAS PARA ALUMNOS:\n"
            "1. Responde de forma clara y directa para facilitar el APRENDIZAJE del inglés.\n"
            "2. Si en el contexto encuentras notas metodológicas, guías docentes o planes de clase, IGNÓRALOS por completo.\n"
            "3. PROHIBIDO mostrar o recomendar guías de enseñanza para profesores.\n"
            "4. PROHIBIDO decir frases como 'revisa los archivos' o 'según el material'. Responde directamente como tutor experto.\n"
            "5. Si el contexto no contiene datos suficientes para la duda de aprendizaje, di explícitamente: 'No dispongo de datos suficientes en el material de estudio para responder a esa consulta.'\n\n"
            "Contexto de estudio disponible:\n"
            "{context}"
        )

        prompt_profesor_str = (
            "Eres un Asistente y Mentor Académico en Pedagogía y Didáctica del Inglés (ELT Consultant).\n"
            "Tu objetivo principal es ayudar a los PROFESORES a enseñar inglés, planificar clases, diseñar metodologías y gestionar el aula.\n\n"
            "🌐 REGLA ESTRICTA DE IDIOMA:\n"
            "1. DEBES responder OBLIGATORIAMENTE en el idioma indicado: {language}.\n"
            "2. Si el idioma es 'Español' o el usuario pregunta en español, redacta la respuesta pedagógica en español.\n\n"
            "⚠️ REGLAS EXCLUSIVAS PARA PROFESORES:\n"
            "1. Responde con un enfoque pedagógico y didáctico orientado a la ENSEÑANZA de inglés.\n"
            "2. Brinda estrategias de enseñanza, dinámicas de clase y explicaciones metodológicas.\n"
            "3. PROHIBIDO decir frases como 'revisa los archivos' o 'según el material'. Responde directamente como consultor experto.\n"
            "4. Si el contexto no contiene datos pedagógicos suficientes, di explícitamente: 'No dispongo de datos suficientes en la base pedagógica para responder a esa consulta.'\n\n"
            "Contexto pedagógico disponible:\n"
            "{context}"
        )

        prompt_alumno = ChatPromptTemplate.from_messages([
            ("system", prompt_alumno_str),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
        ])

        prompt_profesor = ChatPromptTemplate.from_messages([
            ("system", prompt_profesor_str),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
        ])

        # 4. Cadenas LCEL independientes
        rag_chain_alumno = (
            RunnablePassthrough.assign(
                context=lambda x: x["context"],
                english_level=lambda x: x.get("english_level", "SIN_EVALUAR"),
                language=lambda x: x.get("language", "Español")
            )
            | prompt_alumno
            | self.llm
            | StrOutputParser()
        )

        rag_chain_profesor = (
            RunnablePassthrough.assign(
                context=lambda x: x["context"],
                language=lambda x: x.get("language", "Español")
            )
            | prompt_profesor
            | self.llm
            | StrOutputParser()
        )

        # 5. Configuración de Memoria Persistente con RunnableWithMessageHistory
        self.conversational_chain_alumno = RunnableWithMessageHistory(
            rag_chain_alumno,
            self._get_session_history,
            input_messages_key="input",
            history_messages_key="chat_history",
        )

        self.conversational_chain_profesor = RunnableWithMessageHistory(
            rag_chain_profesor,
            self._get_session_history,
            input_messages_key="input",
            history_messages_key="chat_history",
        )
        logger.info("RAG Service initialized successfully with Dual Prompts and SQL Chat History.")

    def _get_user_info(self, user_id: int) -> tuple[str, str]:
        """ Consulta el rol y el nivel de inglés del usuario en SQLite """
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.id == user_id).first()
            role = user.role.lower() if user and user.role else "alumno"
            level = getattr(user, "english_level", "sin_evaluar") or "sin_evaluar"
            return role, level.upper()
        finally: 
            db.close()

    def _get_user_role(self, user_id: int) -> str:
        """ Consulta el rol del usuario ('alumno' o 'profesor') en SQLite """
        role, _ = self._get_user_info(user_id)
        return role

    def _retrieve_context_for_user(self, query: str, user_id: int) -> str:
        """Recupera los mejores chunks de ChromaDB respetando el rol del usuario."""
        role = self._get_user_role(user_id)
        logger.info(f"🔎 Filtrando contexto RAG para User ID {user_id} con Rol: '{role}'")

        PALABRAS_DOCENTES = ["pedagogia", "metodologia", "lesson_plan", "docente", "teaching", "profesor", "didactica", "ensenar"]
        all_docs = []

        if role in ["profesor", "admin", "teacher"]:
            # El profesor tiene acceso a TODAS las bases vectoriales
            if self.vector_dbs:
                for cat, vdb in self.vector_dbs.items():
                    docs = vdb.similarity_search(query, k=3)
                    all_docs.extend(docs)
            else:
                all_docs = self.db.similarity_search(query, k=6)
        else:
            # El alumno solo accede a carpetas de estudiante (excluyendo pedagogía)
            if self.vector_dbs:
                for cat, vdb in self.vector_dbs.items():
                    if cat in ["pedagogia", "pedagogía", "docente", "profesores"]:
                        continue
                    docs = vdb.similarity_search(query, k=3)
                    
                    # Filtro de seguridad adicional para la categoría 'otros' por si contiene material mixto
                    if cat == "otros":
                        filtered_docs = []
                        for d in docs:
                            src_lower = d.metadata.get("source", "").lower()
                            sub_lower = d.metadata.get("subfolder", "").lower()
                            txt_lower = d.page_content[:250].lower()
                            es_docente = any(p in src_lower or p in sub_lower or p in txt_lower for p in PALABRAS_DOCENTES)
                            if not es_docente:
                                filtered_docs.append(d)
                        all_docs.extend(filtered_docs)
                    else:
                        all_docs.extend(docs)
            else:
                # Fallback con filtro de metadatos si solo hay un ChromaDB global
                try:
                    filter_condition = {"category": {"$nin": ["pedagogia", "metodologia_docente"]}}
                    all_docs = self.db.similarity_search(query, k=6, filter=filter_condition)
                except Exception:
                    all_docs = self.db.similarity_search(query, k=10)
                    all_docs = [d for d in all_docs if d.metadata.get("category", "").lower() not in ["pedagogia", "metodologia_docente"]][:6]

        return self._format_docs(all_docs[:6])

    def _format_docs(self, docs):
        """Formatea los documentos recuperados para el contexto."""
        return "\n\n".join(doc.page_content for doc in docs)

    def _get_session_history(self, session_id: str) -> BaseChatMessageHistory:
        """Obtiene la instancia de historial vinculada al usuario y sesión (formato 'user_id:session_id')."""
        if ":" in session_id:
            user_str, sess_str = session_id.split(":",1)
            return SQLChatMessageHistory(user_id=int(user_str), session_id = sess_str)
        return SQLChatMessageHistory(user_id=int(session_id), session_id="default")

    def ask(self, query: str, user_id: int, session_id = "default", language: str = "Español") -> str:
        """Envía la consulta del usuario asociándola a su user_id, session_id y preferencia de idioma."""
        role, english_level = self._get_user_info(user_id)
        logger.info(f"Processing query for User ID '{user_id}' (Role: '{role}', Level: '{english_level}', Lang: '{language}'), Session '{session_id}': {query}")
        
        # Obtener contexto filtrado según el ROL del usuario
        context_str = self._retrieve_context_for_user(query, user_id)

        # Seleccionar la cadena conversacional adecuada para el ROL
        composite_key = f"{user_id}:{session_id}"
        target_chain = self.conversational_chain_profesor if role in ["profesor", "admin", "teacher"] else self.conversational_chain_alumno

        response = target_chain.invoke(
            {"input": query, "context": context_str, "english_level": english_level, "language": language},
            config={"configurable": {"session_id": composite_key}}
        )
        return response