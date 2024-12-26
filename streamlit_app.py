import streamlit as st
from gtts import gTTS
import smtplib
from email.mime.text import MIMEText
import requests
import google.generativeai as genai

DEEPTRANSLATE_API_KEY = "d5c0549879msh215534c0e781043p1ec76ajsn937e4b021336"
DEEPTRANSLATE_BASE_URL = "https://deep-translate1.p.rapidapi.com/language/translate/v2"

def translate_text(text, target_lang):
    if not DEEPTRANSLATE_API_KEY:
        return "Error: API key is not configured."
    
    if target_lang == "en":
        return text  # No translation needed for English

    try:
        payload = {"q": text, "target": target_lang, "source": "en"}
        headers = {
            "Content-Type": "application/json",
            "X-RapidAPI-Key": DEEPTRANSLATE_API_KEY,
            "X-RapidAPI-Host": "deep-translate1.p.rapidapi.com"
        }
        response = requests.post(DEEPTRANSLATE_BASE_URL, json=payload, headers=headers)
        print("Status Code:", response.status_code)  # Debugging
        print("Response Headers:", response.headers)  # Debugging
        print("Response Text:", response.text)  # Debugging
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx and 5xx)
        
        translated_text = response.json().get("data", {}).get("translations", {}).get("translatedText")
        if not translated_text:
            return "Error: No translated text returned from the API."
        
        return translated_text
    
    except requests.exceptions.RequestException as req_error:
        return f"Request error: {req_error}"
    except ValueError as val_error:
        return f"Value error: {val_error}"
    except Exception as general_error:
        return f"Unexpected error: {general_error}"

genai.configure(api_key="AIzaSyBzP_urPbe1zBnZwgjhSlVl-MWtUQMEqQA")

def generate_text(prompt):
    try:
        response = genai.chat(messages=[{"content": prompt}])
        return response['messages'][0]['content']
    except Exception as e:
        return f"Error generating content: {e}"


# DeepTranslate API configuration
DEEPTRANSLATE_API_KEY = "d5c0549879msh215534c0e781043p1ec76ajsn937e4b021336"

# Function to use DeepTranslate API for translations
def translate_text(text, target_lang):
    if target_lang == "en":
        return text
    try:
        url = "https://deep-translate1.p.rapidapi.com/language/translate/v2"
        payload = {"q": text, "target": target_lang}
        headers = {
            "content-type": "application/json",
            "X-RapidAPI-Key": DEEPTRANSLATE_API_KEY,
            "X-RapidAPI-Host": "deep-translate1.p.rapidapi.com"
        }
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        translated_text = response.json().get("data", {}).get("translations", {}).get("translatedText", text)
        return translated_text
    except Exception as e:
        st.error(f"Translation failed: {e}")
        return text

# Function for Text-to-Speech
def speak_text(text, lang="en"):
    translated_text = translate_text(text, lang)
    tts = gTTS(text=translated_text, lang=lang)
    audio_file_path = "audio.mp3"
    tts.save(audio_file_path)
    # Stream the audio directly
    with open(audio_file_path, "rb") as audio_file:
        st.audio(audio_file.read())

# Function to send email notification
def send_email(phone_number, recipient_email, message):
    email_address = "your_email@example.com"  # Replace with your email
    app_password = "your_app_password"       # Replace with your app password

    subject = "New Request"
    body = f"{message}\nContact Number: {phone_number}"

    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = email_address
    msg['To'] = recipient_email

    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(email_address, app_password)
            server.send_message(msg)
        return True
    except Exception as e:
        st.error(f"Failed to send email: {e}")
        return False

# App Title and Description
st.title("Akshara: Financial Empowerment for Rural Women in India")
st.write("""
### Welcome to Akshara! 🌸
Empowering women with tools for financial literacy, secure banking, and entrepreneurship.
""")

# Sidebar for Language Selection
languages = {"English": "en", "Hindi": "hi", "Tamil": "ta", "Telugu": "te", "Marathi": "mr"}
lang_choice = st.sidebar.selectbox("Choose Language / भाषा चुनें", list(languages.keys()))
selected_lang = languages[lang_choice]

# Section 1: Financial Literacy 
st.header(translate_text("📚 Financial Literacy Modules", selected_lang))

topics = ["Budgeting Basics", "Micro Investing", "Loan Essentials", "Emergency Funds"]
topic_choice = st.selectbox(translate_text("Choose a topic", selected_lang), topics)

# Predefined lesson content for each topic
lesson_contents = {
    "Budgeting Basics": "Budgeting Basics: Learn how to create and manage a budget to track your income and expenses effectively.",
    "Micro Investing": "Micro Investing: Discover how small investments can grow over time and build wealth for the future.",
    "Loan Essentials": "Loan Essentials: Understand the basics of loans, including interest rates, repayment terms, and responsible borrowing.",
    "Emergency Funds": "Emergency Funds: Learn the importance of saving for emergencies and how to build an emergency fund step by step."
}

