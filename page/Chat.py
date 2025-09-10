# app.py — versi multi-turn + cek duplikasi

import streamlit as st
from src.utils.styling import load_css
from src.utils.config import config
from src.connection.db_connector import MongoDBConnector
from src.data.data_loader import WikipediaFetcher
from src.data.haystack_pipeline import HaystackPipeline

def session():
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    if "haystack_pipeline" not in st.session_state:
        # Inisialisasi koneksi dan pipeline HANYA SEKALI dan simpan di session state
        document_store = MongoDBConnector().document_store
        st.session_state.haystack_pipeline = HaystackPipeline(document_store)
        
def chabot_wiki():
    # st.set_page_config(
    #     page_title=config.get('PAGE_TITLE_CHAT'),
    #     page_icon='🤖',
    #     layout=config.get('LAYOUT_CHAT')
    # )
    
    load_css()
    session()
    
    st.title('🤖 Question Answering Application with Wikipedia')
    
    # Tombol reset chat
    if st.button("🗑️ Clear Chat History"):
        st.session_state.messages = []
        st.session_state.haystack_pipeline.clear_memory()
        st.rerun()

    # Tampilkan riwayat chat
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Input pertanyaan
    if question := st.chat_input("Ask me anything..."):
        # Tampilkan pertanyaan user
        with st.chat_message("user"):
            st.markdown(question)
        st.session_state.messages.append({"role": "user", "content": question})
        
        full_question = question
        
        if len(st.session_state.messages) > 1:
            with st.spinner("✍️ Menulis ulang pertanyaan dengan konteks..."):
                try:
                    # Ambil pipeline rewriter dari Haystack
                    rewriter_pipeline = st.session_state.haystack_pipeline.question_rewriter_pipeline()
                    
                    # Jalankan pipeline untuk mendapatkan pertanyaan yang ditulis ulang
                    rewritten_result = rewriter_pipeline.run({
                        "prompt_builder": {
                            "query": question,
                            "history": st.session_state.haystack_pipeline.chat_memory
                        }
                    })
                    
                    # Ekstrak teks dari hasil rewriting
                    full_question = rewritten_result["generator"]["replies"][0].text
                    
                    # Tampilkan info jika pertanyaan berhasil diubah
                    if full_question.lower() != question.lower():
                         st.info(f"Pertanyaan ditulis ulang: `{full_question}`")
                except Exception as e:
                    st.error(f"Error saat menulis ulang pertanyaan: {e}")
                    # Jika gagal, tetap gunakan pertanyaan asli
                    full_question = question

        with st.spinner("🔍 Searching Wikipedia..."):
            wikipedia_search = WikipediaFetcher(language='id')
            wikipedia_documents = wikipedia_search.fetch_wikipedia_articles(full_question)

        if not wikipedia_documents:
            st.error("No relevant Wikipedia articles found.")
            return

        # Filter dokumen yang belum ada di DB
        new_documents = []
        for doc in wikipedia_documents:
            title = doc["meta"]["title"]
            if not st.session_state.haystack_pipeline.document_exists(title):
                new_documents.append(doc)
            else:
                # st.info(f"📄 Document '{title}' already exists in DB — skipped.")
                continue

        # if new_documents:
        #     with st.spinner(f"💾 Storing {len(new_documents)} new documents..."):
        #         document_objects = [Document(content=doc["content"], meta=doc["meta"]) for doc in new_documents]
        #         pipeline_storing = st.session_state.haystack_pipeline.document_store_pipeline()
        #         pipeline_storing.run({"documents": document_objects})
        # else:
        #     st.info("✅ All documents already exist in database.")

        # Generate jawaban dengan riwayat percakapan
        with st.spinner("💭 Thinking..."):
            answer_pipeline = st.session_state.haystack_pipeline.answer_generator_pipeline()
            try:
                answers = answer_pipeline.run({
                    "text_embedder": {"text": full_question},
                    "full_text_retriever": {"query": full_question},
                    "prompt_builder": {
                        "query": full_question,
                        "history": st.session_state.haystack_pipeline.chat_memory
                    }
                })
                reply = answers['generator']['replies'][0]

                # Simpan ke memori & riwayat tampilan
                st.session_state.haystack_pipeline.add_to_memory(full_question, reply.text)
                st.session_state.messages.append({"role": "assistant", "content": reply.text})

                # Tampilkan jawaban
                with st.chat_message("assistant"):
                    st.markdown(reply.text)

            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
                st.write("Pastikan `HF_API_TOKEN` valid dan model tersedia.")

        # Opsional: Tampilkan dokumen yang digunakan
        with st.expander("📚 Retrieved Documents (New & Existing)"):
            for i, doc in enumerate(wikipedia_documents):
                st.markdown(f"**{doc['meta']['title']}**")
                st.text(doc["content"][:300] + "...")