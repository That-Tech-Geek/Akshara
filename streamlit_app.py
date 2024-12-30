import streamlit as st
from gtts import gTTS
import requests
import google.generativeai as genai
import speech_recognition as sr
import json
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

# API Keys and URLs
DEEPTRANSLATE_API_KEY = "d5c0549879msh215534c0e781043p1ec76ajsn937e4b021336"
DEEPTRANSLATE_BASE_URL = "https://deep-translate1.p.rapidapi.com/language/translate/v2"
NEWSAPI_KEY = "81f1784ea2074e03a558e94c792af540"
NEWSAPI_URL = "https://newsapi.org/v2/top-headlines"
LLAMA_API_URL = "https://akshara.streamlit.app"
LLAMA_API_KEY = "LL-ATLBeF16yEleBb6RmOf9g4uGeN4GOUAqbJXY1RuKpSC4x62ABkeigtFVo01o5m0o"  # Replace with your LLAMA API key

# Selenium Setup
def setup_selenium():
    options = Options()
    options.add_argument("--headless=new")  # Ensure headless mode for cloud
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.binary_location = "/path/to/chrome"  # Replace with Chrome binary path if needed
    service = Service('/full/path/to/chromedriver')  # Replace with ChromeDriver path
    try:
        driver = webdriver.Chrome(service=service, options=options)
        return driver
    except Exception as e:
        st.error(f"Error setting up Selenium: {e}")
        raise

# Function to query the LLAMA API using Selenium
def ask_llama_with_selenium(question):
    driver = setup_selenium()
    try:
        driver.get(LLAMA_API_URL)  # Navigate to the API URL
        # Simulate input and interaction if necessary (update as per the API's frontend)
        driver.quit()
        return {"error": "Selenium functionality needs specific adjustments for this API."}
    except Exception as e:
        driver.quit()
        return {"error": "Selenium error", "details": str(e)}

# Function to query the LLAMA API
def ask_llama(question):
    headers = {
        "Authorization": f"Bearer {LLAMA_API_KEY}",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    data = {
        "model": "text-davinci-003",
        "prompt": question,
        "temperature": 0.7,
        "max_tokens": 150
    }
    try:
        response = requests.post(LLAMA_API_URL, headers=headers, json=data)
        response.raise_for_status()

        try:
            response_data = response.json()
            return response_data.get("choices", [{}])[0].get("text", "No response received.")
        except json.JSONDecodeError:
            # Parse HTML response for JavaScript error
            soup = BeautifulSoup(response.text, "html.parser")
            if "You need to enable JavaScript" in soup.text:
                return ask_llama_with_selenium(question)
            return {"error": "Unexpected HTML response.", "parsed_html": soup.text}
    except requests.exceptions.RequestException as e:
        return {"error": "Request error", "details": str(e)}

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