if st.button(translate_text("Start Lesson", selected_lang)):
    lesson_content = lesson_contents.get(topic_choice, "No content available for this topic.")
    
    st.write(translate_text(lesson_content, selected_lang))
    speak_text(lesson_content, selected_lang)


# Section 2: Goal-Oriented Savings Plans
st.header(translate_text("💰 Goal-Oriented Savings", selected_lang))

savings_goal = st.text_input(translate_text("Enter your savings goal (e.g., Buy a cow, open a shop)", selected_lang))
duration = st.number_input(translate_text("How many months to save?", selected_lang), min_value=1, max_value=24)
amount = st.number_input(translate_text("Enter monthly saving amount (INR)", selected_lang), min_value=100)

if st.button(translate_text("Create Savings Plan", selected_lang)):
    total_savings = duration * amount
    st.write(translate_text(f"To achieve your goal of '{savings_goal}' in {duration} months, you need to save {amount} INR per month.", selected_lang))
    st.write(translate_text(f"Total Savings at the end of {duration} months: {total_savings} INR", selected_lang))
    speak_text(f"To achieve your goal of {savings_goal}, save {amount} rupees each month.", selected_lang)

# Section 3: Secure Banking Services
st.header(translate_text("🏦 Banking Services", selected_lang))

bank_options = ["Apply for Loan", "Track Expenses", "Emergency Fund Guidance"]
bank_service = st.selectbox(translate_text("Choose a service", selected_lang), bank_options)

if bank_service == "Apply for Loan":
    loan_amount = st.number_input(translate_text("Enter loan amount (INR)", selected_lang), min_value=1000)
    loan_duration = st.number_input(translate_text("Loan duration (months)", selected_lang), min_value=1, max_value=60)
    loan_purpose = st.text_input(translate_text("Purpose of the loan", selected_lang))
    phone_number = st.text_input(translate_text("Enter your phone number", selected_lang))
    
    if st.button(translate_text("Submit Loan Application", selected_lang)):
        loan_details = f"Loan Amount: {loan_amount} INR\nDuration: {loan_duration} months\nPurpose: {loan_purpose}\nContact: {phone_number}"
        loan_provider_email = "your_email@example.com"  # Replace with the recipient email
        
        if send_email(phone_number, loan_provider_email, loan_details):
            st.success(translate_text("Your loan application has been submitted!", selected_lang))
            speak_text("Your loan application has been submitted!", selected_lang)
        else:
            st.error(translate_text("There was an error sending your loan application.", selected_lang))

# API keys and configurations
DEEPTRANSLATE_API_KEY = "d5c0549879msh215534c0e781043p1ec76ajsn937e4b021336"
NEWSAPI_KEY = "81f1784ea2074e03a558e94c792af540"  # Your NewsAPI key
LLAMA_API_KEY = "LA-02542d15e16848df91306772181a65b8228bee4b269c478994888abe19a2ff11"  # Llama API key
SEARCH_ENGINE_ID = "10a125a1f8ed84071"  # Replace with your Search Engine ID
GOOGLE_SEARCH_API_KEY = "AIzaSyA-SzDdfHqkcHZwSTRXdy2VaVvrescYDUU"  # Replace with your Google Search API key

# Function to fetch Indian financial news using NewsAPI
def fetch_indian_financial_news():
    try:
        url = "https://newsapi.org/v2/everything"
        params = {
            "q": "Indian finance OR India economy OR stock market India OR finance India",
            "apiKey": NEWSAPI_KEY,
            "language": "en",
            "sortBy": "publishedAt",  # Sorting by publication date to get the latest news
        }
        response = requests.get(url, params=params)
        response.raise_for_status()
        news_data = response.json()
        articles = news_data.get("articles", [])
        if articles:
            return articles
        else:
            return "No Indian financial news available at the moment."
    except requests.exceptions.RequestException as e:
        return f"Error fetching Indian financial news: {e}"

# Function to perform search using Google Custom Search
import requests

import requests

# Function to perform a search using Google Custom Search API
def perform_search(query):
    try:
        url = "https://www.googleapis.com/customsearch/v1"
        params = {
            "q": query,
            "cx": SEARCH_ENGINE_ID,
            "key": GOOGLE_SEARCH_API_KEY,
        }
        response = requests.get(url, params=params)
        response.raise_for_status()
        results = response.json().get("items", [])
        if results:
            snippet = results[0].get("snippet", "No snippet available.")
            link = results[0].get("link", "No link available.")
            return snippet, link
        else:
            return None, "No results found."
    except requests.exceptions.RequestException as e:
        return None, f"Error during search: {e}"

