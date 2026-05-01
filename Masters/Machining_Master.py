from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from Database.connection import *
import tkinter


class AutocompleteCombobox(ttk.Combobox):

    def set_completion_list(self, completion_list):
        self._completion_list = sorted(completion_list, key=str.lower)
        self._hits = []
        self._hit_index = 0
        self.position = 0
        self.bind('<KeyRelease>', self.handle_keyrelease)
        self['values'] = self._completion_list

    def autocomplete(self, delta=0):
        if delta:
            self.delete(self.position, tkinter.END)
        else:
            self.position = len(self.get())

        _hits = []
        for element in self._completion_list:
            if element.lower().startswith(self.get().lower()):
                _hits.append(element)

        if _hits != self._hits:
            self._hit_index = 0
            self._hits = _hits

        if _hits == self._hits and self._hits:
            self._hit_index = (self._hit_index + delta) % len(self._hits)

        if self._hits:
            self.delete(0, tkinter.END)
            self.insert(0, self._hits[self._hit_index])
            self.select_range(self.position, tkinter.END)

    def handle_keyrelease(self, event):
        if event.keysym == "BackSpace":
            self.delete(self.index(tkinter.INSERT), tkinter.END)
            self.position = self.index(tkinter.END)

        if len(event.keysym) == 1:
            self.autocomplete()


