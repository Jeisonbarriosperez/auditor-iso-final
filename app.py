import streamlit as st
from groq import Groq
import docx
from pypdf import PdfReader

# Configuración de la página
st.set_page_config(page_title="Chat Auditor IA - ISO 42001", layout="centered")

st.title("Sistema de Auditoría con Chat Inteligente")
st.subheader("Análisis Continuo de Contratos (TXT, Word, PDF)")

# Barra lateral para la API Key
st.sidebar.header("Configuración")
api_key = st.sidebar.text_input(
    "Introduce tu Groq API Key:", 
    type="password", 
    help="Consigue tu llave gratuita en console.groq.com"
)

st.markdown("""
Este software corporativo avanzado permite auditar contratos y documentos 
legales en formatos **TXT, Word (.docx) y PDF** utilizando una API privada
en la nube. Toda la extracción de texto se realiza de forma local en el servidor de la aplicación, 
garantizando la gobernanza y privacidad de datos exigida por la norma **ISO 42001**.
""")

# INICIALIZAR LA MEMORIA (Session State)
# Si es la primera vez que carga la página, creamos la lista de mensajes vacía
if "messages" not in st.session_state:
    st.session_state.messages = []

# Botón para borrar el historial y empezar de nuevo
if st.sidebar.button("Borrar historial de chat"):
    st.session_state.messages = []
    st.rerun()

# Componente para subir archivos
uploaded_file = st.file_uploader(
    "Sube el contrato o documento (.txt, .docx, .pdf)", 
    type=["txt", "docx", "pdf"]
)

document_text = ""

if uploaded_file is not None:
    try:
        # Extracción de texto según formato
        if uploaded_file.name.endswith('.txt'):
            document_text = uploaded_file.read().decode("utf-8")
        elif uploaded_file.name.endswith('.docx'):
            doc = docx.Document(uploaded_file)
            fullText = [para.text for para in doc.paragraphs]
            document_text = '\n'.join(fullText)
        elif uploaded_file.name.endswith('.pdf'):
            pdf_reader = PdfReader(uploaded_file)
            fullText = [page.extract_text() for page in pdf_reader.pages if page.extract_text()]
            document_text = '\n'.join(fullText)

        if document_text.strip() == "":
            st.error("No se pudo extraer texto del archivo.")
        else:
            st.success(f"Documento '{uploaded_file.name}' indexado en la memoria de la sesión.")
            
            # MENTENER VISIBLE EL HISTORIAL DE CHAT
            # Dibujamos en pantalla todos los mensajes que ya se han enviado/recibido
            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

            # CAJA DE CHAT (Estilo ChatGPT abajo de la pantalla)
            if user_question := st.chat_input("Escribe aquí tu pregunta sobre el documento..."):
                
                if not api_key:
                    st.warning("Por favor, introduce tu Groq API Key en la barra lateral.")
                else:
                    # 1. Mostrar la pregunta del usuario en la pantalla inmediatamente
                    with st.chat_message("user"):
                        st.markdown(user_question)
                    
                    # 2. Guardar la pregunta en la "libreta de notas" (memoria)
                    st.session_state.messages.append({"role": "user", "content": user_question})
                    
                    # 3. Preparar el envío a la IA
                    with st.chat_message("assistant"):
                        with st.spinner("Pensando..."):
                            try:
                                client = Groq(api_key=api_key)
                                
                                # Definimos las reglas estrictas del auditor
                                system_prompt = (
                                    "Eres un auditor legal experto bajo la norma ISO 42001. "
                                    f"Analiza el siguiente DOCUMENTO principal:\n\n{document_text}\n\n"
                                    "Instrucciones: Responde las preguntas del usuario basándote estrictamente en el documento. "
                                    "Como estás en un chat continuo, toma en cuenta el historial de la conversación si el usuario "
                                    "te pide aclaraciones o resúmenes de respuestas anteriores. Si algo no está, di que no está y no inventes."
                                )
                                
                                # Creamos el paquete de mensajes: Reglas + Todo el Historial guardado
                                api_messages = [{"role": "system", "content": system_prompt}]
                                for msg in st.session_state.messages:
                                    api_messages.append({"role": msg["role"], "content": msg["content"]})
                                
                                # Llamada a Groq usando el nuevo modelo de Meta
                                completion = client.chat.completions.create(
                                    model="llama-3.3-70b-versatile",
                                    messages=api_messages,
                                    temperature=0.2,
                                )
                                
                                response_text = completion.choices[0].message.content
                                
                                # 4. Mostrar la respuesta de la IA en pantalla
                                st.markdown(response_text)
                                
                                # 5. Guardar la respuesta de la IA en la "libreta" para la siguiente pregunta
                                st.session_state.messages.append({"role": "assistant", "content": response_text})
                                
                            except Exception as e:
                                st.error(f"Error con el servidor de IA: {e}")
                                
    except Exception as e:
        st.error(f"Error al procesar el archivo: {e}")