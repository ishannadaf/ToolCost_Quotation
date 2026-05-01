from ast import Delete
from logging import root
from tkinter import *
from tkinter import messagebox
from Database.connection import *
from tkinter import simpledialog

def Frm_Firm_Master(master, login_id, idn):
    def On_Start():
        sql1 = f"SELECT * FROM firm_master WHERE login_id = {DATABASE_SYN} and id = {DATABASE_SYN}"
        db_cursor.execute(sql1, (login_id, 1))
        data1 = db_cursor.fetchall()
        if data1 != []:
            TxtName.delete(0, END)
            TxtAddress.delete(0, END)
            TxtContact.delete(0, END)
            TxtEmail.delete(0, END)
            TxtBankName.delete(0, END)
            TxtBankAcc.delete(0, END)
            TxtIFSC.delete(0, END)
            TxtGST.delete(0, END)
            TxtName.insert(0, data1[0][1])
            TxtAddress.insert(0, data1[0][2])
            TxtContact.insert(0, data1[0][3])
            if data1[0][4] is not None:
                TxtEmail.insert(0, str(data1[0][4]))
            TxtBankName.insert(0, str(data1[0][5]))
            TxtBankAcc.insert(0, str(data1[0][6]))
            TxtIFSC.insert(0, str(data1[0][7]))
            TxtGST.insert(0, str(data1[0][8]))

        TxtName.focus()
    def Save_Data():
        n1 = TxtName.get()
        n2 = TxtAddress.get()
        n3 = TxtContact.get()
        n4 = TxtEmail.get()
        n5 = TxtBankName.get()
        n6 = TxtBankAcc.get()
        n7 = TxtIFSC.get()
        n8 = TxtGST.get()
        if n1 != "" and n2 != "" and n3 != "" and n5 != "" and n6 != "" and n7 != "" and n8 != "":
            sql1 = f"SELECT * FROM firm_master"
            db_cursor.execute(sql1)
            data1 = db_cursor.fetchall()
            if data1 == []:
                sql2 = f"INSERT INTO firm_master (firm_name, firm_address, firm_contact, email_address, firm_bank_name, firm_bank_acc, firm_bank_ifsc, firm_gst, login_id) VALUES ({DATABASE_SYN}, {DATABASE_SYN}, {DATABASE_SYN}, {DATABASE_SYN}, {DATABASE_SYN}, {DATABASE_SYN}, {DATABASE_SYN}, {DATABASE_SYN}, {DATABASE_SYN})"
                db_cursor.execute(sql2, (n1, n2, n3, n4, n5, n6, n7, n8, login_id))
            else:
                # 🔐 Ask for password before update
                entered_password = simpledialog.askstring(
                    "Authentication Required",
                    "Enter password to update:",
                    show="*",
                    parent=frm_firm_master
                )

                # If user cancels
                if entered_password is None:
                    return

                # 👉 Set your actual password here
                CORRECT_PASSWORD = "vishal123"

                if entered_password != CORRECT_PASSWORD:
                    messagebox.showerror("Error", "Incorrect Password!", parent=frm_firm_master)
                    frm_firm_master.destroy()
                sql2 = f"UPDATE firm_master SET firm_name = {DATABASE_SYN}, firm_address = {DATABASE_SYN}, firm_contact = {DATABASE_SYN}, email_address = {DATABASE_SYN}, firm_bank_name = {DATABASE_SYN}, firm_bank_acc = {DATABASE_SYN}, firm_bank_ifsc = {DATABASE_SYN}, firm_gst = {DATABASE_SYN} WHERE login_id = {DATABASE_SYN} and id = {DATABASE_SYN}"
                db_cursor.execute(sql2, (n1, n2, n3, n4, n5, n6, n7, n8, login_id, 1))
            db_connection.commit()
            messagebox.showinfo("Success", "Data Saved Successfully", parent=frm_firm_master)
        else:
            messagebox.showerror("Error","Please fill all fields.", parent=frm_firm_master)
    
    if idn == 1:
        frm_firm_master = Tk()
    else:
        frm_firm_master = Toplevel(master)
    frm_firm_master.geometry("600x620+450+70")
    frm_firm_master.title("Firm Details")
    frm_firm_master.resizable(False, False)
    LblHead = Label(frm_firm_master, text='Firm Master', font=('Times New Roman', 22))
    LblHead.place(x=230, y=10)
    
    Frm1 = LabelFrame(frm_firm_master, height=560, width=580)
    Frm1.place(x=10, y=50)
    
    LblName = Label(Frm1, text='Name', font=('Times New Roman', 18))
    LblName.place(x=25, y=30)
    TxtName = Entry(Frm1, font=('Times New Roman', 18), width=31, justify='center')
    TxtName.place(x=155, y=30)
    
    LblAddress = Label(Frm1, text='Address', font=('Times New Roman', 18))
    LblAddress.place(x=25, y=90)
    TxtAddress = Entry(Frm1, font=('Times New Roman', 18), width=31, justify='center')
    TxtAddress.place(x=155, y=90)
    
    def only_int(new_value):
        return (new_value.isdigit() or new_value == "") and len(new_value) < 11
    
    vcmd = (frm_firm_master.register(only_int), "%P")
    LblContact = Label(Frm1, text='Contact', font=('Times New Roman', 18))
    LblContact.place(x=25, y=150)
    TxtContact = Entry(Frm1, font=('Times New Roman', 18),validate="key", validatecommand=vcmd, width=31, justify='center')
    TxtContact.place(x=155, y=150)
    
    LblEmail = Label(Frm1, text='Email', font=('Times New Roman', 18))
    LblEmail.place(x=25, y=210)
    TxtEmail = Entry(Frm1, font=('Times New Roman', 18), width=31, justify='center')
    TxtEmail.place(x=155, y=210)
    
    
    LblBankName = Label(Frm1, text='Bank Name', font=('Times New Roman', 18))
    LblBankName.place(x=25, y=270)
    TxtBankName = Entry(Frm1, font=('Times New Roman', 18), width=31, justify='center')
    TxtBankName.place(x=155, y=270)
    
    def only_int1(new_value):
        return (new_value.isdigit() or new_value == "") and len(new_value) < 20
    
    vcmd1 = (frm_firm_master.register(only_int1), "%P")
    
    LblBankAcc = Label(Frm1, text='Account No.', font=('Times New Roman', 18))
    LblBankAcc.place(x=25, y=330)
    TxtBankAcc = Entry(Frm1, font=('Times New Roman', 18), validatecommand=vcmd1, validate="key", width=31, justify='center')
    TxtBankAcc.place(x=155, y=330)
    
    
    LblIFSC = Label(Frm1, text='IFSC Code', font=('Times New Roman', 18))
    LblIFSC.place(x=25, y=390)
    TxtIFSC = Entry(Frm1, font=('Times New Roman', 18), width=31, justify='center')
    TxtIFSC.place(x=155, y=390)
    
    LblGST = Label(Frm1, text='GST No.', font=('Times New Roman', 18))
    LblGST.place(x=25, y=450)
    TxtGST = Entry(Frm1, font=('Times New Roman', 18), width=31, justify='center')
    TxtGST.place(x=155, y=450)
    
    BtnSave = Button(Frm1, text='Save', font=('Times New Roman', 14), width=14, fg='white', bg='green', command=Save_Data)
    BtnSave.place(x=140, y=500)
    BtnExit = Button(Frm1, text='Exit', font=('Times New Roman', 14), width=14, fg='white', bg='red',command=frm_firm_master.destroy)
    BtnExit.place(x=330, y=500)
    
    On_Start()
    
    def f1(event):
        if TxtName.get() != '':
            TxtAddress.focus()
            
    def f2(event):
        if TxtAddress.get() != '':
            TxtContact.focus()
    
    def f3(event):
        if TxtName.get() and TxtAddress.get() and TxtContact.get():
            Save_Data()
    
    def close_window(event=None):
        #print("Closing window...")
        frm_firm_master.destroy()
    TxtName.bind("<Return>", f1)
    TxtAddress.bind("<Return>", f2)
    TxtContact.bind("<Return>", f3)
    frm_firm_master.bind("<Escape>", lambda e: close_window())
    # frm_firm_master.mainloop()
    return frm_firm_master