# LexIndia - An AI assistant for Indian lawyers
# Built by: Deepak Saxena
# Version: 1.0
import re
import requests
import os
from dotenv import load_dotenv
import anthropic

load_dotenv()

INDIAN_KANOON_TOKEN = os.getenv("INDIAN_KANOON_TOKEN")
CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY")

app_name = "LexIndia"
version = "1.0"
divider = "=" * 40

print(divider)
print(f"Welcome to {app_name} - Your AI Legal Assistant")
print(divider)
print("Loading Indian Law Database...")
print("Ready to assist lawyers")
print(divider)
print(f"{app_name} Version: {version}")

# Testing Internet Connection
print(divider)
print("Testing Internet Connection...")
response = requests.get("https://httpbin.org/get")
if response.status_code == 200:
    print("Internet Connection: Successful")
else:
    print("Internet Connection: Failed")
print(divider)

# Testing Indian Kanoon API
if INDIAN_KANOON_TOKEN:
    print("API Key: Loaded Successfully")
else:
    print("API Key: Not Found. Please check your .env file.")

# Testing Claude API
if CLAUDE_API_KEY:
    print("Claude API Key: Loaded Successfully")
else:
    print("API Key: Not Found. Please check your .env file.")
# Function to search for cases using Indian Kanoon API

def summarize_case(title, court, date, judgment_text = ''):
    client = anthropic.Anthropic(api_key = CLAUDE_API_KEY)

    if judgment_text:
        content = f"Here is the full judgment text:\n{judgment_text[:6000]}"
    else:
        content = f"Case: {title}\nCourt: {court}\nDate: {date}"

    prompt = f"""You are a legal assistant specializing in Indian law.

{content}

Please provide:
1. Brief facts of the case
2. What the court decided
3. The key legal principle established
4. How a lawyer can use this case in arguments
5. Any similar cases that can be cited along with this case
6. Any potential weaknesses in the case that opposing counsel might exploit

Keep the summary concise and practical for a practicing lawyer."""

    try:
        message = client.messages.create(
            model = "claude-haiku-4-5-20251001",
            max_tokens= 2048,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        return message.content[0].text
    except Exception as e:
        return f"Error: {str(e)}"
    
def fetch_judgment(doc_id):
    url = f"https://api.indiankanoon.org/doc/{doc_id}/"
    headers = {"Authorization": f"Token {INDIAN_KANOON_TOKEN}"}
    try:
        response = requests.post(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            return data.get('doc', '')
        else:
            return ''
    except Exception as e:
            return ''

def search_cases(query):
    print(divider)
    print(f"searching for {query}")

    params = {"formInput": query, "pagenum": 0}
    url = "https://api.indiankanoon.org/search/"

    headers = {"Authorization": f"Token {INDIAN_KANOON_TOKEN}"}

    try:
        search_response = requests.post(url, headers=headers, params=params)
        if search_response.status_code == 200:
            results = search_response.json()
            print(f"Total Results Found: {results['found']}")
            print(divider)
            for doc in results['docs'][:3]:
                clean_title = re.sub(r'<[^>]+>', '', doc['title'])
                clean_court = re.sub(r'<[^>]+>', '', doc['docsource'])
                doc_id = doc['tid']
                print(f"Case: {clean_title}")
                print(f"Court: {clean_court}")
                print(f"Date: {doc['publishdate']}")
                print("Fetching full judgment...")
                judgment_text = fetch_judgment(doc_id)
                print('AI Summary:')
                print(summarize_case(clean_title, clean_court, doc['publishdate'],judgment_text))
                print(divider)
        
        else:
            print(f"Search Failed. Status Code: {search_response.status_code}")
    except Exception as e:
        print("Connection Error. Please Check Your Internet and Try Again Later.")


search_history = []

while True:
    search_query = input("\nEnter your legal query here: ")
    if search_query.strip().lower() == "exit":
        print(divider)
        print("Your search history:")
    
        for i, search in enumerate(search_history):
            print(f"{i+1}. {search}")
        print(divider)
        print("Thank you for using LexIndia. Goodbye!")
        break
    if len(search_query.strip()) < 5:
        print("Please enter a valid legal query.")
        continue
    search_history.append(search_query)
    search_cases(search_query)