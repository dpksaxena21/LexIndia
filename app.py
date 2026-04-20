# LexIndia: Streamlit Web Interface
# Built by: Deepak Saxena

import streamlit as st
import requests
import os
import re
import anthropic
from dotenv import load_dotenv
from tavily import TavilyClient
from docx import Document
from docx.shared import Pt, Inches
from io import BytesIO

load_dotenv()
INDIAN_KANOON_TOKEN = os.getenv("INDIAN_KANOON_TOKEN")
CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
ECOURTS_API_KEY = os.getenv("ECOURTS_API_KEY")

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

        # Search India Code for statutory text
        with st.spinner("Searching India Code for statutory text..."):
            try:
                tavily_client = TavilyClient(api_key=TAVILY_API_KEY)
                india_code_results = tavily_client.search(
                    query=f"{search_query} site:indiacode.nic.in",
                    search_depth="basic",
                    max_results=3
                )
                india_code_text = ""
                for result in india_code_results.get("results", []):
                    india_code_text += f"**{result['title']}**\n{result['content'][:500]}\n\n"
                if india_code_text:
                    st.markdown("### 📜 Statutory Text — India Code")
                    st.markdown(india_code_text)
                    st.markdown("---")
            except Exception:
                pass

        with st.spinner("Searching Indian Kanoon for cases..."):
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

# ─── LEXTRACK MODULE ─────────────────────────────────────────────────────────

elif st.session_state.module == "lextrack":
    st.markdown("## 📡 LexTrack — Live Case Updates")
    st.markdown("*Enter a CNR number to get real-time case status, hearing dates, and orders.*")
    st.markdown("---")
    
    st.info("💡 **What is CNR?** Every court case in India has a unique CNR (Case Number Record). Format: DLHC010001232024 — State code + Court code + Case number + Year")
    
    col1, col2, col3 = st.columns([1,4,1])
    with col2:
        with st.form("lextrack_form"):
            cnr_number = st.text_input(
                label="CNR Number",
                placeholder="e.g. DLHC010001232024",
                label_visibility="collapsed"
            )
            track_clicked = st.form_submit_button("📡 Track Case")
            if track_clicked and not cnr_number:
                st.warning("Please enter a CNR Number")
            if track_clicked and cnr_number:
                st.session_state.history.append({"module": "📡 LexTrack", "query": cnr_number})
                with st.spinner("Fetching live case data from eCourts..."):
                    try:
                        url = f"https://webapi.ecourtsindia.com/api/partner/case/{cnr_number.strip().upper()}"
                        headers = {"Authorization": f"Bearer {ECOURTS_API_KEY}"}
                        response = requests.get(url, headers=headers)
                        if response.status_code == 200:
                            data = response.json()
                            st.success("✅ Case found!")
                            st.markdown("---")
                            
                        
                            # Case Details
                            st.markdown("### 📋 Case Details")
                            case_data = data.get('data', {}).get('courtCaseData', {})
                            entity_info = data.get('data', {}).get('entityInfo', {})
                            col1, col2 = st.columns(2)
                            with col1:
                                st.markdown(f"**Case Number:** {case_data.get('filingNumber', 'N/A')}")
                                st.markdown(f"**Case Type:** {case_data.get('caseTypeRaw', 'N/A')}")
                                st.markdown(f"**Filing Date:** {case_data.get('filingDate', 'N/A')}")
                                st.markdown(f"**Status:** {case_data.get('caseStatus', 'N/A')}")
                            with col2:
                                st.markdown(f"**Court:** {case_data.get('courtName', 'N/A')}")
                                st.markdown(f"**Judge:** {', '.join(case_data.get('judges', ['N/A']))}")
                                st.markdown(f"**Next Hearing:** {entity_info.get('nextDateOfHearing', 'N/A')}")
                                st.markdown(f"**Last Hearing:** {case_data.get('lastHearingDate', 'N/A')}")

                            # Parties
                            st.markdown("---")
                            st.markdown("### 👥 Parties")
                            col1, col2 = st.columns(2)
                            with col1:
                                st.markdown(f"**Petitioner:** {', '.join(case_data.get('petitioners', ['N/A']))}")
                            with col2:
                                st.markdown(f"**Respondent:** {', '.join(case_data.get('respondents', ['N/A']))}")

                            # Orders
                            # Orders
                            orders = case_data.get('judgmentOrders', [])
                            files = data.get('data', {}).get('files', {}).get('files', [])
                            if orders:
                                st.markdown("---")
                                st.markdown("### 📄 Recent Orders")
                                for i, order in enumerate(orders[:3]):
                                    st.markdown(f"**{order.get('orderDate', 'N/A')}** — {order.get('orderType', 'N/A')}")
                                    if i < len(files):
                                        markdown_content = files[i].get('markdownContent', '')
                                        if markdown_content:
                                            with st.expander("📖 Read Full Order"):
                                                st.markdown(markdown_content)

                            # IAs
                            ias = case_data.get('interlocutoryApplications', [])
                            if ias:
                                st.markdown("---")
                                st.markdown("### 📑 Interlocutory Applications")
                                for ia in ias[:3]:
                                    st.markdown(f"**{ia.get('regNo', 'N/A')}** — Filed by: {ia.get('filedBy', 'N/A')} — Status: {ia.get('status', 'N/A')}")
                                           
                        elif response.status_code == 404:
                            st.error("Case not found. Please check the CNR Number and try again")
                        elif response.status_code == 401:
                            st.error("API authentication failed. Please check your API key.")
                        else:
                            st.error(f"Error fetching case data. Status: {response.status_code}")
                    except Exception as e:
                        st.error(f"Connection error: {str(e)}")

