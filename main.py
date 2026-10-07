import json
from datetime import datetime

try:
    with open("expenses.json","r") as file:
        expenses = json.load(file)
except FileNotFoundError:
    expenses = []

def show_menu():
    print("""
    ===== Expense Tracker ===== 
    1. Add Expense 
    2. View Expenses 
    3. View Summary 
    4. Delete Expense 
    5. Exit""")
    choices = input("Enter your choice: ")
    return choices

def add_expense():
    while True:
        try:
            amount = float(input("Enter the amount: "))
            break
        except ValueError:
            print("Invalid. Please enter number")

    category = input("Enter the category: ")
    while True:
        try:
            date = input("Enter the date: ")
            datetime.strptime(date, "%Y-%m-%d")
            break
        except ValueError:
            print("Enter date correctly.")
    description = input("Enter the description: ")

    expense = {
        "amount": amount,
        "category": category,
        "date": date,
        "description": description
    }
    return  expense

def category_total(expense):
    totals = {}
    for i in expense:
        category = i["category"]
        if category not in totals:
            totals[category] = 0
        totals[category] = totals[category] + i["amount"]
    return  totals

def monthly_total(expense):
    totals = {}
    for i in expense:
        data = i["date"]
        month = data[:7]
        if month not in totals:
            totals[month] = 0
        totals[month] = totals[month] + i["amount"]
    return  totals

def display_summary(category_totals,monthly_totals):
    print("\n===== Expense Summary =====")
    for category, amount in category_totals.items():
        print(f"{category}: ₹{amount:.2f}")
    print("\nMonthly Totals: ")
    for month, amount in monthly_totals.items():
        print(f"{month}: ₹{amount:.2f}")

def display_expenses(expense):
    print("===== All Expenses =====")
    if not expense:
        print("No expenses recorded yet.")
        return
    for i in expense:
        print(f"Amount: ₹{i['amount']:.2f}\n Category: {i['category']}\n Date: {i['date']}\n Description: {i['description']}\n ")

def delete_expense(expenses):
    if not expenses:
        print("No expenses recorded yet.")
        return
    for index, expense in enumerate(expenses, start=1):
        print(f"{index}. {expense['category']} - {expense['amount']:.2f} - {expense['date']} - {expense['description']}")
    try:
        choices = int(input("Enter expense number to delete: "))
        if 1 <= choices <= len(expenses):
            expenses.pop(choices - 1)
        else:
            print("Invalid number")
    except ValueError:
        print("Invalid number")

while True:
    choice = show_menu()
    if choice == "1":
        exp = add_expense()
        expenses.append(exp)
    elif choice == "2":
        display_expenses(expenses)
    elif choice == "3":
        category = category_total(expenses)
        monthly = monthly_total(expenses)
        display_summary(category,monthly)
    elif choice == "4":
        delete_expense(expenses)

    elif choice == "5":
        with open("expenses.json", "w") as file:
            json.dump(expenses, file)
        break
    else:
        print("Invalid choice. Please select 1-5.")



