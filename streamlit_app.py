import streamlit as st
from gtts import gTTS
import requests
import speech_recognition as sr  # For voice input
from deep_translator import GoogleTranslator  # For translation
import tempfile
from bs4 import BeautifulSoup  # For parsing HTML responses
import pyaudio

# API Keys and URLs
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
        print("Response Status Code:", response.status_code)  # Log the status code
        print("Response Headers:", response.headers)  # Log the headers
        print("Raw response:", response.text)  # Log the raw response text

        # Check if the response is HTML
        if "html" in response.headers.get("Content-Type", ""):
            # Parse the HTML response
            soup = BeautifulSoup(response.text, 'html.parser')
            error_message = soup.get_text()  # Get all text from the HTML
            return f"Error: Received HTML response. Details: {error_message}"

        response.raise_for_status()  # Raise an error for bad responses
        response_json = response.json()  # Attempt to parse the JSON response
        return response_json.get("choices", [{}])[0].get("text", "No response received.")
    except requests.exceptions.HTTPError as http_err:
        return f"HTTP error occurred: {http_err}"
    except requests.exceptions.RequestException as req_err:
        return f"Request error occurred: {req_err}"
    except ValueError as json_err:
        return f"JSON decode error: {json_err}"
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

# Function to play TTS audio in the target language
def play_tts(text, lang):
    try:
        tts = gTTS(text=text, lang=lang)
        with tempfile.NamedTemporaryFile(delete=True, suffix=".mp3") as tmp_file:
            tts.save(tmp_file.name)
            st.audio(tmp_file.name)
    except Exception as e:
        st.error(f"TTS Error: {str(e)}")

# App Title and Description
st.title("Akshara: Financial Empowerment for Rural Women in India")
st.write("""
### Welcome to Akshara ! 🌸
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
    audio_file = play_tts(lesson_content, selected_lang)
    st.audio(audio_file, format='audio/mp3')

# Section 2: Goal-Oriented Savings Plans
st.header(translate_text("💰 Goal-Oriented Savings", selected_lang))

savings_goal = st.text_input(translate_text("Enter your savings goal (e.g., Buy a cow, open a shop)", selected_lang))
duration = st.number_input(translate_text("How many months to save?", selected_lang), min_value=1, max_value=24)
amount = st.number_input(translate_text("Enter monthly saving amount (INR)", selected_lang), min_value=100)

if st.button(translate_text("Create Savings Plan", selected_lang)):
    total_savings = duration * amount
    savings_message = translate_text(f"To achieve your goal of '{savings_goal}' in {duration} months, you need to save {amount} INR per month.", selected_lang)
    st.write(savings_message)
    st.write(translate_text(f"Total Savings at the end of {duration} months: {total_savings} INR", selected_lang))
    audio_file = play_tts(savings_message, selected_lang)
    st.audio(audio_file, format='audio/mp3')

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
        audio_file = play_tts("Your loan application has been submitted!", selected_lang)
        st.audio(audio_file, format='audio/mp3')

# Section: Ask a Question (Text or Voice)
st.header(translate_text("❓ Ask a Question", selected_lang))
question_input = st.text_input(translate_text("Type your question here", selected_lang))

if st.button(translate_text("Ask", selected_lang)):
    answer = ask_llama(question_input)
    st.write(translate_text(f" Answer: {answer.strip()}", selected_lang))
    audio_file = play_tts(answer.strip(), selected_lang)
    st.audio(audio_file, format='audio/mp3')

st.write(translate_text("Or ask by voice:", selected_lang))
if st.button(translate_text("Record Voice", selected_lang)):
    voice_question = record_voice_input()
    if "Error" not in voice_question:
        st.write(translate_text(f"You asked: {voice_question}", selected_lang))
        answer = ask_llama(voice_question)
        st.write(translate_text(f"Answer: {answer.strip()}", selected_lang))
        audio_file = play_tts(answer.strip(), selected_lang)
        st.audio(audio_file, format='audio/mp3')
    else:
        st.error(translate_text(voice_question, selected_lang))

# Footer
st.write("### Thank you for using Akshara! 🌼")
