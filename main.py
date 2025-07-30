#!/usr/bin/env python3

from flask import Flask, render_template, request, redirect
import csv
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
import requests
import gspread
from oauth2client.service_account import ServiceAccountCredentials

app = Flask(__name__)

load_dotenv()
API_KEY = os.getenv("EXCHANGE_API_KEY")

CSV_FILE = "expenses.csv"


def get_exchange_rate(from_currency="RWF", to_currency="USD", fallback_rate=1):
    """Module for exchange rate"""
    if not API_KEY:
        return fallback_rate

    url = f"https://api.exchangerate.host/convert?from={from_currency}&to={to_currency}&amount=1&access_key={API_KEY}"
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        if response.status_code == 200 and data.get("success", False):
            return data["result"]
    except Exception:
        pass
    return fallback_rate


def export_to_google_sheets():
    """function to export data"""
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("service_account.json", scope)
    client = gspread.authorize(creds)

    sheet = client.open("expenses-tracker").sheet1
    sheet.clear()
    sheet.append_row(["Expense", "Amount", "Date"])

    if not os.path.exists(CSV_FILE):
        return

    with open(CSV_FILE, "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        rows = [[row["expense"], row["amount"], row["date"]] for row in reader]
        sheet.append_rows(rows)


@app.route("/", methods=["GET"])
def index():
    """main page"""
    return render_template("index.html")


@app.route("/add", methods=["POST"])
def add_expense():
    """add expenses"""
    expense = request.form["expense"]
    amount = request.form["amount"]
    date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open(CSV_FILE, "a", newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=["expense", "amount", "date"])
        if os.path.getsize(CSV_FILE) == 0:
            writer.writeheader()
        writer.writerow({"expense": expense, "amount": amount, "date": date})

    export_to_google_sheets()
    return redirect("/")


@app.route("/report", methods=["GET"])
def view_report():
    """View report function"""
    filter_option = request.args.get("filter", "all")
    to_currency = request.args.get("currency", "RWF")

    convert = to_currency != "RWF"
    rate = get_exchange_rate("RWF", to_currency) if convert else 1

    report = []
    total_rwf = 0
    total_converted = 0
    now = datetime.now()

    if not os.path.exists(CSV_FILE) or os.path.getsize(CSV_FILE) == 0:
        return render_template("index.html", report=[], currency=to_currency, total_rwf=0, total_converted=0)

    with open(CSV_FILE, "r", encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for entry in reader:
            try:
                entry_date = datetime.strptime(entry["date"], "%Y-%m-%d %H:%M:%S")
            except ValueError:
                continue

            show = (
                (filter_option == "daily" and entry_date.date() == now.date()) or
                (filter_option == "weekly" and now - timedelta(days=7) <= entry_date <= now) or
                (filter_option == "monthly" and entry_date.month == now.month and entry_date.year == now.year) or
                (filter_option == "all")
            )

            if show:
                amount_rwf = float(entry["amount"])
                converted = round(amount_rwf * rate, 2) if convert else None
                total_rwf += amount_rwf
                total_converted += converted if converted else 0
                report.append({
                    "date": entry["date"],
                    "expense": entry["expense"],
                    "amount_rwf": amount_rwf,
                    "converted": converted
                })

    return render_template("index.html", report=report, currency=to_currency,
                           total_rwf=total_rwf, total_converted=round(total_converted, 2))


if __name__ == '__main__':
    app.run(debug=True)