# Function to summarize content using Llama API
def summarize_content_with_llama(content):
    try:
        url = "https://api.llama.ai/v1/completions"  # Replace with actual Llama API endpoint
        headers = {
            "Authorization": f"Bearer {LLAMA_API_KEY}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": "llama-2",
            "prompt": f"Please summarize the following text:\n{content}\nProvide a brief summary in plain language.",
            "temperature": 0.7,
            "max_tokens": 200  # Adjust summary length as needed
        }
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 401:
            return "Error: Unauthorized access. Check your API key or permissions."
        response.raise_for_status()
        return response.json().get("choices", [{}])[0].get("text", "No summary available.").strip()
    except requests.exceptions.RequestException as e:
        return f"Error summarizing content: {e}"

# Function to translate text using DeepTranslate
def translate_text(text, target_lang):
    if target_lang == "en":
        return text
    try:
        url = "https://deep-translate1.p.rapidapi.com/language/translate/v2"
        payload = {"q": text, "target": target_lang, "source": "en"}
        headers = {
            "Content-Type": "application/json",
            "X-RapidAPI-Key": DEEPTRANSLATE_API_KEY,
            "X-RapidAPI-Host": "deep-translate1.p.rapidapi.com",
        }
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()["data"]["translations"]["translatedText"]
    except requests.exceptions.RequestException as e:
        return f"Translation failed: {e}"

# Function to search, summarize, and translate
def search_and_explain(query, target_lang):
    snippet, link = perform_search(query)
    if not snippet:
        return f"No results found for {query}.\nError: {link}"
    
    summary = summarize_content_with_llama(snippet)
    if "Error" in summary:
        return summary
    
    translated_summary = translate_text(summary, target_lang)
    if "Translation failed" in translated_summary:
        return translated_summary
    
    return f"Explanation in {target_lang}:\n{translated_summary}\n\nSource: {link}"

# Function to translate text using DeepTranslate
def translate_text(text, target_lang):
    if target_lang == "en":
        return text
    try:
        url = "https://deep-translate1.p.rapidapi.com/language/translate/v2"
        payload = {"q": text, "target": target_lang, "source": "en"}
        headers = {
            "Content-Type": "application/json",
            "X-RapidAPI-Key": DEEPTRANSLATE_API_KEY,
            "X-RapidAPI-Host": "deep-translate1.p.rapidapi.com",
        }
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()["data"]["translations"]["translatedText"]
    except requests.exceptions.RequestException as e:
        return f"Translation failed: {e}"

# Function to search, summarize, and translate
def search_and_explain(query, target_lang):
    snippet, link = perform_search(query)
    if not snippet:
        return f"No results found for {query}.\nError: {link}"
    
    summary = summarize_content_with_llama(snippet)
    if "Error" in summary:
        return summary
    
    translated_summary = translate_text(summary, target_lang)
    if "Translation failed" in translated_summary:
        return translated_summary
    
    return f"Explanation in {target_lang}:\n{translated_summary}\n\nSource: {link}"


# Function to translate text using DeepTranslate
def translate_text(text, target_lang):
    if target_lang == "en":
        return text
    try:
        url = "https://deep-translate1.p.rapidapi.com/language/translate/v2"
        payload = {"q": text, "target": target_lang, "source": "en"}
        headers = {
            "Content-Type": "application/json",
            "X-RapidAPI-Key": DEEPTRANSLATE_API_KEY,
            "X-RapidAPI-Host": "deep-translate1.p.rapidapi.com",
        }
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()["data"]["translations"]["translatedText"]
    except requests.exceptions.RequestException as e:
        return f"Translation failed: {e}"

# Function to search, summarize, and translate
def search_and_explain(query, target_lang):
    snippet, link = perform_search(query)
    if not snippet:
        return f"No results found for {query}.\nError: {link}"
    
    summary = summarize_content_with_llama(snippet)
    if "Error" in summary:
        return summary
    
    translated_summary = translate_text(summary, target_lang)
    if "Translation failed" in translated_summary:
        return translated_summary
    
    return f"Explanation in {target_lang}:\n{translated_summary}\n\nSource: {link}"


# Streamlit app setup
st.title("Indian Financial News and Knowledge Assistant")
st.write("Get the latest Indian financial news and insights!")

# Sidebar for Indian Financial News
st.sidebar.header("Indian Financial News 📰")
indian_financial_news = fetch_indian_financial_news()

if isinstance(indian_financial_news, list):
    for article in indian_financial_news[:500]:  # Limit to 500 latest articles
        st.sidebar.markdown(f"**{article['title']}**")
        st.sidebar.markdown(f"[Read more]({article['url']})")
        st.sidebar.markdown("---")
else:
    st.sidebar.write(indian_financial_news)

# Language Selection Dropdown
languages = {"English": "en", "Hindi": "hi", "Tamil": "ta", "Telugu": "te", "Marathi": "mr"}
lang_choice = st.selectbox("Choose Language / भाषा चुनें", list(languages.keys()), key="language_selectbox")
selected_lang = languages[lang_choice]

# User input for query
query = st.text_input("Enter your query or topic:", key="query_input")

# Display search results and summary
if query.strip():
    result = search_and_explain(query, selected_lang)
    st.write(result)
else:
    st.error("Please enter a query before proceeding!")
