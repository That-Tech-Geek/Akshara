import streamlit as st
from gtts import gTTS
import requests
import speech_recognition as sr
from deep_translator import GoogleTranslator
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
import pickle
from sklearn.ensemble import RandomForestRegressor
import pandas

# API Keys and URLs
NEWSAPI_KEY = st.secrets["newsapi_key"]
COHERE_API_KEY = st.secrets["COHERE_API_KEY"]
SENDER_EMAIL = st.secrets["sender_email"]
APP_PASSWORD = st.secrets["app_password"]
NEWSAPI_URL = "https://newsapi.org/v2/top-headlines"
LINK = st.secrets["LINK"]
RECEIVER_EMAIL = st.secrets["receiver-email"]

# Function to translate text using deep_translator
def translate_text(text, target_lang):
    if target_lang == "en":
        return text
    try:
        return GoogleTranslator(source='auto', target=target_lang).translate(text)
    except Exception as e:
        return f"Translation error: {str(e)}"

# Load BERT model for risk assessment
def load_and_train_model():
    try:
        # Load the dataset from the provided URL
        url = "https://raw.githubusercontent.com/That-Tech-Geek/Akshara/main/insurance.csv"
        df = pd.read_csv(url)

        # Debugging: Print the first few rows and columns of the DataFrame
        st.write("DataFrame Columns:", df.columns.tolist())
        st.write("First few rows of the DataFrame:")
        st.write(df.head())

        # Preprocess the data (convert categorical variables to numerical)
        df = pd.get_dummies(df, columns=['sex', 'smoker', 'region'], drop_first=True)

        # Define features and target variable
        X = df.drop('expenses', axis=1)  # Use 'expenses' as the target variable
        y = df['expenses']

        # Train the Random Forest model
        model = RandomForestRegressor(n_estimators=100, random_state=42)
        model.fit(X, y)

        # Return the model and the feature names
        return model, X.columns.tolist()  # Return the feature names as a list

    except Exception as e:
        st.error(f"An error occurred while loading the model: {str(e)}")
        return None, None  # Return None if there was an error

# Fetch financial news
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
        return response.json().get("articles", [])
    except Exception as e:
        st.error(f"Error fetching financial news: {e}")
        return []

# Function to interact with Cohere API
def ask_cohere(question):
    try:
        llm = cohere.Client(COHERE_API_KEY)
        prompt_template = PromptTemplate(input_variables=["question"], template="{question}")
        chain = LLMChain(llm=llm, prompt=prompt_template)
        return chain.run({"question": question})
    except Exception as e:
        return f"Error: {e}"

# Send email function
def send_email(receiver_email, subject, body):
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(SENDER_EMAIL, APP_PASSWORD)
            message = f"Subject: {subject}\n\n{body}"
            server.sendmail(SENDER_EMAIL, receiver_email, message)
        st.success("Email sent successfully!")
    except Exception as e:
        st.error(f"Failed to send email: {e}")

# Record voice input and convert to text
def record_voice_input():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("Listening... Please speak now.")
        try:
            audio = recognizer.listen(source, timeout=5)
            return recognizer.recognize_google(audio)
        except sr.WaitTimeoutError:
            return "Timeout: No input detected."
        except sr.UnknownValueError:
            return "Error: Could not understand the audio."
        except Exception as e:
            return f"Error: {e}"

# Play TTS audio in the target language
def play_tts(text, lang):
    try:
        tts = gTTS(text=text, lang=lang)
        # Create a temporary file without auto-deletion
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
            tts.save(tmp_file.name)
            return tmp_file.name  # Return the file name for audio playback
    except Exception as e:
        st.error(f"TTS Error: {str(e)}")
        return None  # Return None if there was an error

# Set page configuration
st.set_page_config(page_title="Aksha₹a", page_icon="💵")

# App Title and Description
st.title("Akshara: Financial Empowerment for Rural India")
st.write("""
### Welcome to Akshara!
#### Empowering Rural India with tools for financial literacy, secure banking, and entrepreneurship.
""")

st.markdown(f"[Click here to Join the Entrepreneur Army]({LINK})")
st.markdown(f"[Help & Support](https://akshara-nps-tracker.streamlit.app)")
st.write(f"Insurance Charge Predictor is currently in development, and hence will not be functional now.")

# Sidebar for Language Selection
languages = {
    "English": "en", "Hindi": "hi", "Bengali": "bn", "Telugu": "te", 
    "Marathi": "mr", "Tamil": "ta", "Urdu": "ur", "Gujarati": "gu", "Malayalam": "ml", 
    "Kannada": "kn", "Odia": "or", "Punjabi": "pa", "Assamese": "as", 
    "Maithili": "mai", "Sanskrit": "sa", "Konkani": "kok", "Sindhi": "sd", 
    "Dogri": "doi", "Bodo": "bo", "Manipuri": "mni", "Nepali": "ne", 
    "Santali": "sat", "Kashmiri": "ks", "Maithili": "mai", "Tulu": "tcy", 
    "Khasi": "kha", "Mizo": "lus", "Bengali (Bangla)": "bn", 
    "Gurmukhi": "guru", "Assamese (Asamiya)": "as"
}
lang_choice = st.sidebar.selectbox("Choose Language / भाषा चुनें", list(languages.keys()))
selected_lang = languages[lang_choice]

# Sidebar for Financial News
st.sidebar.header(translate_text("📰 Financial News", selected_lang))
news_articles = fetch_financial_news()
if news_articles:
    for article in news_articles[:5]:
        title = article.get("title", "No Title")
        url = article.get("url", "#")
        translated_title = translate_text(title, selected_lang)
        st.sidebar.markdown(f"[**{translated_title}**]({url})")
else:
    st.sidebar.write(translate_text("No news available at the moment.", selected_lang))

# Section 1: Financial Literacy 
st.header(translate_text("📚 Financial Literacy Modules", selected_lang))

topics = [
    "Budgeting Basics", "Micro Investing", "Loan Essentials", 
    "Emergency Funds", "Savings Strategies", "Retirement Planning", 
    "Debt Management", "Insurance Essentials", "Tax Planning", 
    "Building Creditworthiness"
]
topic_choice = st.selectbox(translate_text("Choose a topic", selected_lang), topics)

