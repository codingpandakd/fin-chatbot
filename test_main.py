import unittest
from unittest.mock import patch, MagicMock
from datetime import date, datetime, timedelta

# Assuming main.py is in the same directory or accessible in PYTHONPATH
# If main.py is one level up, you might need path adjustments in a real scenario,
# but for this environment, direct import should work if both are in /app
import main

# Define a fixed "today" for consistent testing of relative date queries
FIXED_TODAY = date(2025, 5, 15)

MOCK_TRANSACTIONS_BASE = [
    # Expenses
    {"date": "2025-05-01", "amount": -50.00, "description": "Coffee Shop", "category": "food"},
    {"date": "2025-05-02", "amount": -20.00, "description": "Grocery Store", "category": "food"},
    {"date": "2025-05-04", "amount": -30.00, "description": "Restaurant", "category": "food"},
    {"date": "2025-05-05", "amount": -15.00, "description": "Bus Ticket", "category": "transport"},
    {"date": "2025-04-20", "amount": -25.00, "description": "Books", "category": "education"},
    {"date": "2025-04-28", "amount": -10.00, "description": "Snacks", "category": "food"},

    # Income
    {"date": "2025-05-03", "amount": 200.00, "description": "Salary Deposit", "category": "salary"},
    {"date": "2025-04-15", "amount": 120.00, "description": "Freelance Payment", "category": "freelance"},
    {"date": "2025-03-10", "amount": 190.00, "description": "Old Salary Deposit", "category": "salary"}, # Older income

    # Mixed Category (hypothetical, if a category could have in/out)
    {"date": "2025-05-10", "amount": 50.00, "description": "Project A Bonus", "category": "projectA"},
    {"date": "2025-05-11", "amount": -10.00, "description": "Project A Software", "category": "projectA"},
]

class TestFinancialFunctions(unittest.TestCase):

    def setUp(self):
        # Make a deep copy of transactions for each test to avoid modification issues
        self.mock_transactions = [t.copy() for t in MOCK_TRANSACTIONS_BASE]
        # It's good practice to also patch main.account if functions directly use it.
        # For functions that accept transactions as an argument, this is less critical for those specific functions.
        self.patcher_account = patch('main.account', {'transactions': self.mock_transactions, 'balance': 1000.0})
        self.mocked_account = self.patcher_account.start()
        main.account['transactions'] = self.mock_transactions # Ensure it's updated for process_query

    def tearDown(self):
        self.patcher_account.stop()

    # --- Tests for get_spending_by_date_range ---
    def test_spending_range_includes_some(self):
        start_date = date(2025, 5, 1)
        end_date = date(2025, 5, 4)
        # Expected: -50 (Coffee) + -20 (Grocery) + -30 (Restaurant) = -100. Function returns positive sum.
        self.assertEqual(main.get_spending_by_date_range(self.mock_transactions, start_date, end_date), 100.00)

    def test_spending_range_includes_none(self):
        start_date = date(2025, 1, 1)
        end_date = date(2025, 1, 31)
        self.assertEqual(main.get_spending_by_date_range(self.mock_transactions, start_date, end_date), 0.00)

    def test_spending_range_empty_transactions(self):
        start_date = date(2025, 5, 1)
        end_date = date(2025, 5, 4)
        self.assertEqual(main.get_spending_by_date_range([], start_date, end_date), 0.00)

    def test_spending_range_all_transactions(self):
        start_date = date(2025, 1, 1)
        end_date = date(2025, 12, 31)
        # Expected: 50+20+30+15+25+10+10 = 160
        self.assertEqual(main.get_spending_by_date_range(self.mock_transactions, start_date, end_date), 160.00)

    # --- Tests for get_income_by_date_range ---
    def test_income_range_includes_some(self):
        start_date = date(2025, 4, 1)
        end_date = date(2025, 4, 30)
        # Expected: 120 (Freelance)
        self.assertEqual(main.get_income_by_date_range(self.mock_transactions, start_date, end_date), 120.00)

    def test_income_range_includes_none(self):
        start_date = date(2024, 1, 1)
        end_date = date(2024, 12, 31) # Range with no income transactions
        self.assertEqual(main.get_income_by_date_range(self.mock_transactions, start_date, end_date), 0.00)

    def test_income_range_empty_transactions(self):
        start_date = date(2025, 5, 1)
        end_date = date(2025, 5, 4)
        self.assertEqual(main.get_income_by_date_range([], start_date, end_date), 0.00)

    def test_income_range_all_transactions(self):
        start_date = date(2025, 1, 1)
        end_date = date(2025, 12, 31)
        # Expected: 200 (Salary) + 120 (Freelance) + 190 (Old Salary) + 50 (Project A Bonus) = 560
        self.assertEqual(main.get_income_by_date_range(self.mock_transactions, start_date, end_date), 560.00)


    # --- Tests for get_total_income ---
    def test_total_income_with_income(self):
        # Expected: 200 + 120 + 190 + 50 = 560
        self.assertEqual(main.get_total_income(self.mock_transactions), 560.00)

    def test_total_income_no_income(self):
        expenses_only = [t for t in self.mock_transactions if t['amount'] < 0]
        self.assertEqual(main.get_total_income(expenses_only), 0.00)

    def test_total_income_empty_transactions(self):
        self.assertEqual(main.get_total_income([]), 0.00)

    # --- Tests for get_income_by_category ---
    def test_income_category_exists(self):
        # Expected for "salary": 200 (Salary) + 190 (Old Salary) = 390
        self.assertEqual(main.get_income_by_category("salary"), 390.00)
        self.assertEqual(main.get_income_by_category("freelance"), 120.00)

    def test_income_category_case_insensitivity(self):
        self.assertEqual(main.get_income_by_category("SALary"), 390.00)
        self.assertEqual(main.get_income_by_category("FrEeLanCe"), 120.00)


    def test_income_category_not_exists(self):
        self.assertEqual(main.get_income_by_category("nonexistent"), 0.00)

    def test_income_category_mixed_types(self):
        # Category "projectA" has +50 and -10. Should only sum income.
        self.assertEqual(main.get_income_by_category("projectA"), 50.00)
        # Category "food" only has expenses.
        self.assertEqual(main.get_income_by_category("food"), 0.00)


    def test_income_category_empty_transactions(self):
        # Temporarily use empty list for this specific main.account.transactions
        original_transactions = main.account['transactions']
        main.account['transactions'] = []
        self.assertEqual(main.get_income_by_category("salary"), 0.00)
        main.account['transactions'] = original_transactions # Restore


