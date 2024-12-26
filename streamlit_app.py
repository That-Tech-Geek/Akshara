import streamlit as st
from gtts import gTTS
import requests
import speech_recognition as sr
import json

DEEPTRANSLATE_API_KEY = "d5c0549879msh215534c0e781043p1ec76ajsn937e4b021336"
DEEPTRANSLATE_BASE_URL = "https://deep-translate1.p.rapidapi.com/language/translate/v2"
NEWSAPI_KEY = "81f1784ea2074e03a558e94c792af540"
NEWSAPI_URL = "https://newsapi.org/v2/top-headlines"
LLAMA_API_URL = "https://api.llama.com/v1/query"  # Replace with the actual LLAMA API endpoint
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
        "model": "text-davinci-003",  # Adjust model if necessary
        "prompt": question,
        "temperature": 0.7,
        "max_tokens": 150
    }
    try:
        response = requests.post(LLAMA_API_URL, headers=headers, json=data)
        response.raise_for_status()

        # Check if the response is JSON
        try:
            response_data = response.json()
            return response_data.get("choices", [{}])[0].get("text", "No response received.")
        except json.JSONDecodeError:
            return f"Error: Expected JSON but received HTML or plain text. Response: {response.text}"
    except requests.exceptions.RequestException as e:
        return f"Request error: {e}"

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
