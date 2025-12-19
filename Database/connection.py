
import sqlite3
import mysql.connector
from datetime import datetime
DATABASE_NAME = "MYSQL"
DATABASE_SYN = "%s"


db_connection = mysql.connector.connect(host="localhost", user="root", password="omicron", auth_plugin='mysql_native_password')  
db_cursor = db_connection.cursor(buffered=True)
db_cursor.execute("use tool_management")

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

def Quotation_Id_Funct(cid):
    today_str = datetime.now().strftime("%d%m%y")

    query = f"SELECT quotation_id FROM quotation_master WHERE login_id = {DATABASE_SYN} ORDER BY quotation_id DESC LIMIT 1"
    db_cursor.execute(query, (cid,))
    row = db_cursor.fetchone()

    if row is None:
        seq_no = 1
    else:
        last_id = row[0]            # e.g. "020225003"
        seq_no = int(last_id[-3:]) + 1

    new_quotation_id = f"{today_str}{seq_no:03d}"
    return new_quotation_id

def Invoice_Id_Funct(login_id):
    today_str = datetime.now().strftime("%d%m%y")

    query = """
        SELECT invoice_id
        FROM quotation_master
        WHERE login_id = %s
        ORDER BY invoice_id DESC
        LIMIT 1
    """
    db_cursor.execute(query, (login_id,))
    row = db_cursor.fetchone()

    if row is None or row[0] is None:
        # No previous non-NULL invoice_id
        seq_no = 1
    else:
        last_id = row[0]   # e.g. "020225003"
        seq_no = int(last_id[-3:]) + 1

    new_invoice_id = f"{today_str}{seq_no:03d}"
    return new_invoice_id