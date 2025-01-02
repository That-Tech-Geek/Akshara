import streamlit as st
from gtts import gTTS
import requests
import speech_recognition as sr  # For voice input
from deep_translator import GoogleTranslator  # For translation
import tempfile
from bs4 import BeautifulSoup  # For parsing HTML responses
import pyaudio
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import json
from langchain import Cohere
from langchain.chains import LLMChain
import cohere
from langchain.prompts import PromptTemplate

# API Keys and URLs
NEWSAPI_KEY = st.secrets["newsapi_key"]
COHERE_API_KEY = st.secrets["cohere_api_key"]
sender_email = st.secrets["sender_email"]
app_password = st.secrets["app_password"]
NEWSAPI_URL = "https://newsapi.org/v2/top-headlines"

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
        "category": "business",  # Replace "business" with a valid category supported by the API
        "language": "en",
        "country": "in"
    }
    try:
        response = requests.get(NEWSAPI_URL, params=params)
        response.raise_for_status()
        news_data = response.json()
        return news_data.get("articles", [])
    except Exception as e:
        print(f"Error fetching financial news: {e}")  # Log the error for debugging
        return []

# Define the function to use Cohere with Langchain
def ask_cohere(question):
    try:
        # Initialize the Cohere model using the API key directly
        llm = Cohere(cohere_api_key=COHERE_API_KEY, temperature=0.7)

        # Create a prompt template. This can be expanded or customized as needed.
        prompt_template = PromptTemplate(input_variables=["question"], template="{question}")

        # Create an LLMChain with the prompt template and Cohere model
        chain = LLMChain(llm=llm, prompt=prompt_template)

        # Ask the question and get the response
        response = chain.run({"question": question})

        # Return the result
        return response

    except Exception as e:
        return f"Error: {e}"

