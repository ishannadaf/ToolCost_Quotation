from tkinter import *
from tkinter import messagebox
from Database.connection import *


def Frm_Gst_Percentage(master):

    gst_details = Toplevel(master)

    gst_details.geometry("400x250+550+250")
    gst_details.title("GST Details")

    def On_start():
        gst_entry.delete(0, END)
        sql1 = "SELECT gst_per FROM gst_percentage_table WHERE id = 1"
        db_cursor.execute(sql1)
        result = db_cursor.fetchone()
        if result:
            gst_entry.insert(0, str(result[0]))
        gst_entry.focus()

    def save_gst_details():
        gst_number = gst_entry.get()
        if gst_number:
            sql1 = "UPDATE gst_percentage_table SET gst_percentage=%s WHERE id = 1"
            db_cursor.execute(sql1, (gst_number,))
            db_connection.commit()
            messagebox.showinfo("Success", "GST details saved successfully.", master=gst_details)

    def only_int(new_value):
        if new_value == "":
            return True
        try:
            float(new_value)
            return True
        except ValueError:
            return False

    gst_label = Label(gst_details, text="GST Percentage", font=("Arial", 20))
    gst_label.place(x=100, y=30)
    gst_number_label = Label(gst_details, text="GST (%):", font=('Times New Roman', 16))
    gst_number_label.place(x=80, y=100)
    vcmd = (gst_details.register(only_int), "%P")
    gst_entry = Entry(gst_details, font=('Times New Roman', 16), width=8,validate="key", validatecommand=vcmd, justify='center')
    gst_entry.place(x=180, y=100)

    BtnSave = Button(gst_details, text="Save", font=('Times New Roman', 12), fg='white', bg='green', width=12, command=save_gst_details)
    BtnSave.place(x=150, y=150)
    
    On_start()
    gst_details.bind("<Escape>", lambda e: gst_details.destroy())
    # gst_details.mainloop()
    return gst_details