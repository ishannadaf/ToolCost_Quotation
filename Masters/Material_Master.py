from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from Database.connection import *

def Frm_material_master(master):
    
    def clear_data():
        TxtName.delete(0, END)
        TxtPrice.delete(0, END)
        TxtDensity.delete(0, END)
        
    def on_start():
        clear_data()
        TxtName.focus()
        sql1 = f"SELECT * FROM material_master"
        db_cursor.execute(sql1)
        data1 = db_cursor.fetchall()
        trv.delete(*trv.get_children())
        if db_cursor.rowcount != 0:
            cnt = 1
            for i in data1:
                trv.insert("", 'end', text=str(cnt), values=(str(cnt), str(i[1]), str(i[2]), str(i[3]), str(i[0])))
                cnt += 1
                
        LblMasterId['text'] = ''
        BtnSave['text'] = 'Save'
        
    def show_selected_record(event):
        for selection in trv.selection():
            item = trv.item(selection)
        
        i1 = item["values"]
        clear_data()
        TxtName.insert(0, i1[1])
        TxtDensity.insert(0, i1[2])
        TxtPrice.insert(0, i1[3])
        LblMasterId['text'] = i1[4]
        BtnSave['text'] = 'Update'

    def save_data():
        name = TxtName.get()
        density = TxtDensity.get()
        price = TxtPrice.get()
        
        if name != '' and price != '' and BtnSave['text'] == 'Save' and price != '':
            sql1 = f"INSERT INTO material_master (name, density, rate) VALUES ({DATABASE_SYN}, {DATABASE_SYN}, {DATABASE_SYN})"
            db_cursor.execute(sql1, (name, price))
            db_connection.commit()
            messagebox.showinfo("Success", "Data Saved Successfully", parent=material_master)
            on_start()
        elif name != '' and price != '' and BtnSave['text'] == 'Update' and price != '':
            sql1 = f"UPDATE material_master SET name = {DATABASE_SYN}, density = {DATABASE_SYN}, rate = {DATABASE_SYN} WHERE id = {DATABASE_SYN}"
            db_cursor.execute(sql1, (name, density, price, LblMasterId['text']))
            db_connection.commit()
            messagebox.showinfo("Success", "Data Updated Successfully", parent=material_master)
            on_start()
        else:
            messagebox.showerror("Error", "Please fill all data", parent=material_master)

    def delete_data():
        if LblMasterId['text'] != '':
            sql1 = f"DELETE FROM material_master WHERE id = {DATABASE_SYN}"
            db_cursor.execute(sql1, (LblMasterId['text'],))
            db_connection.commit()
            messagebox.showinfo("Success", "Data deleted successfully", parent=material_master)
            on_start()

    material_master = Toplevel(master)
    material_master.geometry("600x400+430+200")
    
    LblHead = Label(material_master, text='Material Master', font=('Times New Roman', 22))
    LblHead.place(x=200, y=10)
    
    Frm1 = LabelFrame(material_master, width=580, height=320)
    Frm1.place(x=10, y=60)
    
    LblName = Label(Frm1, text='Name', font=('Times New Roman', 14))
    LblName.place(x=70, y=10)
    TxtName = Entry(Frm1, font=('Times New Roman', 14), width=18)
    TxtName.place(x=20, y=40)
    
    LblDensity = Label(Frm1, text='Density', font=('Times New Roman', 14))
    LblDensity.place(x=240, y=10)
    TxtDensity = Entry(Frm1, font=('Times New Roman', 14), width=18)
    TxtDensity.place(x=200, y=40)
    
    LblPrice = Label(Frm1, text='Price', font=('Times New Roman', 14))
    LblPrice.place(x=430, y=10)
    TxtPrice = Entry(Frm1, font=('Times New Roman', 14), width=18)
    TxtPrice.place(x=380, y=40)
    
    BtnSave = Button(Frm1, text='Save', font=('Times New Roman', 12), width=12, bg='green', fg='white', command=save_data)
    BtnSave.place(x=110, y=80)
    BtnDelete = Button(Frm1, text='Delete', font=('Times New Roman', 12), width=12, bg='brown', fg='white', command=delete_data)
    BtnDelete.place(x=240, y=80)
    BtnExit = Button(Frm1, text='Exit', font=('Times New Roman', 12), width=12, bg='red', fg='white',command=material_master.destroy)
    BtnExit.place(x=370, y=80)
    
    LblMasterId = Label(material_master, text='')
    LblMasterId.place(x=1000, y=1000)
    
    scrolly=Scrollbar(Frm1 , orient=VERTICAL)
    scrolly.place(x=550, y=140, height=170)
    
    trv=ttk.Treeview(Frm1 , columns=("no" , "name", "density", "price") , yscrollcommand=scrolly.set )#, xscrollcommand=scrollx.set
    scrolly.config(command=trv.yview)

    trv.heading("no" , text="No.")
    trv.heading("name" , text="Name")
    trv.heading("density" , text="Density")
    trv.heading("price" , text="Price")
    
    trv["show"]="headings"

    trv.column("no" , width=70, anchor='center')
    trv.column("name" , width=200, anchor='center')
    trv.column("density" , width=80, anchor='center')
    trv.column("price" , width=80, anchor='center')
    
    trv.place(x=20, y=140, width=530, height=170)
    
    on_start()
    trv.bind("<Double-1>", show_selected_record)
    material_master.bind("<Escape>", lambda e: material_master.destroy())
    # material_master.mainloop()
    return material_master
# Frm_material_master(1)