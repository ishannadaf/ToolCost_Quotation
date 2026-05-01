# Main.py
from datetime import datetime, timedelta, date
import hashlib
import uuid
import platform
import subprocess
from tkinter import *

from tkinter import messagebox
from Database.connection import *  # db_cursor, db_connection, DATABASE_SYN
from ToolCostLogin import Main_Function

SECRET = 93847561
SKY = "#00A3E0"
WHITE = "#FFFFFF"

# -------------------------------------------------------
# 1. Read Hard Disk Serial Number
# -------------------------------------------------------
def get_hdd_serial():
    try:
        output = subprocess.check_output(
            'wmic diskdrive get serialnumber',
            shell=True
        ).decode(errors="ignore").splitlines()

        serials = [line.strip() for line in output if line.strip() and "SerialNumber" not in line]
        return serials[0] if serials else "UNKNOWN"
    except Exception:
        return "UNKNOWN"

def get_old_hwid():
    parts = []
    try:
        parts.append(platform.node())
    except Exception:
        pass
    try:
        parts.append(hex(uuid.getnode()))
    except Exception:
        pass

    if not parts:
        parts.append("UNKNOWN")

    raw = "|".join(parts).encode()
    digest = hashlib.sha256(raw).hexdigest()
    num = int(digest, 16) % 10**6
    return f"{num:06d}"

def compute_hw_values():
    """
    Returns: (hdd_serial, old_hwid_6, final_hw_code_8)
    """
    hdd = get_hdd_serial()
    oldid = get_old_hwid()
    digest = hashlib.sha256((hdd + oldid).encode()).hexdigest()
    final_num = int(digest, 16) % 10**8
    final_code = f"{final_num:08d}"
    return hdd, oldid, final_code


def validate_license_in_db(var_hdd, var_sec, hwid_var):
    """
    Check if there is an active and valid license for this machine in secret_key table.

    Returns (True, msg) if OK, else (False, error_msg)
    """
    hdd, oldid, final_code = compute_hw_values()
    today = date.today()

    sql = (
        f"SELECT secret_key_hard, secret_key_1, secret_keycol, "
        f"valid_from, valid_till, active_ "
        f"FROM secret_key "
        #f"WHERE secret_key_1={DATABASE_SYN} "
        f"WHERE secret_keycol={DATABASE_SYN} "
        f"AND active_={DATABASE_SYN} "
        f"ORDER BY valid_till DESC"
    )

    db_cursor.execute(sql, (hdd, '1'))
    row = db_cursor.fetchone()

    if not row:
        return False, "No active license found for this machine."

    valid_from = row[3]
    valid_till = row[4]

    if not (valid_from <= today <= valid_till):
        sql1 = "UPDATE secret_key SET active_ = '0'"
        db_cursor.execute(sql1)
        db_connection.commit()
        return False, f"License expired. Valid till: {valid_till}"

    # If everything ok, also push to UI vars
    var_hdd.set(str(hdd))
    var_sec.set(str(oldid))
    hwid_var.set(final_code)

    return True, "License valid."


def refresh_code(hwid_var, var_hdd, var_sec):
    hdd, oldid, final_code = compute_hw_values()
    var_hdd.set(str(hdd))
    var_sec.set(str(oldid))
    hwid_var.set(final_code)


def validate_block(P):
    if len(P) > 4:
        return False
    return P.isdigit() or P == ""


def get_secret_key(key1_var, key2_var, key3_var, key4_var):
    return key1_var.get() + key2_var.get() + key3_var.get() + key4_var.get()


def save_data(root, hwid_var, var_hdd, key1_var, key2_var, key3_var, key4_var):
    secret_16 = get_secret_key(key1_var, key2_var, key3_var, key4_var)
    code = hwid_var.get()
    hdd_code = var_hdd.get()
    dt1 = date.today()

    if len(secret_16) != 16 or not secret_16.isdigit():
        messagebox.showerror("Error", "Secret key must be 16 digits (numbers only).")
        return

    if not code:
        messagebox.showerror("Error", "Generate hardware code first.")
        return

    base = secret_16[:14]
    checksum = secret_16[14:]

    hw_from_key = base[:8]
    exp_part = base[8:14]  # YYMMDD

    expected_val = (sum(ord(c) for c in base) + SECRET) % 100
    expected_checksum = f"{expected_val:02d}"

    if checksum != expected_checksum:
        messagebox.showerror("Error", "Invalid secret key (checksum failed).")
        return

    if hw_from_key != code:
        messagebox.showerror("Error", "This secret key does not match this machine.")
        return

    try:
        dt2 = datetime.strptime(exp_part, "%y%m%d").date()
    except ValueError:
        messagebox.showerror("Error", "Secret key has invalid expiry date inside.")
        return

    if dt1 > dt2:
        messagebox.showerror("Error", f"This license already expired on {dt2}.")
        return

    sql1 = (
        "INSERT INTO secret_key "
        "(secret_key_hard, secret_key_1, secret_keycol, valid_from, valid_till, active_) "
        f"VALUES ({DATABASE_SYN}, {DATABASE_SYN}, {DATABASE_SYN}, {DATABASE_SYN}, {DATABASE_SYN}, {DATABASE_SYN})"
    )

    db_cursor.execute(sql1, (secret_16, code, hdd_code, dt1, dt2, '1'))
    try:
        db_connection.commit()
    except Exception:
        pass

    messagebox.showinfo("Saved", f"Licence Key Activated from {dt1} to {dt2}")
    root.destroy()
    Main_Function()


