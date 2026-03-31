from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from Database.connection import *
from tkinter import filedialog
import tkinter

class AutocompleteCombobox(ttk.Combobox):

    def set_completion_list(self, completion_list):
            """Use our completion list as our drop down selection menu, arrows move through menu."""
            self._completion_list = sorted(completion_list, key=str.lower) # Work with a sorted list
            self._hits = []
            self._hit_index = 0
            self.position = 0
            self.bind('<KeyRelease>', self.handle_keyrelease)
            self['values'] = self._completion_list  # Setup our popup menu

    def autocomplete(self, delta=0):
            """autocomplete the Combobox, delta may be 0/1/-1 to cycle through possible hits"""
            if delta: # need to delete selection otherwise we would fix the current position
                    self.delete(self.position, tkinter.END)
            else: # set position to end so selection starts where textentry ended
                    self.position = len(self.get())
            # collect hits
            _hits = []
            for element in self._completion_list:
                    if element.lower().startswith(self.get().lower()): # Match case insensitively
                            _hits.append(element)
            # if we have a new hit list, keep this in mind
            if _hits != self._hits:
                    self._hit_index = 0
                    self._hits=_hits
            # only allow cycling if we are in a known hit list
            if _hits == self._hits and self._hits:
                    self._hit_index = (self._hit_index + delta) % len(self._hits)
            # now finally perform the auto completion
            if self._hits:
                    self.delete(0,tkinter.END)
                    self.insert(0,self._hits[self._hit_index])
                    self.select_range(self.position,tkinter.END)

    def handle_keyrelease(self, event):
            """event handler for the keyrelease event on this widget"""
            if event.keysym == "BackSpace":
                    self.delete(self.index(tkinter.INSERT), tkinter.END)
                    self.position = self.index(tkinter.END)
            if event.keysym == "Left":
                    if self.position < self.index(tkinter.END): # delete the selection
                            self.delete(self.position, tkinter.END)
                    else:
                            self.position = self.position-1 # delete one character
                            self.delete(self.position, tkinter.END)
            if event.keysym == "Right":
                    self.position = self.index(tkinter.END) # go to end (no selection)
            if len(event.keysym) == 1:
                    self.autocomplete()