# ─── LEXDRAFT MODULE ─────────────────────────────────────────────────────────
elif st.session_state.module == "lexdraft":
    st.markdown("## ✍️ LexDraft — Legal Document Generator")
    st.markdown("*Select a document type, fill in the details, and get a professionally drafted legal document.*")
    st.markdown("---")

    st.info("🤖 **LexDraft AI** is purpose-built for Indian legal drafting — trained on Indian court formats, BNS/BNSS/CPC provisions, and High Court filing standards. Documents are generated with court-accurate structure and legal language. Please review for factual accuracy and verify case citations before filing, as AI may occasionally make errors in specific citations or local court rules.")

    doc_category = st.selectbox("Select Category", [
        "Criminal",
        "Supreme Court",
        "High Court",
        "Civil",
        "Affidavits",
        "Notices",
        "General"
    ])

    doc_types = {
        "Criminal": [
            "Regular Bail Application (S.483 BNSS)",
            "Anticipatory Bail Application (S.482 BNSS)",
            "Quashing Petition (S.528 BNSS)",
            "Discharge Application",
            "Bail Cancellation Opposition",
            "Revision Petition (Criminal)",
            "Default Bail Application (S.187 BNSS)",
            "Surrender Application"
        ],
        "Supreme Court": [
            "SLP (Civil) — Art. 136",
            "SLP (Criminal) — Art. 136",
            "Civil Appeal",
            "Criminal Appeal",
            "Review Petition",
            "Curative Petition",
            "Writ Petition (Art. 32) — Fundamental Rights",
            "Transfer Petition"
        ],
        "High Court": [
            "Writ Petition (Art. 226) — Mandamus",
            "Writ Petition (Art. 226) — Certiorari",
            "Writ Petition (Art. 226) — Habeas Corpus",
            "Writ Appeal",
            "Criminal Appeal",
            "Criminal Revision Petition",
            "Anticipatory Bail (High Court)",
            "Letters Patent Appeal"
        ],
        "Civil": [
            "Plaint",
            "Written Statement",
            "Interlocutory Application",
            "Contempt Petition",
            "Execution Application",
            "Revision Petition (Civil)",
            "Appeal against Decree",
            "Injunction Application (Order 39 CPC)"
        ],
        "Affidavits": [
            "General Affidavit",
            "Supporting Affidavit",
            "Counter Affidavit",
            "Rejoinder Affidavit",
            "Affidavit of Assets and Liabilities",
            "Affidavit of Undertaking",
            "Affidavit in lieu of Examination in Chief"
        ],
        "Notices": [
            "Legal Notice",
            "Reply to Legal Notice",
            "Cheque Bounce Notice (S.138 NI Act)",
            "Consumer Complaint Notice",
            "RTI Application",
            "Section 80 CPC Notice",
            "Eviction Notice",
            "Defamation Notice"
        ],
        "General": [
            "Vakalatnama",
            "Memo of Appearance",
            "Power of Attorney (General)",
            "Power of Attorney (Special)",
            "Rent Agreement",
            "MOU (Memorandum of Understanding)",
            "Settlement Agreement",
            "Consumer Complaint (NCDRC/State/District)"
        ]
    }

    doc_type = st.selectbox("Select Document Type", doc_types[doc_category])

    st.markdown("---")
    st.markdown("### 📝 Fill in the Details")

    col1, col2 = st.columns(2)
    with col1:
        court_name = st.text_input("Court Name", placeholder="e.g. High Court of Delhi at New Delhi")
        petitioner_name = st.text_input("Petitioner / Applicant Name", placeholder="e.g. Ramesh Kumar")
        respondent_name = st.text_input("Respondent Name", placeholder="e.g. State of Delhi")
    with col2:
        case_number = st.text_input("Case Number (if any)", placeholder="e.g. FIR No. 123/2024")
        petitioner_advocate = st.text_input("Advocate Name", placeholder="e.g. Adv. Suresh Sharma")
        date = st.text_input("Date", placeholder="e.g. 21st April 2025")

    facts = st.text_area("Brief Facts of the Case", placeholder="Describe the facts of the case in brief...", height=150)
    grounds = st.text_area("Grounds / Prayer", placeholder="List the grounds for relief or specific prayer...", height=100)

    if st.button("✍️ Generate Document"):
        if not petitioner_name or not facts:
            st.warning("Please fill in at least Petitioner Name and Facts.")
        else:
            with st.spinner("Drafting your legal document..."):
                client = anthropic.Anthropic(api_key=CLAUDE_API_KEY)
                prompt = f"""You are a senior Indian lawyer with 30 years of experience drafting legal documents for Indian courts.

Document Type: {doc_type}
Court: {court_name}
Case Number: {case_number}
Petitioner/Applicant: {petitioner_name}
Respondent: {respondent_name}
Advocate: {petitioner_advocate}
Date: {date}
Facts: {facts}
Grounds/Prayer: {grounds}

STRICT FORMATTING RULES:
- Follow exact Indian court formatting standards
- Use proper legal language — "respectfully showeth", "humbly prays", "most respectfully"
- All sections must be numbered
- Include proper cause title
- Always end with PRAYER clause and VERIFICATION where required
- Cite BNS/BNSS for offences after July 2024, IPC/CrPC for older matters

DOCUMENT TEMPLATES:

═══ REGULAR BAIL APPLICATION (S.439 BNSS) ═══
IN THE COURT OF [COURT NAME]
BAIL APPLICATION NO. ___ OF [YEAR]

IN THE MATTER OF:
[ACCUSED NAME] ... Applicant/Accused
VERSUS
STATE OF [STATE] ... Respondent

APPLICATION FOR REGULAR BAIL UNDER SECTION 483 BNSS, 2023

MOST RESPECTFULLY SHOWETH:
1. That the applicant [name], aged [age], S/o [father], resident of [address], is the accused in FIR No. [X]/[YEAR] registered at PS [Name] under Sections [X] BNS, 2023.
2. That the applicant was arrested on [date] and has been in judicial custody since [date].
3. That the chargesheet has/has not been filed.
4. [Additional facts]

GROUNDS:
I. That the applicant has deep roots in the community and is not a flight risk.
II. That the applicant has no prior criminal antecedents.
III. That the allegations are false and motivated.
IV. That the investigation is complete and custody is not required.
V. That Article 21 of the Constitution guarantees right to personal liberty.
VI. That the offence is [bailable/triable by Magistrate].

PRAYER:
It is prayed that this Hon'ble Court may be pleased to:
(a) Release the applicant on bail on such terms as deemed fit;
(b) Pass any other order in the interest of justice.

Place: [City]               [Advocate Name]
Date: [Date]                Advocate for Applicant

VERIFICATION:
I, [Name], verify that the contents are true and correct to the best of my knowledge. Verified at [Place] on [Date].

═══ ANTICIPATORY BAIL APPLICATION (S.438 BNSS) ═══
IN THE COURT OF [SESSIONS COURT / HIGH COURT]
ANTICIPATORY BAIL APPLICATION NO. ___ OF [YEAR]

IN THE MATTER OF:
[APPLICANT NAME] ... Applicant
VERSUS
STATE OF [STATE] ... Respondent

APPLICATION FOR ANTICIPATORY BAIL UNDER SECTION 438 BNSS, 2023

MOST RESPECTFULLY SHOWETH:
1. That the applicant apprehends arrest in connection with [case/FIR details].
2. That the applicant is [description — occupation, address, background].
3. That the applicant has not been arrested and no FIR has been registered / FIR No. [X] has been registered.
4. [Facts explaining why arrest is apprehended]

GROUNDS:
I. That the apprehension of arrest is well-founded.
II. That the applicant is innocent and has been falsely implicated.
III. That the applicant is a respectable member of society with no criminal antecedents.
IV. That the applicant undertakes to cooperate with the investigation.
V. That custodial interrogation is not required.

PRAYER:
It is prayed that this Hon'ble Court may be pleased to:
(a) Direct that in the event of arrest, the applicant be released on bail;
(b) Grant interim protection from arrest till disposal of this application;
(c) Pass any other order in the interest of justice.

Place: [City]               [Advocate Name]
Date: [Date]                Advocate for Applicant

VERIFICATION:
Verified at [Place] on [Date] that contents are true and correct.

═══ QUASHING PETITION (S.528 BNSS) ═══
IN THE HIGH COURT OF [STATE] AT [CITY]
CRIMINAL MISCELLANEOUS PETITION NO. ___ OF [YEAR]

IN THE MATTER OF:
[PETITIONER NAME] ... Petitioner
VERSUS
STATE OF [STATE] AND ANR. ... Respondents

PETITION UNDER SECTION 528 BNSS, 2023 FOR QUASHING OF FIR NO. [X]/[YEAR]

MOST RESPECTFULLY SHOWETH:
1. That the Petitioner challenges FIR No. [X]/[YEAR] registered at PS [Name] under Sections [X] BNS.
2. That the facts giving rise to the FIR are: [facts].
3. That the FIR is liable to be quashed on the following grounds.

GROUNDS:
I. That the FIR does not disclose any cognizable offence.
II. That the FIR is filed with malafide intent to harass the Petitioner.
III. That the matter is purely civil in nature and has been given criminal colour.
IV. That there has been a settlement between parties [if applicable].
V. That continuation of proceedings would be abuse of process of court.

PRAYER:
It is prayed that this Hon'ble Court may be pleased to:
(a) Quash FIR No. [X]/[YEAR] and all proceedings arising therefrom;
(b) Stay further investigation during pendency of this petition;
(c) Pass any other order as deemed fit.

Place: [City]               [Advocate Name]
Date: [Date]                Advocate for Petitioner

═══ DISCHARGE APPLICATION ═══
IN THE COURT OF [COURT NAME]
[CASE TYPE] NO. [NUMBER] OF [YEAR]

IN THE MATTER OF:
STATE OF [STATE] ... Prosecution
VERSUS
[ACCUSED NAME] ... Accused

APPLICATION FOR DISCHARGE UNDER SECTION 250 BNSS, 2023

MOST RESPECTFULLY SHOWETH:
1. That the applicant/accused is facing trial in the above case.
2. That chargesheet was filed on [date] under Sections [X] BNS.
3. That the material on record does not make out a prima facie case.
4. [Supporting facts]

GROUNDS:
I. That there is no sufficient ground for proceeding against the accused.
II. That the evidence collected during investigation is insufficient.
III. That the prosecution witnesses are unreliable.
IV. That the alleged offence is not made out from the facts on record.

PRAYER:
It is prayed that this Hon'ble Court may be pleased to:
(a) Discharge the accused from the charges framed;
(b) Pass any other order in the interest of justice.

Place: [City]               [Advocate Name]
Date: [Date]                Advocate for Accused

═══ DEFAULT BAIL APPLICATION (S.187 BNSS) ═══
IN THE COURT OF [COURT NAME]
BAIL APPLICATION NO. ___ OF [YEAR]

IN THE MATTER OF:
[ACCUSED NAME] ... Applicant
VERSUS
STATE OF [STATE] ... Respondent

APPLICATION FOR DEFAULT BAIL UNDER SECTION 187(3) BNSS, 2023

MOST RESPECTFULLY SHOWETH:
1. That the applicant was arrested on [date] in connection with FIR No. [X]/[YEAR] under Sections [X] BNS.
2. That [60/90] days have elapsed since the date of arrest.
3. That the investigation agency has failed to file chargesheet within the statutory period.
4. That the applicant is entitled to bail as a matter of right under Section 187(3) BNSS.

GROUNDS:
I. That the statutory period of [60/90] days has expired without filing of chargesheet.
II. That the right to default bail is an indefeasible right of the accused.
III. That the Supreme Court in Rakesh Kumar Paul v. State of Assam has held that default bail cannot be defeated.

PRAYER:
It is prayed that this Hon'ble Court may be pleased to:
(a) Release the applicant on default bail forthwith;
(b) Pass any other order in the interest of justice.

Place: [City]               [Advocate Name]
Date: [Date]                Advocate for Applicant

═══ REVISION PETITION (CRIMINAL) ═══
IN THE [SESSIONS COURT / HIGH COURT] OF [STATE]
CRIMINAL REVISION PETITION NO. ___ OF [YEAR]

IN THE MATTER OF:
[PETITIONER NAME] ... Petitioner/Revisionist
VERSUS
[RESPONDENT NAME] ... Respondent

CRIMINAL REVISION PETITION UNDER SECTION 442 BNSS, 2023
AGAINST ORDER DATED [DATE] PASSED BY [COURT NAME] IN [CASE NO.]

MOST RESPECTFULLY SHOWETH:
1. That the Petitioner is aggrieved by the order dated [date] passed by [court].
2. That the facts of the case are: [facts].
3. That the impugned order is illegal and liable to be set aside.

GROUNDS:
I. That the learned court below has committed an error of law.
II. That the impugned order is contrary to the evidence on record.
III. That the impugned order is perverse and arbitrary.
IV. That the court below failed to consider material evidence.

PRAYER:
It is prayed that this Hon'ble Court may be pleased to:
(a) Set aside/modify the impugned order dated [date];
(b) Pass such other order as deemed fit.

Place: [City]               [Advocate Name]
Date: [Date]                Advocate for Petitioner

═══ SLP (CIVIL/CRIMINAL) — ART. 136 ═══
IN THE SUPREME COURT OF INDIA
SPECIAL LEAVE PETITION ([CIVIL/CRIMINAL]) NO. ___ OF [YEAR]

IN THE MATTER OF:
[PETITIONER NAME] ... Petitioner(s)
VERSUS
[RESPONDENT NAME] ... Respondent(s)

SPECIAL LEAVE PETITION UNDER ARTICLE 136 OF THE CONSTITUTION OF INDIA
AGAINST JUDGMENT DATED [DATE] OF THE HIGH COURT OF [STATE] IN [CASE NO.]

MOST RESPECTFULLY SHOWETH:
1. That the Petitioner is aggrieved by the impugned judgment dated [date].
2. [Chronological facts]

QUESTIONS OF LAW:
A. Whether the High Court erred in [specific issue]?
B. Whether the judgment is contrary to settled law on [point]?

GROUNDS:
I. That the impugned judgment is contrary to law and facts.
II. That the High Court failed to appreciate [point].
III. That the matter involves substantial question of law of public importance.
IV. That the judgment is in conflict with Supreme Court precedents.

PRAYER:
It is prayed that this Hon'ble Court may be pleased to:
(a) Grant Special Leave to Appeal;
(b) Stay the impugned judgment;
(c) After admission, allow the appeal and set aside the impugned judgment;
(d) Pass any other order as deemed fit.

Place: [City]               [Advocate Name]
Date: [Date]                Advocate for Petitioner

═══ CIVIL APPEAL ═══
IN THE SUPREME COURT OF INDIA / HIGH COURT OF [STATE]
CIVIL APPEAL NO. ___ OF [YEAR]

IN THE MATTER OF:
[APPELLANT NAME] ... Appellant
VERSUS
[RESPONDENT NAME] ... Respondent

MEMORANDUM OF CIVIL APPEAL
AGAINST JUDGMENT DATED [DATE] OF [COURT] IN [CASE NO.]

MOST RESPECTFULLY SHOWETH:
1. That the Appellant is aggrieved by the judgment and decree dated [date].
2. [Facts]

GROUNDS OF APPEAL:
1. That the learned court below erred in [ground 1].
2. That the findings are contrary to evidence on record.
3. That the impugned judgment is perverse and unsustainable in law.

PRAYER:
It is prayed that this Hon'ble Court may be pleased to:
(a) Allow this appeal;
(b) Set aside the impugned judgment;
(c) Pass decree in favour of the Appellant;
(d) Award costs.

Place: [City]               [Advocate Name]
Date: [Date]                Advocate for Appellant

═══ REVIEW PETITION ═══
IN THE SUPREME COURT OF INDIA / HIGH COURT OF [STATE]
REVIEW PETITION NO. ___ OF [YEAR]
IN [CASE TYPE] NO. [NUMBER] OF [YEAR]

IN THE MATTER OF:
[PETITIONER NAME] ... Petitioner
VERSUS
[RESPONDENT NAME] ... Respondent

REVIEW PETITION UNDER ORDER XLVII RULE 1 CPC / ARTICLE 137 OF THE CONSTITUTION

MOST RESPECTFULLY SHOWETH:
1. That the Petitioner seeks review of judgment dated [date] in [case no.].
2. That the following errors apparent on the face of record warrant review.

GROUNDS FOR REVIEW:
I. Error apparent on face of record: [specific error].
II. Discovery of new and important evidence: [details if applicable].
III. Any other sufficient reason: [details].

PRAYER:
It is prayed that this Hon'ble Court may be pleased to:
(a) Review and recall the judgment dated [date];
(b) After review, pass appropriate orders;
(c) Pass any other order as deemed fit.

Place: [City]               [Advocate Name]
Date: [Date]                Advocate for Petitioner

═══ CURATIVE PETITION ═══
IN THE SUPREME COURT OF INDIA
CURATIVE PETITION NO. ___ OF [YEAR]
IN [CASE TYPE] NO. [NUMBER] OF [YEAR]

IN THE MATTER OF:
[PETITIONER NAME] ... Petitioner
VERSUS
[RESPONDENT NAME] ... Respondent

CURATIVE PETITION UNDER ARTICLE 142 OF THE CONSTITUTION OF INDIA
[AS PER RUPA ASHOK HURRA v. ASHOK HURRA (2002) 4 SCC 388]

MOST RESPECTFULLY SHOWETH:
1. That all remedies including Review have been exhausted.
2. That the final judgment of this Court dated [date] suffers from grave miscarriage of justice.
3. That the present petition is certified by a Senior Advocate as per requirements.

GROUNDS:
I. That there has been violation of principles of natural justice.
II. That the petitioner was not heard before the order was passed.
III. That a Judge who was party to the lis participated in the decision.

PRAYER:
It is prayed that this Hon'ble Court may be pleased to:
(a) Exercise curative jurisdiction and recall the judgment dated [date];
(b) Pass appropriate orders to prevent miscarriage of justice.

Place: [City]               [Advocate Name]
Date: [Date]                Senior Advocate / Advocate for Petitioner

═══ WRIT PETITION (ART. 226 / ART. 32) ═══
IN THE [HIGH COURT OF [STATE] / SUPREME COURT OF INDIA]
WRIT PETITION ([CIVIL/CRIMINAL]) NO. ___ OF [YEAR]

IN THE MATTER OF:
[PETITIONER NAME]
S/o [Father], aged [Age], Resident of [Address] ... Petitioner
VERSUS
1. [RESPONDENT 1]
2. [RESPONDENT 2]                              ... Respondent(s)

WRIT PETITION UNDER ARTICLE [226/32] OF THE CONSTITUTION OF INDIA
SEEKING WRIT OF [MANDAMUS/CERTIORARI/HABEAS CORPUS/PROHIBITION/QUO WARRANTO]

MOST RESPECTFULLY SHOWETH:

FACTS:
1. That the Petitioner is [description].
2. [Chronological facts]

QUESTIONS OF LAW:
A. Whether [Question 1]?
B. Whether [Question 2]?

GROUNDS:
I. That the impugned action is violative of Article [14/19/21] of the Constitution.
II. That the Respondent has acted without jurisdiction.
III. That the Petitioner has exhausted all alternative remedies.
IV. That irreparable harm will be caused if relief is not granted.

PRAYER:
It is prayed that this Hon'ble Court may be pleased to:
(a) Issue writ of [MANDAMUS/CERTIORARI] directing [specific relief];
(b) Stay impugned order/action during pendency;
(c) Pass such other orders as deemed fit.

Date: [Date]                [Advocate Name]
Place: [City]               Advocate for Petitioner

═══ CONTEMPT PETITION ═══
IN THE [HIGH COURT / SUPREME COURT] OF [STATE]
CONTEMPT PETITION (CIVIL) NO. ___ OF [YEAR]
IN [ORIGINAL CASE NO.]

IN THE MATTER OF:
[PETITIONER NAME] ... Petitioner
VERSUS
[RESPONDENT/CONTEMNOR NAME] ... Respondent/Contemnor

CONTEMPT PETITION UNDER SECTION 11 OF THE CONTEMPT OF COURTS ACT, 1971
FOR WILFUL DISOBEDIENCE OF ORDER DATED [DATE]

MOST RESPECTFULLY SHOWETH:
1. That this Hon'ble Court passed an order dated [date] directing [specific direction].
2. That the Respondent/Contemnor was duly served with the said order.
3. That despite the order, the Respondent has wilfully failed to comply.
4. That the non-compliance is deliberate and intentional.

GROUNDS:
I. That the order dated [date] is clear and unambiguous.
II. That the Respondent has knowledge of the order.
III. That the non-compliance is wilful and deliberate.
IV. That the Petitioner has suffered prejudice due to non-compliance.

PRAYER:
It is prayed that this Hon'ble Court may be pleased to:
(a) Issue notice to the Respondent/Contemnor;
(b) Hold the Respondent guilty of contempt of court;
(c) Punish the Respondent as per law;
(d) Direct compliance of the order dated [date];
(e) Pass any other order as deemed fit.

Place: [City]               [Advocate Name]
Date: [Date]                Advocate for Petitioner

VERIFICATION:
Verified at [Place] on [Date] that contents are true and correct.

═══ REVISION PETITION (CIVIL) ═══
IN THE [DISTRICT COURT / HIGH COURT] OF [STATE]
CIVIL REVISION NO. ___ OF [YEAR]

IN THE MATTER OF:
[PETITIONER NAME] ... Petitioner/Revisionist
VERSUS
[RESPONDENT NAME] ... Respondent

CIVIL REVISION PETITION UNDER SECTION 115 CPC
AGAINST ORDER DATED [DATE] PASSED BY [COURT] IN [CASE NO.]

MOST RESPECTFULLY SHOWETH:
1. That the Petitioner is aggrieved by the order dated [date].
2. [Facts of the original case]
3. That the impugned order is illegal and erroneous.

GROUNDS:
I. That the court below has exercised jurisdiction not vested in it by law.
II. That the court below has failed to exercise jurisdiction vested in it.
III. That the court below has acted illegally or with material irregularity.
IV. That the impugned order has caused grave injustice to the Petitioner.

PRAYER:
It is prayed that this Hon'ble Court may be pleased to:
(a) Call for the record of the case;
(b) Set aside/modify the impugned order;
(c) Pass such other order as deemed fit.

Place: [City]               [Advocate Name]
Date: [Date]                Advocate for Petitioner

═══ PLAINT ═══
IN THE COURT OF [COURT NAME]
CIVIL SUIT NO. ___ OF [YEAR]

[PLAINTIFF NAME]
S/o [Father], aged [Age], Resident of [Address]  ... Plaintiff
VERSUS
[DEFENDANT NAME]
Resident of [Address]                            ... Defendant

PLAINT UNDER ORDER VII RULE 1 CPC

MOST RESPECTFULLY SHOWETH:

1. CAUSE OF ACTION: The cause of action arose on [date] at [place] within jurisdiction of this Court.
2. VALUATION: The suit is valued at Rs. [Amount] for court fees and jurisdiction.
3. LIMITATION: The suit is within limitation as [reason].

FACTS:
4. [Numbered chronological facts]

LEGAL GROUNDS:
5. [Legal basis for the claim]

PRAYER:
Wherefore it is prayed that this Court may pass a decree:
(a) For [recovery of money / permanent injunction / declaration / specific performance];
(b) For interest at [X]% per annum;
(c) For costs of the suit;
(d) For such other relief as deemed fit.

Date: [Date]                [Advocate Name]
Place: [City]               Advocate for Plaintiff

VERIFICATION:
I, [Plaintiff Name], verify that the contents are true and correct to the best of my knowledge. Verified at [Place] on [Date].

═══ WRITTEN STATEMENT ═══
IN THE COURT OF [COURT NAME]
CIVIL SUIT NO. [NUMBER] OF [YEAR]

[PLAINTIFF NAME]                                 ... Plaintiff
VERSUS
[DEFENDANT NAME]                                 ... Defendant

WRITTEN STATEMENT ON BEHALF OF DEFENDANT
FILED UNDER ORDER VIII RULE 1 CPC

PRELIMINARY OBJECTIONS:
1. That the suit is not maintainable in law or on facts.
2. That this Court has no territorial/pecuniary jurisdiction.
3. That the suit is barred by limitation under Article [X] of the Limitation Act.
4. That the plaintiff has no cause of action against the defendant.
5. That the suit is bad for non-joinder of necessary parties.

REPLY ON MERITS:
Para-wise reply to plaint:
Para 1: [Admitted / Denied / Not admitted]
Para 2: [Response]
[Continue para by para]

ADDITIONAL FACTS IN DEFENCE:
1. [Facts supporting defendant's case]

PRAYER:
It is prayed that the suit be dismissed with exemplary costs.

Date: [Date]                [Advocate Name]
Place: [City]               Advocate for Defendant

VERIFICATION:
I, [Defendant Name], verify that the contents are true and correct. Verified at [Place] on [Date].

═══ INTERLOCUTORY APPLICATION ═══
IN THE COURT OF [COURT NAME]
[CASE TYPE] NO. [NUMBER] OF [YEAR]

IN THE MATTER OF:
[PETITIONER NAME] ... Petitioner/Applicant
VERSUS
[RESPONDENT NAME] ... Respondent

INTERLOCUTORY APPLICATION NO. ___ OF [YEAR]
FOR [STAY / INJUNCTION / DIRECTION / EXEMPTION]

MOST RESPECTFULLY SHOWETH:
1. That the above case is pending before this Court.
2. That the Applicant seeks interim relief on the following grounds.
3. [Facts necessitating interim relief]

GROUNDS:
I. That there is a prima facie case in favour of the Applicant.
II. That the balance of convenience lies in favour of granting relief.
III. That irreparable loss and injury will be caused if relief is not granted.
IV. That the Respondent will not suffer any prejudice.

PRAYER:
It is prayed that this Hon'ble Court may be pleased to:
(a) [Grant specific interim relief — stay/injunction/direction];
(b) Pass any other order as deemed fit.

Place: [City]               [Advocate Name]
Date: [Date]                Advocate for Applicant

VERIFICATION:
Verified at [Place] on [Date] that contents are true and correct.

═══ EXECUTION APPLICATION ═══
IN THE COURT OF [COURT NAME]
EXECUTION PETITION NO. ___ OF [YEAR]
IN CIVIL SUIT / DECREE NO. [NUMBER] OF [YEAR]

[DECREE HOLDER NAME] ... Decree Holder
VERSUS
[JUDGMENT DEBTOR NAME] ... Judgment Debtor

APPLICATION FOR EXECUTION OF DECREE UNDER ORDER XXI CPC

MOST RESPECTFULLY SHOWETH:
1. That this Court passed a decree dated [date] in [case no.] in favour of the Decree Holder.
2. That the decree is for [payment of Rs. X / delivery of property / specific performance].
3. That the Judgment Debtor has failed to comply with the decree.
4. That the decree has not been satisfied till date.

GROUNDS:
I. That the decree is final and executable.
II. That the Judgment Debtor is deliberately avoiding compliance.
III. That the Decree Holder is entitled to execution as per law.

PRAYER:
It is prayed that this Court may be pleased to:
(a) Execute the decree dated [date] against the Judgment Debtor;
(b) Attach and sell the property of Judgment Debtor;
(c) Issue warrant of arrest of Judgment Debtor [if applicable];
(d) Pass any other order as deemed fit.

Place: [City]               [Advocate Name]
Date: [Date]                Advocate for Decree Holder

═══ INJUNCTION APPLICATION (ORDER 39 CPC) ═══
IN THE COURT OF [COURT NAME]
CIVIL SUIT NO. ___ OF [YEAR]

[PLAINTIFF NAME] ... Plaintiff
VERSUS
[DEFENDANT NAME] ... Defendant

APPLICATION UNDER ORDER XXXIX RULES 1 AND 2 CPC
FOR TEMPORARY INJUNCTION

MOST RESPECTFULLY SHOWETH:
1. That the above suit is filed for [relief sought].
2. That the Defendant threatens to [specific act causing harm].
3. [Facts establishing urgency]

GROUNDS:
I. PRIMA FACIE CASE: That the Plaintiff has a strong prima facie case.
II. BALANCE OF CONVENIENCE: That balance of convenience favours the Plaintiff.
III. IRREPARABLE INJURY: That the Plaintiff will suffer irreparable loss if injunction is not granted.
IV. That the Defendant has no right to [specific act].

PRAYER:
It is prayed that this Court may be pleased to:
(a) Grant ad-interim temporary injunction restraining the Defendant from [specific act] during pendency of suit;
(b) Make the injunction absolute after notice;
(c) Pass any other order as deemed fit.

Place: [City]               [Advocate Name]
Date: [Date]                Advocate for Plaintiff

═══ GENERAL AFFIDAVIT ═══
AFFIDAVIT

I, [Full Name], S/o [Father's Name], aged [Age] years, Occupation: [Occupation],
Resident of [Complete Address],
do hereby solemnly affirm and state on oath as under:

1. That I am the deponent herein and am fully conversant with the facts stated herein.
2. That [Content — numbered paragraphs].
3. That this affidavit is made for the purpose of [purpose] and for no other purpose.

DEPONENT

VERIFICATION:
Verified at [Place] on [Date] that the contents of the above affidavit are true and correct to the best of my knowledge, belief and information. Nothing material has been concealed.

DEPONENT

Solemnly affirmed before me on [Date] at [Place].

NOTARY / OATH COMMISSIONER

═══ SUPPORTING AFFIDAVIT ═══
IN THE COURT OF [COURT NAME]
[CASE TYPE] NO. [NUMBER] OF [YEAR]

AFFIDAVIT IN SUPPORT OF [PETITION/APPLICATION]

I, [Full Name], S/o [Father's Name], aged [Age] years, Resident of [Address],
being the Petitioner/Applicant in the above matter, do hereby solemnly affirm and state as under:

1. That I am the Petitioner in the above case and am fully aware of the facts.
2. That the contents of the accompanying [petition/application/plaint] have been drafted under my instructions.
3. That the facts stated in the accompanying [document] are true and correct to the best of my knowledge.
4. That [Additional supporting facts].
5. That I have not suppressed any material fact from this Hon'ble Court.

DEPONENT

VERIFICATION:
Verified at [Place] on [Date] that the contents of the above affidavit are true and correct to the best of my knowledge and belief.

DEPONENT
[NOTARY/OATH COMMISSIONER]

═══ COUNTER AFFIDAVIT ═══
IN THE COURT OF [COURT NAME]
[CASE TYPE] NO. [NUMBER] OF [YEAR]

[PETITIONER NAME] ... Petitioner
VERSUS
[RESPONDENT NAME] ... Respondent

COUNTER AFFIDAVIT ON BEHALF OF RESPONDENT

I, [Full Name], S/o [Father's Name], aged [Age] years, Designation: [X],
[Organisation/Address], being the Respondent/authorised representative,
do hereby solemnly affirm and state as under:

1. That I am the Respondent and am authorised to file this counter affidavit.
2. Para-wise reply to the petition:
   Para 1 of petition: [Admitted / Denied with reasons]
   Para 2 of petition: [Response]
   [Continue para by para]
3. That the petition is misconceived and liable to be dismissed.
4. That [Additional facts in support of Respondent's case].
5. That the Petitioner has suppressed material facts from this Court.

DEPONENT

VERIFICATION:
Verified at [Place] on [Date] that the contents are true and correct to the best of my knowledge and belief.

DEPONENT
[NOTARY/OATH COMMISSIONER]

═══ REJOINDER AFFIDAVIT ═══
IN THE COURT OF [COURT NAME]
[CASE TYPE] NO. [NUMBER] OF [YEAR]

[PETITIONER NAME] ... Petitioner
VERSUS
[RESPONDENT NAME] ... Respondent

REJOINDER AFFIDAVIT ON BEHALF OF PETITIONER

I, [Full Name], S/o [Father's Name], aged [Age] years, Resident of [Address],
being the Petitioner in the above matter, do hereby solemnly affirm and state as under:

1. That I have read the Counter Affidavit filed by the Respondent.
2. Para-wise reply to Counter Affidavit:
   Para 1 of Counter Affidavit: [Admitted / Denied / Response]
   Para 2: [Response]
   [Continue para by para]
3. That the contents of the Counter Affidavit are denied except what is specifically admitted.
4. That [Additional facts in rebuttal].
5. That the petition deserves to be allowed.

DEPONENT

VERIFICATION:
Verified at [Place] on [Date] that the contents are true and correct.

DEPONENT
[NOTARY/OATH COMMISSIONER]

═══ AFFIDAVIT OF ASSETS AND LIABILITIES ═══
AFFIDAVIT OF ASSETS AND LIABILITIES

I, [Full Name], S/o [Father's Name], aged [Age] years, Resident of [Address],
do hereby solemnly affirm and state as under:

MOVABLE ASSETS:
1. Bank Accounts: [Details of accounts, balances]
2. Vehicles: [Details]
3. Jewellery: [Details and approximate value]
4. Investments/Shares/FDs: [Details]
5. Cash in hand: Rs. [Amount]

IMMOVABLE ASSETS:
1. Property 1: [Address, area, approximate value]
2. Property 2: [Details]

LIABILITIES:
1. Loans: [Details of outstanding loans]
2. Other liabilities: [Details]

That the above information is true and correct to the best of my knowledge.

DEPONENT

VERIFICATION:
Verified at [Place] on [Date].
DEPONENT
[NOTARY]

═══ AFFIDAVIT OF UNDERTAKING ═══
AFFIDAVIT OF UNDERTAKING

I, [Full Name], S/o [Father's Name], aged [Age] years, Resident of [Address],
do hereby solemnly affirm and undertake as under:

1. That I undertake to [specific undertaking — appear before court / not leave country / report to police etc.].
2. That I undertake to comply with all conditions imposed by this Hon'ble Court.
3. That I am aware that breach of this undertaking may result in [consequences].
4. That this undertaking is given voluntarily and without any coercion.

DEPONENT

VERIFICATION:
Verified at [Place] on [Date].
DEPONENT
[NOTARY/OATH COMMISSIONER]

═══ LEGAL NOTICE ═══
[ADVOCATE NAME]
ADVOCATE — [BAR COUNCIL]
[OFFICE ADDRESS]
Enrollment No.: [X] | Phone: [X]

Date: [Date]
By Registered Post A.D. / Speed Post

To,
[Recipient Name]
[Complete Address]

Sub: LEGAL NOTICE

Sir/Madam,

Under specific instructions from and on behalf of my client [Client Name],
S/o [Father], Resident of [Address], I hereby serve upon you the following legal notice:

1. That my client [background].
2. [Chronological facts — numbered]
3. That despite [demand/request dated X], you have failed to [comply].
4. That your conduct has caused my client [loss/damage/injury].

You are hereby called upon to [specific demand — pay Rs. X / vacate premises / perform obligation]
within [15/30] days from receipt of this notice,
failing which my client shall be constrained to initiate appropriate
[civil / criminal] proceedings against you before the competent court,
entirely at your cost and consequences, without any further notice.

This notice is without prejudice to all other rights and remedies available to my client.

Yours faithfully,

[Advocate Name]
Advocate for [Client Name]

(Note: Please acknowledge receipt. Copy retained.)

═══ REPLY TO LEGAL NOTICE ═══
[ADVOCATE NAME]
ADVOCATE
[ADDRESS]

Date: [Date]
By Registered Post A.D.

To,
[Original Notice Sender's Advocate Name]
[Address]

Sub: REPLY TO YOUR LEGAL NOTICE DATED [DATE] ON BEHALF OF [CLIENT NAME]

Sir/Madam,

I have received your legal notice dated [date] on behalf of [Noticee's client name].
Under instructions from my client [Client Name], I give the following reply:

1. That the contents of the notice are denied except what is specifically admitted herein.
2. That [Para-wise reply to each allegation in notice].
3. That the claim of Rs. [X] is [denied/disputed] for the following reasons: [reasons].
4. That my client has [already complied / is ready to comply / has no liability].

Without prejudice to the above, my client reserves all rights and remedies.

Yours faithfully,

[Advocate Name]
Advocate for [Client Name]

═══ CHEQUE BOUNCE NOTICE (S.138 NI ACT) ═══
[ADVOCATE NAME], ADVOCATE
[ADDRESS] | Enrollment No. [X]

Date: [Date]
By Registered Post A.D.

To,
[Drawer/Accused Name]
[Complete Address]

Sub: STATUTORY NOTICE UNDER SECTION 138 READ WITH SECTION 142
OF THE NEGOTIABLE INSTRUMENTS ACT, 1881

Sir/Madam,

Under instructions from my client [Payee/Complainant Name], I hereby give you notice:

1. That you had issued Cheque No. [X] dated [Date] for Rs. [Amount]/- (Rupees [in words] only)
   drawn on [Bank Name], [Branch Name], Account No. [X],
   towards [discharge of legally enforceable liability / loan repayment / payment for goods etc.].

2. That the said cheque was presented for encashment on [date] and was
   returned/dishonoured on [date] with the memo "[Insufficient Funds / Account Closed / Payment Stopped]".

3. That the dishonour of the cheque constitutes an offence punishable under Section 138
   of the Negotiable Instruments Act, 1881.

You are hereby called upon to pay Rs. [Amount]/- (Rupees [in words]) to my client
within FIFTEEN DAYS from the date of receipt of this notice.

In the event of failure to make payment within the said period, my client shall be
constrained to initiate criminal proceedings against you under Section 138 of the
Negotiable Instruments Act, 1881 before the competent Magistrate,
without any further notice to you.

[Advocate Name]
Advocate for [Payee/Client Name]

═══ CONSUMER COMPLAINT NOTICE ═══
Date: [Date]

To,
[Opposite Party — Company/Service Provider Name]
[Registered Office Address]

Sub: LEGAL NOTICE UNDER THE CONSUMER PROTECTION ACT, 2019

Sir/Madam,

Under instructions from my client [Consumer Name], Resident of [Address], I serve this notice:

1. That my client availed [goods/services] from you on [date] for Rs. [Amount].
2. That the [goods were defective / service was deficient] in the following manner: [details].
3. That despite complaint dated [date], you have failed to redress the grievance.
4. That my client has suffered loss of Rs. [Amount] on account of your deficiency in service.

You are hereby called upon to [refund Rs. X / replace the product / provide proper service]
within 15 days, failing which my client shall file a Consumer Complaint before the
[District/State/National] Consumer Disputes Redressal Commission,
seeking compensation including damages and litigation costs.

[Advocate Name]
Advocate for [Consumer/Client Name]

═══ SECTION 80 CPC NOTICE ═══
Date: [Date]
By Registered Post A.D.

To,
1. The Secretary, [Government Department],
   Government of [State/India], [Address]
2. [Other Government Official if applicable]

Sub: NOTICE UNDER SECTION 80 OF THE CODE OF CIVIL PROCEDURE, 1908

Sir,

Under instructions from my client [Client Name], I hereby give you notice of
intention to institute a civil suit against the Government of [State/India] and
its officials in respect of the following:

1. That my client [description].
2. [Facts of the case — numbered paragraphs].
3. That the Government/its official has caused loss of Rs. [Amount] to my client by [act/omission].
4. That my client intends to file a civil suit for [recovery/injunction/declaration].

This notice is given as required under Section 80 CPC before institution of suit.
If the matter is not settled within [60] days, suit shall be filed without further notice.

[Advocate Name]
Advocate for [Client Name]

═══ EVICTION NOTICE ═══
Date: [Date]

To,
[Tenant Name]
[Property Address]

Sub: NOTICE TO VACATE PREMISES

Sir/Madam,

Under instructions from my client [Landlord Name], owner of the premises situated at
[Complete Property Address], I hereby serve you with this eviction notice:

1. That my client is the lawful owner of the above premises.
2. That you have been occupying the said premises as tenant since [date] at monthly rent of Rs. [X].
3. That [Reason for eviction — non-payment of rent / expiry of lease / personal requirement etc.].
4. That despite [oral/written] request, you have failed to vacate.

You are hereby called upon to vacate and hand over peaceful possession of the premises
within [15/30] days from receipt of this notice,
failing which my client shall be compelled to initiate eviction proceedings before the
Rent Controller/Civil Court at your risk and cost.

[Advocate Name]
Advocate for [Landlord/Client Name]

═══ DEFAMATION NOTICE ═══
Date: [Date]

To,
[Defamer's Name]
[Address]

Sub: LEGAL NOTICE FOR DEFAMATION

Sir/Madam,

Under instructions from my client [Client Name], I hereby serve this legal notice:

1. That my client is a [description — professional/businessman/public figure].
2. That you have made the following false and defamatory statement(s) on [date/platform]:
   "[Exact defamatory statement]"
3. That the said statement is false, baseless and made with malicious intent.
4. That the statement has caused serious damage to my client's reputation and career.

You are hereby called upon to:
(a) Immediately retract the said statement;
(b) Issue a public apology to my client;
(c) Pay damages of Rs. [Amount] towards loss of reputation.

Failing compliance within 7 days, my client shall initiate both civil and criminal
proceedings for defamation under Section 356 BNS, 2023 without further notice.

[Advocate Name]
Advocate for [Client Name]

═══ RTI APPLICATION ═══
To,
The Public Information Officer,
[Name of Public Authority],
[Complete Address]

Sub: APPLICATION UNDER SECTION 6(1) OF THE RIGHT TO INFORMATION ACT, 2005

Sir/Madam,

I, [Full Name], S/o [Father's Name], aged [Age] years,
Resident of [Complete Address], Phone: [X], Email: [X],
wish to obtain the following information under RTI Act, 2005:

INFORMATION SOUGHT:
1. [Specific Question 1 — be precise and specific]
2. [Specific Question 2]
3. [Additional queries]

Period for which information is sought: [From Date] to [To Date]

I am depositing the prescribed fee of Rs. 10/- by [Cash/DD/IPO/Online].
I belong to [BPL category — exempt from fee / General category].

If the information is not held by your office, please transfer under Section 6(3) RTI Act.

Date: [Date]                    Signature
Place: [City]                   [Full Name]
                                [Contact Details]

═══ VAKALATNAMA ═══
IN THE COURT OF [COURT NAME]
[CASE TYPE] NO. [NUMBER] OF [YEAR]

VAKALATNAMA

I/We, [Client Full Name], S/o/D/o/W/o [Father/Husband Name],
aged [Age] years, Resident of [Complete Address],
being the [Petitioner/Respondent/Accused/Complainant] in the above case,
do hereby appoint, retain and authorise:

SHRI/SMT. [ADVOCATE NAME]
Advocate, [State Bar Council]
Enrollment No.: [X]
Office Address: [Address]

to appear, plead, act and represent me/us in the above noted case and in
all proceedings arising therefrom or connected therewith including
execution proceedings, review petitions, and any appeals.

I/We further authorise the said Advocate to:
(a) Sign, verify and file all pleadings, petitions, applications and documents on my/our behalf;
(b) Engage or instruct any other Advocate to appear in this matter;
(c) Accept service of all processes and notices on my/our behalf;
(d) Compromise or settle the matter if deemed appropriate;
(e) Take all such steps as may be necessary for the proper conduct of this case.

I/We agree to ratify all acts done by the said Advocate in pursuance of this authority.
I/We undertake to pay all fees, charges and expenses as agreed.

Date: [Date]                    Signature/Thumb Impression
Place: [City]                   [Client Name]
                                [Contact No.]

Accepted: [Advocate Signature]

═══ MEMO OF APPEARANCE ═══
IN THE COURT OF [COURT NAME]
[CASE TYPE] NO. [NUMBER] OF [YEAR]

MEMO OF APPEARANCE

[Advocate Name], Advocate, Enrollment No. [X],
[Office Address],
hereby enters appearance on behalf of the [Petitioner/Respondent/Accused/Complainant]
in the above case.

Date: [Date]                    [Advocate Name]
Place: [City]                   Advocate for [Party Name]
                                Enrollment No.: [X]

═══ POWER OF ATTORNEY ═══
GENERAL / SPECIAL POWER OF ATTORNEY

I, [Grantor Full Name], S/o [Father], aged [Age], Resident of [Address] (GRANTOR),

do hereby appoint [Attorney Name], S/o [Father], aged [Age], Resident of [Address] (ATTORNEY),
as my true and lawful Attorney to act on my behalf.

I hereby authorise my said Attorney to do the following acts:

[FOR GENERAL POA:]
1. To manage, supervise and look after all my movable and immovable properties.
2. To appear before all courts, tribunals and authorities.
3. To execute documents, deeds and agreements on my behalf.
4. To receive and give receipts for all moneys due to me.
5. To do all other acts necessary for the above purposes.

[FOR SPECIAL POA — add specific purpose:]
To specifically: [Specific act — sell property at X / appear in case no. X / manage bank account X]

I agree to ratify all acts of my Attorney done under this Power of Attorney.

In witness whereof I set my hand this [date] at [place].

Signature: _______________
[Grantor Name]

WITNESSES:
1. [Witness 1 Name, Address, Signature]
2. [Witness 2 Name, Address, Signature]

[NOTARY]

═══ RENT AGREEMENT ═══
RENT AGREEMENT

This Rent Agreement is executed on [Date] at [Place] between:

LANDLORD: [Full Name], S/o [Father], aged [Age], Resident of [Address] (hereinafter "Landlord")

AND

TENANT: [Full Name], S/o [Father], aged [Age], Resident of [Address] (hereinafter "Tenant")

WHEREAS the Landlord is the owner of premises situated at [Complete Property Address]
(hereinafter "Premises").

NOW THIS AGREEMENT WITNESSETH AS UNDER:

1. TERM: The Landlord agrees to let and the Tenant agrees to take the Premises on rent for a period of [11 months] commencing from [date] to [date].

2. RENT: Monthly rent of Rs. [Amount]/- payable on or before [5th] of each month.

3. SECURITY DEPOSIT: Rs. [Amount]/- paid as refundable security deposit.

4. PURPOSE: The Premises shall be used for [residential/commercial] purpose only.

5. MAINTENANCE: Minor repairs shall be done by Tenant. Major structural repairs by Landlord.

6. SUBLETTING: The Tenant shall not sublet the Premises without written consent.

7. TERMINATION: Either party may terminate with [1 month] written notice.

8. UTILITIES: [Electricity/Water/Society maintenance] charges shall be paid by Tenant.

9. RENEWAL: The agreement may be renewed by mutual consent.

10. GOVERNING LAW: This agreement shall be governed by the laws of India.

IN WITNESS WHEREOF the parties have signed this agreement on the date first mentioned.

LANDLORD: _______________        TENANT: _______________
[Name]                           [Name]

WITNESSES:
1. _______________
2. _______________

═══ MOU (MEMORANDUM OF UNDERSTANDING) ═══
MEMORANDUM OF UNDERSTANDING

This MOU is entered into on [Date] between:

PARTY 1: [Full Name/Company Name], Resident/Registered at [Address] (hereinafter "Party 1")

AND

PARTY 2: [Full Name/Company Name], Resident/Registered at [Address] (hereinafter "Party 2")

BACKGROUND:
[Brief background of why this MOU is being executed]

NOW THE PARTIES AGREE AS UNDER:

1. PURPOSE: The purpose of this MOU is to [describe purpose].

2. OBLIGATIONS OF PARTY 1:
   (a) [Obligation 1]
   (b) [Obligation 2]

3. OBLIGATIONS OF PARTY 2:
   (a) [Obligation 1]
   (b) [Obligation 2]

4. DURATION: This MOU shall remain in force for [period] from the date of signing.

5. CONFIDENTIALITY: Both parties agree to maintain confidentiality of information shared.

6. DISPUTE RESOLUTION: Disputes shall be resolved by [arbitration/mediation/courts at City].

7. GOVERNING LAW: This MOU shall be governed by the laws of India.

8. NON-BINDING: [If applicable] This MOU is not legally binding and represents only the intent of the parties.

IN WITNESS WHEREOF the parties have signed this MOU on the date mentioned above.

PARTY 1: _______________         PARTY 2: _______________
[Name]                           [Name]
[Date]                           [Date]

═══ SETTLEMENT AGREEMENT ═══
SETTLEMENT AGREEMENT

This Settlement Agreement is entered into on [Date] between:

PARTY 1: [Full Name], Resident of [Address] (hereinafter "Party 1")

AND

PARTY 2: [Full Name], Resident of [Address] (hereinafter "Party 2")

WHEREAS a dispute existed between the parties regarding [nature of dispute];

AND WHEREAS the parties have amicably resolved the dispute;

NOW THIS AGREEMENT WITNESSETH:

1. That Party 2 agrees to pay Party 1 a sum of Rs. [Amount]/- in full and final settlement.
2. Payment schedule: [Rs. X on date / in installments]
3. That upon receipt of the said amount, Party 1 agrees to withdraw [case no. / complaint].
4. That both parties release each other from all claims arising from the dispute.
5. That this settlement is in full and final satisfaction of all claims.
6. That neither party shall initiate any future proceedings regarding this dispute.

IN WITNESS WHEREOF the parties sign this agreement on [date].

PARTY 1: _______________         PARTY 2: _______________

WITNESSES:
1. _______________
2. _______________

═══ CONSUMER COMPLAINT (COMMISSION) ═══
BEFORE THE [DISTRICT/STATE/NATIONAL] CONSUMER DISPUTES REDRESSAL COMMISSION
[PLACE]

COMPLAINT NO. ___ OF [YEAR]

[COMPLAINANT NAME]
S/o [Father], aged [Age], Resident of [Address]   ... Complainant
VERSUS
[OPPOSITE PARTY NAME]
[Registered Address]                              ... Opposite Party

CONSUMER COMPLAINT UNDER SECTION 35 OF THE CONSUMER PROTECTION ACT, 2019

MOST RESPECTFULLY SHOWETH:

1. That the Complainant is a consumer as defined under Section 2(7) of the Consumer Protection Act, 2019.
2. That the Opposite Party is engaged in [business description].
3. That on [date], the Complainant availed [goods/services] from the Opposite Party for Rs. [Amount].
4. That the [goods were defective as per Section 2(10) / service was deficient as per Section 2(11)].
5. [Detailed facts of deficiency]

GROUNDS:
I. That the Opposite Party is guilty of deficiency in service under Section 2(11) CPA 2019.
II. That the Opposite Party indulged in unfair trade practice under Section 2(47).
III. That the Complainant has suffered monetary loss of Rs. [Amount].
IV. That this Commission has jurisdiction as the claim is within [District/State/National] limits.

RELIEF CLAIMED:
(a) Refund of Rs. [Amount] paid;
(b) Compensation of Rs. [Amount] for deficiency in service;
(c) Rs. [Amount] for mental agony and harassment;
(d) Litigation costs of Rs. [Amount];
(e) Any other relief as deemed fit.

Date: [Date]                    [Complainant/Advocate Name]
Place: [City]

VERIFICATION:
I, [Complainant Name], verify that the contents are true and correct. Verified at [Place] on [Date].

Now using ALL the above templates as exact format guides, draft the complete {doc_type} using the specific details provided.
Fill every placeholder with the actual information given.
Do not leave any section incomplete.
Use BNS/BNSS for matters after July 2024, IPC/CrPC for older matters.
Make it professional, complete and ready to file in Indian courts."""

                try:
                    message = client.messages.create(
                        model="claude-haiku-4-5-20251001",
                        max_tokens=4096,
                        messages=[{"role": "user", "content": prompt}]
                    )
                    st.markdown("---")
                    st.markdown("### 📄 Generated Document")
                    
                    generated_doc = message.content[0].text
                    st.markdown(generated_doc)
                    st.session_state.history.append({"module": "✍️ LexDraft", "query": f"{doc_type} - {petitioner_name}"})
                    
                    st.markdown("---")
                    # Generate Word document
                    doc = Document()
                    # Set margins
                    for section in doc.sections:
                        section.top_margin = Inches(1)
                        section.bottom_margin = Inches(1)
                        section.left_margin = Inches(1.25)
                        section.right_margin = Inches(1.25)
                    # Add content line by line
                    for line in generated_doc.split('\n'):
                        clean_line = line.strip()
                        # Remove markdown bold markers
                        clean_line = clean_line.replace('**', '').replace('*', '').replace('###', '').replace('##', '').replace('#', '')
                        if clean_line == '---' or clean_line == '':
                            doc.add_paragraph('')
                        else:
                            para = doc.add_paragraph(clean_line)
                            para.runs[0].font.size = Pt(12)
                            para.runs[0].font.name = 'Times New Roman'
                    # Save to buffer
                    buffer = BytesIO()
                    doc.save(buffer)
                    buffer.seek(0)
                    file_name = f"{doc_type}_{petitioner_name}_{date}.docx".replace(" ", "_").replace("/", "_").replace("(", "").replace(")", "")
                    st.download_button(
                        label="⬇️ Download as Word Document (.docx)",
                        data=buffer,
                        file_name=file_name,
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                    )
                except Exception as e:
                    st.error(f"Error: {str(e)}")
                                
# ─── COMING SOON MODULES ─────────────────────────────────────────────────────
else:
    st.markdown("## 🚧 Coming Soon")
    st.markdown(f"**{st.session_state.module.upper()}** is under development.")
    st.markdown("We are building this module. Check back soon.")
    st.markdown("---")
    st.markdown("Meanwhile, use **LexSearch** or **LexPlain** from the sidebar.")