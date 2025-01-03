import streamlit as st
from gtts import gTTS
import requests
import speech_recognition as sr  # For voice input
from deep_translator import GoogleTranslator  # For translation
import tempfile
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import json
import cohere
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
import pandas as pd
import numpy as np
import hashlib
import datetime
from transformers import BertTokenizer, BertModel
import torch

# API Keys and URLs
NEWSAPI_KEY = st.secrets["newsapi_key"]
COHERE_API_KEY = st.secrets["COHERE_API_KEY"]
sender_email = st.secrets["sender_email"]
app_password = st.secrets["app_password"]
NEWSAPI_URL = "https://newsapi.org/v2/top-headlines"
LINK = st.secrets["LINK"]

# Function to translate text using deep_translator
def translate_text(text, target_lang):
    if target_lang == "en":
        return text  # No translation needed for English

    try:
        translated = GoogleTranslator(source='auto', target=target_lang).translate(text)
        return translated
    except Exception as e:
        return f"Translation error: {str(e)}"

def load_risk_model(model_name='bert-base-uncased'):
    tokenizer = BertTokenizer.from_pretrained(model_name)
    model = BertModel.from_pretrained(model_name)
    model.eval()
    return model, tokenizer

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
        print(f"Error fetching financial news: {e}")
        return []

# Define the function to use cohere with Langchain
def ask_cohere(question):
    try:
        llm = cohere.Client(COHERE_API_KEY)  # Initialize the cohere model
        prompt_template = PromptTemplate(input_variables=["question"], template="{question}")
        chain = LLMChain(llm=llm, prompt=prompt_template)
        response = chain.run({"question": question})
        return response
    except Exception as e:
        return f"Error: {e}"

# Email Function
receiver_email = st.secrets["receiver-email"]
def send_email(receiver_email, subject, body):
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, app_password)  # Use app_password for login
            message = f"Subject: {subject}\n\n{body}"
            server.sendmail(sender_email, receiver_email, message)
        print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")

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
            return tmp_file.name  # Return the file name for audio playback
    except Exception as e:
        st.error(f"TTS Error: {str(e)}")

# Set page configuration
st.set_page_config(page_title="Aksha₹a", page_icon="💵")

# App Title and Description
st.title("Akshara: Financial Empowerment for Rural India")
st.write("""
### Welcome to Akshara!
#### Empowering Rural India with tools for financial literacy, secure banking, and entrepreneurship.
""")

st.markdown(f"[Click here to Join the Entrepreneur Army]({LINK})")
st.markdown(f"[Help & Support](https://akshara-nps-tracker.streamlit.app )")

# Sidebar for Language Selection
languages = {"English": "en", "Hindi": "hi", "Bengali": "bn", "Telugu": "te", "Marathi": "mr", "Tamil": "ta", "Urdu": "ur", "Gujarati": "gu", "Malayalam": "ml", "Kannada": "kn", "Odia": "or", "Punjabi": "pa", "Assamese": "as", "Maithili": "mai", "Sanskrit": "sa", "Konkani": "kok", "Sindhi": "sd", "Dogri": "doi", "Bodo": "bo", "Manipuri": "mni", "Nepali": "ne", "Santali": "sat", "Kashmiri": "ks", "Maithili": "mai", "Tulu": "tcy", "Khasi": "kha", "Mizo": "lus", "Bengali (Bangla)": "bn", "Gurmukhi": "guru", "Assamese (Asamiya)": "as"}
lang_choice = st.sidebar.selectbox("Choose Language / भाषा चुनें", list(languages.keys()))
selected_lang = languages[lang_choice]

# Sidebar for Financial News
st.sidebar.header(translate_text("📰 Financial News", selected_lang))
news_articles = fetch_financial_news()
if news_articles:
    for article in news_articles[:5]:  # Display top 5 articles
        title = article.get("title", "No Title")
        url = article.get("url", "#")
        translated_title = translate_text(title, selected_lang)
        st.sidebar.markdown(f"[**{translated_title}**]({url})")
else:
    st.sidebar.write(translate_text("No news available at the moment.", selected_lang))

# Section 1: Financial Literacy 
st.header(translate_text("📚 Financial Literacy Modules", selected_lang))

topics = ["Budgeting Basics", "Micro Investing", "Loan Essentials", "Emergency Funds", "Savings Strategies", "Retirement Planning", "Debt Management", "Insurance Essentials", "Tax Planning", "Building Creditworthiness"]
topic_choice = st.selectbox(translate_text("Choose a topic", selected_lang), topics)

