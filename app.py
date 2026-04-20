# LexIndia: Streamlit Web Interface
# Built by: Deepak Saxena

import streamlit as st
import requests
import os
import re
import anthropic
from dotenv import load_dotenv
from tavily import TavilyClient

load_dotenv()
INDIAN_KANOON_TOKEN = os.getenv("INDIAN_KANOON_TOKEN")
CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

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
    .stApp, .main, section[data-testid="stMain"] {
        background-color: #ffffff !important;
    }
    .stApp p, .stApp h1, .stApp h2, .stApp h3,
    .stApp h4, .stApp li, .stApp span, .stApp div,
    .stMarkdown p, .stMarkdown h1, .stMarkdown h2,
    .stMarkdown h3, .stMarkdown li {
        color: #333333 !important;
    }
    [data-testid="stSidebar"] {
        background-color: #1a2744 !important;
    }
    [data-testid="stSidebar"] * {
        color: #ffffff !important;
    }
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
    [data-testid="stExpander"] {
        background-color: #ffffff !important;
        border: 1px solid #e0e0e0;
        border-radius: 8px;
    }
    [data-testid="stExpander"] * {
        color: #333333 !important;
    }
    .stTextInput > div > div > input {
        border: 2px solid #1a2744;
        border-radius: 8px;
        font-size: 16px;
        padding: 12px;
        color: #333333 !important;
    }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# Initialise session state
if "module" not in st.session_state:
    st.session_state.module = "lexsearch"
if "history" not in st.session_state:
    st.session_state.history = []
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Sidebar Navigation
with st.sidebar:
    st.markdown("## ⚖️ LexIndia")
    st.markdown("*Your AI Legal Assistant*")
    st.markdown("---")
    st.markdown("### Navigation")

    with st.expander("🔍 Research", expanded=True):
        if st.button("LexSearch - Case Research"):
            st.session_state.module = "lexsearch"
        if st.button("LexPlain - Law Explainer"):
            st.session_state.module = "lexplain"
        if st.button("LexConstitute - Constitutional Advisor"):
            st.session_state.module = "lexconstitute"
        if st.button("LexGlobe - International Law"):
            st.session_state.module = "lexglobe"

    with st.expander("✍️ Drafting"):
        if st.button("LexScan - Document Analyser"):
            st.session_state.module = "lexscan"
        if st.button("LexDraft - Draft Generator"):
            st.session_state.module = "lexdraft"
        if st.button("LexDebate - Counter Argument Generator"):
            st.session_state.module = "lexdebate"

    with st.expander("📁 File Management"):
        if st.button("LexDiary - Case Diary"):
            st.session_state.module = "lexdiary"
        if st.button("LexVault - File Storage"):
            st.session_state.module = "lexvault"
        if st.button("LexChat - Legal Chatbot"):
            st.session_state.module = "lexchat"
        if st.button("LexTrack - Live Case Updates"):
            st.session_state.module = "lextrack"

    with st.expander("📊 Intelligence"):
        if st.button("LexPredict - Outcome Predictor"):
            st.session_state.module = "lexpredict"
        if st.button("LexBench - Judge Analysis"):
            st.session_state.module = "lexbench"
        if st.button("LexPulse - Trend Dashboard"):
            st.session_state.module = "lexpulse"
        if st.button("LexVoice - Regional Languages"):
            st.session_state.module = "lexvoice"
        if st.button("LexMap - Court Locator"):
            st.session_state.module = "lexmap"

    st.markdown("---")
    st.markdown("### 🕐 Recent Searches")
    if st.session_state.history:
        for item in reversed(st.session_state.history[-10:]):
            st.markdown(f"**{item['module']}**")
            st.markdown(f"*{item['query'][:60]}...*" if len(item['query']) > 60 else f"*{item['query']}*")
            st.markdown("---")
    else:
        st.markdown("*No searches yet.*")
    st.markdown("*Powered by Indian Kanoon API and Claude AI*")

# Main Page Header
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

# ─── LEXSEARCH MODULE ────────────────────────────────────────────────────────
if st.session_state.module == "lexsearch":
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

    if search_clicked and search_query:
        st.session_state.history.append({"module": "🔍 LexSearch", "query": search_query})
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