def show_activation_screen(root, error_msg, var_hdd, var_sec, hwid_var,
                           key1_var, key2_var, key3_var, key4_var):

    for w in root.winfo_children():
        w.destroy()

    root.title("License Hardware Key")
    root.configure(bg=SKY)

    Label(root, text="Hardware License Key",
          font=("Times New Roman", 30, "bold"),
          bg=SKY, fg=WHITE).pack(pady=10)

    if error_msg:
        Label(root, text=error_msg,
              font=("Times New Roman", 14, "bold"),
              bg=SKY, fg="yellow").pack()

    Label(root, text="Send this code to the provider for activation",
          font=("Times New Roman", 20),
          bg=SKY, fg=WHITE).pack()

    code_frame = Frame(root, bg=SKY)
    code_frame.pack(pady=20)

    Label(code_frame, text="Code:",
          font=("Times New Roman", 20, "bold"),
          bg=SKY, fg=WHITE).grid(row=0, column=0, padx=10)

    Entry(code_frame, textvariable=hwid_var,
          font=("Consolas", 22, "bold"),
          width=18, justify="center",
          bg="#007BB8", fg="white",
          insertbackground="white").grid(row=0, column=1, padx=10)

    Button(code_frame, text="Generate",
           width=12, font=("Times New Roman", 14, "bold"),
           bg="#005F8A", fg="white",
           activebackground="#004C70",
           command=lambda: refresh_code(hwid_var, var_hdd, var_sec)).grid(row=0, column=2, padx=10)

    Label(root, text="Enter 16-digit Secret Key",
          font=("Times New Roman", 20, "bold"),
          bg=SKY, fg=WHITE).pack()

    secret_frame = Frame(root, bg=SKY)
    secret_frame.pack(pady=10)

    vcmd = root.register(validate_block)

    entry_style = {
        "font": ("Consolas", 20, "bold"),
        "width": 4,
        "justify": "center",
        "bg": "#007BB8",
        "fg": "white",
        "insertbackground": "white",
        "validate": "key",
        "validatecommand": (vcmd, "%P")
    }

    Entry(secret_frame, textvariable=key1_var, **entry_style).grid(row=0, column=0, padx=5)
    Label(secret_frame, text="-", font=("Times New Roman", 25, "bold"),
          bg=SKY, fg=WHITE).grid(row=0, column=1)
    Entry(secret_frame, textvariable=key2_var, **entry_style).grid(row=0, column=2, padx=5)
    Label(secret_frame, text="-", font=("Times New Roman", 25, "bold"),
          bg=SKY, fg=WHITE).grid(row=0, column=3)
    Entry(secret_frame, textvariable=key3_var, **entry_style).grid(row=0, column=4, padx=5)
    Label(secret_frame, text="-", font=("Times New Roman", 25, "bold"),
          bg=SKY, fg=WHITE).grid(row=0, column=5)
    Entry(secret_frame, textvariable=key4_var, **entry_style).grid(row=0, column=6, padx=5)

    Button(root, text="Save",
           width=15, font=("Times New Roman", 18, "bold"),
           bg="#004C70", fg="white",
           activebackground="#002F49",
           command=lambda: save_data(root, hwid_var, var_hdd,
                                     key1_var, key2_var, key3_var, key4_var)
           ).pack(pady=15)
    
def main():
    root = Tk()
    root.title("Checking License...")
    root.geometry("700x420+400+200")
    root.resizable(False, False)
    root.configure(bg=SKY)

    var_hdd = StringVar()
    var_sec = StringVar()
    hwid_var = StringVar()

    key1_var = StringVar()
    key2_var = StringVar()
    key3_var = StringVar()
    key4_var = StringVar()
    
    is_valid, msg = validate_license_in_db(var_hdd, var_sec, hwid_var)

    if is_valid:
        root.destroy()
        Main_Function()
    else:
        show_activation_screen(root, msg, var_hdd, var_sec,
                               hwid_var, key1_var, key2_var, key3_var, key4_var)

    root.mainloop()


main()
    # try:
    #     main()
    # except Exception:
    #     # helpful for EXE: show traceback instead of silent crash
    #     import traceback
    #     traceback.print_exc()
    #     input("\nError occurred. Press Enter to exit...")
