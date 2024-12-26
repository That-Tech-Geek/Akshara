import streamlit as st
from gtts import gTTS
import requests
import google.generativeai as genai
import speech_recognition as sr
import json
from bs4 import BeautifulSoup

DEEPTRANSLATE_API_KEY = "d5c0549879msh215534c0e781043p1ec76ajsn937e4b021336"
DEEPTRANSLATE_BASE_URL = "https://deep-translate1.p.rapidapi.com/language/translate/v2"
NEWSAPI_KEY = "81f1784ea2074e03a558e94c792af540"
NEWSAPI_URL = "https://newsapi.org/v2/top-headlines"
LLAMA_API_URL = "https://akshara.streamlit.app"
LLAMA_API_KEY = "LL-ATLBeF16yEleBb6RmOf9g4uGeN4GOUAqbJXY1RuKpSC4x62ABkeigtFVo01o5m0o"  # Replace with your LLAMA API key

# Function to translate text using DeepTranslate API
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
        response.raise_for_status()
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

# Function to fetch financial news
def fetch_financial_news():
    params = {
        "apiKey": NEWSAPI_KEY,
        "category": "business",
        "language": "en",
        "country": "in"
    }
    try:
        response = requests.get(NEWSAPI_URL, params=params)
        response.raise_for_status()
        news_data = response.json()
        return news_data.get("articles", [])
    except Exception as e:
        return []

# Function to query the LLAMA API
def ask_llama(question):
    headers = {
        "Authorization": f"Bearer {LLAMA_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "text-davinci-003",  # Make sure this is the correct model for LLAMA
        "prompt": question,
        "temperature": 0.7,
        "max_tokens": 150
    }
    try:
        response = requests.post(LLAMA_API_URL, headers=headers, json=data)
        response.raise_for_status()

        # Print raw response for debugging
        print("Raw response:", response.text)

        # Attempt to parse the response as JSON
        try:
            response_data = response.json()
            return response_data.get("choices", [{}])[0].get("text", "No response received.")
        except json.JSONDecodeError:
            # If the response is not JSON, parse it as HTML
            soup = BeautifulSoup(response.text, "html.parser")
            parsed_data = {tag.name: tag.text for tag in soup.find_all()}
            return {
                "error": "Expected JSON but received HTML.",
                "parsed_html": parsed_data
            }
    except requests.exceptions.RequestException as e:
        return {"error": "Request error", "details": str(e)}

# Function to record voice input and convert to text
def record_voice_input():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("Listening... Please speak now.")
        try:
            audio = recognizer.listen(source, timeout=5)
            text = recognizer.recognize_google(audio)
            return text
        except sr.WaitTimeoutError:
            return "Timeout: No input detected."
        except sr.UnknownValueError:
            return "Error: Could not understand the audio."
        except Exception as e:
            return f"Error: {e}"

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

# Sidebar for Financial News
st.sidebar.header(translate_text("📰 Financial News", selected_lang))
news_articles = fetch_financial_news()
if news_articles:
    for article in news_articles[:5]:  # Display top 5 articles
        title = article.get("title", "No Title")
        url = article.get("url", "#")
        # Translate title before displaying it
        translated_title = translate_text(title, selected_lang)
        st.sidebar.markdown(f"[**{translated_title}**]({url})")
else:
    st.sidebar.write(translate_text("No news available at the moment.", selected_lang))

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

# Section 2: Goal-Oriented Savings Plans
st.header(translate_text("💰 Goal-Oriented Savings", selected_lang))

savings_goal = st.text_input(translate_text("Enter your savings goal (e.g., Buy a cow, open a shop)", selected_lang))
duration = st.number_input(translate_text("How many months to save?", selected_lang), min_value=1, max_value=24)
amount = st.number_input(translate_text("Enter monthly saving amount (INR)", selected_lang), min_value=100)

if st.button(translate_text("Create Savings Plan", selected_lang)):
    total_savings = duration * amount
    st.write(translate_text(f"To achieve your goal of '{savings_goal}' in {duration} months, you need to save {amount} INR per month.", selected_lang))
    st.write(translate_text(f"Total Savings at the end of {duration} months: {total_savings} INR", selected_lang))

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
        st.success(translate_text("Your loan application has been submitted!", selected_lang))
# Section: Ask a Question (Text or Voice)
st.header(translate_text("❓ Ask a Question", selected_lang))
question_input = st.text_input(translate_text("Type your question here", selected_lang))

if st.button(translate_text("Ask", selected_lang)):
    answer = ask_llama(question_input)
    st.write(translate_text(f"Answer: {answer.strip()}", selected_lang))

st.write(translate_text("Or ask by voice:", selected_lang))
if st.button(translate_text("Record Voice", selected_lang)):
    voice_question = record_voice_input()
    if "Error" not in voice_question:
        st.write(translate_text(f"You asked: {voice_question}", selected_lang))
        answer = ask_llama(voice_question)
        st.write(translate_text(f"Answer: {answer.strip()}", selected_lang))
    else:
        st.error(translate_text(voice_question, selected_lang))
