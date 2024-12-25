import streamlit as st
from gtts import gTTS
import os
import smtplib
from email.mime.text import MIMEText
from googletrans import Translator
from urllib.parse import parse_qs
import google.generativeai as genai

# Configure Google Generative AI
genai.configure(api_key="AIzaSyBzP_urPbe1zBnZwgjhSlVl-MWtUQMEqQA")

# Initialize translator
translator = Translator()

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

# Function for Translation
def translate_text(text, target_lang):
    if target_lang == "en":
        return text
    try:
        return translator.translate(text, dest=target_lang).text
    except Exception as e:
        st.error(f"Translation failed: {e}")
        return text

# Function for Text-to-Speech
def speak_text(text, lang="en"):
    translated_text = translate_text(text, lang)
    tts = gTTS(text=translated_text, lang=lang)
    audio_file_path = "audio.mp3"
    tts.save(audio_file_path)
    
    # Play the audio
    with open(audio_file_path, "rb") as audio_file:
        st.audio(audio_file.read())
    
    # Cleanup
    if os.path.exists(audio_file_path):
        os.remove(audio_file_path)

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

# Section 1: Financial Literacy
st.header(translate_text("📚 Financial Literacy Modules", selected_lang))

topics = ["Budgeting Basics", "Micro Investing", "Loan Essentials", "Emergency Funds"]
topic_choice = st.selectbox(translate_text("Choose a topic", selected_lang), topics)

if st.button(translate_text("Start Lesson", selected_lang)):
    try:
        # Generate lesson content using Google Generative AI
        response = genai.generate(
            model="text-bison-001",
            prompt=f"Create a detailed learning module on {topic_choice} for rural Indian women with low financial literacy."
        )
        lesson_content = response.generations[0].text
    except Exception as e:
        lesson_content = f"Error generating content: {e}"

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
