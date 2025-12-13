# generate_secret_key.py
from datetime import datetime, timedelta

# Keep this value PRIVATE and same as in Main.py (if you later add checksum validation there)
SECRET = 93847561


def generate_license_key(hwcode: str, from_date: datetime | None = None, days_valid: int = 365):
    """
    hwcode    : 8-digit hardware code from client's Main.py
    from_date: start date of license; if None, uses today
    days_valid: for how many days license is valid (default 365)

    Returns: (secret_key_16, valid_from_date, valid_till_date)
    """
    hwcode = hwcode.strip()

    if len(hwcode) != 8 or not hwcode.isdigit():
        raise ValueError("Hardware Code must be exactly 8 digits.")

    if from_date is None:
        from_date = datetime.today()

    valid_from = from_date.date()
    valid_till = (from_date + timedelta(days=days_valid)).date()

    # expiry encoded as YYMMDD (6 digits)
    exp_part = valid_till.strftime("%y%m%d")   # e.g. 260310

    # Base = 8-digit HW + 6-digit expiry = 14 digits
    base = hwcode + exp_part

    # 2-digit checksum based on SECRET (optional, but good)
    checksum_val = (sum(ord(c) for c in base) + SECRET) % 100
    checksum = f"{checksum_val:02d}"           # always 2 digits

    # Final 16-digit secret key
    secret_key = base + checksum

    return secret_key, valid_from, valid_till


def Main_Function(hwcode, days_str):
    print("=== License Key Generator ===")
    if days_str == "":
        days = 365
    else:
        try:
            days = int(days_str)
        except ValueError:
            # print("Invalid days. Using 365.")
            days = 365

    try:
        key, valid_from, valid_till = generate_license_key(hwcode, days_valid=days)
        return key, valid_from, valid_till
    except ValueError as e:
        print("Error:", e)
        return

#     print("\nHardware Code :", hwcode)
#     print("Valid From    :", valid_from)
#     print("Valid Till    :", valid_till)
#     print("16-digit Key  :", key)

#     print("\nSend this 16-digit key to your client.")
#     print("When client enters it, Main.py will read the expiry date from the key automatically.")


# if __name__ == "__main__":
#     Main_Function(23247204, 365)
