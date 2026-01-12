# main.py
from getpass import getpass
from accounts_store import load_data, save_data, create_account, account_exists
from auth import authenticate
from operations import deposit, withdraw, transfer, mini_statement, check_balance

def prompt_card():
    return input("Enter card number: ").strip()

def prompt_pin(hidden=True):
    if hidden:
        return getpass("Enter PIN: ").strip()
    return input("Enter PIN: ").strip()

def user_menu_loop(data, account):
    while True:
        print("\n--- ATM MENU ---")
        print("1) Check Balance")
        print("2) Deposit")
        print("3) Withdraw")
        print("4) Transfer")
        print("5) Mini Statement")
        print("6) Logout")
        choice = input("Choose option: ").strip()
        try:
            if choice == "1":
                print(f"Balance: ₹{check_balance(account):.2f}")
            elif choice == "2":
                amount = float(input("Amount to deposit: "))
                newbal = deposit(data, account, amount)
                print(f"Deposit successful. New balance: ₹{newbal:.2f}")
            elif choice == "3":
                amount = float(input("Amount to withdraw: "))
                newbal = withdraw(data, account, amount)
                print(f"Withdraw successful. New balance: ₹{newbal:.2f}")
            elif choice == "4":
                to_card = input("Recipient card number: ").strip()
                amount = float(input("Amount to transfer: "))
                newbal = transfer(data, account, to_card, amount)
                print(f"Transfer successful. New balance: ₹{newbal:.2f}")
            elif choice == "5":
                stm = mini_statement(account)
                if not stm:
                    print("No transactions yet.")
                else:
                    print(f"Last {len(stm)} transactions:")
                    for tx in stm:
                        ts = tx["timestamp"]
                        print(f" - {ts} | {tx['type']} | ₹{tx['amount']:.2f} | {tx['details']} | Balance: ₹{tx['balance_after']:.2f}")
            elif choice == "6":
                print("Logged out.")
                break
            else:
                print("Invalid option.")
        except ValueError as e:
            print("Error:", e)
        except Exception as e:
            print("Unexpected error:", e)

def admin_menu(data):
    while True:
        print("\n--- ADMIN MENU ---")
        print("1) Create account")
        print("2) List accounts")
        print("3) Back")
        choice = input("Choose option: ").strip()
        try:
            if choice == "1":
                card = input("New card number: ").strip()
                name = input("Account holder name: ").strip()
                pin = getpass("Set PIN (4-6 digits): ").strip()
                initial = float(input("Initial balance: ") or 0)
                create_account(data, card, pin, name, initial)
                save_data(data)
                print("Account created.")
            elif choice == "2":
                accounts = data.get("accounts", {})
                if not accounts:
                    print("No accounts.")
                else:
                    for c, a in accounts.items():
                        print(f"- {c} | {a['name']} | Balance: ₹{a['balance']:.2f}")
            elif choice == "3":
                break
            else:
                print("Invalid option.")
        except Exception as e:
            print("Error:", e)

def main_loop():
    data = load_data()
    # ensure sample admin password prompt omitted for now; we use CLI create-account
    while True:
        print("\n=== ATM Simulator ===")
        print("1) User Login")
        print("2) Admin Menu")
        print("3) Exit")
        choice = input("Choose option: ").strip()
        if choice == "1":
            data = load_data()  # reload for latest
            card = prompt_card()
            pin = prompt_pin()
            ok, resp = authenticate(card, pin, data)
            if ok:
                print(f"Welcome {resp['name']}!")
                user_menu_loop(data, resp)
            else:
                print("Auth failed:", resp)
        elif choice == "2":
            admin_menu(data)
            data = load_data()
        elif choice == "3":
            print("Bye.")
            break
        else:
            print("Invalid option.")

if __name__ == "__main__":
    main_loop()