# Predefined lesson content for each topic
lesson_contents = {
    "Budgeting Basics": "Budgeting is the cornerstone of financial health. It involves understanding your income, planning your expenses, and making thoughtful financial decisions. For households, it’s the difference between living paycheck to paycheck and having a stable financial future. At its simplest, budgeting helps prioritize needs over wants, ensuring essential expenses like rent, utilities, and groceries are covered while leaving room for savings and discretionary spending. Without a budget, it’s easy to lose track of where money goes, often resulting in unnecessary debt or financial strain.The first step in budgeting is to determine your total monthly income. This includes your salary, side hustle earnings, or any passive income sources. For example, a family earning $4,000 a month needs to know this figure to allocate expenses effectively. The next step is listing all expenses. These can be divided into fixed costs like rent or mortgage payments and variable costs like groceries, entertainment, and transportation. By comparing income to expenses, households can spot areas of overspending or identify potential savings opportunities.One of the best hacks for effective budgeting is the 50/30/20 rule. This rule suggests allocating 50% of your income to needs, 30% to wants, and 20% to savings or debt repayment. For instance, a family with a $5,000 monthly income might allocate $2,500 for rent, groceries, and utilities (needs), $1,500 for dining out or vacations (wants), and $1,000 for savings or paying down credit card debt. This simple formula ensures a balanced approach to spending while encouraging financial discipline.Tracking expenses is another crucial aspect of budgeting. Apps like Mint or YNAB (You Need A Budget) simplify this by categorizing expenses and offering real-time insights. Alternatively, traditional methods like keeping a notebook or using an Excel spreadsheet can also be effective. For example, a household might discover they’re spending $300 a month on coffee shop visits and decide to cut it to $100 by brewing coffee at home. Small adjustments like these can lead to significant savings over time.Another budgeting trick is to embrace automation. Setting up automatic transfers to savings accounts or automating bill payments ensures that financial priorities are met before discretionary spending takes over. For instance, scheduling a $200 monthly transfer to a high-yield savings account can help a family build an emergency fund without having to think about it. Automation removes the temptation to skip saving and fosters consistent progress toward financial goals.Households can also benefit from meal planning as a budgeting hack. Preparing weekly meal plans reduces grocery bills, minimizes food waste, and curbs the urge to order takeout. For example, a family spending $600 a month on dining out can cut this expense in half by cooking at home. Batch cooking and using leftovers creatively can make this process even more efficient.When it comes to saving on household expenses, creativity goes a long way. Simple habits like turning off lights in unused rooms, air-drying clothes instead of using a dryer, or sealing drafts to improve home insulation can lower utility bills. Additionally, buying in bulk, shopping during sales, and using coupons are practical ways to stretch a household budget further. For instance, buying pantry staples like rice or pasta in bulk can save a family hundreds of dollars annually.Budgeting isn’t just about cutting back—it’s also about setting financial goals and rewarding progress. A family saving for a vacation, for example, might allocate $200 a month to a “dream trip” fund. Tracking the fund’s growth can be motivating, turning saving into a positive experience rather than a restrictive chore. Similarly, celebrating small wins, like paying off a credit card or hitting a savings milestone, reinforces good financial habits.In conclusion, budgeting is a vital skill that provides households with a roadmap to financial stability. By following simple principles like the 50/30/20 rule, tracking expenses, and embracing practical hacks, families can take control of their finances and achieve their goals. With thoughtful planning and a few creative strategies, budgeting can transform financial stress into a sense of empowerment and security.",
    "Micro Investing": "In recent years, micro-investing has emerged as a transformative trend in personal finance, empowering individuals to dip their toes into the world of investing without requiring significant upfront capital. At its core, micro-investing involves investing small amounts of money, often spare change from everyday transactions, into various financial instruments like stocks, bonds, or ETFs. This innovation is revolutionizing the way people think about wealth creation, especially for those who may have previously considered investing inaccessible or intimidating.Imagine a scenario where you visit your favorite coffee shop and buy a latte for $4.25. A micro-investing app linked to your bank account might round up your purchase to $5.00 and invest the remaining $0.75 into a diversified portfolio. Over time, these small contributions add up, much like filling a piggy bank with loose change. The beauty of micro-investing lies in its simplicity—it seamlessly integrates into your daily life, requiring little effort or financial expertise. For households living paycheck to paycheck, this can be a game-changer, offering an opportunity to build a financial cushion with minimal disruption to their budgets.To understand the power of micro-investing, consider a typical household grocery shopping trip. Suppose a family spends $92.40 at the supermarket. With micro-investing, the bill is rounded up to $93, and the extra $0.60 is invested. Over a month, if the family makes 10 similar transactions, they would have invested $6 without even noticing it. While this may seem trivial, the real magic happens when these small amounts are invested in the stock market and benefit from compounding. Even modest annual returns can lead to significant growth over time, turning spare change into meaningful savings.Another relatable example is the subscription services many households use. From streaming platforms like Netflix to gym memberships, subscription fees often end in uneven amounts, such as $14.99 or $9.95. Micro-investing apps can round these payments up to the nearest dollar and invest the difference. For a family juggling multiple subscriptions, this could result in several small investments each month, creating a steady and consistent pathway to wealth accumulation.Micro-investing also teaches valuable lessons about the power of consistency. Consider a child saving allowance money in a jar. Each week, they add a few coins and watch their savings grow. Micro-investing operates on the same principle but amplifies the growth potential by putting that money to work in financial markets. For instance, a household could link their micro-investing account to a joint checking account and pool their spare change. Over time, this collective effort could fund family goals like a vacation, a child’s education, or even early retirement.For working professionals, micro-investing can also act as a stepping stone into more sophisticated financial strategies. Let’s say an individual uses an app to invest $1 from every coffee purchase over a year. Not only do they accumulate savings, but they also gain exposure to concepts like portfolio diversification, risk tolerance, and market fluctuations. This hands-on experience builds confidence and encourages people to explore larger-scale investments, such as contributing to retirement accounts or purchasing individual stocks.One particularly appealing aspect of micro-investing is its ability to break down barriers to entry. Traditional investing often requires substantial initial capital, discouraging many middle- and lower-income families from participating. Micro-investing, on the other hand, democratizes access to financial markets. Whether you’re a college student spending spare change on textbooks or a parent managing household expenses, micro-investing allows anyone to get started with as little as a few cents at a time.Even household chores can serve as an analogy for micro-investing. Imagine cleaning your home one room at a time rather than tackling the entire house at once. The small, incremental effort feels manageable, and before you know it, the whole house is spotless. Similarly, micro-investing involves small, manageable contributions that collectively lead to substantial financial progress. This incremental approach is particularly appealing for those who find traditional investing overwhelming or unattainable.Moreover, micro-investing aligns well with long-term financial planning. Picture a family saving for a child’s college education by setting aside just $0.50 from every debit card transaction. Over 18 years, these small investments could grow into a significant fund, thanks to compound interest. The same strategy could be applied to other long-term goals, such as buying a home or starting a business, proving that micro-investing is not just about short-term gains but also about creating a sustainable financial future.In conclusion, micro-investing is a powerful tool for households looking to build wealth without the pressure of large upfront commitments. By leveraging spare change and integrating investing into everyday activities, families can make financial progress one small step at a time. The concept is as simple as saving loose coins in a jar but amplified by technology and financial markets. Whether you’re saving for a rainy day, a major life event, or simply looking to secure your financial future, micro-investing offers an accessible and effective solution for turning small actions into meaningful outcomes.",
    "Loan Essentials": "Loans play a significant role in modern financial systems, providing individuals, families, and businesses with access to funds they might not immediately possess. To understand loans better, it is crucial to break down their key elements and illustrate them through household examples that are relatable and practical.At its core, a loan is a sum of money borrowed from a lender, with the promise to repay it over time, typically with added interest. Imagine a family deciding to renovate their kitchen. The total cost for new cabinets, countertops, and appliances amounts to $20,000. While the family’s savings can cover part of the expense, they need $10,000 more to complete the project. To bridge this gap, they approach a bank for a personal loan. The bank agrees to lend the $10,000 at an annual interest rate of 8%, repayable over three years. Here, the loan serves as a financial tool enabling the family to achieve their goal without exhausting their savings entirely.Interest is one of the most critical components of a loan. It is essentially the cost of borrowing money, expressed as a percentage of the loan amount. Let’s consider a different scenario: A young couple wishes to buy their first car, priced at $15,000. They secure a loan for the full amount from their local credit union. The credit union offers a 5% interest rate over a five-year repayment period. By the end of the loan term, the couple will have paid more than $15,000 due to the interest. This additional cost is the price of having immediate access to the car, which they might need for commuting to work or running errands.Another important aspect of loans is the repayment schedule. Repayments are typically structured into monthly installments that include both principal (the original loan amount) and interest. For instance, a family planning to send their child to college may take out a student loan to cover tuition fees. If the loan amount is $40,000 with a 6% interest rate and a ten-year repayment plan, the family will make monthly payments calculated to cover both the borrowed amount and the interest accrued. A well-planned repayment schedule ensures that the borrower can manage their finances effectively without defaulting on the loan.Collateral is a feature often associated with secured loans. This means the borrower pledges an asset, such as a house or car, as security for the loan. A common household example is a mortgage. When a family buys a house worth $250,000, they might make a $50,000 down payment and borrow the remaining $200,000 through a mortgage. The house itself serves as collateral, giving the lender a form of protection; if the family fails to repay the loan, the lender can sell the house to recover the owed amount. Collateralized loans usually come with lower interest rates compared to unsecured loans because the risk to the lender is reduced.In contrast, unsecured loans do not require collateral but often come with higher interest rates due to the increased risk for the lender. Consider a parent taking out a $5,000 loan to fund a family vacation. Without any assets tied to the loan, the lender relies solely on the borrower’s creditworthiness and income to ensure repayment. While this type of loan offers more flexibility, the higher cost underscores the importance of borrowing responsibly and within one’s means.Credit scores and credit history significantly influence loan approval and terms. A good credit score indicates a borrower’s reliability in repaying debts, which can result in lower interest rates and higher borrowing limits. For example, a young professional with a solid credit history might secure a loan for a home theater system at a 7% interest rate, while someone with a poor credit history might be offered the same loan at a 12% interest rate or denied altogether. This demonstrates how a strong credit profile can save households money over time.Another type of loan frequently encountered in households is the credit card, which operates as a form of revolving credit. Imagine a family using their credit card to purchase a $1,000 laptop. If they repay the full amount within the grace period, they avoid any interest charges. However, if they choose to pay only the minimum balance each month, interest will accumulate on the remaining balance, potentially making the laptop significantly more expensive in the long run. This example highlights the importance of understanding loan terms and managing debt wisely.Debt consolidation loans offer another practical solution for households managing multiple debts. Suppose a family has accumulated $20,000 in debt spread across several credit cards, each with high interest rates ranging from 15% to 20%. By consolidating this debt into a single loan with a 10% interest rate, they can simplify their repayments and reduce their overall interest burden. This strategy can help families regain control of their finances and work toward becoming debt-free.Emergency loans are another critical aspect of household finance. Unexpected expenses, such as medical emergencies or urgent home repairs, can strain even the most carefully planned budgets. For instance, if a family’s furnace breaks down in the middle of winter, they may need an emergency loan to cover the $5,000 repair cost. While such loans often come with higher interest rates, they provide a lifeline in situations where immediate funds are necessary.Finally, understanding the long-term implications of loans is crucial for households. Borrowing decisions should always align with financial goals and repayment capabilities. For example, while taking out a home equity loan to remodel a kitchen might increase the property’s value, using the same loan for discretionary expenses, such as luxury vacations, may not be a wise financial move. By carefully evaluating the purpose and terms of a loan, families can make informed decisions that enhance their financial well-being.In conclusion, loans are powerful financial tools that, when used responsibly, can help households achieve their goals, manage unexpected expenses, and improve their quality of life. By understanding the essentials of loans, such as interest, repayment schedules, collateral, and credit scores, and by applying this knowledge to real-life scenarios, families can make informed borrowing decisions that support their long-term financial health.",
    "Emergency Funds": "Life has an uncanny way of throwing unexpected challenges at us, and more often than not, these challenges come with financial burdens. Whether it’s a medical emergency, sudden job loss, car repairs, or unexpected home expenses, having an emergency fund can act as your financial safety net. This fund, when built strategically, can help you navigate life's curveballs without plunging into debt. In this essay, we'll explore emergency funds in detail, peppered with practical tips, hacks, and relatable household examples to make the concept approachable for everyone.At its core, an emergency fund is money set aside specifically for unforeseen expenses. It’s not your vacation fund, nor is it the money you save for a new gadget or car upgrade. Think of it as a financial fire extinguisher—something you hope never to use but are grateful for in times of need. For example, imagine your refrigerator breaks down just before the peak summer season. Without an emergency fund, you might resort to using a credit card, leading to high-interest debt. But with a well-maintained fund, you can pay for the repair outright, saving yourself from financial stress.A golden rule for building an emergency fund is to aim for three to six months’ worth of living expenses. Start by calculating your essential monthly costs: rent or mortgage, utilities, groceries, transportation, and any recurring expenses like insurance premiums. For instance, if your basic monthly outgo is ₹50,000, your emergency fund target should be ₹1.5 to ₹3 lakhs. However, don’t let this figure overwhelm you. Start small. Even saving ₹500 or ₹1,000 a month can accumulate over time. Remember the saying, “Little drops make the mighty ocean.”One of the simplest hacks to jumpstart your emergency fund is the 30-day no-spend challenge. For an entire month, commit to buying only essentials. No eating out, no impulsive online shopping, and no fancy coffee runs. Channel the money you save into your emergency fund. A family I know used this trick and managed to save ₹12,000 in a single month, which gave them a significant head start on their fund.Another effective method is the “round-up” savings hack. Many digital banking apps offer this feature, where every purchase you make is rounded up to the nearest ₹10 or ₹100, and the difference is automatically transferred to a savings account. For example, if you spend ₹452 on groceries, the app rounds it up to ₹500 and transfers ₹48 to your savings. Over time, these small contributions can add up significantly without you even noticing.Household examples can provide more inspiration for saving. Think of meal prepping, for instance. Preparing meals at home not only saves money but also reduces food waste. A couple I know started cooking in bulk on Sundays and packing lunches for the week. This saved them ₹3,000 a month, which went directly into their emergency fund. Similarly, families can sell unused items lying around the house. Old furniture, electronics, or even books gathering dust can be sold online for cash, which can then be funneled into savings.When it comes to storing your emergency fund, accessibility is key. It should be easy to access in emergencies but not so easy that you’re tempted to dip into it for non-essential expenses. A high-yield savings account is a popular choice because it keeps your money liquid while earning some interest. Alternatively, you could consider opening a separate bank account exclusively for emergencies. One family labeled their emergency account “Only Break in Case of Fire” to discourage themselves from spending the money frivolously.One trick to make emergency savings less painful is the “pay yourself first” approach. Treat your emergency fund contribution like any other bill. As soon as your salary comes in, transfer a fixed amount—say ₹5,000—into your fund. Automating this transfer ensures consistency and eliminates the temptation to skip a month. For instance, a teacher I met set up an automatic transfer of ₹2,500 every payday. Within a year, she had saved ₹60,000 without even feeling the pinch.Of course, building an emergency fund isn’t just about saving; it’s also about avoiding unnecessary expenses. Adopt the “wait 48 hours” rule for non-essential purchases. If you’re tempted to buy something, wait two days before making the decision. Often, you’ll find that the urge to buy fades, and the money can stay in your account instead.It’s also wise to involve the entire household in building an emergency fund. Kids can participate by turning off lights when not in use or choosing budget-friendly snacks. Spouses can challenge each other to find the best discounts or deals during grocery runs. One family I know turned saving into a fun competition, awarding a small prize to the family member who contributed the most to the fund each month.Emergency funds are not a luxury; they’re a necessity. Think of them as a financial buffer that protects your present and future. The peace of mind they provide is priceless, allowing you to focus on the solution rather than the financial strain when crises arise. With a little discipline, creativity, and the strategies shared above, building and maintaining an emergency fund becomes a manageable and even enjoyable process.So, start today. Whether you’re setting aside ₹100 or ₹10,000, every rupee counts. Life may be unpredictable, but your preparedness doesn’t have to be. As the saying goes, “Prepare for the worst, hope for the best.” With a solid emergency fund, you’re not just hoping—you’re ready.",
    "Savings Strategies": "Saving money is an essential life skill that provides financial security and helps achieve long-term goals. However, adopting effective savings strategies often feels challenging, especially in the face of rising costs and unexpected expenses. The key to successful saving lies in breaking down the process into manageable steps and incorporating clever tricks and practical examples to make it a habit rather than a chore.To begin with, it is crucial to understand the power of budgeting. A well-crafted budget is the foundation of any savings plan. Start by listing all sources of income and categorizing expenses into fixed and variable costs. Fixed costs include rent, utilities, and insurance, while variable costs cover discretionary spending such as dining out and entertainment. A simple yet effective hack is the '50/30/20 rule': allocate 50% of income to necessities, 30% to wants, and 20% to savings or debt repayment. For instance, if your monthly income is $2,000, set aside $400 for savings right at the start. Treat it like a non-negotiable bill—out of sight, out of temptation.Small, consistent changes in daily habits can lead to significant savings over time. One common household example is meal prepping. Preparing meals at home instead of eating out not only saves money but also promotes healthier eating. A family of four can save hundreds of dollars a month by cooking in bulk and storing portions in the freezer. Additionally, creating a shopping list before heading to the grocery store can prevent impulse purchases. A clever hack is to shop with cash instead of credit cards. When you have a limited amount of physical money, you’re less likely to overspend.Another simple yet overlooked strategy is to focus on reducing recurring expenses. For instance, scrutinize subscription services. Do you really need three streaming platforms, a monthly gym membership, and a subscription box service? Canceling underused services can free up significant funds. Similarly, take advantage of annual billing options for services you genuinely need, as they often come with discounts compared to monthly payments. A practical household example is switching to energy-efficient appliances and lightbulbs. While the initial investment may seem high, they reduce electricity bills significantly over time.When it comes to shopping, timing is everything. Savvy savers plan purchases around seasonal sales and clearance events. For instance, buying winter clothing in March or purchasing holiday decorations in January can yield substantial discounts. Another hack is to use cashback apps or browser extensions that automatically apply coupons at checkout. Combining these tools with loyalty programs ensures you get the best deals. For example, using a store’s rewards card while shopping for groceries can lead to free items or discounts over time.Saving on transportation is another area where small changes can make a big difference. Carpooling with colleagues, biking, or using public transportation can significantly reduce fuel and maintenance costs. If driving is unavoidable, ensure your car is regularly maintained to improve fuel efficiency. Another clever tip is to bundle errands into a single trip to save both time and fuel. For those who live in urban areas, consider switching to a pay-as-you-go car rental service for occasional needs instead of owning a car, which comes with insurance, registration, and maintenance costs.One of the most effective long-term savings strategies is automating your finances. Set up an automatic transfer to a dedicated savings account every payday. This 'set it and forget it' approach ensures consistent saving without requiring active decision-making. Additionally, consider opening a high-yield savings account or investing in low-risk instruments like certificates of deposit (CDs) to earn interest on your savings. A real-life example is a family using automatic transfers to build an emergency fund that covers three to six months of living expenses. This cushion provides peace of mind during unexpected financial crises.Another creative hack is to adopt a minimalist mindset. This doesn’t mean depriving yourself but rather focusing on quality over quantity. For instance, instead of buying several cheap pairs of shoes that wear out quickly, invest in one durable pair. Over time, you’ll save money and reduce waste. A household example is decluttering and selling unused items online. Platforms like eBay or Facebook Marketplace can turn your unwanted belongings into cash. Additionally, borrowing instead of buying is an underrated trick. Need a power drill for a one-time project? Borrow it from a neighbor or rent it instead of purchasing.Savings strategies also extend to family activities and entertainment. Opt for free or low-cost activities such as picnics in the park, game nights, or exploring local hiking trails. Many cities offer free museum days or community events that provide fun without the hefty price tag. For example, a family can save hundreds annually by replacing trips to the movie theater with movie nights at home using a projector and popcorn made from scratch.Lastly, it’s essential to periodically review your financial goals and adjust strategies as needed. Life circumstances change, and so should your savings plan. A practical example is negotiating bills—many service providers are willing to lower rates to retain customers. Call your internet or insurance provider and ask for discounts or promotional offers. Over time, these small efforts add up, contributing to a robust savings portfolio.In conclusion, saving money doesn’t have to be a burdensome task. By implementing clever tricks, making small lifestyle adjustments, and staying consistent, anyone can develop effective savings habits. From budgeting and meal prepping to automating finances and embracing minimalism, these strategies ensure financial stability while leaving room for enjoying life. Remember, every penny saved is a step closer to achieving your financial dreams.",
    "Retirement Planning": "Retirement planning can feel like a daunting process, but with the right mindset and approach, it can be both manageable and rewarding. Imagine it like preparing for a long, relaxing road trip. To ensure you enjoy the journey without stress, you need a clear route, a full tank, and contingencies for unexpected stops. Here, we’ll explore simple tricks, hacks, and household examples to make your retirement planning a breeze.First, let’s talk about saving early. The magic of compounding is a powerful ally in retirement planning. Think of it as planting a mango tree in your backyard. The earlier you plant it, the sooner it grows and bears fruit. A small seed today can turn into a bountiful harvest years down the line. Similarly, contributing even modest amounts to your retirement fund early can result in significant growth over time. If you’re in your 20s or 30s, start by setting aside just 10% of your income into a retirement account. It might seem like a small amount now, but over 30 or 40 years, the compounded returns can create a sizable nest egg.Budgeting is another critical aspect of retirement planning. Picture your monthly expenses as a series of jars in your kitchen—one for groceries, one for utilities, one for entertainment, and so on. To save effectively for retirement, create an extra jar labeled “retirement” and make it a priority to fill it each month. A trick to achieve this is to treat your retirement contribution like a non-negotiable bill. Automating your savings ensures you’re consistently adding to your fund without the temptation to spend elsewhere.Next, think about diversifying your investments. Relying on a single source of income in retirement is like cooking with only one ingredient—your meals will lack flavor and variety. Spread your investments across stocks, bonds, real estate, and other assets. For example, if you own your home, consider its value as part of your retirement plan. Alternatively, rental properties can provide a steady income stream in your later years. Diversification reduces risk and ensures you’re not overly reliant on one financial source.Now, let’s address debt. Carrying debt into retirement is like trying to swim with weights on your ankles. Prioritize paying off high-interest debts such as credit card balances and personal loans as early as possible. For example, if you’re paying $200 monthly toward a car loan, consider increasing the payment to $250 to shorten the loan term and reduce interest. Once your debts are cleared, redirect those payments into your retirement fund. This way, you’re building a future for yourself instead of paying for past expenses.Another clever hack is to visualize your retirement goals vividly. Imagine you’re planning a dream vacation—you’d pick a destination, calculate the costs, and plan the itinerary. Retirement works the same way. Do you dream of traveling the world, starting a small business, or simply enjoying time with family? Create a mental image of your ideal retirement lifestyle and estimate the costs associated with it. This vision helps you stay motivated to save and invest wisely.One household example for managing expenses is practicing “lifestyle inflation control.” Whenever you get a raise or bonus, it’s tempting to upgrade your car, home, or wardrobe. Instead, treat these windfalls as opportunities to boost your retirement savings. For instance, if you receive a $5,000 bonus, allocate half to your retirement fund and use the rest for modest indulgences. Over time, this habit can significantly increase your savings while still allowing you to enjoy life’s little pleasures.Health care is a major expense in retirement, so planning ahead can save you from financial stress. Think of it as stocking up your medicine cabinet—prevention is better than cure. Invest in health insurance and consider setting up a health savings account (HSA) if you’re eligible. Regular exercise, a balanced diet, and routine health checkups are small, everyday investments in your future health that can reduce medical costs later on.Now, let’s not forget the importance of a side hustle. In today’s gig economy, there are numerous ways to generate additional income. It’s like growing a kitchen garden—you’re not relying solely on the supermarket for your vegetables. Whether it’s freelancing, tutoring, or selling handmade crafts, a side hustle can provide extra funds for your retirement account. Plus, it can be a rewarding activity to continue even during retirement.Finally, keep an emergency fund separate from your retirement savings. Life’s unexpected expenses, like car repairs or medical bills, shouldn’t derail your long-term goals. Think of it as having a spare tire in your car—it’s there for emergencies, not for everyday use. Aim to save three to six months’ worth of living expenses in a liquid and accessible account. This safety net will give you peace of mind and keep your retirement plan on track.Retirement planning doesn’t have to be overwhelming or complicated. By starting early, managing your budget wisely, and incorporating these tricks and hacks into your daily life, you can create a secure and fulfilling future. Remember, the key is consistency and adaptability. Just as a well-tended garden flourishes over time, so too will your retirement fund if you nurture it with care and intention.",
    "Debt Management": "Debt is a common part of life, whether it’s a mortgage, student loan, credit card balance, or even a small loan from a friend. However, managing debt can feel overwhelming if left unchecked. By breaking it down and using clever tricks and household analogies, anyone can take control of their finances and reduce the stress of debt management.Imagine your debts as ingredients in your kitchen pantry. Some are staples, like rice or flour (long-term loans like mortgages), while others are snacks that can be consumed quickly (short-term debts like credit card bills). To cook effectively, you need to know what’s in your pantry. Similarly, the first step in debt management is understanding your debts—know how much you owe, to whom, and at what interest rate. Create a simple spreadsheet or use a budgeting app to keep track.Managing debt is like cleaning your house. Should you start with the smallest mess or tackle the largest pile first? The snowball method encourages you to pay off your smallest debts first, gaining quick wins that boost motivation. On the other hand, the avalanche method focuses on clearing debts with the highest interest rates first, saving you more money in the long run. Both methods work, so choose the one that matches your personality. Think of it like decluttering—some people prefer clearing one drawer at a time, while others want to address the most chaotic room.To manage debt, you need a solid budget, just like a recipe ensures a balanced meal. Start with your income as the main ingredient and divide it into essential expenses (housing, utilities, food), debt repayment, and discretionary spending. The 50/30/20 rule can act as your guide: allocate 50% of your income to needs, 30% to wants, and 20% to savings and debt payments. If 20% seems too high, consider cutting back on luxuries like daily coffee shop visits or dining out. Making coffee at home can save you thousands over a year—money that can go toward reducing debt.Many people forget that debts, like the prices at a flea market, are often negotiable. If you’re struggling, call your creditors and explain your situation. You may be able to secure a lower interest rate, extend repayment terms, or settle for a reduced amount. Think of it like bargaining at the market—if you don’t ask, you’ll never know what discounts are available.Managing spending can be tricky when using credit cards. Try the envelope system—withdraw cash for specific categories like groceries, entertainment, and transport. Once the envelope is empty, you stop spending. It’s like meal prepping for your finances: you plan ahead and stick to what you’ve allocated. This simple trick helps curb overspending and ensures more money goes toward paying off debt.If your budget feels too tight to make meaningful debt payments, consider adding a side hustle to the mix. Think of it as planting a vegetable garden—you invest time and effort upfront, but the rewards can significantly supplement your pantry. Freelancing, tutoring, selling handmade goods, or even renting out an unused room can provide extra cash to chip away at your debt.Interest is like a slow leak in a faucet—it might not seem like much, but over time, it adds up significantly. High-interest debts, like credit cards, can drain your finances faster than you realize. Prioritize paying these off quickly. If possible, transfer your balance to a lower-interest card or consolidate debts into a single loan with a more favorable rate. This is like fixing the leak before it floods your home.An emergency fund is like having a spare tire in your car—it keeps you from getting stranded when life throws unexpected expenses your way. Aim to save at least three to six months’ worth of essential expenses. This prevents you from relying on credit cards or loans when emergencies arise, keeping your debt levels stable. Start small—save $500, then build from there.Debt management doesn’t always mean earning more; it often means spending smarter. Look for hidden expenses, like unused subscriptions or high utility bills. Simple changes, like switching to energy-efficient bulbs or cooking meals at home, can save hundreds of dollars annually. These savings can then be redirected toward debt repayment. It’s like finding extra change in your couch cushions—it might seem small, but it adds up over time.Paying off debt is a long journey, so celebrate your victories along the way. When you clear a credit card balance or finish paying off a car loan, reward yourself in small, budget-friendly ways. It’s like finishing a long workout—you deserve a moment to enjoy the progress you’ve made.Lastly, changing your mindset is crucial. Instead of viewing debt as a burden, see it as a challenge you’re capable of conquering. Visualize a future where you’re debt-free, and remind yourself of this goal when tempted to overspend. This shift is like planting flowers in a barren yard—it takes time, but the results are worth it.Debt management isn’t a one-size-fits-all process, but with these tricks, hacks, and household analogies, it becomes a manageable and even empowering journey. Like a well-organized home or a deliciously balanced meal, a debt-free life is the result of consistent effort, thoughtful planning, and a little creativity.",
    "Insurance Essentials": "Insurance is often seen as a boring necessity—something we grudgingly pay for and hope never to use. However, understanding insurance essentials can not only protect you from financial disaster but also save you money, time, and stress in the long run. In this essay, we’ll dive deep into the fundamentals of insurance, peppered with practical tips, clever hacks, and relatable household examples to help you make the most of it.At its core, insurance is a promise: you pay a premium to transfer your financial risks to an insurance company. This promise comes in many forms—health insurance, car insurance, life insurance, home insurance, and more. Think of it like pooling resources in a community. If one neighbor’s house burns down, everyone chips in to help them rebuild. By paying a small amount regularly, you avoid the risk of bearing a huge cost when something goes wrong.Let’s start with health insurance, often the most critical yet confusing type. Imagine your body is like a car. You wouldn’t skip oil changes or tire replacements, right? Health insurance works similarly: it helps you cover preventive care, like annual checkups, and shields you from the high costs of “major repairs,” such as surgeries or hospital stays. A smart hack here is to understand your deductible—the amount you pay before insurance kicks in. If you have a high-deductible plan, set aside an emergency fund equal to your deductible in a Health Savings Account (HSA). Not only is this money tax-free, but you can use it for medical expenses whenever needed. Think of it as a “health rainy day fund.”Car insurance is another area where small hacks can lead to big savings. Have you ever wondered why premiums vary so much? It’s because insurers assess risk based on factors like your driving record, location, and even the type of car you drive. A great tip is to bundle your car and home insurance with the same provider, as most companies offer multi-policy discounts. For example, if your car is an older model with a low market value, consider dropping collision coverage. Instead, put the money you save into a separate fund for future car repairs or replacement. It’s like deciding not to pay for an extended warranty on an old appliance—you know the replacement cost is manageable.When it comes to home insurance, think of your house as a treasure chest filled with all your possessions. Your policy not only protects the structure but also the contents inside. Here’s a trick: take an inventory of your belongings by snapping photos or shooting a quick video of each room. Store this digitally for easy access in case you need to file a claim. One household example is the classic scenario of a burst pipe flooding your basement. If you document your belongings ahead of time, you’ll have an easier time proving the value of that ruined sofa or TV. Also, don’t overlook add-ons like flood or earthquake insurance if you live in high-risk areas. These are like the extra locks you’d put on a door if you knew you lived in a rough neighborhood.Life insurance might seem like something only parents or the elderly need, but it’s a financial safety net for anyone with dependents or debts. Imagine a family as a table with multiple legs. If one leg (the breadwinner) breaks, the table can still stand—thanks to life insurance. A household trick here is to buy term life insurance instead of whole life insurance. Term policies are simpler and cheaper, allowing you to get more coverage for less money. Use the savings to invest in your retirement or a college fund for your kids. Another hack is to reassess your policy every few years. As your financial situation changes, you might find you need more or less coverage.Travel insurance, while often overlooked, can be a lifesaver for frequent flyers or vacationers. Think of it as a seatbelt for your trip—it might seem unnecessary until something goes wrong. Did you know that travel insurance often covers lost baggage, flight cancellations, and even emergency medical evacuations? If you’re a household with a love for globetrotting, buy an annual travel policy instead of separate ones for each trip. It’s like buying a membership at your favorite gym instead of paying for single visits—it saves you money and hassle.Finally, disability insurance is like the spare tire in your car—something you don’t think about until you desperately need it. If you rely on your income to pay for groceries, rent, or your child’s education, disability insurance ensures that you’re not financially stranded if you can’t work due to illness or injury. A great hack here is to check if your employer offers group disability insurance. Often, it’s cheaper than buying an individual policy. If you’re self-employed, look for policies that allow you to customize the waiting period and benefit duration to lower your premiums.Across all types of insurance, one universal trick is to shop around and compare quotes regularly. Insurers often reward new customers with discounts, so it pays to be a savvy shopper. Think of this like switching cell phone plans—sometimes, loyalty doesn’t pay off. Another practical tip is to raise your deductible if you can afford it. A higher deductible means lower premiums, and the money saved can be put into an emergency fund.Insurance doesn’t have to be daunting or dull. By understanding the basics and using these tricks and hacks, you can turn it into a powerful tool for financial security. From bundling policies to documenting your belongings, small actions can lead to significant benefits. So, the next time you pay your premiums, remember—you’re not just buying insurance; you’re buying peace of mind.",
    "Tax Planning": "Tax planning in India is an essential aspect of financial management, which allows individuals and businesses to optimize their tax liabilities while complying with the country’s tax laws. The Indian tax system is complex, with various exemptions, deductions, and credits available under different provisions of the Income Tax Act, making it crucial for taxpayers to plan their taxes wisely to avoid unnecessary financial burdens. Tax planning is not only about reducing taxes but also about managing one’s finances efficiently to save for the future while staying within the boundaries of the law.The first step in tax planning involves understanding the different types of taxes that an individual or business is subject to. In India, the primary taxes include income tax, Goods and Services Tax (GST), and various other indirect taxes. For individuals, the Income Tax Act lays down various tax slabs based on annual income, which range from 0% to 30% for taxpayers below 60 years of age. With these progressive rates, individuals can plan their finances to ensure that they fall into the lower tax brackets, thus minimizing their tax liability.A fundamental way to reduce tax liability is through exemptions, deductions, and rebates available under various sections of the Income Tax Act. One of the most commonly used exemptions is Section 80C, which allows deductions of up to Rs. 1.5 lakh on investments in specified instruments like Public Provident Fund (PPF), Employees' Provident Fund (EPF), Life Insurance Premiums, National Savings Certificates (NSC), and tax-saving Fixed Deposits. These instruments not only help reduce taxable income but also promote long-term financial planning. For example, an individual contributing to a PPF account not only enjoys tax deductions but also accumulates tax-free interest, making it a win-win strategy for tax planning.Another popular way to save taxes is through the deduction under Section 80D, which allows taxpayers to claim deductions for premiums paid for health insurance policies. This deduction can go up to Rs. 25,000 for individuals below 60 years of age and up to Rs. 50,000 for senior citizens. This not only provides tax benefits but also ensures that the taxpayer has sufficient coverage in case of medical emergencies. By incorporating these small, yet effective, strategies into their financial planning, individuals can save a significant amount in taxes while securing their financial future.Household expenses also offer tax-saving opportunities. A practical example is the payment of home loan interest. Section 24 of the Income Tax Act allows taxpayers to claim a deduction of up to Rs. 2 lakh on the interest paid on home loans. This means that if someone is servicing a home loan, a portion of the interest paid every year is eligible for tax deduction, thus reducing their taxable income. Additionally, for first-time homebuyers, Section 80EEA allows an additional deduction of Rs. 1.5 lakh on interest payments. Taxpayers can combine both deductions to maximize their savings.Furthermore, investing in the National Pension Scheme (NPS) also offers significant tax benefits under Section 80CCD. NPS contributions can provide additional deductions up to Rs. 50,000, which is over and above the Rs. 1.5 lakh limit of Section 80C. This can be a great way to not only reduce taxes but also build a retirement corpus that is relatively low-cost compared to other pension schemes.For those who are self-employed or run small businesses, tax planning involves more than just income tax; it includes strategies like managing GST liabilities and optimizing deductions related to business expenses. For instance, a small business owner can claim deductions for various expenses such as rent, salaries, and office supplies. If the business owner runs a home-based office, a portion of the household expenses, such as electricity bills and internet costs, can be claimed as business expenses, thus lowering the taxable income of the business.Taxpayers can also take advantage of capital gains tax exemptions. When individuals sell long-term capital assets like real estate or stocks, they are subject to capital gains tax. However, if the property is sold after a holding period of more than two years, it qualifies as a long-term capital asset, and the tax on the gain can be minimized by investing in specific instruments like the Capital Gains Account Scheme or by reinvesting in another property under Section 54. This trick helps individuals save significant amounts on taxes while also creating wealth through property investment.Additionally, if a taxpayer is engaged in any agricultural activity or owns agricultural land, they are eligible for a tax exemption on income derived from agriculture, which is an often-overlooked provision. Farmers can use this exemption to plan their income sources and ensure that their earnings from agricultural activities remain tax-free.In the Indian tax system, understanding the nuances of tax planning is crucial for maximizing savings and investments. A little creativity in how one allocates their income and expenses can go a long way in minimizing tax liabilities. A well-thought-out strategy will ensure that individuals not only save on taxes but also build a solid financial foundation. Whether it is through the simple act of contributing to a PPF account or the more sophisticated approach of managing capital gains and home loan interests, tax planning can empower individuals and businesses to make smarter financial decisions.Lastly, it is essential to note that tax planning must always be carried out within the legal framework. The goal is not to evade taxes but to optimize the tax burden using available provisions and exemptions. By doing so, individuals can ensure that their financial resources are being used in the most efficient manner, contributing to both their short-term savings and long-term financial goals. In the ever-evolving tax landscape of India, staying informed about the latest updates and amendments to the tax laws is also crucial to ensure that one’s tax planning strategies remain effective and legally sound.",
    "Building Creditworthiness": "Building creditworthiness in India is a crucial element for anyone looking to gain access to financial resources, be it for personal loans, home loans, credit cards, or even starting a business. In the Indian context, where access to credit plays a pivotal role in realizing personal and professional goals, understanding how to build and maintain a strong credit score becomes an essential part of one’s financial journey. However, building creditworthiness isn’t just about borrowing money; it’s about building a reputation in the eyes of lenders, ensuring you’re seen as a responsible borrower capable of repaying your debts on time. While there are no shortcuts to building solid creditworthiness, there are plenty of tricks, hacks, and household examples that can simplify the process and make it less intimidating.At the core of building creditworthiness is maintaining a good credit score. In India, the Credit Information Bureau (India) Limited, or CIBIL, is one of the most prominent credit bureaus that calculate an individual’s credit score, which ranges from 300 to 900. A score above 750 is considered excellent, while a score below 600 can significantly hinder your ability to obtain loans or credit. Now, for those just starting their credit journey or looking to improve their score, one of the most effective ways to build credit is by getting a credit card. But here’s the trick – don’t rush into getting a high-limit credit card without understanding how to use it effectively. Start with a low-limit credit card or a secured credit card, where you deposit a sum of money as collateral, and use it for small, manageable purchases like grocery bills or mobile recharges. The idea here is to establish a history of responsible credit usage. Pay off your credit card bill on time, every time. This timely payment contributes positively to your credit score.One might think that just keeping their credit card usage in check is enough, but there’s more to the story. A hack that many financial experts swear by is maintaining a low credit utilization ratio. This means you should aim to use less than 30% of your available credit limit. For example, if your credit limit is ₹10,000, you should aim to use no more than ₹3,000 at any given point. Keeping your credit utilization low ensures that you don’t appear desperate for credit, which can negatively impact your creditworthiness. It also shows that you’re in control of your finances, not relying excessively on borrowed money. This technique is often referred to as ‘credit discipline,’ and it’s an easy way to keep your credit score moving upwards.Another effective method for building creditworthiness in the Indian scenario is taking out a small loan and repaying it consistently. This could be a personal loan or a loan against gold, which is common in India. But be careful; this isn’t about taking loans unnecessarily. The trick is to borrow a manageable amount, one that you are sure you can repay without any difficulty, and then ensure you make your EMI payments on time. Timely repayment is the key to making a strong impression on lenders. It’s like paying rent for a house; you must make sure your landlord is happy with your consistency before you can move to a bigger house. Similarly, lenders will reward your timely payments by offering better credit options down the road.However, it’s also important to be mindful of another household example that many overlook – avoiding multiple loan applications in a short span. When you apply for loans or credit cards frequently, each inquiry is recorded on your credit report and might reduce your score. This is because multiple inquiries in a short time frame could indicate to lenders that you are desperate for credit, potentially leading them to question your financial stability. The trick here is to only apply for credit when absolutely necessary and to be strategic about when you do so.A crucial but often ignored aspect of building creditworthiness in India is maintaining a clean financial history, which means avoiding defaults and late payments on any existing loans or bills. It’s not just your credit card or loan payments that count; utility bills like electricity, water, or mobile phone bills can also have an impact on your credit score if they are reported to credit bureaus. Many people have the misconception that their creditworthiness is solely built through loans and credit cards. In reality, your ability to pay for utilities on time and manage monthly payments efficiently is an important part of your overall financial responsibility. A simple trick here is to set up automated payments for bills that are recurring, so you never miss a due date. This ensures that you’re not only protecting your credit score but also building trust with lenders who will see you as a reliable borrower.Building creditworthiness in India can also be enhanced by avoiding the temptation to keep too many credit cards open. This is a scenario that many find themselves in – opening multiple cards for the rewards, discounts, and perks they offer. However, having too many open lines of credit, even if you don’t use them, can negatively affect your score. It’s like owning a wardrobe full of clothes you never wear – it just adds clutter. Instead, focus on one or two cards and use them wisely. This will help you maintain a healthy credit history without overwhelming yourself with excess credit.A household trick that’s incredibly effective but often overlooked is the power of a stable income. Lenders are more likely to approve loans if they see a consistent and predictable income. In India, many people work in informal sectors, where income is irregular. However, if you’re employed, ensure that your payslips or bank statements show a steady stream of income. If you are self-employed, you’ll need to demonstrate a history of consistent earnings, usually through your income tax returns (ITR). This is an often overlooked but powerful factor in building creditworthiness because a reliable income increases your trustworthiness in the eyes of lenders.Lastly, one of the most important tricks to building creditworthiness is understanding and correcting any mistakes on your credit report. You can get a free credit report from agencies like CIBIL once a year. Review it for any errors, such as incorrect account details or missed payments that were actually paid on time. If you find discrepancies, challenge them immediately. A simple correction could significantly improve your score and your creditworthiness.In the end, building creditworthiness in India is not an overnight process, but it’s entirely within reach. Through strategic use of credit cards, timely payments, maintaining a low credit utilization ratio, and ensuring you stay on top of utility payments, anyone can build a strong credit profile. The key is consistency, discipline, and making well-informed financial decisions. Just like how small household habits like saving on groceries or budgeting for a family trip add up over time, small steps in credit management can lead to significant rewards in the form of financial opportunities. By understanding these tricks and hacks, you not only make yourself more creditworthy but also lay the foundation for financial freedom and success."
}

