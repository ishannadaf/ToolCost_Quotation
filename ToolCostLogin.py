from tkinter import *
from PIL import ImageTk, Image
from Dashboard_Master import Frm_Master_Dashboard
from Database.connection import *
from Dashboard import Dashboard
from tkinter import messagebox
import os
import sys

def Main_Function():
    def resource_path(relative_path):
        """Get absolute path to resource (for PyInstaller compatibility)."""
        try:
            base_path = sys._MEIPASS  # PyInstaller temp folder
        except Exception:
            base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path)

    icon_path = resource_path(r"D:\\ToolCosting\\Images\\logo.ico")

    def exit():
        root_login.destroy()

    def on_start():
        TxtId.delete(0, END)
        TxtPass.delete(0, END)
        TxtId.focus()

    def login():
        n1 = TxtId.get()
        n2 = TxtPass.get()
        #n3 = TxtYear.get()
        #n4 = lst.index(n3) + 1
        if n1 == 'master' and n2 == 'master':
            root_login.destroy()
            Frm_Master_Dashboard(1)

        elif n1 != "" and n2 != "":
            sql1 = f"SELECT id from login_master WHERE user_name = {DATABASE_SYN} and user_pass = {DATABASE_SYN}"
            db_cursor.execute(sql1, (n1, n2))
            data1 = db_cursor.fetchall()
            if db_cursor.rowcount != 0:
                root_login.destroy()
                Dashboard(data1[0][0])
            else:
                messagebox.showerror("Error", "Invalid username or password...", parent=root_login)

    root_login = Tk()
    root_login.geometry("600x400+400+200")
    root_login.iconbitmap(icon_path)
    screen_width = 600
    screen_height = 400
    lst = []
    image1 = Image.open("D:\ToolCosting\Images\login_background.png")
    resized_image= image1.resize((screen_width,screen_height), Image.LANCZOS)

    img = ImageTk.PhotoImage(resized_image)
    label = Label(root_login, image = img)
    label.pack()

    frm1 = LabelFrame(root_login, width=260, height=140)
    frm1.place(x=300, y=250)

    LblId = Label(frm1, text='Username', font=('Times New Roman', 15))
    LblId.place(x=10, y=20)
    TxtId = Entry(frm1, width=12, font=('Times New Roman', 15), justify='center')
    TxtId.place(x=110, y=20)

    LblPass = Label(frm1, text='Password', font=('Times New Roman', 15))
    LblPass.place(x=10, y=60)
    TxtPass = Entry(frm1, width=12, show="*", font=('Times New Roman', 15), justify='center')
    TxtPass.place(x=110, y=60)

    BtnLogin = Button(frm1, text='Login', bg='green', fg='white', font=('Times New Roman', 11), width=12, command=login)
    BtnLogin.place(x=20, y=100)
    BtnExit = Button(frm1, text='Exit', bg='red', fg='white', font=('Times New Roman', 11), width=12, command=exit)
    BtnExit.place(x=130, y=100)

    def f1(event):
        TxtPass.focus()

    def f2(event):
        login()

    TxtId.bind('<Return>', f1)
    TxtPass.bind('<Return>', f2)

    on_start()
    root_login.mainloop()

