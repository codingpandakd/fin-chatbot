import streamlit as st
import json
import os
from datetime import datetime, timedelta, date

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


# Get total income
def get_total_income(transactions):
    total = sum(t["amount"] for t in transactions if t["amount"] > 0)
    return total


# Get income by category
def get_income_by_category(category_name):
    total = sum(t["amount"] for t in account["transactions"] if t["category"].lower() == category_name.lower() and t["amount"] > 0)
    return total


# Get largest transaction
def get_largest_transaction():
    expenses = [t for t in account["transactions"] if t["amount"] < 0]
    if not expenses:
        return None
    largest = max(expenses, key=lambda x: abs(x["amount"]))
    return largest


# Get spending by date range
def get_spending_by_date_range(transactions, start_date_obj, end_date_obj):
    total_spent = 0
    for t in transactions:
        try:
            transaction_date_obj = datetime.strptime(t["date"], "%Y-%m-%d").date()
            if t["amount"] < 0 and start_date_obj <= transaction_date_obj <= end_date_obj:
                total_spent += abs(t["amount"])
        except ValueError:
            # Handle cases where date parsing might fail for a transaction, though unlikely with current data
            print(f"Warning: Could not parse date for transaction: {t}")
            continue
    return total_spent


# Get income by date range
def get_income_by_date_range(transactions, start_date_obj, end_date_obj):
    total_income = 0
    for t in transactions:
        try:
            transaction_date_obj = datetime.strptime(t["date"], "%Y-%m-%d").date()
            if t["amount"] > 0 and start_date_obj <= transaction_date_obj <= end_date_obj:
                total_income += t["amount"]
        except ValueError:
            print(f"Warning: Could not parse date for transaction: {t}") # Should not happen with current data
            continue
    return total_income


# Process user query (rule-based)
def process_query(query):
    query = query.lower().strip()

    # Check balance
    if "balance" in query:
        return f"Your balance is ${account['balance']:.2f}."

    # List transactions (general, or filtered for income)
    # Handles "transaction history", "show my transactions", "show income transactions"
    elif "transaction" in query or "history" in query:
        if "income" in query : # e.g. "show income transactions"
            response = "Income transactions:\n"
            income_transactions = [t for t in account["transactions"] if t["amount"] > 0]
            if not income_transactions:
                return "No income transactions found."
            # Sort by date, most recent first, then format
            for t in sorted(income_transactions, key=lambda x: x['date'], reverse=True):
                response += f"{t['date']}: {t['description']} (${t['amount']:+.2f}, {t['category']})\n"
        else: # General transaction history
            response = "Recent transactions:\n"
            # Display last 5 transactions or fewer if not enough, most recent first
            # Sorting by date before taking last 5 might be better if data isn't pre-sorted. Assuming it is for now.
            display_transactions = sorted(account["transactions"], key=lambda x: x['date'], reverse=True)[-5:]
            if not display_transactions:
                return "No transactions found."
            for t in display_transactions:
                response += f"{t['date']}: {t['description']} (${t['amount']:+.2f}, {t['category']})\n"
        return response.strip()


    # Total spending (more specific to avoid clashes)
    elif "spent" in query and "total" in query: # e.g. "how much have I spent in total?"
        total_spent_val = sum(abs(t["amount"]) for t in account["transactions"] if t["amount"] < 0)
        return f"You've spent ${total_spent_val:.2f} in total."

    # Total income
    elif "income" in query and "total" in query : # e.g. "how much income in total?"
        total_income_val = get_total_income(account["transactions"])
        return f"Your total income is ${total_income_val:.2f}."

    # Spending by category (more specific)
    elif "spend on food" in query or ("food" in query and "spent" in query): # order matters for parsing "food"
        total = get_spending_by_category("food")
        return f"You spent ${total:.2f} on food."
    elif "spend on transport" in query or ("transport" in query and "spent" in query):
        total = get_spending_by_category("transport")
        return f"You spent ${total:.2f} on transport."
    # Add other spending categories as needed

    # Income by category (e.g., "income from salary")
    elif "income from" in query:
        category_name = query.split("income from")[-1].strip().rstrip('?.!') # Remove punctuation
        if category_name:
            total_income_cat = get_income_by_category(category_name)
            if total_income_cat > 0:
                 return f"You received ${total_income_cat:.2f} as income from {category_name}."
            else:
                 return f"No income found from {category_name} or '{category_name}' is not an income category."
        else: # "income from " with nothing after
            return "Please specify a category for income (e.g., 'income from salary')."


    # Income last month
    elif "income last month" in query or ("last month" in query and "income" in query):
        today = date.today()
        first_day_current_month = today.replace(day=1)
        end_of_last_month = first_day_current_month - timedelta(days=1)
        start_of_last_month = end_of_last_month.replace(day=1)
        total_income_last_month = get_income_by_date_range(account["transactions"], start_of_last_month, end_of_last_month)
        return f"Your income last month ({start_of_last_month.strftime('%B %Y')}) was ${total_income_last_month:.2f} (from {start_of_last_month.strftime('%Y-%m-%d')} to {end_of_last_month.strftime('%Y-%m-%d')})."

    # Largest transaction (implies expense)
    elif "largest" in query or "biggest" in query: # This implies expense
        largest = get_largest_transaction()
        if largest:
            return f"Your largest expense was ${abs(largest['amount']):.2f} at {largest['description']} on {largest['date']}."
        return "No expenses found."

    # Spending last week
    elif "last week" in query and "spend" in query:
        today = date.today()
        start_of_last_week = today - timedelta(days=today.weekday() + 7)
        end_of_last_week = today - timedelta(days=today.weekday() + 1)
        total_spent = get_spending_by_date_range(account["transactions"], start_of_last_week, end_of_last_week)
        return f"You spent ${total_spent:.2f} last week (from {start_of_last_week.strftime('%Y-%m-%d')} to {end_of_last_week.strftime('%Y-%m-%d')})."

    # Spending in a specific month
    elif "in " in query and ("spend" in query or "expenses" in query): # e.g. "how much did I spend in May?"
        # Basic month extraction, assumes "in [Month]" format for spending
        try:
            # query.split("in ")[1] gets text after "in "
            # .split(" ")[0] gets the first word (month)
            month_name_str = query.split("in ")[1].split(" ")[0].strip().lower().rstrip('?.!')
            month_map = {
                "january": 1, "february": 2, "march": 3, "april": 4,
                "may": 5, "june": 6, "july": 7, "august": 8,
                "september": 9, "october": 10, "november": 11, "december": 12
            }
            month_number = month_map.get(month_name_str)

            if month_number:
                current_year = datetime.now().year
                start_date_month = date(current_year, month_number, 1)
                if month_number == 12:
                    end_date_month = date(current_year, 12, 31)
                else:
                    end_date_month = date(current_year, month_number + 1, 1) - timedelta(days=1)

                total_spent = get_spending_by_date_range(account["transactions"], start_date_month, end_date_month)
                return f"You spent ${total_spent:.2f} in {month_name_str.capitalize()} {current_year} (from {start_date_month.strftime('%Y-%m-%d')} to {end_date_month.strftime('%Y-%m-%d')})."
            else:
                return "Could not determine the month from your query. Please use a full month name (e.g., 'in April')."
        except IndexError:
            # This might happen if "in " is at the end of the query
            return "Sorry, I couldn't understand the date range. Try 'how much did I spend last week?' or 'what were my expenses in April?'"


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