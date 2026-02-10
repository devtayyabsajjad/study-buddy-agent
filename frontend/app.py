import sys
import os
import time
import logging

# Add the project root to sys.path so we can import from backend
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import uuid
import streamlit as st

from backend.config import settings as backend_settings
from backend.utils.chunking import chunk_text, validate_chunk
from backend.storage.in_memory_store import InMemoryStore, DocChunk
from backend.loaders.pdf_loader import read_pdf_bytes
from backend.loaders.text_loader import read_text_bytes
from backend.services.chat_service import answer_question_from_docs
from backend.utils.file_validator import FileValidationError, validate_file_size, validate_file_type
from backend.utils.error_handler import handle_error, StudyBuddyError

from frontend.ui.sidebar import render_sidebar
from frontend.ui.chat_widgets import render_chat, render_sources, render_welcome_message
from frontend.ui.styles import get_custom_css
from frontend.ui.animations import (
    get_loading_animation, 
    get_success_animation, 
    get_progress_bar,
    get_upload_zone_animation,
    get_typing_indicator
)
from frontend.ui.branding import render_logo

# Page config with modern theme
st.set_page_config(
    page_title="Agent Solver - Proactive STEM Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/yourusername/study-buddy',
        'Report a bug': "https://github.com/yourusername/study-buddy/issues",
        'About': "# Agent Solver\nYour proactive STEM study companion."
    }
)

# Inject custom CSS
st.markdown(get_custom_css(), unsafe_allow_html=True)
st.markdown(get_upload_zone_animation(), unsafe_allow_html=True)

# ---------- Session State ----------
if "store" not in st.session_state:
    st.session_state.store = InMemoryStore()

if "chat" not in st.session_state:
    st.session_state.chat = []

if "processing" not in st.session_state:
    st.session_state.processing = False

if "error_message" not in st.session_state:
    st.session_state.error_message = None

# Cache Logo for performance
if "logo_b64" not in st.session_state:
    from frontend.ui.chat_widgets import get_base64_image
    _frontend_dir = os.path.dirname(os.path.abspath(__file__))
    logo_path = os.path.join(_frontend_dir, "assets", "logo.png")
    if not os.path.exists(logo_path):
        logo_path = os.path.join(_frontend_dir, "assests", "logo.png")
    img_b64 = get_base64_image(logo_path)
    st.session_state.logo_b64 = f"data:image/png;base64,{img_b64}" if img_b64 else "🤖"

# ---------- Sidebar ----------
ui_settings = render_sidebar(st.session_state.store)

if ui_settings["clear_chat"]:
    st.session_state.chat = []
    st.toast("✅ Chat history cleared!", icon="🧹")
    time.sleep(0.5)
    st.rerun()

if ui_settings["remove_docs"]:
    st.session_state.store = InMemoryStore()
    st.toast("✅ All documents removed!", icon="🗑️")
    time.sleep(0.5)
    st.rerun()

# ---------- Main Layout ----------
render_logo(width=140)
st.markdown("# Agent Solver")
st.markdown("<h3 style='text-align: center;'>Your AI Study Assistant</h3>", unsafe_allow_html=True)

# Error toast
if st.session_state.error_message:
    st.error(st.session_state.error_message)
    st.session_state.error_message = None

# Main Chat Area (Single Column)
chat_container = st.container(height=600)

with chat_container:
    if not st.session_state.chat:
        render_welcome_message()
    else:
        render_chat(st.session_state.chat)

# Input area
question = st.chat_input("Ask a question about your documents...")

# ---------- File Processing Logic (uploads from sidebar) ----------
uploads = ui_settings.get("uploads", [])

