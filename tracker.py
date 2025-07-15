#!/usr/bin/python3
import json

def add_expense():

    list_of_items = []

    record_expense = True

    print("Add your expenses or Type 'done' to finish: ")
    while record_expense:
        expense = input("Add expense: ")
        if expense == "done":
            record_expense = False
        else:
            amount = float(input("Add amount: "))
            list_of_items.append({"expense":expense, "amount": amount})

    with open("expenses.json", "w", encoding='utf-8') as f:
            json.dump(list_of_items, f, indent=4)
            print("Saving data...")

def view_report():
    with open("expenses.json", "r", encoding='utf-8') as f:
         list_of_items = json.load(f)

    print("\nExpense Report:")
    total = 0
    for entry in list_of_items:
        print(f"{entry['expense']}: {entry['amount']} RWF")
        total += entry["amount"]
    return f"\nTotal: {total} RWF"