# Email Function
receiver_email = "sambit1912@gmail.com"
# Define the send_email function
def send_email(receiver_email, subject, body):
    # Setup the server and send the email (example using Gmail)
    sender_email = "sambit1912@gmail.com"  # Replace with your email
    password = "noqx vfqm zrhk sggm"  # Replace with your email password or app password
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, password)
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
        # Translate title before displaying it
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
    "Budgeting Basics": "Budgeting is a cornerstone of financial management that enables individuals and households to live within their means, achieve financial stability, and work toward their long-term goals. A budget is essentially a plan that allocates income across various categories of expenses, savings, and discretionary spending, ensuring that money is used wisely and aligns with one’s financial priorities. Effective budgeting begins with a clear understanding of income sources, which could include salaries, freelance earnings, rental income, or even irregular sources like bonuses. Once income is tracked, the next step is to record all expenses, which typically fall into categories such as fixed expenses (e.g., rent or mortgage payments), variable expenses (e.g., groceries and utilities), discretionary spending (e.g., dining out or entertainment), and savings goals. For instance, in a household where the monthly income is ₹80,000, the family might allocate ₹20,000 for rent, ₹10,000 for groceries, ₹5,000 for utilities, and ₹5,000 for savings, leaving the remaining ₹40,000 for transportation, education, healthcare, and other needs. Such meticulous planning not only prevents overspending but also helps identify areas where cost-cutting can be implemented to save more. For example, switching to energy-efficient appliances or meal planning can reduce utility and grocery bills. Moreover, budgeting tools like apps or spreadsheets can simplify tracking and provide a real-time snapshot of financial health. Households with a well-structured budget can also better prepare for irregular expenses like annual insurance premiums or festival-related spending. Over time, consistent budgeting fosters discipline, enabling families to pay off debts, build an emergency fund, and invest in their future, creating a foundation for financial independence and peace of mind.",
    "Micro Investing": "Micro investing represents a revolutionary approach to wealth building that empowers individuals, even those with limited disposable income, to start their investment journey with small, manageable amounts. This strategy leverages the power of compounding, where even modest, consistent contributions grow exponentially over time. Unlike traditional investing, which may require significant initial capital, micro-investing democratizes access to financial markets through platforms that accept investments as low as ₹100 or ₹500 per month. For example, a household that decides to invest ₹500 monthly into a diversified mutual fund or exchange-traded fund (ETF) with an average annual return of 7% could see their investment grow significantly over a decade. While the total contribution over 10 years would be ₹60,000, compounding could nearly double this amount to around ₹1,20,000, demonstrating how small, disciplined contributions accumulate over time. In a household context, micro-investing can serve specific goals, such as saving for a child’s education, creating a vacation fund, or even planning for a down payment on a home. These investments can be automated, ensuring consistency and eliminating the temptation to skip contributions. Furthermore, micro-investing encourages financial literacy, as families learn about different investment options, risks, and the importance of diversification. By leveraging micro-investing platforms, households can also invest in theme-based portfolios, such as sustainable funds or technology-driven sectors, aligning investments with personal values or interests. Over time, this approach not only builds wealth but also inculcates a savings mindset, making financial growth accessible to everyone, regardless of income level.",
    "Loan Essentials": "Loans are an integral part of modern financial systems, offering individuals and families the ability to fund significant expenses like buying a home, pursuing higher education, or starting a business. Understanding the basics of loans is crucial for making informed decisions and avoiding the pitfalls of over-borrowing or mismanagement. A loan is essentially borrowed money that must be repaid with interest, which is the cost of borrowing. The two main components to consider are the principal amount (the original sum borrowed) and the interest rate (expressed as a percentage of the principal). For example, a household might take a home renovation loan of ₹2,00,000 with a 10% annual interest rate and a 5-year repayment term. Using an EMI (Equated Monthly Installment) formula, the family would need to pay ₹4,240 monthly. It’s vital to carefully read the loan agreement, which outlines terms such as prepayment penalties, late fees, and variable versus fixed interest rates. A fixed rate remains constant, offering predictability, while a variable rate can fluctuate with market conditions, potentially increasing costs. Responsible borrowing involves evaluating one’s repayment capacity, ensuring that the EMI does not exceed 30-40% of monthly income. For instance, a family earning ₹50,000 monthly should ideally limit their EMI to ₹15,000 or less to avoid financial strain. Additionally, understanding concepts like the debt-to-income ratio (DTI) helps families gauge whether they’re taking on too much debt relative to their earnings. Tools like online EMI calculators or financial advisors can aid in assessing loan affordability. Ultimately, loans, when used wisely, can be a powerful financial tool to achieve life’s milestones, but they require disciplined repayment and a thorough understanding of associated costs to avoid falling into debt traps.",
    "Emergency Funds": "An emergency fund is a critical component of financial planning, serving as a safety net to cover unexpected expenses like medical emergencies, car repairs, or job loss without derailing long-term financial goals. Building an emergency fund begins with determining the ideal amount to save, typically three to six months’ worth of living expenses, depending on individual circumstances such as job stability or family size. For example, a family with monthly expenses of ₹40,000 should aim for an emergency fund of ₹1,20,000 to ₹2,40,000. Saving this amount might seem daunting, but breaking it into manageable monthly contributions makes it achievable. For instance, setting aside ₹5,000 monthly could accumulate ₹60,000 in just one year. Placing these funds in a high-yield savings account or a liquid mutual fund ensures they remain easily accessible while earning some returns. In a household setting, an emergency fund can prevent financial stress during unforeseen events, such as a sudden hospitalization requiring ₹50,000 for treatment. Without such a fund, the family might resort to high-interest credit cards or personal loans, which could exacerbate financial strain. It’s essential to differentiate an emergency fund from other savings goals; this fund should only be used for genuine emergencies and replenished immediately afterward. Automating savings or using budgeting tools can help families consistently contribute to their emergency fund. Over time, having this financial cushion not only provides peace of mind but also enhances overall financial resilience, enabling households to navigate life’s uncertainties without jeopardizing their financial future.", 
    "Savings Strategies": "Savings strategies are essential for building financial resilience, achieving life goals, and preparing for unexpected challenges. Saving effectively requires households to distinguish between short-term, medium-term, and long-term financial needs. For instance, consider a family saving for a child’s birthday party next month (short-term), a family vacation in six months (medium-term), and a new car purchase in three years (long-term). Short-term savings can be stashed in easily accessible bank accounts, while medium-term goals might benefit from recurring deposits offering higher interest rates. Long-term savings, such as buying a house or planning for retirement, require investment in instruments like fixed deposits, mutual funds, or public provident funds to benefit from compounding interest. Households can employ specific strategies, like the 50/30/20 rule, which allocates 50% of income to necessities (e.g., rent, groceries), 30% to discretionary expenses (e.g., dining out, entertainment), and 20% to savings. For example, a household with ₹60,000 monthly income could allocate ₹30,000 to bills, ₹18,000 to wants, and ₹12,000 to savings. Creative savings tactics, such as setting up automatic transfers to a savings account or using cash-back apps, can make savings habitual. Households may also embrace frugality by repurposing leftover food instead of discarding it, turning off unused appliances, or shopping during sales to save on expenses. Ultimately, disciplined saving helps families navigate financial challenges while working toward their dreams.", 
    "Retirement Planning": "Retirement planning involves preparing for a phase of life when active income ceases, ensuring a steady flow of funds to sustain living standards and address medical or leisure needs. Effective planning requires estimating future expenses, factoring in inflation, and choosing investment tools that maximize growth while minimizing risks. For instance, a couple in their 30s with a combined monthly income of ₹1,50,000 might estimate that they’ll need ₹6 crore by retirement to cover living expenses and healthcare. By investing ₹20,000 monthly in mutual funds offering an 8% annual return, they can build this corpus over 30 years. Household examples include parents discussing how retirement savings might impact family budgeting. For instance, they may choose to reduce monthly dining-out expenses to ensure they can afford long-term SIP contributions. Families should regularly review retirement plans, adjusting contributions as salaries grow or expenses change. Utilizing employer benefits like EPF (Employee Provident Fund) or contributing to government-backed schemes like PPF ensures safe, tax-saving options. Households can also consider diversifying into fixed-income plans or real estate investments. By planning early and consistently, families reduce the financial stress associated with aging and create opportunities to pursue hobbies or travel in retirement without compromising on their quality of life", 
    "Debt Management": "Managing debt responsibly is critical to maintaining financial stability and avoiding a cycle of high-interest payments. Households often grapple with various forms of debt, such as home loans, education loans, and credit card dues. Distinguishing between good debt, which creates assets (like a home loan), and bad debt, which accumulates liabilities (like an unpaid credit card balance), is key. For example, a family with ₹50,000 in credit card debt at an annual interest rate of 36% might focus on reducing this burden through the avalanche method (paying high-interest loans first) or consolidating debts with a personal loan offering a lower interest rate of 12%. Commonplace strategies include tracking expenses to free up funds for repayment. A family might decide to cut down on entertainment subscriptions, switch to more economical grocery brands, or temporarily halt non-essential purchases. Parents could also involve children by explaining the importance of prioritizing necessities over wants, fostering an early understanding of debt responsibility. Tools like debt calculators help households visualize repayment timelines and interest savings, motivating them to stick to their repayment schedules. Over time, disciplined debt management improves credit scores and reduces financial stress, allowing families to redirect funds toward savings and investments.", 
    "Insurance Essentials": "Insurance is a financial safety net, offering protection against uncertainties that could otherwise drain household savings. Families need to understand and prioritize various types of insurance, including health, life, motor, and home insurance. Consider a family of four with a single breadwinner earning ₹1,00,000 monthly. A term life insurance policy with a ₹1 crore sum assured ensures financial security for dependents if the earning member passes away. Similarly, a health insurance policy covering ₹10 lakh protects the family against rising medical costs. Common household examples include comparing insurance plans during renewal to find the best coverage at the lowest premiums or filing a motor insurance claim after a minor accident. Parents might also teach children the value of health insurance by explaining how it helped during a hospital stay or illness. Comprehensive policies like home insurance provide peace of mind, especially for families living in flood-prone areas. Regularly reviewing insurance needs ensures that coverage keeps up with life changes, such as marriage, childbirth, or purchasing new assets. Investing in the right insurance policies protects households from financial turmoil, ensuring stability and peace of mind during crises.", 
    "Tax Planning": "Tax planning is the process of optimizing finances to minimize tax liability while complying with legal requirements. Households can benefit from understanding deductions under the Income Tax Act, such as Section 80C, which allows a deduction of up to ₹1.5 lakh annually for investments in instruments like PPF, ELSS funds, or life insurance. For example, a salaried individual earning ₹8 lakh annually could reduce taxable income by ₹2 lakh through these deductions and additional benefits under Section 80D for health insurance premiums. Families can also leverage rebates on home loan interest under Section 24(b) or explore tax-saving fixed deposits offering benefits for five-year lock-ins. For households with children, tuition fee deductions provide additional relief. Practical examples include using free online tools to estimate tax liability or consulting with a tax advisor to ensure all eligible deductions are claimed. By strategically aligning savings and investments with tax benefits, families retain more of their income for long-term goals. Tax planning also instills financial discipline, as individuals must carefully document expenses, contributions, and deductions to avoid errors during return filing.", 
    "Building Creditworthiness": "Creditworthiness is a measure of financial responsibility, reflecting an individual’s ability to manage borrowed funds effectively. A high credit score unlocks benefits like lower interest rates, higher loan approvals, and favorable terms. Families can build credit by ensuring timely repayment of EMIs, credit card dues, or utility bills. For instance, a household that consistently repays a ₹10,000 monthly credit card bill on time demonstrates financial discipline, positively impacting their credit score. Household strategies include using only 30-40% of the available credit limit to maintain healthy utilization rates. For instance, a family with a ₹1,00,000 limit should aim to use no more than ₹40,000 monthly. Parents might also use their own financial behavior as a teaching tool, helping teenagers build credit early by adding them as authorized users on a family credit card. Reviewing credit reports annually ensures that inaccuracies or fraudulent activities are promptly addressed. Building strong creditworthiness not only eases financial stress but also prepares households for significant future investments like purchasing a home or starting a business.", 
}
    

