import streamlit as st
import os
import sys
import tempfile

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from main import AidaAIAssistant
except ImportError as e:
    st.error(f"Import Error: {e}")
    st.error("Please ensure all files (main.py, config.py, models.py, processors.py, services.py) are in the same directory")
    st.stop()

# Page config
st.set_page_config(
    page_title="Aida AI Document Processor",
    page_icon="📄",
    layout="wide"
)

# Initialize session state
if 'processed_result' not in st.session_state:
    st.session_state.processed_result = None

# Title
st.title("📄 Aida AI Document Processor")
st.markdown("Upload medical documents (PDF, DOCX, JPG, PNG) for AI analysis")

# Sidebar
with st.sidebar:
    st.header("📋 Supported Files")
    st.markdown("- 📕 PDF")
    st.markdown("- 📘 DOCX/DOC")
    st.markdown("- 🖼️ JPG/JPEG")
    st.markdown("- 🖼️ PNG")
    st.markdown("---")
    st.markdown("### ℹ️ Info")
    

# Main content
uploaded_file = st.file_uploader(
    "Choose a document",
    type=['pdf', 'docx', 'doc', 'jpg', 'jpeg', 'png']
)

if uploaded_file:
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.info(f"**📄 File:** {uploaded_file.name}")
        st.info(f"**💾 Size:** {uploaded_file.size / 1024:.2f} KB")
    
    with col2:
        if st.button("🚀 Analyze Document", type="primary", use_container_width=True):
            # Save uploaded file temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp:
                tmp.write(uploaded_file.getvalue())
                tmp_path = tmp.name
            
            try:
                # Process document
                with st.spinner("🔄 Processing document..."):
                    assistant = AidaAIAssistant()
                    result = assistant.analyze_document(tmp_path)
                    st.session_state.processed_result = result
                
                # Clean up
                os.unlink(tmp_path)
                
                if 'error' in result:
                    st.error(f"❌ Error: {result['message']}")
                else:
                    st.success("✅ Document processed successfully!")
            
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
                if os.path.exists(tmp_path):
                    os.unlink(tmp_path)

# Display results
if st.session_state.processed_result and 'error' not in st.session_state.processed_result:
    result = st.session_state.processed_result
    
    st.markdown("---")
    st.header("📊 Analysis Results")
    
    # Metadata
    with st.expander("📄 Document Metadata", expanded=True):
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Type", result['metadata']['file_type'].upper())
        col2.metric("Category", result['metadata']['category'])
        col3.metric("Pages", result['metadata']['num_pages'])
        col4.metric("Date", result['metadata']['creation_date'])
    
    # Patient Info
    with st.expander("👤 Patient Information", expanded=True):
        col1, col2, col3 = st.columns(3)
        patient = result['patient_info']
        col1.markdown(f"**Name:** {patient['name'] or 'N/A'}")
        col2.markdown(f"**DOB:** {patient['date_of_birth'] or 'N/A'}")
        col3.markdown(f"**Address:** {patient['address'] or 'N/A'}")
    
    # Extracted Values
    with st.expander("📊 Extracted Medical Values", expanded=True):
        values = result['extracted_values']
        if values:
            for key, value in values.items():
                st.markdown(f"**{key}:** {value}")
        else:
            st.info("No medical values extracted")
    
    # Summary
    with st.expander("📝 Summary", expanded=True):
        st.markdown(result['summary'])
    
    # Raw Text
    with st.expander("📃 Extracted Text"):
        st.text_area("Raw Text", result['raw_text'], height=300, disabled=True)

# Footer
st.markdown("---")
st.markdown("Made with ❤️ using Aida AI")