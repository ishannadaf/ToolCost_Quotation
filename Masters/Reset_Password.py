from tkinter import *
from tkinter import messagebox
from Database.connection import *



def Frm_Reset_Password(master, login_id):
    def On_Start():
        TxtCurr.delete(0, END)
        TxtNew.delete(0, END)
        TxtConfirm.delete(0, END)
        
    def Save_Record():
        n1 = TxtCurr.get()
        n2 = TxtNew.get()
        n3 = TxtConfirm.get()
        
        if n1 and n2 and n3:
            if n2 == n3:
                sql1 = f"UPDATE login_master SET user_pass = '{n3}' WHERE id = '1' and user_pass = '{n1}'"
                db_cursor.execute(sql1)
                if db_cursor.rowcount > 0:
                    db_connection.commit()
                    messagebox.showinfo("Success", "Password updated successfully", parent=frm_password)
                    On_Start()
                else:
                    messagebox.showerror("Error", "Old password not matched.", parent=frm_password)
            else:
                messagebox.showwarning("Warning", "New password and Confirmed password not matched.", parent=frm_password)

    frm_password = Tk()
    frm_password.geometry("500x350+500+250")

    LblHead = Label(frm_password, text='Reset Password', font=('Times New Roman', 26, 'bold'), fg='red')
    LblHead.place(x=130, y=10)

    LblCurr = Label(frm_password, text='Current', font=('Times New Roman', 20))
    LblCurr.place(x=50, y=80)
    TxtCurr = Entry(frm_password, width=15, font=('Times New Roman', 20))
    TxtCurr.place(x=160, y=80)

    LblNew = Label(frm_password, text='New', font=('Times New Roman', 20))
    LblNew.place(x=50, y=150)
    TxtNew = Entry(frm_password, width=15, font=('Times New Roman', 20),show="*")
    TxtNew.place(x=160, y=150)

    LblConfirm = Label(frm_password, text='New', font=('Times New Roman', 20))
    LblConfirm.place(x=50, y=220)
    TxtConfirm = Entry(frm_password, width=15, font=('Times New Roman', 20),show="*")
    TxtConfirm.place(x=160, y=220)

    BtnSave = Button(frm_password, text='Save', font=('Times New Roman', 14), width=18, bg='green', fg='white', command=Save_Record)
    BtnSave.place(x=160, y=280)

    def f1(event):
        TxtNew.focus()
        
    def f2(event):
        TxtConfirm.focus()
        
    TxtCurr.bind('<Return>', f1)
    TxtNew.bind('<Return>', f2)

    frm_password.mainloop()