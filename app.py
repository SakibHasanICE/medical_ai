import streamlit as st
import os
import sys
import tempfile

from dotenv import load_dotenv


# Add current directory to path

load_dotenv()


def get_openai_api_key():
    # Prefer Streamlit Cloud secrets
    if "OPENAI_API_KEY" in st.secrets:
        return st.secrets["OPENAI_API_KEY"]
    # Fallback to .env
    elif os.getenv("OPENAI_API_KEY"):
        return os.getenv("OPENAI_API_KEY")
    else:
        return None

api_key = get_openai_api_key()

if not api_key:
    st.error("❌ OpenAI API key not found! Please set it in `.env` (local) or Streamlit Secrets (cloud).")
    st.stop()
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from main import AidaAIAssistant
except ImportError as e:
    st.error(f"Import Error: {e}")
    st.error("Please ensure all files (main.py, config.py, models.py, processors.py, services.py) are in the same directory")
    st.stop()

# Translations
TRANSLATIONS = {
    'en': {
        'page_title': 'Aida AI Document Processor',
        'title': 'Aida AI Document Processor',
        'subtitle': 'Upload medical documents (PDF, DOCX, JPG, PNG) for AI analysis',
        'supported_files': 'Supported Files',
        'info': 'Info',
        'language': 'Language',
        'choose_document': 'Choose a document',
        'file': 'File',
        'size': 'Size',
        'analyze_button': 'Analyze Document',
        'processing': 'Processing document...',
        'error': 'Error',
        'success': 'Document processed successfully!',
        'analysis_results': 'Analysis Results',
        'document_metadata': 'Document Metadata',
        'type': 'Type',
        'category': 'Category',
        'pages': 'Pages',
        'date': 'Date',
        'patient_info': 'Patient Information',
        'name': 'Name',
        'dob': 'DOB',
        'address': 'Address',
        'extracted_values': 'Extracted Medical Values',
        'no_values': 'No medical values extracted',
        'summary': 'Summary',
        'extracted_text': 'Extracted Text',
        'raw_text': 'Raw Text',
        'footer': 'Made with ❤️ using Aida AI'
    },
    'fr': {
        'page_title': 'Processeur de Documents Aida AI',
        'title': 'Processeur de Documents Aida AI',
        'subtitle': 'Téléchargez des documents médicaux (PDF, DOCX, JPG, PNG) pour l\'analyse IA',
        'supported_files': 'Fichiers Supportés',
        'info': 'Info',
        'language': 'Langue',
        'choose_document': 'Choisir un document',
        'file': 'Fichier',
        'size': 'Taille',
        'analyze_button': 'Analyser le Document',
        'processing': 'Traitement du document...',
        'error': 'Erreur',
        'success': 'Document traité avec succès!',
        'analysis_results': 'Résultats de l\'Analyse',
        'document_metadata': 'Métadonnées du Document',
        'type': 'Type',
        'category': 'Catégorie',
        'pages': 'Pages',
        'date': 'Date',
        'patient_info': 'Informations du Patient',
        'name': 'Nom',
        'dob': 'Date de Naissance',
        'address': 'Adresse',
        'extracted_values': 'Valeurs Médicales Extraites',
        'no_values': 'Aucune valeur médicale extraite',
        'summary': 'Résumé',
        'extracted_text': 'Texte Extrait',
        'raw_text': 'Texte Brut',
        'footer': 'Fait avec ❤️ en utilisant Aida AI'
    }
}

# Initialize session state
if 'processed_result' not in st.session_state:
    st.session_state.processed_result = None
if 'language' not in st.session_state:
    st.session_state.language = 'en'

# Page config
st.set_page_config(
    page_title=TRANSLATIONS[st.session_state.language]['page_title'],
    page_icon="📄",
    layout="wide"
)

# Get current translations
t = TRANSLATIONS[st.session_state.language]

# Title
st.title(f"📄 {t['title']}")
st.markdown(t['subtitle'])

# Sidebar
with st.sidebar:
    # Language selector at top
    lang = st.selectbox(
        t['language'],
        options=['en', 'fr'],
        format_func=lambda x: '🇬🇧 English' if x == 'en' else '🇫🇷 Français',
        index=0 if st.session_state.language == 'en' else 1,
        key='lang_selector'
    )
    
    if lang != st.session_state.language:
        st.session_state.language = lang
        st.rerun()
    
    st.markdown("---")
    st.header(f"📋 {t['supported_files']}")
    st.markdown("- 📕 PDF")
    st.markdown("- 📘 DOCX/DOC")
    st.markdown("- 🖼️ JPG/JPEG")
    st.markdown("- 🖼️ PNG")
    st.markdown("---")
    st.markdown(f"### ℹ️ {t['info']}")

# Main content
uploaded_file = st.file_uploader(
    t['choose_document'],
    type=['pdf', 'docx', 'doc', 'jpg', 'jpeg', 'png']
)

if uploaded_file:
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.info(f"**📄 {t['file']}:** {uploaded_file.name}")
        st.info(f"**💾 {t['size']}:** {uploaded_file.size / 1024:.2f} KB")
    
    with col2:
        if st.button(f"🚀 {t['analyze_button']}", type="primary", use_container_width=True):
            # Save uploaded file temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp:
                tmp.write(uploaded_file.getvalue())
                tmp_path = tmp.name
            
            try:
                # Process document
                with st.spinner(f"🔄 {t['processing']}"):
                    assistant = AidaAIAssistant()
                    result = assistant.analyze_document(tmp_path)
                    st.session_state.processed_result = result
                
                # Clean up
                os.unlink(tmp_path)
                
                if 'error' in result:
                    st.error(f"❌ {t['error']}: {result['message']}")
                else:
                    st.success(f"✅ {t['success']}")
            
            except Exception as e:
                st.error(f"❌ {t['error']}: {str(e)}")
                if os.path.exists(tmp_path):
                    os.unlink(tmp_path)

# Display results
if st.session_state.processed_result and 'error' not in st.session_state.processed_result:
    result = st.session_state.processed_result
    
    st.markdown("---")
    st.header(f"📊 {t['analysis_results']}")
    
    # Metadata
    with st.expander(f"📄 {t['document_metadata']}", expanded=True):
        col1, col2, col3, col4 = st.columns(4)
        col1.metric(t['type'], result['metadata']['file_type'].upper())
        col2.metric(t['category'], result['metadata']['category'])
        col3.metric(t['pages'], result['metadata']['num_pages'])
        col4.metric(t['date'], result['metadata']['creation_date'])
    
    # Patient Info
    with st.expander(f"👤 {t['patient_info']}", expanded=True):
        col1, col2, col3 = st.columns(3)
        patient = result['patient_info']
        col1.markdown(f"**{t['name']}:** {patient['name'] or 'N/A'}")
        col2.markdown(f"**{t['dob']}:** {patient['date_of_birth'] or 'N/A'}")
        col3.markdown(f"**{t['address']}:** {patient['address'] or 'N/A'}")
    
    # Extracted Values
    with st.expander(f"📊 {t['extracted_values']}", expanded=True):
        values = result['extracted_values']
        if values:
            for key, value in values.items():
                st.markdown(f"**{key}:** {value}")
        else:
            st.info(t['no_values'])
    
    # Summary
    with st.expander(f"📝 {t['summary']}", expanded=True):
        st.markdown(result['summary'])
    
    # Raw Text
    with st.expander(f"📃 {t['extracted_text']}"):
        st.text_area(t['raw_text'], result['raw_text'], height=300, disabled=True)

# Footer
st.markdown("---")
st.markdown(t['footer'])