# Predefined lesson content for each topic
lesson_contents = {
    "Budgeting Basics": "Budgeting is a cornerstone of financial management...",
    "Micro Investing": "Micro investing represents a revolutionary approach...",
    "Loan Essentials": "Loans are an integral part of modern financial systems...",
    "Emergency Funds": "An emergency fund is a critical component of financial planning...",
    "Savings Strategies": "Savings strategies are essential for building financial resilience...",
    "Retirement Planning": "Retirement planning involves preparing for a phase of life...",
    "Debt Management": "Managing debt responsibly is critical to maintaining financial stability...",
    "Insurance Essentials": "Insurance is a financial safety net, offering protection against uncertainties...",
    "Tax Planning": "Tax planning is the process of optimizing finances to minimize tax liability...",
    "Building Creditworthiness": "Creditworthiness is a measure of financial responsibility..."
}

if st.button(translate_text("Start Lesson", selected_lang)):
    lesson_content = lesson_contents.get(topic_choice, "No content available for this topic.")
    translated_lesson_content = translate_text(lesson_content, selected_lang)
    st.write(translated_lesson_content)
    audio_file = play_tts(translated_lesson_content, selected_lang)
    st.audio(audio_file, format='audio/mp3')

# Section 2: Goal-Oriented Savings Plans
st.header(translate_text("💰 Goal-Oriented Savings", selected_lang))

savings_goal_desc = st.text_input(translate_text("Enter your savings goal (e.g., Buy a cow, open a shop)", selected_lang))
savings_goal_amount = st.number_input(translate_text("Enter the total savings goal amount (INR)", selected_lang), min_value=100)
duration = st.number_input(translate_text("How many months to save?", selected_lang), min_value=1, max_value=24)
monthly_savings = st.number_input(translate_text("Enter monthly saving amount (INR)", selected_lang), min_value=100)

if st.button(translate_text("Create Savings Plan", selected_lang)):
    total_savings = duration * monthly_savings
    savings_gap = savings_goal_amount - total_savings

    if total_savings >= savings_goal_amount:
        savings_message = translate_text(
            f"To achieve your goal of '{savings_goal_desc}' in {duration} months, your current plan of saving {monthly_savings} INR per month is sufficient.",
            selected_lang
        )
    else:
        min_required_savings = round(savings_goal_amount / duration, 2)
        savings_message = translate_text (f"To achieve your goal of '{savings_goal_desc}' in {duration} months, you need to save {savings_goal_amount} INR in total. "
            f"Your current plan of saving {monthly_savings} INR per month will only result in {total_savings} INR, leaving a gap of {savings_gap} INR.",
            selected_lang
        )
        savings_message += translate_text(
            f"\n\nTo meet your goal, you need to save at least {min_required_savings} INR per month.", selected_lang
        )

        suggestions = translate_text(
            f"Consider these options to reach your goal:\n"
            f"1. Increase your monthly savings to {min_required_savings} INR.\n"
            f"2. Extend your savings duration if possible.\n"
            f"3. Explore additional income sources or reduce expenses to save more.",
            selected_lang
        )
        savings_message += f"\n\n{suggestions}"

    st.write(savings_message)
    st.write(translate_text(f"Total Savings at the end of {duration} months: {total_savings} INR", selected_lang))
    audio_file = play_tts(savings_message, selected_lang)
    st.audio(audio_file, format='audio/mp3')
    st.write("For any additional questions, reach out to your network of entrepreneurs!")

st.header(translate_text("EasyLoan Application", selected_lang))
Name = st.text_input(translate_text("Enter name of borrower", selected_lang))
Locality = st.text_input(translate_text("Enter place of residence in 'locality, city' format (Example: Hisar, Haryana or Ashok Vihar, Delhi)", selected_lang))
Loan_Amount = st.text_input(translate_text("Enter amount to borrow", selected_lang))
Reason = st.text_input(translate_text("Enter reason/cause for borrowing of loan", selected_lang))
Occupation = st.text_input(translate_text("Enter your Occupation", selected_lang))
Collateral = st.text_input(translate_text("Enter any collateral you may have as a security against the loan", selected_lang))
Monthly_Income = st.text_input(translate_text("Enter monthly income", selected_lang))
ph_no = st.text_input(translate_text("Enter Phone Number", selected_lang))

if st.button(translate_text("Submit Details", selected_lang)):
    subject = "Loan Application Details"
    body = f"Name: {Name}\nLocality: {Locality}\nLoan Amount: {Loan_Amount}\nReason: {Reason}\n" \
           f"Occupation: {Occupation}\nCollateral: {Collateral}\nMonthly Income: {Monthly_Income}\nPhone Number: {ph_no}"

    send_email(receiver_email, subject, body)
    st.success(translate_text("Your loan application details have been sent!", selected_lang))

# Section: Ask a Question (Text or Voice)
st.header(translate_text("Ask Akshara", selected_lang))
question_input = st.text_input(translate_text("Type your question here", selected_lang))

if st.button(translate_text("Ask", selected_lang)):
    answer = ask_cohere(question_input)
    st.write(translate_text(f" Answer: {answer.strip()}", selected_lang))
    audio_file = play_tts(answer.strip(), selected_lang)
    st.audio(audio_file, format='audio/mp3')

