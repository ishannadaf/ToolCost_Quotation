
import sqlite3
import mysql.connector
from datetime import datetime
DATABASE_NAME = "MYSQL"
DATABASE_SYN = "%s"


db_connection = mysql.connector.connect(host="localhost", user="root", password="omicron", auth_plugin='caching_sha2_password')  
db_cursor = db_connection.cursor(buffered=True)
db_cursor.execute("use tool_management")

def Get_Firm_Details(login_id):
        sql1 = f"SELECT firm_name, firm_contact, firm_address, email_address FROM firm_master where login_id = {DATABASE_SYN}"
        db_cursor.execute(sql1, (login_id,))
        data1 = db_cursor.fetchall()
        return data1[0][0], data1[0][1], data1[0][2], data1[0][3]

def Max_No(tb_name, col_name, cid):
    id_no = 0
    query = f"SELECT {col_name} FROM {tb_name} where login_id = {cid}"
    db_cursor.execute(query)
    db_cursor.rowcount
    if db_cursor.rowcount == 0:
        id_no = 1
    else:
        rows = db_cursor.fetchall()
        for row in rows:  
            id_no = row[0]
            id_no = id_no + 1
    return id_no

def Customer_Details(cust_name, login_id):
    sql1 = f"SELECT party_name, contact, address, id FROM account_master WHERE party_name = {DATABASE_SYN} and login_id = {DATABASE_SYN}"
    db_cursor.execute(sql1, (cust_name, login_id))
    data1 = db_cursor.fetchall()
    return data1[0][0], data1[0][1], data1[0][2], data1[0][3]

from datetime import datetime

def Quotation_Id_Funct(cid):
    # ✅ Get firm name
    firm_name, _, _, _ = Get_Firm_Details(cid)

    # ✅ First 2 characters of firm name
    firm_prefix = firm_name.strip().upper()[:2]

    today_str = datetime.now().strftime("%d%m%y")

    # ✅ New format: AB-Q-280226-
    prefix = f"{firm_prefix}-Q-{today_str}-"
    like_pattern = f"{prefix}%"

    query = """
        SELECT quotation_id
        FROM quotation_master
        WHERE login_id = %s
          AND quotation_id LIKE %s
        ORDER BY quotation_id DESC
        LIMIT 1
    """
    db_cursor.execute(query, (cid, like_pattern))
    row = db_cursor.fetchone()

    if row is None:
        seq_no = 1
    else:
        last_id = row[0]          # e.g. "AB-Q-280226-004"
        last_seq = int(last_id.split("-")[-1])
        seq_no = last_seq + 1

    new_quotation_id = f"{prefix}{seq_no:03d}"
    return new_quotation_id

from datetime import datetime

def Invoice_Id_Funct(login_id):
    # ✅ Get firm name
    firm_name, _, _, _ = Get_Firm_Details(login_id)

    # ✅ First 2 characters of firm name
    firm_prefix = firm_name.strip().upper()[:2]

    today_str = datetime.now().strftime("%d%m%y")

    # ✅ New format: AB-I-280226-
    prefix = f"{firm_prefix}-I-{today_str}-"
    like_pattern = f"{prefix}%"

    query = """
        SELECT invoice_id
        FROM quotation_master
        WHERE login_id = %s
          AND invoice_id LIKE %s
        ORDER BY invoice_id DESC
        LIMIT 1
    """

    db_cursor.execute(query, (login_id, like_pattern))
    row = db_cursor.fetchone()

    if row is None:
        seq_no = 1
    else:
        last_id = row[0]           # e.g. "AB-I-280226-004"
        last_seq = int(last_id.split("-")[-1])
        seq_no = last_seq + 1

    new_invoice_id = f"{prefix}{seq_no:03d}"
    return new_invoice_id


def Generate_Next_Challan(quotation_id):
    sql = "SELECT MAX(CAST(chalan_id AS UNSIGNED)) FROM delivery_manage_master where quot_no = %s"
    db_cursor.execute(sql, (quotation_id,))
    result = db_cursor.fetchone()

    if result[0] is None:
        next_no = 1
    else:
        next_no = int(result[0]) + 1

    return str(next_no).zfill(4)

def get_terms_conditions(quotation_id):
    sql = "SELECT terms_conditions FROM quotation_master WHERE quotation_id = %s"
    db_cursor.execute(sql, (quotation_id,))
    result = db_cursor.fetchone()
    if result and result[0]:
        return result[0].split("\n")
    return []