if st.button(translate_text("Start Lesson", selected_lang)):
    lesson_content = lesson_contents.get(topic_choice, "No content available for this topic.")
    translated_lesson_content = translate_text(lesson_content, selected_lang)  # Translate lesson content
    st.write(translated_lesson_content)
    audio_file = play_tts(translated_lesson_content, selected_lang)  # Pass translated content to TTS
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
        # Goal achievable with current plan
        savings_message = translate_text(
            f"To achieve your goal of '{savings_goal_desc}' in {duration} months, your current plan of saving {monthly_savings} INR per month is sufficient.",
            selected_lang
        )
    else:
        # Goal not achievable, calculate the minimum required monthly savings
        min_required_savings = round(savings_goal_amount / duration, 2)
        savings_message = translate_text(
            f"To achieve your goal of '{savings_goal_desc}' in {duration} months, you need to save {savings_goal_amount} INR in total. "
            f"Your current plan of saving {monthly_savings} INR per month will only result in {total_savings} INR, leaving a gap of {savings_gap} INR.",
            selected_lang
        )
        savings_message += translate_text(
            f"\n\nTo meet your goal, you need to save at least {min_required_savings} INR per month.", selected_lang
        )

        # Provide actionable suggestions
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

# Trigger the email when the button is pressed
if st.button(translate_text("Submit Details", selected_lang)):
    # Prepare the email details
    subject = "Loan Application Details"
    body = f"Name: {Name}\nLocality: {Locality}\nLoan Amount: {Loan_Amount}\nReason: {Reason}\n" \
           f"Occupation: {Occupation}\nCollateral: {Collateral}\nMonthly Income: {Monthly_Income}\nPhone Number: {ph_no}"
    receiver_email = "recipient@example.com"  # Replace with actual recipient email

    # Call send_email function to send the details
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

# Footer
st.write("### Thank you for using Akshara! 🌼")