# ─── LEXPLAIN MODULE ─────────────────────────────────────────────────────────
elif st.session_state.module == "lexplain":
    st.markdown("## 📖 LexPlain — Law Explainer")
    st.markdown("*Type any legal concept, section, or term and get a plain language explanation.*")
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 4, 1])
    with col2:
        with st.form("lexplain_form"):
            legal_query = st.text_input(
                label="Legal Query",
                placeholder="e.g. What is res judicata? Explain Section 302 IPC. What is anticipatory bail?",
                label_visibility="collapsed"
            )
            explain_clicked = st.form_submit_button("💡 Explain")
            if explain_clicked and not legal_query:
                st.warning("Please enter a legal concept to explain.")
    if explain_clicked and legal_query:
        st.session_state.history.append({"module": "📖 LexPlain", "query": legal_query})
        with st.spinner("Generating explanation..."):
            client = anthropic.Anthropic(api_key=CLAUDE_API_KEY)
            prompt = f"""You are a legal expert specializing in Indian law.

A lawyer or law student has asked: "{legal_query}"

Please provide:
1. Simple plain language explanation (as if explaining to a non-lawyer)
2. Technical legal definition
3. Key elements or requirements
4. Relevant Indian laws, sections, or articles
5. Important cases that established or clarified this concept
6. Practical examples of how this applies in real cases

Be clear, accurate, and practical."""
            try:
                message = client.messages.create(
                    model="claude-haiku-4-5-20251001",
                    max_tokens=4096,
                    messages=[{"role": "user", "content": prompt}]
                )
                st.markdown("### 💡 Explanation")
                st.markdown(message.content[0].text)
            except Exception as e:
                st.error(f"Error: {str(e)}")

# ─── LEXDEBATE MODULE ─────────────────────────────────────────────────────────
elif st.session_state.module == "lexdebate":
    st.markdown("## ⚔️ LexDebate - Counter Argument Finder")
    st.markdown("*Enter your legal argument and get the strongest counter arguments from Indian case law.*")
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 4, 1])
    with col2:
        with st.form("lexdebate_form"):
            argument = st.text_area(
                label="Legal Argument",
                placeholder="e.g. My client should get bail because he has no prior criminal record...",
                height=150,
                label_visibility="collapsed"
            )
            debate_clicked = st.form_submit_button("⚔️ Find Counter Arguments")
            if debate_clicked and not argument:
                st.warning("Please enter a legal argument.")
    if debate_clicked and argument:
        st.session_state.history.append({"module": "⚔️ LexDebate", "query": argument[:80]})
        with st.spinner("Finding counter arguments..."):
            client = anthropic.Anthropic(api_key=CLAUDE_API_KEY)
            prompt = f"""You are a senior Indian lawyer preparing for the opposing side.

A lawyer has made this argument:
"{argument}"

Please provide:
1. The strongest counter-arguments the opposing counsel will make
2. Indian cases that support the opposing position
3. Weaknesses in the original argument
4. How the original lawyer can strengthen their argument
5. Relevant sections or provisions the opposing side will cite

Be specific, cite actual Indian cases, and be practical for a courtroom setting."""
            try:
                message = client.messages.create(
                    model="claude-haiku-4-5-20251001",
                    max_tokens=4096,
                    messages=[{"role": "user", "content": prompt}]
                )
                st.markdown("### ⚔️ Counter Arguments")
                st.markdown(message.content[0].text)
            except Exception as e:
                st.error(f"Error: {str(e)}")

# ─── LEXCONSTITUTE MODULE ────────────────────────────────────────────────────
elif st.session_state.module == "lexconstitute":
    st.markdown("## 🏛️ LexConstitute - Constitutional Advisor")
    st.markdown("*Ask any constitutional question and get an answer with relevant Articles, landmark cases, amendments, and live current affairs.*")
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 4, 1])
    with col2:
        with st.form("lexconstitute_form"):
            const_query = st.text_input(
                label="Constitutional Query",
                placeholder="e.g. What are the limits of Article 19? Explain basic structure doctrine.",
                label_visibility="collapsed"
            )
            const_clicked = st.form_submit_button("🏛️ Get Constitutional Analysis")
            if const_clicked and not const_query:
                st.warning("Please enter a constitutional question.")
    if const_clicked and const_query:
        st.session_state.history.append({"module": "🏛️ LexConstitute", "query": const_query})
        with st.spinner("Searching for latest developments..."):
            try:
                tavily_client = TavilyClient(api_key=TAVILY_API_KEY)
                search_results = tavily_client.search(
                    query=f"{const_query} India Supreme Court 2024 2025",
                    search_depth="basic",
                    max_results=5
                )
                recent_news = ""
                for result in search_results.get("results", []):
                    recent_news += f"- {result['title']}: {result['content'][:300]}\n"
            except Exception:
                recent_news = "No recent news available."
        with st.spinner("Generating constitutional analysis..."):
            client = anthropic.Anthropic(api_key=CLAUDE_API_KEY)
            prompt = f"""You are a constitutional law expert specializing in Indian law.

Question: "{const_query}"

Recent news and developments from the web:
{recent_news}

Please provide:
1. Constitutional provisions — relevant Articles with exact text
2. Simple plain language explanation of each Article with real life examples
3. Landmark Supreme Court cases that established key principles
4. Current legal position — how courts interpret this today
5. Recent developments — based on the news above
6. Practical implications for lawyers and citizens
7. Constitutional Amendments — relevant amendments that changed this provision
8. Pending issues — unresolved constitutional questions

Be thorough, cite actual cases, and include current affairs where relevant."""
            try:
                message = client.messages.create(
                    model="claude-haiku-4-5-20251001",
                    max_tokens=4096,
                    messages=[{"role": "user", "content": prompt}]
                )
                st.markdown("### 🏛️ Constitutional Analysis")
                st.markdown(message.content[0].text)
            except Exception as e:
                st.error(f"Error: {str(e)}")