def Frm_Account_Master(master, login_id):
    def clear_data():
        TxtAcc.delete(0, END)
        TxtProv.delete(0, END)
        TxtContact.delete(0, END)
        TxtAdd.delete("1.0", END)
        LblPdfPath['text'] = ''
        TxtMasterId['text'] = ''
        
    def on_start():
        clear_data()
        trv.delete(*trv.get_children())
        sql1 = f"SELECT * FROM account_master where login_id = {DATABASE_SYN}"
        db_cursor.execute(sql1, (login_id,))
        data1 = db_cursor.fetchall()
        cnt = 1
        acc_lst = []
        for i in data1:
            trv.insert("", 'end', text=i[0], values=(str(cnt), str(i[1]), i[3], str(i[4]), i[0], i[2], i[5]))
            cnt += 1
            acc_lst.append(i[1])
        BtnSave['text'] = 'Save'
        TxtAcc.set_completion_list(acc_lst)
        TxtAcc.focus()

    def Delete_Data():
        master_id = TxtMasterId['text']
        if master_id != '':
            sql1 = f"DELETE FROM account_master WHERE id = {DATABASE_SYN}"
            db_cursor.execute(sql1, (master_id,))
            db_connection.commit()
            messagebox.showinfo("Success", "Account deleted successfully.", parent = acc_master)
            on_start()
            
    def value_exists_in_column(tree, column_index, value_to_find):
        for row_id in tree.get_children():
            row_values = tree.item(row_id, "values")
            if str(row_values[column_index]).lower() == str(value_to_find).lower():
                return False
        return True

    def Save_Data():
        name = TxtAcc.get()
        providers = TxtProv.get()
        contact = TxtContact.get()
        addr = TxtAdd.get("1.0", END)
        pdf_path = LblPdfPath1['text']
        master_id = TxtMasterId['text']
        
        if len(addr) > 70:
            messagebox.showerror("Error", "Address should be less characters.", parent = acc_master)
            return
        
        if value_exists_in_column(trv, 1, name) and name != '' and contact != '' and providers != '' and BtnSave['text'] == 'Save':
            sql1 = f"INSERT INTO account_master (party_name, provider_names, contact, address, pdf_path, login_id) VALUES ({DATABASE_SYN}, {DATABASE_SYN}, {DATABASE_SYN}, {DATABASE_SYN}, {DATABASE_SYN}, {DATABASE_SYN})"
            db_cursor.execute(sql1, (name, providers, contact, addr, pdf_path, login_id))
            db_connection.commit()
            messagebox.showinfo("Success", "Account created successfully.", parent = acc_master)
            on_start()
        elif name != '' and contact != '' and providers != '' and BtnSave['text'] == 'Update':
            sql2 = f"UPDATE account_master SET party_name = {DATABASE_SYN}, provider_names = {DATABASE_SYN}, contact = {DATABASE_SYN}, address = {DATABASE_SYN}, pdf_path = {DATABASE_SYN} WHERE id = {DATABASE_SYN}"
            db_cursor.execute(sql2, (name, providers, contact, addr, pdf_path, master_id))
            db_connection.commit()
            messagebox.showinfo("Success", "Account Updated successfully.", parent = acc_master)
            on_start()
        else:
            messagebox.showerror("Error", f"Data already present for {name} or \nCheck required fields.", parent = acc_master)
        
            
    def show_selected_record(event):
        for selection in trv.selection():
            item = trv.item(selection)
        
        i1 = item["values"]
        clear_data()
        
        TxtAcc.insert(0, i1[1])
        TxtProv.insert(0, i1[5])
        TxtContact.insert(0, i1[2])
        TxtAdd.insert("1.0", i1[3])
        LblPdfPath['text'] = i1[6]
        TxtMasterId['text'] = str(i1[4])
        
        BtnSave['text'] = 'Update'
    
    def New_Entry():
        on_start()

    def choose_pdf_path():
        file_path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")], parent=acc_master)
        if file_path:
            pdf_name = file_path.split('/')[-1]
            LblPdfPath['text'] = pdf_name
            LblPdfPath1['text'] = file_path
    
    def only_int(new_value):
        return (new_value.isdigit() or new_value == "") and len(new_value) < 11
    
    acc_master = Toplevel(master)
    acc_master.title("Customer Details")
    acc_master.geometry("1000x450+225+150")
    
    LblHead = Label(acc_master, text='Customer Details', font=('Times New Roman',26), fg='blue')
    LblHead.place(x=365,y=5)
    
    Frm1 = LabelFrame(acc_master, text='Customer Details', font=('Times New Roman',12), width=480, height=370)
    Frm1.place(x=20, y=60)
    
    LblAcc = Label(Frm1, text='Company Name', font=('Times New Roman',14))
    LblAcc.place(x=10, y=20)
    TxtAcc = AutocompleteCombobox(Frm1, font=('Times New Roman',14), width=48, justify='center')
    TxtAcc.place(x=12, y=50)
    
    LblProv = Label(Frm1, text='Providers', font=('Times New Roman',14))
    LblProv.place(x=10, y=90)
    TxtProv = Entry(Frm1, font=('Times New Roman',14), width=35)
    TxtProv.place(x=12, y=120)
    
    LblContact = Label(Frm1, text='Contact', font=('Times New Roman',14))
    LblContact.place(x=340, y=90)
    vcmd = (acc_master.register(only_int), "%P")
    TxtContact = Entry(Frm1, font=('Times New Roman',14),validate="key", validatecommand=vcmd, width=13, justify='center')
    TxtContact.place(x=340, y=120)
    
    LblAdd = Label(Frm1, text='Company Address', font=('Times New Roman',14))
    LblAdd.place(x=10, y=160)
    TxtAdd = Text(Frm1, font=('Times New Roman',14), width=50, height=2)
    TxtAdd.place(x=12, y=190)
    
    LblPdf = Label(Frm1, text='Select PDF', font=('Times New Roman',14))
    LblPdf.place(x=10, y=250)
    BtnAdd = Button(Frm1, text='Choose Pdf File', font=('Times New Roman',12), width=14, command=choose_pdf_path)
    BtnAdd.place(x=120, y=245)
    LblPdfPath = Label(Frm1, text='ishan.pdf', font=('Times New Roman',12))
    LblPdfPath.place(x=270, y=250)
    LblPdfPath1 = Label(Frm1, text='', font=('Times New Roman',12))
    LblPdfPath1.place(x=600, y=250)
    
    Frm2 = LabelFrame(Frm1, text='', font=('Times New Roman',12), width=450, height=50)
    Frm2.place(x=10, y=285)
    
    BtnNew = Button(Frm2, text='New', font=('Times New Roman',12), width=10, bg='blue', fg='white', command=New_Entry)
    BtnNew.place(x=5, y=5)
    BtnSave = Button(Frm2, text='Save', font=('Times New Roman',12), width=10, bg='green', fg='white', command=Save_Data)
    BtnSave.place(x=115, y=5)
    BtnDelete = Button(Frm2, text='Delete', font=('Times New Roman',12), width=10, bg='brown', fg='white', command=Delete_Data)
    BtnDelete.place(x=225, y=5)
    BtnExit = Button(Frm2, text='Exit', font=('Times New Roman',12), width=10, bg='red', fg='white', command=acc_master.destroy)
    BtnExit.place(x=335, y=5)
    
    scrolly=Scrollbar(acc_master , orient=VERTICAL)
    scrollx=Scrollbar(acc_master , orient=HORIZONTAL)
    
    trv=ttk.Treeview(acc_master , columns=("no" , "company_name" , "contact_no", "Address") , yscrollcommand=scrolly.set , xscrollcommand=scrollx.set)
    scrolly.place(x=970, y=70, height=360)
    scrollx.place(x=510, y=430, width=460)
    scrolly.config(command=trv.yview)
    scrollx.config(command=trv.xview)

    trv.heading("no" , text="No.")
    trv.heading("company_name" , text="Company Name")
    trv.heading("contact_no" , text="Contact")
    trv.heading("Address" , text="Address")
    #trv.heading("Provider" , text="Provider")
    
    trv["show"]="headings"

    trv.column("no" , width=40, anchor='center')
    trv.column("company_name" , width=120, anchor='w')
    trv.column("contact_no" , width=80, anchor='center')
    trv.column("Address" , width=130, anchor='w')
    #trv.column("Provider" , width=100, anchor='center')
    
    trv.place(x=510, y=70, width=460, height=360)
    
    TxtMasterId = Label(acc_master, text='')
    TxtMasterId.place(x=1500, y=1500)
    
    def f1(evevnt):
        n1 = TxtAcc.get()
        if n1 != '':
            try:
                sql1 = f"SELECT party_name, provider_names, contact, address FROM account_master where party_name = '{n1}' and login_id = '{login_id}'"
                db_cursor.execute(sql1)
                data1 = db_cursor.fetchall()

                TxtProv.delete(0, END)
                TxtContact.delete(0, END)
                TxtAdd.delete("1.0", END)
                
                TxtAcc.set(data1[0][0])
                TxtProv.insert(0, data1[0][1])
                TxtContact.insert(0, data1[0][2])
                TxtAdd.insert("1.0", data1[0][3])
            except:
                TxtProv.delete(0, END)
                TxtContact.delete(0, END)
                TxtAdd.delete("1.0", END)
        else:
            TxtProv.delete(0, END)
            TxtContact.delete(0, END)
            TxtAdd.delete("1.0", END)
    
    def f2(event):
        if TxtAcc.get():
            TxtProv.focus()
    #TxtContact, TxtAdd
    def f3(event):
        if TxtProv.get():
            TxtContact.focus()
    
    def f4(event):
        if TxtContact.get():
            TxtAdd.focus()
    
    on_start()
    TxtAcc.bind('<KeyRelease>', f1, add='+')
    trv.bind("<Double-1>", show_selected_record)
    
    TxtAcc.bind('<Return>', f2)
    TxtProv.bind('<Return>', f3)
    TxtContact.bind('<Return>', f4)
    acc_master.bind("<Escape>", lambda e: acc_master.destroy())
    # acc_master.mainloop()
    return acc_master

#Frm_Account_Master(1)