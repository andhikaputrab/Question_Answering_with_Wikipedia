import streamlit as st
from src.utils.styling import load_css
from page.Profile import show_profile
from page.Overview import show_overview
from page.Chat import chabot_wiki

st.set_page_config(
    layout="wide"
)
    
@st.cache_resource
def Home():
    load_css()
    
    st.title("Welcome to the Question Answering App")
    st.markdown("""
        <div style="text-align: justify">

        **Get Quick Answers to All Your Questions.**
        Whether you're a student conducting research, a professional in need of data, or simply curious about the world around you, this app is designed to help. Just type in your question, and let the app provide you with in-depth explanations, supported by the trusted resources of Wikipedia.

        **Explore a Variety of Topics:**
        * 🏛️ World History and Civilization
        * 🔬 Science and Technology
        * 🎨 Arts and Culture
        * 🌍 Geography and Exploration
        * 💡 People and Discoveries
        </div>
    """, unsafe_allow_html=True)
    
    with st.expander("How Does This App Work?"):
        st.markdown("""
        This app works in three simple steps to provide you with the best answers:

        1.  **Input Your Question**
            * Simply type your question into the provided field.

        2.  **Data Processing**
            * The system automatically searches for relevant information from the **Wikipedia API**, a vast knowledge base.
            * Next, the **Gemini LLM (Large Language Model)** reads, analyzes, and summarizes this information to construct a coherent and relevant answer.

        3.  **Answer Presentation**
            * You will receive an accurate and easy-to-understand answer, presented directly on your screen.
        """)

# --- Sidebar ---
st.sidebar.markdown(
    """
    <div style="text-align: center;">
        <h1 style="color: #4CAF50;">Portofolio</h1>
    </div>
    """,
    unsafe_allow_html=True
)

# st.sidebar.markdown("---")
st.sidebar.image("static/img/QA.png", use_container_width=True)

# Navigation radio buttons
page = st.sidebar.radio(
    "Pilih Halaman",
    ["Home", "Profile", "Chat QA"],
)

if page == "Home":
    Home()
elif page == "Profile":
    show_profile()
elif page == "Chat QA":
    chabot_wiki()
    
st.sidebar.markdown("---")