class TestProcessQuery(unittest.TestCase):

    def setUp(self):
        self.mock_transactions = [t.copy() for t in MOCK_TRANSACTIONS_BASE]
        # Patch main.account for process_query tests
        self.patcher_account = patch('main.account', {'transactions': self.mock_transactions, 'balance': 1000.0})
        self.mocked_account = self.patcher_account.start()
        main.account['transactions'] = self.mock_transactions # Ensure it's updated

        # Patch date/datetime objects for date-sensitive queries
        self.patcher_date_today = patch('main.date')
        self.mock_date = self.patcher_date_today.start()
        self.mock_date.today.return_value = FIXED_TODAY

        self.patcher_datetime_now = patch('main.datetime')
        self.mock_datetime = self.patcher_datetime_now.start()
        self.mock_datetime.now.return_value = MagicMock(year=FIXED_TODAY.year, month=FIXED_TODAY.month, day=FIXED_TODAY.day)
        self.mock_datetime.strptime = datetime.strptime # Keep original strptime

    def tearDown(self):
        self.patcher_account.stop()
        self.patcher_date_today.stop()
        self.patcher_datetime_now.stop()

    def test_query_spending_last_week(self):
        # FIXED_TODAY is 2025-05-15 (Thursday)
        # Last week: Monday 2025-05-05 to Sunday 2025-05-11
        # Expenses: Bus Ticket (-15 on 05-05), Project A Software (-10 on 05-11) = 25
        expected_start = FIXED_TODAY - timedelta(days=FIXED_TODAY.weekday() + 7) # 2025-05-05
        expected_end = FIXED_TODAY - timedelta(days=FIXED_TODAY.weekday() + 1)   # 2025-05-11
        response = main.process_query("how much did I spend last week?")
        self.assertIn("You spent $25.00 last week", response)
        self.assertIn(f"(from {expected_start.strftime('%Y-%m-%d')} to {expected_end.strftime('%Y-%m-%d')})", response)

    def test_query_spending_in_month_april(self):
        # Expenses in April 2025: Books (-25 on 04-20), Snacks (-10 on 04-28) = 35
        # Year is FIXED_TODAY.year = 2025
        response = main.process_query("what were my expenses in April?")
        self.assertIn("You spent $35.00 in April 2025", response)
        self.assertIn("(from 2025-04-01 to 2025-04-30)", response)

    def test_query_spending_in_month_may(self):
        # Expenses in May 2025: Coffee (-50), Grocery (-20), Restaurant (-30), Bus (-15), Project A Software (-10) = 125
        response = main.process_query("what were my expenses in may?") # Test lowercase month
        self.assertIn("You spent $125.00 in May 2025", response)
        self.assertIn("(from 2025-05-01 to 2025-05-31)", response)


    def test_query_income_last_month(self):
        # FIXED_TODAY is 2025-05-15. Last month is April 2025.
        # Income in April 2025: Freelance Payment (120.00 on 04-15)
        response = main.process_query("what was my income last month?")
        self.assertIn("Your income last month (April 2025) was $120.00", response)
        self.assertIn("(from 2025-04-01 to 2025-04-30)", response)

    def test_query_total_income(self):
        # Total income: 200 + 120 + 190 + 50 = 560
        response = main.process_query("how much income did I receive in total?")
        self.assertEqual(response, "Your total income is $560.00.")
        response_variant = main.process_query("total income")
        self.assertEqual(response_variant, "Your total income is $560.00.")


    def test_query_show_income_transactions(self):
        response = main.process_query("show my income transactions")
        self.assertIn("Income transactions:", response)
        self.assertIn("2025-05-10: Project A Bonus ($+50.00, projectA)", response) # Most recent income in mock
        self.assertIn("2025-05-03: Salary Deposit ($+200.00, salary)", response)
        self.assertIn("2025-04-15: Freelance Payment ($+120.00, freelance)", response)
        self.assertIn("2025-03-10: Old Salary Deposit ($+190.00, salary)", response)
        self.assertNotIn("Coffee Shop", response) # Expense

    def test_query_income_from_category_salary(self):
        # Income from salary: 200 + 190 = 390
        response = main.process_query("how much income from salary?")
        self.assertEqual(response, "You received $390.00 as income from salary.")
        response_case = main.process_query("income from SALARY") # Test case insensitivity of query
        self.assertEqual(response_case, "You received $390.00 as income from SALARY.")


    def test_query_income_from_category_freelance(self):
        response = main.process_query("how much income from freelance?")
        self.assertEqual(response, "You received $120.00 as income from freelance.")

    def test_query_income_from_category_nonexistent(self):
        response = main.process_query("how much income from unicorn breeding?")
        self.assertEqual(response, "No income found from unicorn breeding or 'unicorn breeding' is not an income category.")

    def test_query_income_from_category_food(self): # food only has expenses
        response = main.process_query("how much income from food?")
        self.assertEqual(response, "No income found from food or 'food' is not an income category.")


if __name__ == '__main__':
    unittest.main()
