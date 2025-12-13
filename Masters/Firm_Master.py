from tkinter import *
from tkinter import messagebox
from Database.connection import *

def Frm_Firm_Master(master, login_id, idn):
    def On_Start():
        sql1 = f"SELECT * FROM firm_master WHERE login_id = {DATABASE_SYN} and id = {DATABASE_SYN}"
        db_cursor.execute(sql1, (login_id, 1))
        data1 = db_cursor.fetchall()
        if data1 != []:
            TxtName.delete(0, END)
            TxtAddress.delete(0, END)
            TxtContact.delete(0, END)
            TxtName.insert(0, data1[0][1])
            TxtAddress.insert(0, data1[0][2])
            TxtContact.insert(0, data1[0][3])
    def Save_Data():
        n1 = TxtName.get()
        n2 = TxtAddress.get()
        n3 = TxtContact.get()
        if n1 != "" and n2 != "" and n3 != "":
            sql1 = f"SELECT * FROM firm_master"
            db_cursor.execute(sql1)
            data1 = db_cursor.fetchall()
            if data1 == []:
                sql2 = f"INSERT INTO firm_master (firm_name, firm_address, firm_contact, login_id) VALUES ({DATABASE_SYN}, {DATABASE_SYN}, {DATABASE_SYN}, {DATABASE_SYN})"
                db_cursor.execute(sql2, (n1, n2, n3, login_id))
            else:
                sql2 = f"UPDATE firm_master SET firm_name = {DATABASE_SYN}, firm_address = {DATABASE_SYN}, firm_contact = {DATABASE_SYN} WHERE login_id = {DATABASE_SYN} and id = {DATABASE_SYN}"
                db_cursor.execute(sql2, (n1, n2, n3, login_id, 1))
            db_connection.commit()
            messagebox.showinfo("Success", "Data Saved Successfully", parent=frm_firm_master)
    
    if idn == 1:
        frm_firm_master = Tk()
    else:
        frm_firm_master = Toplevel(master)
    frm_firm_master.geometry("600x350+450+200")
    frm_firm_master.title("Firm Details")
    
    LblHead = Label(frm_firm_master, text='Firm Master', font=('Times New Roman', 22))
    LblHead.place(x=250, y=10)
    
    Frm1 = LabelFrame(frm_firm_master, height=290, width=580)
    Frm1.place(x=10, y=50)
    
    LblName = Label(Frm1, text='Name', font=('Times New Roman', 18))
    LblName.place(x=35, y=30)
    TxtName = Entry(Frm1, font=('Times New Roman', 18), width=30, justify='center')
    TxtName.place(x=140, y=30)
    
    LblAddress = Label(Frm1, text='Address', font=('Times New Roman', 18))
    LblAddress.place(x=35, y=90)
    TxtAddress = Entry(Frm1, font=('Times New Roman', 18), width=30, justify='center')
    TxtAddress.place(x=140, y=90)
    
    LblContact = Label(Frm1, text='Contact', font=('Times New Roman', 18))
    LblContact.place(x=35, y=150)
    TxtContact = Entry(Frm1, font=('Times New Roman', 18), width=30, justify='center')
    TxtContact.place(x=140, y=150)
    
    BtnSave = Button(Frm1, text='Save', font=('Times New Roman', 14), width=14, fg='white', bg='green', command=Save_Data)
    BtnSave.place(x=140, y=210)
    BtnExit = Button(Frm1, text='Exit', font=('Times New Roman', 14), width=14, fg='white', bg='red',command=frm_firm_master.destroy)
    BtnExit.place(x=330, y=210)
    
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
            
    TxtName.bind("<Return>", f1)
    TxtAddress.bind("<Return>", f2)
    TxtContact.bind("<Return>", f3)
    frm_firm_master.mainloop()
