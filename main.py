import streamlit as st
import json
import os

# Mock bank account data (loaded from/saved to JSON)
ACCOUNT_FILE = "account.json"
DEFAULT_ACCOUNT = {
    "balance": 500.00,
    "transactions": [
        {"date": "2025-05-01", "amount": -50.00, "description": "Coffee Shop", "category": "food"},
        {"date": "2025-05-02", "amount": -20.00, "description": "Grocery Store", "category": "food"},
        {"date": "2025-05-03", "amount": 100.00, "description": "Salary Deposit", "category": "income"},
        {"date": "2025-05-04", "uvamount": -30.00, "description": "Restaurant", "category": "food"},
        {"date": "2025-05-05", "amount": -15.00, "description": "Bus Ticket", "category": "transport"},
    ]
}


# Load or initialize account data
def load_account():
    if os.path.exists(ACCOUNT_FILE):
        with open(ACCOUNT_FILE, "r") as f:
            return json.load(f)
    return DEFAULT_ACCOUNT


# Save account data
def save_account(account):
    with open(ACCOUNT_FILE, "w") as f:
        json.dump(account, f, indent=4)


account = load_account()


# Get total spent by category
def get_spending_by_category(category):
    total = sum(abs(t["amount"]) for t in account["transactions"] if t["category"] == category and t["amount"] < 0)
    return total


# Get largest transaction
def get_largest_transaction():
    expenses = [t for t in account["transactions"] if t["amount"] < 0]
    if not expenses:
        return None
    largest = max(expenses, key=lambda x: abs(x["amount"]))
    return largest


# Process user query (rule-based)
def process_query(query):
    query = query.lower().strip()

    # Check balance
    if "balance" in query:
        return f"Your balance is ${account['balance']:.2f}."

    # List recent transactions
    elif "transaction" in query or "history" in query:
        response = "Recent transactions:\n"
        for t in account["transactions"][-5:]:
            response += f"{t['date']}: {t['description']} (${t['amount']:.2f}, {t['category']})\n"
        return response.strip()

    # Total spending
    elif "spent" in query and not any(c in query for c in ["food", "transport"]):
        total_spent = sum(abs(t["amount"]) for t in account["transactions"] if t["amount"] < 0)
        return f"You've spent ${total_spent:.2f} in total."

    # Spending by category
    elif "food" in query:
        total = get_spending_by_category("food")
        return f"You spent ${total:.2f} on food."
    elif "transport" in query:
        total = get_spending_by_category("transport")
        return f"You spent ${total:.2f} on transport."

    # Largest transaction
    elif "largest" in query or "biggest" in query:
        largest = get_largest_transaction()
        if largest:
            return f"Your largest expense was ${abs(largest['amount']):.2f} at {largest['description']} on {largest['date']}."
        return "No expenses found."

    # Default response
    else:
        return "Sorry, I didn't understand. Try asking about balance, transactions, spending, or largest expense."


# Streamlit web interface
st.title("FinChat: Your Bank Account Assistant")
st.write("Ask about your balance, transactions, spending, or largest expense.")

# Initialize session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Type your question (e.g., 'What's my balance?')"):
    # Add user message to history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Get and display FinChat response
    response = process_query(prompt)
    st.session_state.messages.append({"role": "assistant", "content": response})
    with st.chat_message("assistant"):
        st.markdown(response)

# Save account data after each interaction
save_account(account)