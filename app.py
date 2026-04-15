# LexIndia: Streamlit Web Interface
# Built by: Deepak Saxena

import streamlit as st
import requests
import os
import re
import anthropic
from dotenv import load_dotenv

load_dotenv()
INDIAN_KANOON_TOKEN = os.getenv("INDIAN_KANOON_TOKEN")
CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY")

# Page Configuration

st.set_page_config(
    page_title="LexIndia - AI Legal Assistant",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling


st.markdown("""
<style>
    /* Force white background everywhere */
    .stApp, .main, section[data-testid="stMain"] {
        background-color: #ffffff !important;
    }
    
    /* Force dark text everywhere in main area */
    .stApp p, .stApp h1, .stApp h2, .stApp h3, 
    .stApp h4, .stApp li, .stApp span, .stApp div,
    .stMarkdown p, .stMarkdown h1, .stMarkdown h2, 
    .stMarkdown h3, .stMarkdown li {
        color: #333333 !important;
    }
    
    /* Sidebar navy */
    [data-testid="stSidebar"] {
        background-color: #1a2744 !important;
    }
    
    /* Sidebar text white */
    [data-testid="stSidebar"] * {
        color: #ffffff !important;
    }
    
    /* Gold buttons */
    .stButton > button {
        background-color: #c9a84c !important;
        color: white !important;
        border: none;
        border-radius: 8px;
        padding: 10px 30px;
        font-size: 16px;
        font-weight: bold;
        width: 100%;
    }
    
    .stButton > button:hover {
        background-color: #b8943d !important;
        color: white !important;
    }
    
    /* Expander white background */
    [data-testid="stExpander"] {
        background-color: #ffffff !important;
        border: 1px solid #e0e0e0;
        border-radius: 8px;
    }
    
    [data-testid="stExpander"] * {
        color: #333333 !important;
    }
    
    /* Search input */
    .stTextInput > div > div > input {
        border: 2px solid #1a2744;
        border-radius: 8px;
        font-size: 16px;
        padding: 12px;
        color: #333333 !important;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# Sidebar Navigation

with st.sidebar:
    st.markdown("## ⚖️ LexIndia")
    st.markdown("*Your AI Legal Assistant*")
    st.markdown("---")

    # Modules Menu
    st.markdown("### Navigation")

    with st.expander("🔍 Research", expanded=True):
        st.button("LexSearch - Case Research")
        st.button("LexPlain - Law Explainer")
        st.button("LexConstitute - Constitutional Advisor")
        st.button("LexGlobe - International Law")

    with st.expander("✍️ Drafting"):
        st.button("LexScan - Document Analyser")
        st.button("LexDraft - Draft Generator")
        st.button("LexDebate - Counter Argument Generator")

    with st.expander("📁 File Management"):
        st.button("LexDiary - Case Diary")
        st.button("LexVault - File Storage")
        st.button("LexChat - Legal Chatbot")
        st.button("LexTrack - Live Case Updates")

    with st.expander("📊 Intelligence"):
        st.button("LexPredict - Outcome Predictor")
        st.button("LexBench - Judge Analysis")
        st.button("LexPulse - Trend Dashboard")
        st.button("LexVoice - Regional Languages")
        st.button("LexMap - Court Locator")
    st.markdown("---")
    st.markdown("*Powered by Indian Kanoon API and Claude AI*")


# Main Page

st.markdown("""
<div style="text-align: center; padding: 40px 0 20px 0;">
    <h1 style="color: #1a2744; font-size: 56px; font-weight: 900; 
               letter-spacing: 4px; margin-bottom: 8px;">
        ⚖️ LEXINDIA
    </h1>
    <p style="color: #c9a84c; font-size: 20px; font-style: italic; 
              margin-bottom: 40px;">
        India's AI Legal Research Assistant
    </p>
</div>
""", unsafe_allow_html=True)

# Search Section
col1, col2, col3 = st.columns([1, 4, 1])

with col2:
    with st.form("search_form"):
        search_query = st.text_input(
            label="Search Query",
            placeholder="Search any case, law, or legal topic...",
            label_visibility="collapsed"
        )
        search_clicked = st.form_submit_button("🔍 Search LexIndia")
        if search_clicked and not search_query:
            st.warning("Please enter a legal query to search.")


# Search Results
if search_clicked and search_query:
    with st.spinner("Searching Indian Kanoon..."):
        params = {"formInput": search_query, "pagenum": 0}
        url = "https://api.indiankanoon.org/search/"
        headers = {"Authorization": f"Token {INDIAN_KANOON_TOKEN}"}
        try:
            response = requests.post(url, headers=headers, params=params)
            if response.status_code == 200:
                results = response.json()
                st.success(f"Found {results['found']} results for '{search_query}'")
                st.markdown("---")
                for index, doc in enumerate(results['docs'][:3]):
                    clean_title = re.sub(r'<[^>]+>', '', doc['title'])
                    clean_court = re.sub(r'<[^>]+>', '', doc['docsource'])
                    if index == 0:
                        st.markdown("### 📌 Best Match")
                    elif index == 1:
                        st.markdown("### 📎 Related Cases")
                    with st.expander(f"📄 {clean_title}"):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.markdown(f"**Court:** {clean_court}")
                        with col2:
                            st.markdown(f"**Date:** {doc['publishdate']}")
                        doc_id = doc['tid']
                        st.markdown(f"**🔗 Full Judgment:** [Read on Indian Kanoon](https://indiankanoon.org/doc/{doc_id}/)")
                        st.markdown("---")
                        st.markdown("**🤖 AI Summary:**")
                        with st.spinner("Generating AI analysis..."):
                            judgment_url = f"https://api.indiankanoon.org/doc/{doc_id}/"
                            j_response = requests.post(judgment_url, headers=headers)
                            judgment_text = ""
                            if j_response.status_code == 200:
                                judgment_text = j_response.json().get('doc', '')
                            client = anthropic.Anthropic(api_key=CLAUDE_API_KEY)
                            if judgment_text:
                                content = f"Full judgment:\n{judgment_text[:6000]}"
                            else:
                                content = f"Case: {clean_title}\nCourt: {clean_court}\nDate: {doc['publishdate']}"
                            prompt = f"""You are a legal assistant specializing in Indian law.
{content}
Provide: 1. Brief facts 2. Court decision 3. Key legal principle 4. How to use in arguments 5. Similar cases 6. Weaknesses
Be concise and practical for a practicing lawyer."""
                            message = client.messages.create(
                                model="claude-haiku-4-5-20251001",
                                max_tokens=4096,
                                messages=[{"role": "user", "content": prompt}]
                            )
                            st.markdown(message.content[0].text)
            else:
                st.error("Search failed. Please try again.")
        except Exception as e:
            st.error("Connection error. Please check your internet connection.")