def Frm_Machining_Master(master):

    def clear_data():
        TxtName.delete(0, END)
        TxtPrice.delete(0, END)

    def get_customer_id():
        if TxtCustName.get() == 'ALL':
            return 0
        sql = "SELECT id FROM account_master WHERE party_name = %s"
        db_cursor.execute(sql, (TxtCustName.get(),))
        data = db_cursor.fetchone()
        return data[0] if data else 0

    def load_customers():
        sql = "SELECT party_name FROM account_master"
        db_cursor.execute(sql)
        data = db_cursor.fetchall()
        cust_names = ['ALL']
        if data:
            cust_names.extend([i[0] for i in data])
        TxtCustName.set_completion_list(cust_names)
        TxtCustName.set('ALL')

    def set_item_list():
        clear_data()
        cust_id = get_customer_id()

        # Default items
        db_cursor.execute("SELECT id, name, price FROM machining_master WHERE cust_id = 0")
        default_items = db_cursor.fetchall()

        # Customer override items
        db_cursor.execute("SELECT id, name, price FROM machining_master WHERE cust_id = %s", (cust_id,))
        cust_items = db_cursor.fetchall()

        cust_dict = {item[1]: (item[0], item[2]) for item in cust_items}

        trv.delete(*trv.get_children())
        cnt = 1

        for item in default_items:
            default_id, name, price = item

            if name in cust_dict:
                cust_item_id, cust_price = cust_dict[name]
                trv.insert("", "end", values=(cnt, name, cust_price, cust_item_id, cust_id))
            else:
                trv.insert("", "end", values=(cnt, name, price, default_id, 0))

            cnt += 1

        BtnSave['text'] = 'Save'
        LblMasterId['text'] = ''
        TxtName.focus()

    def save_data():
        name = TxtName.get().strip()
        price = TxtPrice.get().strip()

        if not name or not price:
            messagebox.showerror("Error", "Please fill all data", parent=machining_master)
            return

        cust_id = get_customer_id()

        # SAVE (New Default Item)
        if BtnSave['text'] == 'Save':
            if cust_id != 0:
                messagebox.showerror("Error", "New item can be added only in ALL", parent=machining_master)
                return

            sql = "INSERT INTO machining_master (name, price, cust_id) VALUES (%s, %s, %s)"
            db_cursor.execute(sql, (name, price, 0))
            db_connection.commit()
            messagebox.showinfo("Success", "Default Data Saved Successfully", parent=machining_master)
            set_item_list()
            clear_data()
            return

        # UPDATE
        if BtnSave['text'] == 'Update':

            if cust_id == 0:
                # Update default
                sql = "UPDATE machining_master SET name=%s, price=%s WHERE id=%s"
                db_cursor.execute(sql, (name, price, LblMasterId['text']))
            else:
                # Check if override exists
                sql = "SELECT id FROM machining_master WHERE name=%s AND cust_id=%s"
                db_cursor.execute(sql, (name, cust_id))
                existing = db_cursor.fetchone()

                if existing:
                    sql = "UPDATE machining_master SET price=%s WHERE id=%s"
                    db_cursor.execute(sql, (price, existing[0]))
                else:
                    sql = "INSERT INTO machining_master (name, price, cust_id) VALUES (%s, %s, %s)"
                    db_cursor.execute(sql, (name, price, cust_id))

            db_connection.commit()
            messagebox.showinfo("Success", "Data Updated Successfully", parent=machining_master)
            set_item_list()
            clear_data()
            BtnSave['text'] = 'Save'

    def delete_data():
        if LblMasterId['text'] != '':
            sql = "DELETE FROM machining_master WHERE id=%s"
            db_cursor.execute(sql, (LblMasterId['text'],))
            db_connection.commit()
            messagebox.showinfo("Success", "Data deleted successfully", parent=machining_master)
            set_item_list()

    def show_selected_record(event):
        selected = trv.selection()
        if not selected:
            return
        item = trv.item(selected[0])
        values = item["values"]

        clear_data()
        TxtName.insert(0, values[1])
        TxtPrice.insert(0, values[2])

        LblMasterId['text'] = values[3]
        BtnSave['text'] = 'Update'

    # ---------------- UI ----------------

    machining_master = Toplevel(master)
    machining_master.geometry("650x500+430+175")
    machining_master.title("Machining Master")
    machining_master.resizable(False, False)
    Label(machining_master, text='Machining Master', font=('Times New Roman', 22)).place(x=200, y=10)

    Frm1 = LabelFrame(machining_master, width=620, height=400)
    Frm1.place(x=10, y=60)

    Label(Frm1, text='Customer Name', font=('Times New Roman', 14)).place(x=50, y=20)
    TxtCustName = AutocompleteCombobox(Frm1, font=('Times New Roman', 14), width=30, justify='center', state='readonly')
    TxtCustName.place(x=250, y=20)

    Label(Frm1, text='Name', font=('Times New Roman', 14)).place(x=80, y=60)
    TxtName = Entry(Frm1, font=('Times New Roman', 14), width=20, justify='center')
    TxtName.place(x=50, y=90)

    Label(Frm1, text='Price', font=('Times New Roman', 14)).place(x=400, y=60)
    TxtPrice = Entry(Frm1, font=('Times New Roman', 14), width=20, justify='center')
    TxtPrice.place(x=350, y=90)

    BtnNew = Button(Frm1, text='New', width=12, bg='blue', fg='white', command=set_item_list)
    BtnNew.place(x=30, y=130)

    BtnSave = Button(Frm1, text='Save', width=12, bg='green', fg='white', command=save_data)
    BtnSave.place(x=160, y=130)

    BtnDelete = Button(Frm1, text='Delete', width=12, bg='brown', fg='white', command=delete_data)
    BtnDelete.place(x=290, y=130)

    BtnExit = Button(Frm1, text='Exit', width=12, bg='red', fg='white', command=machining_master.destroy)
    BtnExit.place(x=420, y=130)

    LblMasterId = Label(machining_master, text='')
    LblMasterId.place(x=1000, y=1000)

    trv = ttk.Treeview(Frm1, columns=("no", "name", "price"))
    trv.heading("no", text="No.")
    trv.heading("name", text="Name")
    trv.heading("price", text="Price")

    trv.column("no", width=60, anchor='center')
    trv.column("name", width=250)
    trv.column("price", width=100, anchor='center')

    trv["show"] = "headings"
    trv.place(x=20, y=190, width=580, height=180)

    trv.bind("<Double-1>", show_selected_record)
    TxtCustName.bind("<<ComboboxSelected>>", lambda e: set_item_list())
    machining_master.bind("<Escape>", lambda e: machining_master.destroy())
    load_customers()
    set_item_list()

    return machining_master