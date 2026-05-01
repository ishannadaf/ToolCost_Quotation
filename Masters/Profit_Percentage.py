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


def Frm_Profit_Per_Master(master):

    def clear_data():
        TxtName.delete(0, END)
        TxtPrice.delete(0, END)
        TxtName.focus()

    def get_customer_id():
        sql = "SELECT id FROM account_master WHERE party_name = %s"
        db_cursor.execute(sql, (TxtCustName.get(),))
        data = db_cursor.fetchone()
        return data[0] if data else 0

    def load_customers():
        sql = "SELECT party_name FROM account_master"
        db_cursor.execute(sql)
        data = db_cursor.fetchall()
        cust_names = []
        if data:
            cust_names.extend([i[0] for i in data])
        TxtCustName.set_completion_list(cust_names)
        TxtCustName.current(0)

    def set_item_list():
        clear_data()
        cust_id = get_customer_id()

        # # Default items
        # db_cursor.execute("SELECT id, profit_per, scrab_per FROM profit_percentage_master WHERE cust_id = 0")
        # default_items = db_cursor.fetchall()

        # Customer override items
        db_cursor.execute("SELECT id, profit_per, scrab_per FROM profit_percentage_master WHERE cust_id = %s", (cust_id,))
        cust_items = db_cursor.fetchall()
        trv.delete(*trv.get_children())
        if cust_items:
            TxtName.insert(0, cust_items[0][1])
            TxtPrice.insert(0, cust_items[0][2])
            trv.insert("", "end", values=(1, TxtCustName.get(), cust_items[0][1], cust_items[0][2], cust_items[0][0]))
            BtnSave['text'] = 'Update'
            LblMasterId['text'] = cust_items[0][0]
        else:
            BtnSave['text'] = 'Save'
            LblMasterId['text'] = ''
        # trv.delete(*trv.get_children())
        # cnt = 1

        # for item in default_items:
        #     default_id, name, price = item

        #     if name in cust_dict:
        #         cust_item_id, cust_price = cust_dict[name]
        #         trv.insert("", "end", values=(cnt, name, cust_price, cust_item_id, cust_id))
        #     else:
        #         trv.insert("", "end", values=(cnt, name, price, default_id, 0))

        #     cnt += 1

        

    def save_data():
        name = TxtName.get().strip()
        price = TxtPrice.get().strip()

        if not name or not price:
            messagebox.showerror("Error", "Please fill all data", parent=machining_master)
            return

        cust_id = get_customer_id()

        # SAVE (New Default Item)
        if BtnSave['text'] == 'Save':
            sql = "INSERT INTO profit_percentage_master (cust_id, profit_per, scrab_per) VALUES (%s, %s, %s)"
            db_cursor.execute(sql, (cust_id, name, price))
            db_connection.commit()
            messagebox.showinfo("Success", "Default Data Saved Successfully", parent=machining_master)
            set_item_list()
            clear_data()
            return

        # UPDATE
        if BtnSave['text'] == 'Update':

            if cust_id == 0:
                # Update default
                sql = "UPDATE profit_percentage_master SET profit_per=%s, scrab_per=%s WHERE id=%s"
                db_cursor.execute(sql, (name, price, LblMasterId['text']))
            else:
                # Check if override exists
                sql = "SELECT id FROM profit_percentage_master WHERE cust_id=%s"
                db_cursor.execute(sql, (cust_id,))
                existing = db_cursor.fetchone()

                if existing:
                    sql = "UPDATE profit_percentage_master SET profit_per=%s, scrab_per=%s WHERE id=%s"
                    db_cursor.execute(sql, (name, price, existing[0]))
                else:
                    sql = "INSERT INTO profit_percentage_master (cust_id, profit_per, scrab_per) VALUES (%s, %s, %s)"
                    db_cursor.execute(sql, (cust_id, name, price))

            db_connection.commit()
            messagebox.showinfo("Success", "Data Updated Successfully", parent=machining_master)
            set_item_list()
            clear_data()
            BtnSave['text'] = 'Save'

    def delete_data():
        if LblMasterId['text'] != '':
            sql = "DELETE FROM profit_percentage_master WHERE id=%s"
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
    machining_master.geometry("650x400+430+175")
    machining_master.title("Machining Master")
    machining_master.resizable(False, False)
    Label(machining_master, text='Profit & Percentage', font=('Times New Roman', 22)).place(x=200, y=10)

    Frm1 = LabelFrame(machining_master, width=620, height=320)
    Frm1.place(x=10, y=60)

    Label(Frm1, text='Customer Name', font=('Times New Roman', 14)).place(x=50, y=20)
    TxtCustName = AutocompleteCombobox(Frm1, font=('Times New Roman', 14), width=30, justify='center', state='readonly')
    TxtCustName.place(x=250, y=20)

    Label(Frm1, text='Profit (%)', font=('Times New Roman', 14)).place(x=80, y=60)
    TxtName = Entry(Frm1, font=('Times New Roman', 14), width=20, justify='center')
    TxtName.place(x=50, y=90)

    Label(Frm1, text='Scrap (%)', font=('Times New Roman', 14)).place(x=400, y=60)
    TxtPrice = Entry(Frm1, font=('Times New Roman', 14), width=20, justify='center')
    TxtPrice.place(x=350, y=90)

    BtnSave = Button(Frm1, text='Save', font=('Times New Roman', 12), width=12, bg='green', fg='white', command=save_data)
    BtnSave.place(x=80, y=130)

    BtnDelete = Button(Frm1, text='Delete', font=('Times New Roman', 12), width=12, bg='brown', fg='white', command=delete_data)
    BtnDelete.place(x=250, y=130)

    BtnExit = Button(Frm1, text='Exit', font=('Times New Roman', 12), width=12, bg='red', fg='white', command=machining_master.destroy)
    BtnExit.place(x=420, y=130)

    LblMasterId = Label(machining_master, text='')
    LblMasterId.place(x=1000, y=1000)

    trv = ttk.Treeview(Frm1, columns=("no", "cust_name", "profit", "scrab"))
    trv.heading("no", text="No.")
    trv.heading("cust_name", text="Customer Name")
    trv.heading("profit", text="Profit (%)")
    trv.heading("scrab", text="Scrap (%)")

    trv.column("no", width=60, anchor='center')
    trv.column("cust_name", width=250)
    trv.column("profit", width=100, anchor='center')
    trv.column("scrab", width=100, anchor='center')

    trv["show"] = "headings"
    trv.place(x=20, y=190, width=580, height=100)

    trv.bind("<Double-1>", show_selected_record)
    TxtCustName.bind("<<ComboboxSelected>>", lambda e: set_item_list())
    machining_master.bind("<Escape>", lambda e: machining_master.destroy())
    load_customers()
    set_item_list()

    return machining_master