# ─── LEXCHAT MODULE ──────────────────────────────────────────────────────────

elif st.session_state.module == "lexchat":
    st.markdown("## 💬 LexChat - Legal Chatbot")
    st.markdown("*Describe your legal situation and get expert advice. Ask follow-up questions.*")
    st.markdown("---")
    
    st.warning("⚠️ **Privacy Notice:** Do not enter client names, case numbers, or any identifying information. Use generic terms like 'my client', 'the accused', 'the complainant'. Your conversation is processed by AI servers.")
    
    # Show conversation history
    for message in st.session_state.chat_history:
        if message["role"] == "user":
            st.markdown(f"**🧑‍⚖️ You:** {message['content']} ")
        else:
            st.markdown(f"**⚖️ LexChat:** {message['content']}")
        st.markdown("---")
        
    # Clear chat button
    if st.session_state.chat_history:
        if st.button("🗑️ Clear Chat"):
            st.session_state.chat_history = []
            st.rerun()
            
    # Input form
    col1, col2, col3 = st.columns([1,4,1])
    with col2:
        with st.form("lexchat_form"):
            user_message = st.text_area(
                label = "Your message",
                placeholder="e.g. My client hit someone with a car. Person is injured. What should I do immediately?",
                height=100,
                label_visibility="collapsed"
            )
            chat_clicked = st.form_submit_button("💬 Send")
            if chat_clicked and not user_message:
                st.warning("Please type your message.")
                
            if chat_clicked and user_message:
                st.session_state.history.append({"module": "💬 LexChat", "query": user_message[:80]})
                st.session_state.chat_history.append({"role": "user", "content": user_message})
                with st.spinner("LexChat is thinking..."):
                    client = anthropic.Anthropic(api_key=CLAUDE_API_KEY)
                    system_prompt = """You are LexChat — a legendary legal mind with over 50 years of experience in Indian and international law.

Your background:
- Former Supreme Court of India advocate with 500+ landmark cases
- Retired High Court Judge with expertise in constitutional, criminal, and civil law
- Deep knowledge of IPC, CrPC, BNS, BNSS, Indian Evidence Act, Constitution of India
- Expert in international law, human rights law, and comparative jurisprudence
- Have appeared before the Supreme Court, High Courts, Sessions Courts, and Tribunals
- Authored legal commentaries and textbooks on Indian criminal and constitutional law
- Mentored hundreds of lawyers across India

Your approach:
- You give precise, practical, actionable legal advice
- You always cite the exact section, article, or case with year and court
- You think like both a defence lawyer AND a prosecutor — you see all angles
- You explain complex law in simple language without losing accuracy
- You anticipate what the opposing side will argue
- You know which judges are strict, which courts are lenient, which arguments work
- You understand the ground reality of Indian courts — not just textbook law

Your rules:
- Never give vague or generic answers
- Always be specific to Indian law and Indian court procedure
- Cite BNS/BNSS for new cases, IPC/CrPC for old cases
- Never encourage sharing client names, case numbers, or identifying details
- If you do not know something — say so honestly rather than guessing
- Always tell the lawyer what to do NEXT — immediate steps, not just theory

You are the lawyer every lawyer wishes they could call at midnight before a hearing."""
                    try:
                        message = client.messages.create(
                            model="claude-haiku-4-5-20251001",
                            max_tokens=4096,
                            system=system_prompt,
                            messages=st.session_state.chat_history
                        )
                        assistant_response = message.content[0].text
                        st.session_state.chat_history.append({"role": "assistant", "content": assistant_response})
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {str(e)}")