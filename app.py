import streamlit as st
from groq import Groq
import docx
from pypdf import PdfReader

st.set_page_config(page_title="Auditor IA Multiformato - ISO 42001", page_icon="🛡️", layout="centered")

st.title("🛡️ Sistema de Auditoría de Documentos Inteligente")
st.subheader("Auditoría de Contratos en TXT, Word y PDF (ISO 42001)")

st.sidebar.header("⚙️ Configuración del Sistema")
api_key = st.sidebar.text_input(
    "Introduce tu Groq API Key:", 
    type="password", 
    help="Consigue tu llave gratuita en console.groq.com"
)

st.markdown("""
Este software corporativo avanzado permite auditar contratos y documentos legales en formatos **TXT, Word (.docx) y PDF** utilizando una API privada en la nube. Toda la extracción de texto se realiza de forma local en el servidor de la aplicación, 
garantizando la gobernanza y privacidad de datos exigida por la norma **ISO 42001**.
""")

uploaded_file = st.file_uploader(
    "📂 Sube el contrato o documento (.txt, .docx, .pdf)", 
    type=["txt", "docx", "pdf"]
)

document_text = ""

if uploaded_file is not None:
    try:
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
            st.error("⚠️ No se pudo extraer texto del archivo. Asegúrate de que no esté protegido o vacío.")
        else:
            st.success(f"✅ Documento '{uploaded_file.name}' cargado y procesado con éxito.")
            
            with st.expander("👀 Ver texto extraído por el sistema"):
                st.text(document_text)
                
            st.write("### 🤖 Acciones de Auditoría Disponibles")
            
            option = st.selectbox(
                "Selecciona un protocolo de análisis automatizado:",
                [
                    "Seleccionar...",
                    "1. Analizar penalidades o sanciones por incumplimiento",
                    "2. Verificar cláusulas de confidencialidad y protección de datos",
                    "3. Generar un resumen ejecutivo de las obligaciones de las partes",
                    "4. Ejecutar prueba de alucinación (Buscar términos inexistentes)",
                    "5. Realizar una pregunta personalizada al documento..."
                ]
            )
            
            user_query = ""
            system_prompt = (
                "Eres un auditor legal experto y oficial de cumplimiento bajo la norma ISO 42001. "
                "Tu trabajo es analizar el documento proporcionado de manera estrictamente objetiva. "
                "Básate ÚNICAMENTE en el texto proporcionado. Si la información no está explícitamente "
                "en el texto, dilo claramente y NO inventes información. No des asesoría legal externa."
            )
            
            if option == "1. Analizar penalidades o sanciones por incumplimiento":
                user_query = "Analiza el documento adjunto y localiza cualquier cláusula que hable sobre penalidades, multas, sanciones o consecuencias por terminación anticipada o incumplimiento. Explica detalladamente qué dice el texto al respecto de forma objetiva."
            elif option == "2. Verificar cláusulas de confidencialidad y protección de datos":
                user_query = "Busca secciones sobre confidencialidad, secreto industrial, propiedad intelectual o protección de datos. Enlista qué restricciones específicas se le imponen a las partes respecto al manejo de la información sensible."
            elif option == "3. Generar un resumen ejecutivo de las obligaciones de las partes":
                user_query = "Resume en párrafos breves cuáles son las obligaciones principales de cada una de las partes firmantes o involucradas en este documento."
            elif option == "4. Ejecutar prueba de alucinación (Buscar términos inexistentes)":
                user_query = "Busca si en el texto se menciona alguna cláusula de 'renovación automática con aumento del 50% anual'. Si este término exacto o similar no existe en el documento, responde estrictamente: 'El documento no contiene cláusulas de renovación automática con penalización de aumento'."
            elif option == "5. Realizar una pregunta personalizada al documento...":
                user_query = st.text_input("Escribe tu pregunta específica sobre el documento:")
                
            if user_query:
                if not api_key:
                    st.warning("⚠️ Por favor, introduce tu Groq API Key en la barra lateral para activar los servidores de IA.")
                else:
                    if st.button("Ejecutar Auditoría Corporativa 🚀"):
                        with st.spinner("Procesando datos de forma segura..."):
                            try:
                                client = Groq(api_key=api_key)
                                full_prompt = f"DOCUMENTO:\n{document_text}\n\nPREGUNTA:\n{user_query}"
                                
                                completion = client.chat.completions.create(
                                    model="llama3-8b-8192",
                                    messages=[
                                        {"role": "system", "content": system_prompt},
                                        {"role": "user", "content": full_prompt}
                                    ],
                                    temperature=0.1,
                                )
                                st.write("### 📝 Dictamen del Auditor Inteligente:")
                                st.info(completion.choices[0].message.content)
                            except Exception as e:
                                st.error(f"Error de conexión con el servidor: {e}")
    except Exception as e:
        st.error(f"Error al procesar el archivo: {e}")