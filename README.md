# fin-chatbot
FinChat: AI-Powered Bank Account Chatbot
FinChat is a simple, web-based chatbot that lets users interact with a mock bank account through natural language queries. Built with Python and Streamlit, it supports checking balances, viewing transactions, analyzing spending by category (e.g., food, transport), and identifying the largest expense. This project demonstrates my learning in Python, web development, and fintech applications.
Features

Balance Check: Ask "What's my balance?" to see the current balance.
Transaction History: Query "Show transactions" to view the last 5 transactions.
Spending Insights: Ask "How much did I spend on food?" or "Total spent" for category or overall spending.
Largest Expense: Query "What's my biggest expense?" to find the highest transaction.
Data Persistence: Account data is saved to account.json for continuity.
Web Interface: A clean, browser-based chat UI powered by Streamlit.

Tech Stack

Python: Core logic and data handling.
Streamlit: Web interface for the chatbot.
uv: Package manager for dependency management.
JSON: Stores mock account data.

Setup Instructions

Prerequisites:

Python 3.8+ (download).
uv package manager (install).


Clone the Repository:
git clone https://github.com/your-username/finchat.git
cd finchat


Set Up with uv:
uv init finchat
uv add streamlit


Run the App:
uv run streamlit run finchat_web.py


A browser window will open (e.g., http://localhost:8501).
Type queries like "What's my balance?" or "Show transactions" in the chat input.



Usage

Example Queries:
"What's my balance?" → "Your balance is $500.00."
"How much did I spend on food?" → "You spent $100.00 on food."
"What's my biggest expense?" → "Your largest expense was $50.00 at Coffee Shop on 2025-05-01."
"Show transactions" → Lists recent transactions with dates, amounts, and categories