if uploads and not st.session_state.processing:
    if "processed_files" not in st.session_state:
        st.session_state.processed_files = set()
        
    new_files = [up for up in uploads if up.name not in st.session_state.processed_files]
    
    if new_files:
        st.session_state.processing = True
        status_container = st.empty()
        
        for up in new_files:
            doc_id = str(uuid.uuid4())
            doc_name = up.name
            file_status = status_container.container()
            
            try:
                with file_status:
                    st.markdown(f"**Processing {doc_name}...**")
                    progress_container = st.empty()
                    st.markdown(get_loading_animation(), unsafe_allow_html=True)
                    
                    validate_file_type(doc_name)
                    validate_file_size(up, max_size_mb=backend_settings.max_file_size_mb, filename=doc_name)
                    
                    full_text = ""
                    if up.type == "application/pdf" or doc_name.lower().endswith(".pdf"):
                        def update_progress(current, total):
                            pct = int((current / total) * 100)
                            progress_container.markdown(get_progress_bar(pct, text=f"Reading page {current}/{total}"), unsafe_allow_html=True)
                        
                        file_bytes = up.read()
                        full_text = read_pdf_bytes(file_bytes, max_size_mb=backend_settings.max_file_size_mb, max_pages=backend_settings.max_pdf_pages, progress_callback=update_progress, batch_size=backend_settings.pdf_batch_size)
                    else:
                        progress_container.markdown(get_progress_bar(50, "Reading text file..."), unsafe_allow_html=True)
                        file_bytes = up.read()
                        full_text = read_text_bytes(file_bytes)
                    
                    chunks = []
                    for ch_text in chunk_text(full_text, backend_settings.chunk_size, backend_settings.chunk_overlap):
                        if validate_chunk(ch_text):
                            chunks.append(DocChunk(doc_id=doc_id, doc_name=doc_name, chunk_id=len(chunks), text=ch_text))
                    
                    if not chunks:
                        raise StudyBuddyError("No valid text found in document.", category="validation")
                    
                    st.session_state.store.upsert_doc(doc_id, doc_name, chunks)
                    st.session_state.processed_files.add(doc_name)
                    
                    progress_container.markdown(get_success_animation(), unsafe_allow_html=True)
                    st.toast(f"Analyzed {doc_name}", icon="✅")
                    time.sleep(1)
                    
            except Exception as e:
                logging.error(f"File upload error for {doc_name}: {e}", exc_info=True)
                st.error(handle_error(e, context=f"Uploading {doc_name}"))
            
            file_status.empty()
        
        st.session_state.processing = False
        status_container.empty()
        if "new_uploads" in st.session_state:
            del st.session_state.new_uploads
        st.rerun()

if question:
    st.session_state.chat.append({"role": "user", "content": question})
    st.rerun()


# Handle response generation (after rerun to show user message first)
if st.session_state.chat and st.session_state.chat[-1]["role"] == "user":
    with chat_container:
        # Note: Chat is already rendered above, so we don't call render_chat again.
        # This prevents the "duplicate questions" flicker.
        
        # Note: Chat already rendered once, skipping double-render pass
        
        avatar_data = st.session_state.logo_b64

        with st.chat_message("assistant", avatar=avatar_data):
            message_placeholder = st.empty()
            message_placeholder.markdown(get_typing_indicator(), unsafe_allow_html=True)
            
            try:
                # Collect chunks from all docs
                all_chunks = []
                for doc_id, _ in st.session_state.store.list_docs():
                    all_chunks.extend(st.session_state.store.get_chunks(doc_id))

                result = answer_question_from_docs(
                    question=st.session_state.chat[-1]["content"],
                    all_chunks=all_chunks,
                    top_k=ui_settings["top_k"],
                )
                
                answer = result["answer"]
                used_excerpts = result["used_excerpts"]

                # Display answer directly (Typewriter removed)
                message_placeholder.markdown(answer)
                
                # Store response
                st.session_state.chat.append({"role": "assistant", "content": answer})
                
                # Render sources
                if used_excerpts:
                    render_sources(used_excerpts)
                    
            except Exception as e:
                error_msg = f"❌ Error: {str(e)}"
                message_placeholder.error(error_msg)
                st.session_state.chat.append({"role": "assistant", "content": error_msg})
