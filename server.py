from fastapi import FastAPI, HTTPException, status, Query,Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, field_validator
from datetime import date as date_type
import uvicorn
import json


app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

class ExpenseInput(BaseModel):
    amount: float = Field(gt=0)
    category: str = Field(min_length=1)
    date: date_type
    description: str = ""

    @field_validator("category")
    @classmethod
    def validate_category(cls, value):
        value = value.strip()
        if not value:
            raise ValueError("Category cannot be empty")
        return value

def validate_month(month):
    if month is None:
        return month

    month_number = int(month.split("-")[1])

    if 1 <= month_number <= 12:
        return month

    raise HTTPException(
        status_code=400,
        detail="Month must be between 01 and 12"
    )

@app.get("/")
def home():
    return {"message": "Welcome to Spendwise Expense Tracker"}

@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(request:Request):
    return templates.TemplateResponse(request=request, name="index.html",context={"request":request})

@app.get("/about")
def about():
    return {
        "project": "SpendWise",
        "type": "Expense Tracker"
    }


@app.get("/expenses")
def get_expenses(category: str | None = None, date: date_type | None = None,month: str | None = Query(default=None,pattern=r"^\d{4}-\d{2}$")):
    expenses = load_expenses()
    if category:
        expenses = [
            expense
            for expense in expenses
            if expense["category"].lower() == category.lower()
        ]
    if date:
        expenses = [
            expense
            for expense in expenses
            if expense["date"] == date.isoformat()
        ]
    if month:
        month = validate_month(month)
        expenses = [
            expense
            for expense in expenses
            if expense["date"].startswith(month)
        ]

    return expenses


def load_expenses():
    try:
        with open("expenses.json","r") as file:
            return json.load(file)
    except FileNotFoundError:
        return []

def save_expenses(expenses):
    with open("expenses.json","w") as file:
        json.dump(expenses,file)

def add_missing_ids():
    expenses = load_expenses()
    for index, expense in enumerate(expenses, start=1):
        if "id" not in expense:
            expense["id"] = index
    save_expenses(expenses)

add_missing_ids()


@app.get("/expenses/summary")
def get_summary(month: str | None= Query(default=None, pattern=r"^\d{4}-\d{2}$")):
    expenses = load_expenses()
    if month:
        month = validate_month(month)
        expenses = [
            expense
            for expense in expenses
            if expense["date"].startswith(month)
        ]
    total_expenses = len(expenses)
    total_amount = sum(
        expense["amount"]
        for expense in expenses
    )
    category_totals = {}
    for expense in expenses:
        category = expense["category"]
        if category not in category_totals:
            category_totals[category] = 0
        category_totals[category] += expense["amount"]
    monthly_totals = {}
    for expense in expenses:
        expense_month = expense["date"][:7]
        if expense_month not in monthly_totals:
            monthly_totals[expense_month] = 0
        monthly_totals[expense_month] += expense["amount"]

    return {
        "total_expenses": total_expenses,
        "total_amount": total_amount,
        "by_category": category_totals,
        "by_month": monthly_totals
    }

@app.post("/expenses/add", status_code=status.HTTP_201_CREATED)
def add_expense(expense_data: ExpenseInput):

    expenses = load_expenses()
    new_id = max([expense["id"] for expense in expenses], default=0) + 1
    new_expense = {
        "id": new_id,
        "amount": expense_data.amount,
        "category": expense_data.category,
        "date": expense_data.date.isoformat(),
        "description": expense_data.description
    }
    expenses.append(new_expense)
    save_expenses(expenses)
    return {
        "message": "Expense added successfully",
        "data": new_expense
    }

@app.put("/expenses/update/{id}")
def update_expense(id: int, expense_data: ExpenseInput):
    expenses = load_expenses()
    expense = next((expense for expense in expenses if expense["id"] == id),None)
    if expense is None:
        raise HTTPException(status_code=404, detail="Expense ID not found")

    updated_expense = {
        "amount": expense_data.amount,
        "category": expense_data.category,
        "date": expense_data.date.isoformat(),
        "description": expense_data.description,
        "id": expense["id"]
    }
    expenses_index = expenses.index(expense)
    expenses[expenses_index] = updated_expense
    save_expenses(expenses)
    return {
        "message": "Expense updated successfully",
        "data": updated_expense
    }

@app.delete("/expenses/delete/{id}")
def delete_expense(id: int):
    expenses = load_expenses()
    expense = next((expense for expense in expenses if expense["id"] == id), None)
    if expense is None:
        raise HTTPException(status_code=404, detail="Expense ID not found")
    expenses.remove(expense)
    save_expenses(expenses)
    return {
        "message": "Expense deleted successfully",
        "data": expense
    }




if __name__ == "__main__":
    uvicorn.run("server:app", reload=True)