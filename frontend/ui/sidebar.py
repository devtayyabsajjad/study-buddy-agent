import streamlit as st
from backend.config import settings as backend_settings
from frontend.ui.branding import render_logo

def render_sidebar(store):
    """Render modern sidebar with settings and controls."""
    with st.sidebar:
        # Display Agent Logo with perfect circular alignment
        render_logo(width=100)
        
        st.markdown("<h2 style='text-align: center; color: #46b8c9; margin-top: -1rem;'>Agent Solver</h2>", unsafe_allow_html=True)
        st.caption("<div style='text-align: center;'>AI Study Companion</div>", unsafe_allow_html=True)
        
        st.markdown("---")
        
        # --- File Upload (in sidebar for Streamlit Cloud reliability) ---
        st.markdown("### 📤 Upload Materials")
        uploads = st.file_uploader(
            "Upload PDF or TXT files",
            type=["pdf", "txt"],
            accept_multiple_files=True,
            label_visibility="collapsed",
            key="sidebar_file_uploader"
        )
        settings = {"uploads": uploads if uploads else []}
        
        st.markdown("---")
        
        # --- Document Status ---
        stats = store.get_statistics()
        if stats["total_docs"] > 0:
            st.markdown("### 📊 Status")
            c1, c2 = st.columns(2)
            c1.metric("Docs", stats["total_docs"])
            c2.metric("Chunks", stats["total_chunks"])
            
            st.markdown("---")
            st.markdown("### 📚 Materials")
            for doc in stats["docs"]:
                with st.expander(f"📄 {doc['doc_name'][:15]}...", expanded=False):
                    st.caption(f"Chunks: {doc['num_chunks']}")
                    if st.button("Unload", key=f"side_del_{doc['doc_id']}", use_container_width=True):
                        store.remove_doc(doc['doc_id'])
                        if "processed_files" in st.session_state and doc['doc_name'] in st.session_state.processed_files:
                            st.session_state.processed_files.remove(doc['doc_name'])
                        st.rerun()
            st.markdown("---")

        st.markdown("### ⚙️ Intelligence")
        
        
        
        # Retrieval settings
        settings["top_k"] = st.slider(
            "Context Depth",
            min_value=1,
            max_value=15,
            value=settings.get("top_k", 5) if "settings" in locals() else 5,
            help="Higher values provide more context but may be slower"
        )
        
        st.markdown("### 📊 System Status")
        
        # Status indicators in a grid
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**Core**")
            st.markdown("`Active`")
        with c2:
            st.markdown("**Model**")
            st.markdown("`Llama-70b`")
            
        st.markdown("---")
        
        st.markdown("### 🛠️ Controls")
        
        c1, c2 = st.columns(2)
        with c1:
            settings["clear_chat"] = st.button(
                "🧹 Clear",
                use_container_width=True,
                help="Clear chat history"
            )
        with c2:
            settings["remove_docs"] = st.button(
                "🗑️ Reset",
                use_container_width=True,
                type="primary",
                help="Remove all documents"
            )
            
        st.markdown("---")
        
        with st.expander("📝 Usage Tips"):
            st.markdown("""
            1. **Upload PDFs**: Drag & drop your study materials
            2. **Wait for Analysis**: Let AI process the content
            3. **Ask Questions**: "Summarize chapter 3" or "What is X?"
            4. **Check Sources**: Verify answers with citations
            """)
            
    return settings