if st.button(translate_text("Start Lesson", selected_lang)):
    lesson_content = lesson_contents.get(topic_choice, "No content available for this topic.")
    translated_lesson_content = translate_text(lesson_content, selected_lang)
    st.write(translated_lesson_content)
    audio_file = play_tts(translated_lesson_content, selected_lang)
    if audio_file:  # Check if audio_file is not None
        st.audio(audio_file, format='audio/mp3')
else:
    st.error("Failed to generate audio.")

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
        savings_message = translate_text(
            f"To achieve your goal of '{savings_goal_desc}' in {duration} months, you need to save {savings_goal_amount} INR in total . Your current plan of saving {monthly_savings} INR per month will only result in {total_savings} INR, leaving a gap of {savings_gap} INR.",
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

# EasyLoan Application Section
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

    send_email(RECEIVER_EMAIL, subject, body)
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
    prev_hash = blockchain[-1]["hash"] if blockchain else "0"
    new_block = create_block(data, prev_hash)
    blockchain.append(new_block)

# App starts
st.title("Innovative Insurance Solutions")

# Blockchain-Powered Community Insurance Pools (BCP)
st.header("Blockchain-Powered Community Insurance Pools (BCP)")
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
            advisory = response.strip()  # Get the generated advisory text
            st.write(translate_text(f" Answer: {advisory}", selected_lang))
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

# Function to load and preprocess the dataset
def load_and_train_model():
    url = "https://raw.githubusercontent.com/That-Tech-Geek/Akshara/main/insurance.csv"
    df = pd.read_csv(url)

    # Debugging: Print the first few rows and columns of the DataFrame
    print("DataFrame Columns:", df.columns)
    print("First few rows of the DataFrame:")
    print(df.head())

    # Preprocess the data (convert categorical variables to numerical)
    df = pd.get_dummies(df, columns=['sex', 'smoker', 'region'], drop_first=True)

    # Define features and target variable
    X = df.drop('expenses', axis=1)
    y = df['expenses']

    # Train the Random Forest model
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X, y)

    return model

