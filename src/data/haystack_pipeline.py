# src/data/haystack_pipeline.py (versi diperbarui)

import streamlit as st
from haystack import Pipeline
from haystack.utils import Secret
from haystack.components.embedders import SentenceTransformersDocumentEmbedder, SentenceTransformersTextEmbedder
from haystack_integrations.components.retrievers.mongodb_atlas import MongoDBAtlasEmbeddingRetriever, MongoDBAtlasFullTextRetriever
from haystack.components.preprocessors import DocumentCleaner, DocumentSplitter
from haystack.components.writers import DocumentWriter
from haystack.document_stores.types import DuplicatePolicy
from haystack.components.builders import PromptBuilder
from haystack.components.builders import ChatPromptBuilder
from haystack.components.generators.chat import HuggingFaceAPIChatGenerator
from haystack_integrations.components.generators.google_genai import GoogleGenAIChatGenerator
from haystack_integrations.components.embedders.google_genai import GoogleGenAITextEmbedder
from haystack.dataclasses import ChatMessage
from haystack.utils import Secret
from haystack.utils.hf import HFGenerationAPIType
from haystack.components.joiners import DocumentJoiner


class HaystackPipeline:
    def __init__(self, document_store):
        self.document_store = document_store
        self.pipeline = self.document_store_pipeline()
        self.chat_memory = []  # Menyimpan riwayat percakapan: list of {"role": "...", "content": "..."}

    def document_exists(self, title):
        """Cek apakah dokumen dengan meta.title = title sudah ada di DB"""
        filters = {"field": "meta.title", "operator": "==", "value": title}
        result = self.document_store.filter_documents(filters=filters)
        return len(result) > 0

    def document_store_pipeline(self):
        pipeline_storing = Pipeline()
        pipeline_storing.add_component("cleaner", DocumentCleaner())
        pipeline_storing.add_component("splitter", DocumentSplitter(split_by="word", split_length=256, split_overlap=100))
        pipeline_storing.add_component("embedder", SentenceTransformersDocumentEmbedder('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2'))
        pipeline_storing.add_component("writer", DocumentWriter(document_store=self.document_store, policy=DuplicatePolicy.OVERWRITE))

        pipeline_storing.connect("cleaner", "splitter")
        pipeline_storing.connect("splitter", "embedder")
        pipeline_storing.connect("embedder", "writer")

        return pipeline_storing

    def question_rewriter_pipeline(self):
        """
        Membuat pipeline yang menulis ulang pertanyaan berdasarkan riwayat percakapan
        agar menjadi pertanyaan yang berdiri sendiri.
        """
        GOOGLE_TOKEN = st.secrets["GOOGLE_TOKEN"]

        rewriter_prompt_template = """
        Berdasarkan riwayat percakapan dan pertanyaan lanjutan berikut, ubah pertanyaan lanjutan tersebut menjadi pertanyaan yang berdiri sendiri dan dapat dipahami tanpa konteks percakapan.
        Hanya kembalikan pertanyaan yang sudah diubah, tanpa tambahan apapun.

        Riwayat Percakapan:
        {% for message in history %}
        {{ message.role }}: {{ message.content }}
        {% endfor %}

        Pertanyaan Lanjutan: {{query}}

        Pertanyaan yang Berdiri Sendiri:
        """
        
        rewriter_pipeline = Pipeline()
        rewriter_pipeline.add_component(
            "prompt_builder", 
            ChatPromptBuilder(template=[ChatMessage.from_user(rewriter_prompt_template)])
        )
        rewriter_pipeline.add_component(
            "generator", 
            GoogleGenAIChatGenerator(api_key=Secret.from_token(GOOGLE_TOKEN))
        )
        rewriter_pipeline.connect("prompt_builder", "generator")
        
        return rewriter_pipeline

    def answer_generator_pipeline(self):
        HF_TOKEN = st.secrets["HF_TOKEN"]
        GOOGLE_TOKEN = st.secrets["GOOGLE_TOKEN"]

        # generator = HuggingFaceAPIChatGenerator(
        #     api_type="serverless_inference_api",
        #     api_params={"model": "Qwen/Qwen2.5-7B-Instruct", "provider": "together"},
        #     token=Secret.from_token(HF_TOKEN)
        # )

        pipeline_generate_answers = Pipeline()
        text_embedder = SentenceTransformersTextEmbedder('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')
        pipeline_generate_answers.add_component("text_embedder", text_embedder)

        embedding_retriever = MongoDBAtlasEmbeddingRetriever(document_store=self.document_store, top_k=3)
        pipeline_generate_answers.add_component("embedding_retriever", embedding_retriever)

        full_text_retriever = MongoDBAtlasFullTextRetriever(document_store=self.document_store, top_k=3)
        pipeline_generate_answers.add_component("full_text_retriever", full_text_retriever)

        joiner = DocumentJoiner(join_mode='reciprocal_rank_fusion', top_k=3)
        pipeline_generate_answers.add_component("joiner", joiner)

        # prompt_builder = PromptBuilder(template="""
        #     Answer the following question using only the information from the provided documents. 
        #     Write the answer as a clear and short, single paragraph in natural language (2–3 sentences maximum).

        #     Chat History:
        #     {% for message in history %}
        #     {{ message.role }}: {{ message.content }}
        #     {% endfor %}

        #     Documents:
        #     {% for doc in documents %}
        #     - {{ doc.content }}
        #     {% endfor %}

        #     Question: {{ query }}
        #     Answer:
        #     """)
        
        template = [
            ChatMessage.from_user("""
            Jawab pertanyaan berikut berdasarkan informasi dari dokumen.
            Tulis jawaban dalam satu paragraf yang jelas dan singkat dalam bahasa yang alami (maksimal 2-3 kalimat).

            Riwayat Percakapan:
            {% for message in history %}
            {{ message.role }}: {{ message.content }}
            {% endfor %}

            Dokumen:
            {% for doc in documents %}
            - {{ doc.content }}
            {% endfor %}

            Pertanyaan: {{ query }}
            Jawaban:                      
            """)
        ]
        
        # pipeline_generate_answers.add_component("prompt_builder", prompt_builder)
        pipeline_generate_answers.add_component("prompt_builder", ChatPromptBuilder(template=template))
        
        genai_chat  = GoogleGenAIChatGenerator(api_key=Secret.from_token(GOOGLE_TOKEN))
        pipeline_generate_answers.add_component("generator", genai_chat)

        # pipeline_generate_answers.connect("text_embedder", "embedding_retriever")
        # pipeline_generate_answers.connect("embedding_retriever", "joiner")
        # pipeline_generate_answers.connect("full_text_retriever", "joiner")
        # pipeline_generate_answers.connect("joiner", "prompt_builder.documents")
        # pipeline_generate_answers.connect("prompt_builder", "generator")

        # return pipeline_generate_answers
        
        # Alirkan output embedding dari text_embedder ke input embedding_retriever
        pipeline_generate_answers.connect("text_embedder.embedding", "embedding_retriever")

        # Alirkan output dokumen dari kedua retriever ke joiner
        pipeline_generate_answers.connect("embedding_retriever.documents", "joiner.documents")
        pipeline_generate_answers.connect("full_text_retriever.documents", "joiner.documents")

        # Alirkan output dokumen gabungan dari joiner ke prompt_builder
        pipeline_generate_answers.connect("joiner.documents", "prompt_builder.documents")
    
        # Alirkan output prompt dari prompt_builder ke generator
        pipeline_generate_answers.connect("prompt_builder.prompt", "generator.messages")

        return pipeline_generate_answers

    def add_to_memory(self, user_message, bot_reply):
        """Simpan percakapan ke memori"""
        self.chat_memory.append({"role": "user", "content": user_message})
        self.chat_memory.append({"role": "assistant", "content": bot_reply})

    def clear_memory(self):
        """Reset riwayat percakapan"""
        self.chat_memory = []