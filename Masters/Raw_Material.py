from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from Database.connection import *

def Frm_Raw_Master(master):

    def clear_data():
        TxtName.delete(0, END)
        TxtPrice.delete(0, END)

    def on_start():
        clear_data()
        TxtName.focus()
        sql1 = f"SELECT * FROM raw_cost"
        db_cursor.execute(sql1)
        data1 = db_cursor.fetchall()
        trv.delete(*trv.get_children())
        if db_cursor.rowcount != 0:
            cnt = 1
            for i in data1:
                trv.insert("", 'end', text=str(cnt), values=(str(cnt), str(i[1]), str(i[2]), str(i[0])))
                cnt += 1
                
        LblMasterId['text'] = ''
        BtnSave['text'] = 'Save'
        
        sql2 = "SELECT name from material_master"
        db_cursor.execute(sql2)
        data1 = db_cursor.fetchall()
        lst_name = [i[0] for i in data1]
        
        TxtName['values'] = lst_name
        TxtName.current(0)
        
    def show_selected_record(event):
        for selection in trv.selection():
            item = trv.item(selection)
        
        i1 = item["values"]
        clear_data()
        TxtName.insert(0, i1[1])
        TxtPrice.insert(0, i1[2])
        LblMasterId['text'] = i1[3]
        BtnSave['text'] = 'Update'

    def save_data():
        name = TxtName.get()
        price = TxtPrice.get().split(' ')[0]
        if name != '' and price != '' and BtnSave['text'] == 'Save':
            sql1 = f"INSERT INTO raw_cost (name, price) VALUES ({DATABASE_SYN}, {DATABASE_SYN})"
            db_cursor.execute(sql1, (name, price))
            db_connection.commit()
            messagebox.showinfo("Success", "Data Saved Successfully", parent=machining_master)
            on_start()
        elif name != '' and price != '' and BtnSave['text'] == 'Update':
            sql1 = f"UPDATE raw_cost SET name = {DATABASE_SYN}, price = {DATABASE_SYN} WHERE id = {DATABASE_SYN}"
            db_cursor.execute(sql1, (name, price, LblMasterId['text']))
            db_connection.commit()
            messagebox.showinfo("Success", "Data Updated Successfully", parent=machining_master)
            on_start()
        else:
            messagebox.showerror("Error", "Please fill all data", parent=machining_master)

    def delete_data():
        if LblMasterId['text'] != '':
            sql1 = f"DELETE FROM raw_cost WHERE id = {DATABASE_SYN}"
            db_cursor.execute(sql1, (LblMasterId['text'],))
            db_connection.commit()
            messagebox.showinfo("Success", "Data deleted successfully", parent=machining_master)
            on_start()
    
    def only_int(char):
        return char.isdigit()

    machining_master = Toplevel(master)
    machining_master.geometry("600x400+430+200")
    
    LblHead = Label(machining_master, text='Raw Material Cost', font=('Times New Roman', 22))
    LblHead.place(x=170, y=10)
    
    Frm1 = LabelFrame(machining_master, width=580, height=320)
    Frm1.place(x=10, y=60)
    
    LblName = Label(Frm1, text='Name', font=('Times New Roman', 14))
    LblName.place(x=100, y=10)
    TxtName = ttk.Combobox(Frm1, font=('Times New Roman', 14), width=20, justify='center')
    TxtName.place(x=50, y=40)
    vcmd = (machining_master.register(only_int), "%S")
    LblPrice = Label(Frm1, text='Rate', font=('Times New Roman', 14))
    LblPrice.place(x=400, y=10)
    TxtPrice = Entry(Frm1, font=('Times New Roman', 14), width=20,validate="key", validatecommand=vcmd, justify='center')
    TxtPrice.place(x=340, y=40)

    BtnSave = Button(Frm1, text='Save', font=('Times New Roman', 12), width=12, bg='green', fg='white', command=save_data)
    BtnSave.place(x=110, y=80)
    BtnDelete = Button(Frm1, text='Delete', font=('Times New Roman', 12), width=12, bg='brown', fg='white', command=delete_data)
    BtnDelete.place(x=240, y=80)
    BtnExit = Button(Frm1, text='Exit', font=('Times New Roman', 12), width=12, bg='red', fg='white',command=machining_master.destroy)
    BtnExit.place(x=370, y=80)
    
    LblMasterId = Label(machining_master, text='')
    LblMasterId.place(x=1000, y=1000)
    
    scrolly=Scrollbar(Frm1 , orient=VERTICAL)
    scrolly.place(x=550, y=140, height=170)
    
    trv=ttk.Treeview(Frm1 , columns=("no" , "name" , "percentage") , yscrollcommand=scrolly.set )#, xscrollcommand=scrollx.set
    scrolly.config(command=trv.yview)

    trv.heading("no" , text="No.")
    trv.heading("name" , text="Name")
    trv.heading("percentage" , text="percentage")
    
    trv["show"]="headings"

    trv.column("no" , width=70, anchor='center')
    trv.column("name" , width=250, anchor='center')
    trv.column("percentage" , width=100, anchor='center')
    
    trv.place(x=20, y=140, width=530, height=170)
    
    on_start()
    trv.bind("<Double-1>", show_selected_record)
    machining_master.bind("<Escape>", lambda e: machining_master.destroy())
    # machining_master.mainloop()
    return machining_master
#Frm_Machining_Master(1)