st.write(translate_text("Or ask by voice:", selected_lang))
if st.button(translate_text("Record Voice", selected_lang)):
    voice_question = record_voice_input()
    if "Error" not in voice_question:
        st.write(translate_text(f"You asked: {voice_question}", selected_lang))
        answer = ask_cohere(voice_question)
        st.write(translate_text(f"Answer: {answer.strip()}", selected_lang))
        audio_file = play_tts(answer.strip(), selected_lang)
        st.audio(audio_file, format='audio/mp3')
    else:
        st.error(translate_text(voice_question, selected_lang))

# Initialize blockchain-like structure
@st.cache_resource
def initialize_blockchain():
    return []

blockchain = initialize_blockchain()

def create_block(data, prev_hash="0"):
    timestamp = str(datetime.datetime.now())
    block_data = f"{data}|{timestamp}|{prev_hash}"
    block_hash = hashlib.sha256(block_data.encode()).hexdigest()
    return {"data": data, "timestamp": timestamp, "prev_hash": prev_hash, "hash": block_hash}

def add_block_to_chain(data):
    if len(blockchain) > 0:
        prev_hash = blockchain[-1]["hash"]
    else:
        prev_hash = "0"
    new_block = create_block(data, prev_hash)
    blockchain.append(new_block)

# App starts
st.title("Innovative Insurance Solutions")

# Blockchain-Powered Community Insurance Pools (BCP)
st .header("Blockchain-Powered Community Insurance Pools (BCP)")
pool_name = st.text_input("Enter Insurance Pool Name")
pool_contribution = st.number_input("Enter Contribution Amount", min_value=0.0, step=1.0)
if st.button("Create Pool"):
    add_block_to_chain({"pool_name": pool_name, "contribution": pool_contribution})
    st.success("Insurance Pool Created!")
    st.write(blockchain)

# User input for insurance query
query = st.text_area("Describe your insurance-related query")
if st.button("Get Advisory"):
    if query:
        try:
            response = ask_cohere(f"Generate an insurance advisory for '{query}'")
            advisory = response.generations[0].text.strip()  # Get the generated advisory text
            st.write(translate_text(f" Answer: {advisory.strip()}", selected_lang))
        except Exception as e:
            st.error(f"An error occurred while generating the advisory: {str(e)}")
    else:
        st.warning("Please enter a query to get advisory.")

# Dynamic Blockchain-Integrated Insurance for Gig & Informal Workers (GigInsure)
st.header("Dynamic Blockchain-Integrated Insurance for Gig & Informal Workers (GigInsure)")
work_pattern = st.text_area("Describe your work pattern")
health_data = st.file_uploader("Upload your health data (CSV)", type="csv")
if st.button("Generate Premium"):
    if health_data:
        health_df = pd.read_csv(health_data)
        st.write("Uploaded Health Data:", health_df.head())
        premium = np.random.uniform(500, 1500)  # Simulated premium calculation
        st.success(f"Your generated premium is ₹{premium:.2f}")
        add_block_to_chain({"work_pattern": work_pattern, "premium": premium})
    else:
        st.warning("Please upload valid health data.")

# Display Blockchain Data
if st.checkbox("Show Blockchain"):
    st.write("Blockchain Data:", blockchain)

def get_prediction(age, sex, bmi, children, smoker, region):
    header = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + "<IAM-Token-goes-here>"}

    if bmi is None:
        python_object = []
    else:
        python_object = [age, sex, float(bmi), children, smoker, region]

    userInput = [python_object]

    payload_scoring = {
        "input_data": [{
            "fields": ["age", "sex", "bmi", "children", "smoker", "region"],
            "values": userInput
        }]
    }

    response_scoring = requests.post(
        "https://us-south.ml.cloud.ibm.com/ml/v4/deployments/<deployment-id-goes-here>/predictions?version=2020-09-01",
        json=payload_scoring, headers=header
    )

    output = json.loads(response_scoring.text)

    for key in output:
        ab = output[key]

    for key in ab[0]:
        bc = ab[0][key]

    roundedCharge = round(bc[0][0], 2)

    return roundedCharge

# Streamlit form elements
st.title("Predictor App")

with st.form(key='prediction_form'):
    age = st.number_input("Age", min_value=0)
    sex = st.selectbox("Sex", ["Male", "Female"])
    bmi = st.number_input("BMI", min_value=0.0)
    children = st.number_input("Children", min_value=0)
    smoker = st.selectbox("Smoker", ["Yes", "No"])
    region = st.selectbox("Region", ["North", "South", "East", "West"])
    
    submit_button = st.form_submit_button(label="Submit")

    if submit_button:
        prediction = get_prediction(age, sex, bmi, children, smoker, region)
        st.write(f"Predicted Charge: {prediction}")

# Footer
st.write("# Thank you for using Akshara!")
