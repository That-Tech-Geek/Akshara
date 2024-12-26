import streamlit as st
from gtts import gTTS
import requests
import google.generativeai as genai

DEEPTRANSLATE_API_KEY = "d5c0549879msh215534c0e781043p1ec76ajsn937e4b021336"
DEEPTRANSLATE_BASE_URL = "https://deep-translate1.p.rapidapi.com/language/translate/v2"

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

# Configure the Generative AI API
genai.configure(api_key="AIzaSyBzP_urPbe1zBnZwgjhSlVl-MWtUQMEqQA")

# Function to generate text using Generative AI API
def generate_text(prompt):
    try:
        response = genai.chat(messages=[{"content": prompt}])
        return response['messages'][0]['content']
    except Exception as e:
        return f"Error generating content: {e}"

# Function for Text-to-Speech
def speak_text(text, lang="en"):
    translated_text = translate_text(text, lang)
    tts = gTTS(text=translated_text, lang=lang)
    audio_file_path = "audio.mp3"
    tts.save(audio_file_path)
    # Stream the audio directly
    with open(audio_file_path, "rb") as audio_file:
        st.audio(audio_file.read())

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
        st.success(translate_text("Your loan application has been submitted!", selected_lang))
        speak_text("Your loan application has been submitted!", selected_lang)
