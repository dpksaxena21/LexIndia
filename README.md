# ⚖️ LexIndia — AI-Powered Legal Research Assistant for Indian Courts

> India's most comprehensive AI legal research platform — built for practicing lawyers, law students, and legal professionals.

🌐 **Live Demo:** [lexindia.streamlit.app](https://lexindia.streamlit.app)
📦 **GitHub:** [github.com/dpksaxena21/LexIndia](https://github.com/dpksaxena21/LexIndia)

---

## 🚀 What is LexIndia?

LexIndia is an AI-powered legal research SaaS with 14 working modules covering every aspect of Indian legal practice — from case research and document drafting to live court tracking and outcome prediction.

Built as a full-stack portfolio project using Python, Streamlit, and 4 live API integrations.

---

## 🧩 14 Modules

| Module | Description |
|--------|-------------|
| 🔍 **LexSearch** | Search 27 crore Indian court cases with AI summaries |
| 📖 **LexPlain** | Plain language explanation of any law or legal concept |
| ⚔️ **LexDebate** | Counter argument finder using Indian case law |
| 🏛️ **LexConstitute** | Constitutional analysis with live Supreme Court updates |
| 💬 **LexChat** | AI legal chatbot with 50-year expert persona |
| 📡 **LexTrack** | Live case tracking by CNR number or party/advocate name |
| ✍️ **LexDraft** | Generate 56 types of legal documents with Word download |
| 🔬 **LexScan** | Upload PDF/Image/Word → AI document analysis with OCR |
| 🌍 **LexGlobe** | International law arsenal — 12-part analysis with ECHR, ICJ, UN treaties |
| 📅 **LexCause** | Daily cause list from eCourts — know your schedule before you leave home |
| 📊 **LexPredict** | Case outcome predictor with factor analysis dashboard and bar charts |
| ⚖️ **LexBench** | Judge analysis — past judgments, judicial philosophy, courtroom strategy |
| 📰 **LexPulse** | Live legal news, Supreme Court updates, trending legal issues |
| 🗺️ **LexMap** | Court locator with Google Maps — find courts, filing guidance, directions |

---

## 🔌 APIs Integrated

- **Indian Kanoon API** — 27 crore Indian court judgments
- **Anthropic Claude API** — Claude Haiku (fast) + Claude Sonnet (deep analysis)
- **Tavily Search API** — Live web search for recent judgments and news
- **eCourts India Partner API** — Live case data, cause lists, CNR lookup

---

## 🛠️ Tech Stack
Python 3.11
Streamlit 1.56
Anthropic SDK 0.91
Tavily Python 0.7
Requests 2.33
python-docx 1.2
PyMuPDF 1.27 (OCR)
pandas

---

## ⚙️ Setup & Run Locally

```bash
# Clone the repo
git clone https://github.com/dpksaxena21/LexIndia.git
cd LexIndia

# Create virtual environment
python -m venv vakilai_env
vakilai_env\Scripts\activate  # Windows
source vakilai_env/bin/activate  # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Add your API keys to .env
INDIAN_KANOON_TOKEN=your_token
CLAUDE_API_KEY=your_key
TAVILY_API_KEY=your_key
ECOURTS_API_KEY=your_key

# Run
streamlit run app.py
```

---

## 🗺️ Roadmap

- [x] Streamlit MVP — 14 modules
- [ ] SDE Rebuild — React + FastAPI + PostgreSQL + Cloudflare R2
- [ ] User authentication and multi-lawyer support
- [ ] Persistent file storage (LexVault)
- [ ] Subscription pricing tiers
- [ ] Mobile app

---

## 👨‍💻 Built By

**Deepak Saxena** — Vaishali, Ghaziabad
Seeking opportunities in product, AI, and full-stack development.

[LinkedIn](https://linkedin.com/in/dpksaxena21) | [GitHub](https://github.com/dpksaxena21/LexIndia)

---

## ⚠️ Disclaimer

LexIndia is a research and portfolio project. AI-generated legal content should always be verified by a qualified advocate before use in court.