#!/usr/bin/python3
import tracker

while True:
    print("My Expense Tracker")
    print("-------------------------------------------")

    print("1. Record Expense")
    print("2. View Report")
    print("3. Exit Application")

    user_choice = int(input("Select your choice: "))

    if user_choice == 1:
        print(tracker.add_expense())
    elif user_choice == 2:
        print(tracker.view_report())
    elif user_choice == 3:
        print("Exiting application...")
        break
