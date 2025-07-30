#!/usr/bin/python3

import gspread
from oauth2client.service_account import ServiceAccountCredentials
import csv
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
import requests

def add_expense():

    list_of_items = []

    record_expense = True

    print("Add your expenses or Type 'done' to finish: ")
    while record_expense:
        expense = input("Add item: ").lower()
        if expense == "done":
            record_expense = False
        else:
            amount = float(input("Add amount: "))
            date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            list_of_items.append({"expense":expense, "amount": amount, "date": date})

    with open("expenses.csv", "a", newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=["expense", "amount", "date"])

        #If file is empty
        if os.path.getsize("expenses.csv") == 0:
            writer.writeheader()
        writer.writerows(list_of_items)

    print("Saving data...")

    #Export to Google Sheets automatically after saving CSV
    result = export_to_google_sheets()
    print(result)

def view_report():
    #Check if file exists
    if not os.path.exists("expenses.csv"):
        return "No expenses recorded yet."

    #Check if file is empty
    if os.path.getsize("expenses.csv") == 0:
        return "Expense report is empty."

    filter_option = input("\nFilter by (daily/weekly/monthly/all): ").lower()
    convert_currency = input("Convert to another currency? (yes/no): ").lower()

    convert = False
    to_currency = "USD"
    rate = 1

    if convert_currency == "yes":
        to_currency = input("Enter target currency code (e.g., USD, EUR, KES): ").upper()
        rate = get_exchange_rate("RWF", to_currency)
        if rate:
            convert = True
        else:
            print("Using RWF only. Could not fetch exchange rate.")

    print("\nExpense Report:")
    total_rwf = 0
    total_converted = 0
    has_data = False
    now = datetime.now()

    with open("expenses.csv", "r", encoding='utf-8') as file:
        reader = csv.DictReader(file)

        for entry in reader:
            try:
                entry_date = datetime.strptime(entry["date"], "%Y-%m-%d %H:%M:%S")
            except ValueError:
                continue

            show_entry = False

            if filter_option == "daily" and entry_date.date() == now.date():
                show_entry = True
            elif filter_option == "weekly" and now - timedelta(days=7) <= entry_date <= now:
                show_entry = True
            elif filter_option == "monthly" and now.month == entry_date.month and now.year == entry_date.year:
                show_entry = True
            elif filter_option == "all":
                show_entry = True

            if show_entry:
                has_data = True
                amount_rwf = float(entry["amount"])
                amount_converted = amount_rwf * rate if convert else None
                total_rwf += amount_rwf
                total_converted += amount_converted if amount_converted else 0

                if convert:
                    print(f"{entry['date']} - {entry['expense']}: {amount_rwf} RWF ({amount_converted:.2f} {to_currency})")
                else:
                    print(f"{entry['date']} - {entry['expense']}: {amount_rwf} RWF")

    if not has_data:
        return f"No expenses found for {filter_option} filter."

    output = f"\nTotal: {total_rwf} RWF"
    if convert:
        output += f"({total_converted:.2f} {to_currency})"

    return output

def export_to_google_sheets():

    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("service_account.json", scope)
    client = gspread.authorize(creds)

    #Open Google Sheet by name
    sheet = client.open("expenses-tracker").sheet1
    sheet.clear()
    sheet.append_row(["Expense", "Amount", "Date"])

    if not os.path.exists("expenses.csv"):
        return "No expenses to export."

    with open("expenses.csv", "r", encoding='utf-8') as file:
        reader = csv.DictReader(file)
        rows = []
        for row in reader:
            rows.append([row["expense"], row["amount"], row["date"]])

        sheet.append_rows(rows)

        return "Expenses exported to Google Sheets successfully!"

load_dotenv()

API_KEY = os.getenv("EXCHANGE_API_KEY")

def get_exchange_rate(from_currency="RWF", to_currency="USD", fallback_rate=None):
    if not API_KEY:
        print("API key not found in environment variables.")
        return fallback_rate

    url = f"https://api.exchangerate.host/convert?from={from_currency}&to={to_currency}&amount=1&access_key={API_KEY}"

    try:
        response = requests.get(url, timeout=10)
        data = response.json()

        if response.status_code == 200 and data.get("success", False):
            rate = data["result"]
            print(f"1 {from_currency} = {rate} {to_currency}")
            return rate
        else:
            print("API error:", data)
            return fallback_rate

    except Exception as e:
        print(f"Exception fetching exchange rate: {e}")
        return fallback_rate
