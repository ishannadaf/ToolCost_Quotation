from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from Database.connection import *
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

def Frm_material_master(master):
    
    def clear_data():
        TxtName.delete(0, END)
        TxtPrice.delete(0, END)
        TxtDensity.delete(0, END)

    def get_customer_id():
        if TxtCustName.get() == 'ALL':
            return 0
        sql = f"SELECT id FROM account_master WHERE party_name = {DATABASE_SYN}"
        db_cursor.execute(sql, (TxtCustName.get(),))
        data = db_cursor.fetchone()
        return data[0] if data else 0

    def set_item_list():
        clear_data()
        cust_id = get_customer_id()

        # Fetch default materials
        db_cursor.execute("SELECT id, name, density, rate FROM material_master WHERE cust_id = 0")
        default_items = db_cursor.fetchall()

        # Fetch customer overrides
        db_cursor.execute("SELECT id, name, density, rate FROM material_master WHERE cust_id = %s", (cust_id,))
        cust_items = db_cursor.fetchall()

        cust_dict = {item[1]: (item[0], item[2], item[3]) for item in cust_items}

        trv.delete(*trv.get_children())
        cnt = 1

        for item in default_items:
            default_id, name, density, rate = item

            if name in cust_dict:
                cust_item_id, cust_density, cust_rate = cust_dict[name]
                trv.insert("", 'end',
                           values=(str(cnt), name, cust_density, cust_rate, cust_item_id, cust_id))
            else:
                trv.insert("", 'end',
                           values=(str(cnt), name, density, rate, default_id, 0))
            cnt += 1

        BtnSave['text'] = 'Save'
        LblMasterId['text'] = ''

    def save_data():
        name = TxtName.get().strip()
        density = TxtDensity.get().strip()
        price = TxtPrice.get().strip()

        if name == '' or density == '' or price == '':
            messagebox.showerror("Error", "Please fill all data", parent=material_master)
            return

        cust_id = get_customer_id()

        # SAVE (only for ALL)
        if BtnSave['text'] == 'Save':
            if cust_id != 0:
                messagebox.showerror("Error", "New material can be added only in ALL", parent=material_master)
                return

            sql = f"INSERT INTO material_master (name, density, rate, cust_id) VALUES ({DATABASE_SYN}, {DATABASE_SYN}, {DATABASE_SYN}, {DATABASE_SYN})"
            db_cursor.execute(sql, (name, density, price, 0))
            db_connection.commit()
            messagebox.showinfo("Success", "Data Saved Successfully", parent=material_master)
            set_item_list()
            clear_data()

        # UPDATE
        elif BtnSave['text'] == 'Update':

            if cust_id == 0:
                # Update default
                sql = f"UPDATE material_master SET name = {DATABASE_SYN}, density = {DATABASE_SYN}, rate = {DATABASE_SYN} WHERE id = {DATABASE_SYN}"
                db_cursor.execute(sql, (name, density, price, LblMasterId['text']))
            else:
                # Check override exists
                sql = f"SELECT id FROM material_master WHERE name = {DATABASE_SYN} AND cust_id = {DATABASE_SYN}"
                db_cursor.execute(sql, (name, cust_id))
                existing = db_cursor.fetchone()

                if existing:
                    sql = f"UPDATE material_master SET density = {DATABASE_SYN}, rate = {DATABASE_SYN} WHERE id = {DATABASE_SYN}"
                    db_cursor.execute(sql, (density, price, existing[0]))
                else:
                    sql = f"INSERT INTO material_master (name, density, rate, cust_id) VALUES ({DATABASE_SYN}, {DATABASE_SYN}, {DATABASE_SYN}, {DATABASE_SYN})"
                    db_cursor.execute(sql, (name, density, price, cust_id))

            db_connection.commit()
            messagebox.showinfo("Success", "Data Updated Successfully", parent=material_master)
            set_item_list()
            clear_data()
            BtnSave['text'] = 'Save'

    def delete_data():
        if LblMasterId['text'] != '':
            sql = f"DELETE FROM material_master WHERE id = {DATABASE_SYN}"
            db_cursor.execute(sql, (LblMasterId['text'],))
            db_connection.commit()
            messagebox.showinfo("Success", "Data deleted successfully", parent=material_master)
            set_item_list()

    def show_selected_record(event):
        selected = trv.selection()
        if not selected:
            return
        item = trv.item(selected[0])
        values = item["values"]

        clear_data()
        TxtName.insert(0, values[1])
        TxtDensity.insert(0, values[2])
        TxtPrice.insert(0, values[3])
        LblMasterId['text'] = values[4]
        BtnSave['text'] = 'Update'

    def on_start():
        clear_data()
        TxtName.focus()

        sql1 = f"SELECT party_name FROM account_master"
        db_cursor.execute(sql1)
        data1 = db_cursor.fetchall()
        cust_names = ['ALL']
        if data1:
            cust_names.extend([i[0] for i in data1])

        TxtCustName.set_completion_list(cust_names)
        TxtCustName.set('ALL')

        set_item_list()

    # ----------------- UI (UNCHANGED) -----------------

    material_master = Toplevel(master)
    material_master.geometry("600x450+430+175")
    
    LblHead = Label(material_master, text='Material Master', font=('Times New Roman', 22))
    LblHead.place(x=200, y=10)
    
    Frm1 = LabelFrame(material_master, width=580, height=370)
    Frm1.place(x=10, y=60)
    
    LblCustName = Label(Frm1, text='Customer Name', font=('Times New Roman', 15))
    LblCustName.place(x=60, y=20)
    TxtCustName = AutocompleteCombobox(Frm1, font=('Times New Roman', 15), width=30, justify='center', state='readonly')
    TxtCustName.place(x=230, y=20)
    
    LblName = Label(Frm1, text='Name', font=('Times New Roman', 14))
    LblName.place(x=70, y=60)
    TxtName = Entry(Frm1, font=('Times New Roman', 14), width=18, justify='center')
    TxtName.place(x=20, y=90)
    
    LblDensity = Label(Frm1, text='Density', font=('Times New Roman', 14))
    LblDensity.place(x=240, y=60)
    TxtDensity = Entry(Frm1, font=('Times New Roman', 14), width=18, justify='center')
    TxtDensity.place(x=200, y=90)
    
    LblPrice = Label(Frm1, text='Price', font=('Times New Roman', 14))
    LblPrice.place(x=430, y=60)
    TxtPrice = Entry(Frm1, font=('Times New Roman', 14), width=18, justify='center')
    TxtPrice.place(x=380, y=90)
    
    BtnSave = Button(Frm1, text='Save', font=('Times New Roman', 12), width=12, bg='green', fg='white', command=save_data)
    BtnSave.place(x=110, y=130)
    BtnDelete = Button(Frm1, text='Delete', font=('Times New Roman', 12), width=12, bg='brown', fg='white', command=delete_data)
    BtnDelete.place(x=240, y=130)
    BtnExit = Button(Frm1, text='Exit', font=('Times New Roman', 12), width=12, bg='red', fg='white',command=material_master.destroy)
    BtnExit.place(x=370, y=130)
    
    LblMasterId = Label(material_master, text='')
    LblMasterId.place(x=1000, y=1000)
    
    scrolly=Scrollbar(Frm1 , orient=VERTICAL)
    scrolly.place(x=550, y=190, height=170)
    
    trv=ttk.Treeview(Frm1 , columns=("no" , "name", "density", "price") , yscrollcommand=scrolly.set )
    scrolly.config(command=trv.yview)

    trv.heading("no" , text="No.")
    trv.heading("name" , text="Name")
    trv.heading("density" , text="Density")
    trv.heading("price" , text="Price")
    
    trv["show"]="headings"

    trv.column("no" , width=70, anchor='center')
    trv.column("name" , width=200, anchor='w')
    trv.column("density" , width=80, anchor='center')
    trv.column("price" , width=80, anchor='center')
    
    trv.place(x=20, y=190, width=530, height=170)
    
    on_start()
    trv.bind("<Double-1>", show_selected_record)
    TxtCustName.bind("<<ComboboxSelected>>", lambda e: set_item_list())
    material_master.bind("<Escape>", lambda e: material_master.destroy())

    return material_master
# Frm_material_master(1)