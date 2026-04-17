# ⚖️ LexIndia
### India's AI-Powered Legal Research Assistant

Built for Indian Lawyers. Powered by Indian Kanoon and Claude AI.

---

## What is LexIndia

LexIndia is an AI legal research tool that searches 10 million+ Indian court judgments and generates instant professional analysis — facts, court decisions, legal principles, how to use in arguments, similar cases, and weaknesses.

Built as India's answer to Harvey AI.

---

## Features

- 🔍 **LexSearch** — Search 10 million+ Indian court judgments live
- 🤖 **AI Analysis** — Claude AI reads actual judgment text and generates professional summaries
- 📌 **Best Match + Related Cases** — Clearly organised results
- 🔗 **Full Judgment Links** — Direct links to Indian Kanoon
- ⚖️ **All Courts** — Supreme Court, High Courts, District Courts, Tribunals
- 📱 **Web Interface** — Clean browser UI built with Streamlit
- ⌨️ **Terminal Version** — Command line interface for developers

---

## Tech Stack

- **Language** — Python
- **AI** — Anthropic Claude API (claude-haiku)
- **Case Database** — Indian Kanoon API (10M+ judgments)
- **Web UI** — Streamlit
- **Security** — python-dotenv for API key management

---

## How to Run

**1. Clone the repository**
git clone https://github.com/dpksaxena21/LexIndia.git
cd LexIndia

**2. Install dependencies**
pip install -r requirements.txt

**3. Set up API keys**

Create a `.env` file:
INDIAN_KANOON_TOKEN = your_indian_kanoon_token
CLAUDE_API_KEY = your_claude_api_key

**4. Run the web app**
streamlit run app.py

**5. Or run the terminal version**
python main.py

---

## Modules Planned

| Module | Description |
|--------|-------------|
| LexSearch | Case research |
| LexPlain | Law explainer |
| LexDraft | Document drafting |
| LexScan | Document analyser |
| LexTrack | Live SC case updates |
| LexVault | Secure file storage |
| LexPredict | Outcome predictor (ML) |
| LexVoice | Hindi/regional languages |
| LexMap | Court locator |

---

## Built By

**Deepak Saxena** — Delhi, India

---

*Built for Indian courts. Indian laws. Indian lawyers. Indian languages.*