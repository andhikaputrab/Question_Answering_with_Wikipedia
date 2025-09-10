import streamlit as st
from src.utils.styling import load_css
from src.utils.config import config
import base64

def get_pdf_download_link(pdf_path, filename):
    with open(pdf_path, "rb") as f:
        bytes_data = f.read()
    b64 = base64.b64encode(bytes_data).decode()
    href = f'<a href="data:application/pdf;base64,{b64}" download="{filename}" class="download-button" style="text-decoration: none; background-color: #4CAF50; color: white; padding: 10px 15px; border-radius: 5px; box-shadow: 2px 2px 5px rgba(0,0,0,0.3);">📥 Download CV</a>'
    return href

def show_profile():
    # st.set_page_config(
    #     page_title=config.get('PAGE_PROFILE_TITLE'), 
    #     page_icon=config.get('PAGE_PROFILE_ICON'), 
    #     layout=config.get('LAYOUT_PROFILE')
    # )
    load_css()

    st.title("👨‍💻 Andhika Putra Bagaskara")
    st.subheader("Data Scientist")

    col1, col2 = st.columns([1, 2])

    with col1:
        st.image("static/img/foto.jpg", width=200, output_format="auto")
    
        st.markdown("### 📞 Contact")
        st.markdown("""
            - 📧 **Email:** andhikaputra1301@gmail.com
            - 📱 **WhatsApp:** 082213676520
        """)
        st.markdown("### 🌐 Social Media")
        st.markdown("""
            <a href="https://www.linkedin.com/in/andhika-putra-bagaskara13/" target="_blank"><img src="https://img.icons8.com/color/48/000000/linkedin.png" style="width: 30px; margin-right: 10px;"></a>
            <a href="https://github.com/andhikaputrab" target="_blank"><img src="https://img.icons8.com/color/48/000000/github.png" style="width: 30px; margin-right: 10px;"></a>
            <a href="https://www.instagram.com/andhikaputrab/" target="_blank"><img src="https://img.icons8.com/color/48/000000/instagram-new--v1.png" style="width: 30px; margin-right: 10px;"></a>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("---")
        st.markdown("### 📝 Summary")
        st.markdown(get_pdf_download_link("cv/CV ATS - Andhika Putra Bagaskara.pdf", "CV_Andhika_Putra_Bagaskara.pdf"), unsafe_allow_html=True)
        st.markdown("""
        <div style="text-align: justify; margin-top: 20px;">
            I am a Bachelor Degree of Informatics Engineering and currently attending Master Degree of Informatics Engineering at Telkom University.
            Proficiency in data processing, visualization, Python, Machine Learning, Tableau, and Excel. Good problem-solving and critical thinking skills, committed to providing accurate data insights to support company 
            decision-making, and highly motivated to continue learning and developing in the field of data analytics.    </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.header("🏢 Working Experience")
    experiences = [
        {
            "role": "Internship",
            "company": "PT Pertamina Persero",
            "period": "Oktober 2022 - Oktober 2023",
            "points": [
                "Automate the management of ticket request data from the website using UiPath and send the analysisvia email to the relevant department.", 
                "Developing a website application for asset management for internal functions using CodeIgniter, MySQL,JavaScript and HTML"
            ]
        },
    ]

    for exp in experiences:
        with st.expander(f"**{exp['company']} - {exp['role']}**"):
            st.markdown(f"**Periode:** {exp['period']}")
            for point in exp['points']:
                st.markdown(f"- {point}")

    st.markdown("---")
    st.header("🧠 Skill")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Technical Skills")
        technical_skills = [
            "Python",
            "Machine Learning",
            "MySQL",
            "Tableau",
            "Data Analysis",
            "Data Visualization",
        ]
    
        for skill in technical_skills: 
            st.markdown(f"- {skill}")
        
    with col2:
        st.subheader("Soft Skill")
        soft_skill = [
            "Communication",
            "Problem Solving",
            "Analytical Thinking",
            "Teamwork"
        ]
    
        for tool in soft_skill: 
            st.markdown(f"- {tool}")

    st.markdown("---")
    st.header("🎓 Education")
    education = [
        {
            "university": "Telkom University",
            "period": "2024 - Present",
            "degree": "Master Degree of Informatics Engineering",
            "relevant_coursework": "Data Analysis, Machine Learning, Artificial Intelligence, Natural Language Processing",
            "GPA": "3.26/4.00",
            }, 
        {
            "university": "Universitas Komputer Indonesia",
            "period": "2017 - 2022",
            "degree": "Bachelor Degree of Informatics Engineering",
            "relevant_coursework": "Software Engineering, Artificial Intelligence, Mobile Programming, Web Programming",
            "GPA": "3.07/4.00",
        }
    ]
    for edu in education:
        with st.expander(f"**{edu['university']} ({edu['period']})**"):
            st.markdown(f"**Degree:** {edu['degree']}")
            st.markdown(f"**Relevant Coursework:** {edu['relevant_coursework']}")
            st.markdown(f"**GPA:** {edu['GPA']}")

    st.markdown("---")
    st.header("🏆 Certifications")
    certifications = [
        {
            "title": "Big Data using Python",
            "orginizer": "Kursus Online – Kominfo",
            "relevant_coursework": "Data Processing, Data Visualization, Python","period": "2021"
            }, 
        {
            "title": "Google Data Analytics",
            "orginizer": "Kursus Online – Kominfo",
            "relevant_coursework": "Data Processing, Data Visualization, Python, R, Tableau",
            "period": "2024"
        }, 
        {
            "title": "English Proficiency Test (EPRT)",
            "orginizer": "Telkom University",
            "period": "2025"
        }
    ]

    for cert in certifications:
        with st.expander(f"**{cert['title']} ({cert['period']})**"):
            st.markdown(f"**Orginizer:** {cert['orginizer']}")
            if cert['title'] == "English Proficiency Test (EPRT)":
                st.markdown("**Score:** 513")
            else:
                st.markdown(f"**Relevant Coursework:** {cert['relevant_coursework']}")