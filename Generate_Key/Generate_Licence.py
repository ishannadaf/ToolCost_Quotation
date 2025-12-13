from tkinter import *
from tkinter import messagebox
from Database.connection import *
from Generate_Key.generate_key import Main_Function
from datetime import datetime
def Frm_Generate_Licence(master, login_id):
    def on_start():
        TxtCustName.delete(0, END)
        TxtCustContact.delete(0, END)
        TxtHardNo.delete(0, END)
        TxtActiveDays.delete(0, END)
        #LblKey['text'] = 'License key : 0000-0000-0000-0000'
        TxtCustName.focus()
        
    def generate_key():
        cust_name = TxtCustName.get()
        cust_contact = TxtCustContact.get()
        hard_no = TxtHardNo.get()
        active_days = TxtActiveDays.get()
        
        if cust_name and cust_contact and hard_no and active_days:
            msg = messagebox.askokcancel("Warning", "You can't edit once key is generated. Continue?")
            if msg:
                key, valid_from, valid_till = Main_Function(hard_no, active_days)
                if key:
                    sql1 = f"INSERT INTO master_table (customer_name, customer_contact, date_of_activation, client_hard_key, client_secret_key, valid_till, active) VALUES ({DATABASE_SYN}, {DATABASE_SYN}, {DATABASE_SYN}, {DATABASE_SYN}, {DATABASE_SYN}, {DATABASE_SYN}, {DATABASE_SYN})"
                    db_cursor.execute(sql1, (cust_name, cust_contact, datetime.today().date(), hard_no, key, valid_till, '1'))
                    db_connection.commit()
                    messagebox.showinfo("Success", "Licence key generate Successfully", parent=frm_license)
                    LblKey['text'] = f"License key : {key[0:4]}-{key[4:8]}-{key[8:12]}-{key[12:]}"
                    on_start()

    def only_int(new_value):
        return (new_value.isdigit() or new_value == "") and len(new_value) < 4
    
    def only_int_contact(new_value):
        return (new_value.isdigit() or new_value == "") and len(new_value) < 11
    
    def only_int_hard(new_value):
        return (new_value.isdigit() or new_value == "") and len(new_value) < 9
    
    frm_license = Toplevel(master)
    frm_license.title("Generate License")
    frm_license.geometry("600x470+450+200")
    
    vcmd = (frm_license.register(only_int), "%P")
    vcmdc = (frm_license.register(only_int_contact), "%P")
    vcmdH = (frm_license.register(only_int_hard), "%P")
    
    LblHead = Label(frm_license, text='Generate License', font=('Times New Roman', 24, 'bold'), fg='purple')
    LblHead.place(x=190, y=10)
    
    Frm1 = LabelFrame(frm_license, width=540, height=130, text='Customer Details')
    Frm1.place(x=30, y=70)
    
    Frm2 = LabelFrame(frm_license, width=540, height=80, text='Hardware Details')
    Frm2.place(x=30, y=220)
    
    LblCustName = Label(Frm1, text='Customer Name', font=('Times New Roman', 16))
    LblCustName.place(x=15, y=10)
    TxtCustName = Entry(Frm1, width=30, font=('Times New Roman', 16), justify='center')
    TxtCustName.place(x=180, y=10)
    
    LblCustContact = Label(Frm1, text='Customer Contact', font=('Times New Roman', 16))
    LblCustContact.place(x=15, y=60)
    TxtCustContact = Entry(Frm1, width=12, validate="key", validatecommand=vcmdc, font=('Times New Roman', 16), justify='center')
    TxtCustContact.place(x=180, y=60)
    
    LblHardNo = Label(Frm2, text='Hard. No.', font=('Times New Roman', 16))
    LblHardNo.place(x=15, y=10)
    TxtHardNo = Entry(Frm2, width=12, validate="key", validatecommand=vcmdH, font=('Times New Roman', 16), justify='center')
    TxtHardNo.place(x=120, y=10)
    
    LblActivDays = Label(Frm2, text='Active. Days', font=('Times New Roman', 16))
    LblActivDays.place(x=280, y=10)
    TxtActiveDays = Entry(Frm2, width=10, validate="key", validatecommand=vcmd, font=('Times New Roman', 16), justify='center')
    TxtActiveDays.place(x=400, y=10)
    
    BtnGenerate = Button(frm_license, text='Generate', font=('Times New Roman', 16), width=20, bg='green', fg='white', command=generate_key)
    BtnGenerate.place(x=180, y=315)
    
    LblKey = Label(frm_license, text='License key : 0000-0000-0000-0000', font=('Times New Roman', 18, 'bold'), fg='red')
    LblKey.place(x=130, y=390)
    on_start()
    
    def f1(event):
        TxtCustContact.focus()
    def f2(event):
        TxtHardNo.focus()
    def f3(event):
        TxtActiveDays.focus()
    
    TxtCustName.bind('<Return>', f1)
    TxtCustContact.bind('<Return>', f2)
    TxtHardNo.bind('<Return>', f3)
    
    frm_license.mainloop()

# Frm_Generate_Licence(1, 1)