# Function to get predictions from the model
def get_prediction(age, sex, bmi, children, smoker, region, model, feature_names):
    # Prepare the input data
    userInput = pd.DataFrame([[age, sex, float(bmi), children, smoker, region]], 
                              columns=['age', 'sex', 'bmi', 'children', 'smoker', 'region'])

    # Preprocess the input data (convert categorical variables to numerical)
    userInput = pd.get_dummies(userInput, columns=['sex', 'smoker', 'region'], drop_first=True)

    # Ensure the input has the same columns as the training data
    userInput = userInput.reindex(columns=feature_names, fill_value=0)

    # Make the prediction
    predicted_expenses = model.predict(userInput)

    return round(predicted_expenses[0], 2)

def show_predict_page():
    
    with st.form('form', clear_on_submit=True):
        age = st.text_input('Age', placeholder='Age')
        sex = st.selectbox("Sex", ['Male', 'Female'])
        bmi = st.text_input('BMI', placeholder='BMI')
        children = st.text_input('Children', placeholder='Number of Children')
        smoker = st.selectbox('Smoker', ['Yes', 'No'])
        reg = ['Northeast', 'Northwest', 'Southeast', 'Southwest']
        region = st.selectbox('Region', reg)

        predict = st.form_submit_button("Predict Expenses")

        if predict:
            try:
                # Validate inputs
                if not age or not bmi or not children:
                    st.error("Please fill in all fields.")
                    return

                age = int(age)
                bmi = float(bmi)
                children = int(children)

                # Ensure the inputs are in the expected format for the model
                predicted_expenses = get_prediction(age, sex, bmi, children, smoker, region, model, feature_names)
                st.success(f'The predicted insurance expenses are: ${predicted_expenses:.2f}')
            except ValueError as e:
                st.error(f"Input error: {str(e)}")
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")

# Run the application
if __name__ == "__main__":
    show_predict_page()

# Footer
st.write("# Thank you for using Akshara!")
