import datetime
from accounts_store import load_data, save_data, check_pin

LOCKOUT_THRESHOLD = 3  # wrong attempts before lock
LOCKOUT_MINUTES = 1  # lock duration in minutes


def is_locked(account: dict) -> bool:
    lu = account.get("locked_until")
    if not lu:
        return False
    try:
        locked_until = datetime.datetime.fromisoformat(lu)
    except Exception:
        return False
    return datetime.datetime.utcnow() < locked_until


def authenticate(card: str, pin: str, data: dict = None):
    """
    Returns (True, account_dict) on success, or (False, "message") on failure.
    """
    data = data or load_data()
    accounts = data.get("accounts", {})
    acc = accounts.get(card)
    if not acc:
        return False, "Card not found."

    if is_locked(acc):
        locked_until = datetime.datetime.fromisoformat(acc["locked_until"])
        remaining = locked_until - datetime.datetime.utcnow()
        secs = int(remaining.total_seconds())
        return False, f"Account locked. Try again in {secs} seconds."

    if check_pin(pin, acc["pin_hash"]):
        acc["wrong_attempts"] = 0
        acc["locked_until"] = None
        save_data(data)
        return True, acc

    # wrong PIN
    acc["wrong_attempts"] = acc.get("wrong_attempts", 0) + 1
    if acc["wrong_attempts"] >= LOCKOUT_THRESHOLD:
        locked_until = datetime.datetime.utcnow() + datetime.timedelta(minutes=LOCKOUT_MINUTES)
        acc["locked_until"] = locked_until.isoformat()
        acc["wrong_attempts"] = 0
        save_data(data)
        return False, f"Too many wrong attempts. Locked until {locked_until.isoformat()} UTC."
    save_data(data)
    remaining = LOCKOUT_THRESHOLD - acc["wrong_attempts"]
    return False, f"Incorrect PIN. {remaining} attempt(s) left."
