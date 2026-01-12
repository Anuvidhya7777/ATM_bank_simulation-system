# operations.py
import uuid
import datetime
from accounts_store import save_data

def add_transaction(account: dict, t_type: str, amount: float, details: str = ""):
    tx = {
        "id": str(uuid.uuid4()),
        "type": t_type,
        "amount": float(amount),
        "balance_after": account["balance"],
        "details": details,
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z"
    }
    account.setdefault("transactions", []).append(tx)

def check_balance(account: dict) -> float:
    return account["balance"]

def deposit(data: dict, account: dict, amount: float) -> float:
    if amount <= 0:
        raise ValueError("Deposit amount must be positive.")
    account["balance"] += amount
    add_transaction(account, "DEPOSIT", amount, "Self deposit")
    save_data(data)
    return account["balance"]

def withdraw(data: dict, account: dict, amount: float) -> float:
    if amount <= 0:
        raise ValueError("Withdraw amount must be positive.")
    if amount > account["balance"]:
        raise ValueError("Insufficient funds.")
    account["balance"] -= amount
    add_transaction(account, "WITHDRAW", amount, "Cash withdrawal")
    save_data(data)
    return account["balance"]

def transfer(data: dict, from_acc: dict, to_card: str, amount: float) -> float:
    if amount <= 0:
        raise ValueError("Transfer amount must be positive.")
    accounts = data.get("accounts", {})
    to_acc = accounts.get(to_card)
    if not to_acc:
        raise ValueError("Recipient card not found.")
    if amount > from_acc["balance"]:
        raise ValueError("Insufficient funds.")
    from_acc["balance"] -= amount
    to_acc["balance"] += amount
    add_transaction(from_acc, "TRANSFER_OUT", amount, f"To {to_card}")
    add_transaction(to_acc, "TRANSFER_IN", amount, f"From {from_acc['card']}")
    save_data(data)
    return from_acc["balance"]

def mini_statement(account: dict, n: int = 10):
    return list(reversed(account.get("transactions", [])))[0:n]
