import os
import json
import bcrypt
#import datetime
from typing import Dict, Any, Optional

DATA_FILE = "accounts.json"


def default_data() -> Dict[str, Any]:
    return {
        "accounts": {},
        "admin": {"password_hash": None}
    }


def load_data(path: str = DATA_FILE) -> Dict[str, Any]:
    if not os.path.exists(path):
        return default_data()
    with open(path, "r") as f:
        return json.load(f)


def save_data(data: Dict[str, Any], path: str = DATA_FILE) -> None:
    # simple save; later we can make atomic writes (tmp+rename)
    with open(path, "w") as f:
        json.dump(data, f, indent=2, default=str)


# -----------------------------
# PIN hashing helpers
# -----------------------------
def hash_pin(pin: str) -> str:
    return bcrypt.hashpw(pin.encode(), bcrypt.gensalt()).decode()


def check_pin(pin: str, pin_hash: str) -> bool:
    try:
        return bcrypt.checkpw(pin.encode(), pin_hash.encode())
    except Exception:
        return False


# -----------------------------
# Account helpers
# -----------------------------
def account_exists(data: Dict[str, Any], card: str) -> bool:
    return card in data.get("accounts", {})


def create_account(data: Dict[str, Any],
                   card: str,
                   pin: str,
                   name: str,
                   initial_balance: float = 0.0) -> Dict[str, Any]:
    accounts = data.setdefault("accounts", {})
    if card in accounts:
        raise ValueError("Card already exists.")
    account = {
        "name": name,
        "card": card,
        "pin_hash": hash_pin(pin),
        "balance": float(initial_balance),
        "transactions": [],
        "wrong_attempts": 0,
        "locked_until": None
    }
    accounts[card] = account
    return account


def get_account(data: Dict[str, Any], card: str) -> Optional[Dict[str, Any]]:
    return data.get("accounts", {}).get(card)


# Create a couple of sample accounts if run directly
if __name__ == "__main__":
    data = load_data()
    if not account_exists(data, "1111222233334444"):
        create_account(data, "1111222233334444", "1234", "Anu", 5000.0)
    if not account_exists(data, "9999888877776666"):
        create_account(data, "9999888877776666", "4321", "Ravi", 2500.0)
    save_data(data)
    print("Sample accounts created (if not already present).")
