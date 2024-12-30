import streamlit as st
from gtts import gTTS
import requests
import speech_recognition as sr
from deep_translator import GoogleTranslator  # Use deep_translator for translation

NEWSAPI_KEY = "81f1784ea2074e03a558e94c792af540"
NEWSAPI_URL = "https://newsapi.org/v2/top-headlines"
LLAMA_API_URL = "https://akshara.streamlit.app"  # Replace with your actual LLaMA API endpoint
LLAMA_API_KEY = "LL-ATLBeF16yEleBb6RmOf9g4uGeN4GOUAqbJXY1RuKpSC4x62ABkeigtFVo01o5m0o"  # Replace with your LLAMA API key

# Function to translate text using deep_translator
def translate_text(text, target_lang):
    if target_lang == "en":
        return text  # No translation needed for English

    try:
        translated = GoogleTranslator(source='auto', target=target_lang).translate(text)
        return translated
    except Exception as e:
        return f"Translation error: {str(e)}"

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

# Function to query the LLaMA API
def ask_llama(question):
    headers = {
        "Authorization": f"Bearer {LLAMA_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "llama-2",  # Replace with the correct model name if needed
        "prompt": question,
        "temperature": 0.7,
        "max_tokens": 150
    }
    try:
        response = requests.post(LLAMA_API_URL, headers=headers, json=data)
        response.raise_for_status()
        return response.json().get("choices", [{}])[0].get("text", "No response received.")
    except Exception as e:
        return f"Error: {e}"

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
    st.sidebar.write(translate_text("No news available at the moment.", selected _lang)) 

# Main Content Area
st.header(translate_text("Ask LLaMA", selected_lang))
user_question = st.text_input(translate_text("What would you like to ask?", selected_lang))

if st.button(translate_text("Submit", selected_lang)):
    if user_question:
        response = ask_llama(user_question)
        st.write(translate_text("LLaMA's Response:", selected_lang))
        st.write(response)
    else:
        st.warning(translate_text("Please enter a question.", selected_lang))

# Voice Input Option
if st.button(translate_text("Record Voice Input", selected_lang)):
    voice_text = record_voice_input()
    st.write(translate_text("You said:", selected_lang))
    st.write(voice_text)
    if voice_text and voice_text != "Error: Could not understand the audio.":
        response = ask_llama(voice_text)
        st.write(translate_text("LLaMA's Response:", selected_lang))
        st.write(response) ```python
    else:
        st.warning(translate_text("Please enter a valid voice input.", selected_lang)
