from tkinter import *
from tkinter import simpledialog
import tkinter.ttk as ttk
from Database.connection import *
from tkinter import messagebox
import os
import tkinter as tk
from datetime import datetime, timedelta
from Quotation.Quotation_Master_PDF import create_quotation_pdf
from tkinter import filedialog
def Frm_New_Invoice(master, login_id):

    all_entries = {}
    # ---------------- HELPER FUNCTIONS ----------------
    
    def enable_esc_close(window):
        #print(window)
        def _close(event=None):
            window.grab_release()
            window.destroy()
            return "break"   # ⛔ STOP event propagation
        window.bind("<Escape>", _close)
        
        
    def resequence_treeview(trv):
        for idx, item in enumerate(trv.get_children(), start=1):
            values = list(trv.item(item, "values"))
            values[0] = idx
            trv.item(item, values=values)

    # ---------------- AUTOCOMPLETE COMBOBOX ----------------

    class AutocompleteCombobox(ttk.Combobox):
        def __init__(self, master=None, **kwargs):
            super().__init__(master, **kwargs)
            self._completion_list = []
            self._default_text = ""

            # Set default text
            self.set(self._default_text)

            # Bindings
            self.bind('<KeyRelease>', self._on_keyrelease)
            self.bind('<Tab>', self._accept_autocomplete)
            self.bind('<Return>', self._accept_autocomplete)

            # 🔥 Detect paste actions
            self.bind('<<Paste>>', self._on_paste)
            self.bind('<Control-v>', self._on_paste)

        def set_completion_list(self, completion_list):
            self._completion_list = sorted(completion_list, key=str.lower)
            self['values'] = self._completion_list

        def _clear_default_if_needed(self):
            if self.get() == self._default_text:
                self.delete(0, tk.END)

        def _on_paste(self, event=None):
            self._clear_default_if_needed()
            # Allow normal paste to continue
            return None

        def _on_keyrelease(self, event):
            # If user starts typing and default is there → clear it
            if self.get() == self._default_text:
                self.delete(0, tk.END)
                return

            if event.keysym in ('BackSpace', 'Left', 'Right', 'Up', 'Down'):
                return

            typed = self.get()
            if not typed:
                return

            for item in self._completion_list:
                if item.lower().startswith(typed.lower()):
                    self.set(item)

                    # Highlight suggestion part
                    self.selection_range(len(typed), tk.END)
                    self.icursor(len(typed))
                    break

        def _accept_autocomplete(self, event=None):
            self.icursor(tk.END)
            self.selection_clear()
            return "break"
    # ---------------- LOAD QUOTATIONS ----------------
    def On_Start_New_Quot():
        all_entries.clear()
        trv_left.delete(*trv_left.get_children())
        trv_right.delete(*trv_right.get_children())

        sql = """
        SELECT 
            qm.quotation_id,
            qmd.part_no,
            qmd.part_desc,
            qmd.part_qty,
            qmd.unit_price,
            qmd.total_price
        FROM quotation_master qm
        INNER JOIN quotation_master_details qmd 
            ON qm.quotation_id = qmd.Quotation_Id
        WHERE NOT EXISTS (
            SELECT 1 FROM invoice_master im
            WHERE im.quot_id = qm.quotation_id
            AND im.part_no = qmd.part_no
        )
        AND qm.login_id = %s
        """

        db_cursor.execute(sql, (login_id,))
        rows = db_cursor.fetchall()

        quot_list = ['']
        for r in rows:
            quot_id = r[0]
            item = (r[1], r[2], r[3], r[4], r[5])
            all_entries.setdefault(quot_id, []).append(item)
            if quot_id not in quot_list:
                quot_list.append(quot_id)

        entQuotationID.set_completion_list(quot_list)
        if quot_list:
            entQuotationID.current(0)
            
        inv_no = Invoice_Id_Funct(login_id)
        lblInvoiceNo.config(text=f"Invoice No: {inv_no}")
        
        entQuotationID.focus_set()
    # ---------------- SEARCH QUOTATION ----------
    
    def search_quotation():
        trv_left.delete(*trv_left.get_children())
        trv_right.delete(*trv_right.get_children())
        quot_id = entQuotationID.get()
        items = all_entries.get(quot_id, [])

        for idx, i in enumerate(items, start=1):
            trv_left.insert("", END, values=(idx, i[0], i[1], i[2], i[3], i[4]))

    # ---------------- MOVE FUNCTIONS ----------------
    def move_right():
        for item in trv_left.selection():
            trv_right.insert("", END, values=trv_left.item(item, "values"))
            trv_left.delete(item)
        resequence_treeview(trv_left)
        resequence_treeview(trv_right)

    def move_left():
        for item in trv_right.selection():
            trv_left.insert("", END, values=trv_right.item(item, "values"))
            trv_right.delete(item)
        resequence_treeview(trv_left)
        resequence_treeview(trv_right)

    def move_all_right():
        for item in trv_left.get_children():
            trv_right.insert("", END, values=trv_left.item(item, "values"))
        trv_left.delete(*trv_left.get_children())
        resequence_treeview(trv_right)

    def move_all_left():
        for item in trv_right.get_children():
            trv_left.insert("", END, values=trv_right.item(item, "values"))
        trv_right.delete(*trv_right.get_children())
        resequence_treeview(trv_left)

    # ---------------- GENERATE INVOICE ----------------
    


    # ---------------- SHOW INVOICE (PDF) ----------------
    def Show_Invoice(po_number, terms_data): 
        Company_Name, Company_Contact, Company_Address, email_id = Get_Firm_Details(login_id) 
        quotation_id = entQuotationID.get() 
        sql1 = f""" select am.party_name, qm.provider_name from account_master am inner join quotation_master qm on am.id = qm.cust_id where qm.quotation_id = '{quotation_id}'; """ 
        db_cursor.execute(sql1) 
        data1 = db_cursor.fetchall() 
        customer_name = data1[0][0] 
        party_name, contact, address, mid = Customer_Details(customer_name, login_id) 
        provider_name = data1[0][1] 
        term_date = (datetime.today() + timedelta(days=30)).strftime('%d-%m-%Y') 
        items = [] 
        invoice_id = lblInvoiceNo['text'].split(": ")[1]
        subtotal = 0
        gst_per = "SELECT gst_per FROM gst_percentage_table WHERE id = 1" 
        db_cursor.execute(gst_per) 
        gst_per = int(db_cursor.fetchone()[0])
        for child in trv_right.get_children(): 
            vals = trv_right.item(child)["values"] 
            items.append({ "no": vals[1], "part_desc": vals[2], "qty": int(vals[3]), "unit_price": int(float(vals[4])), "total_price": int(float(vals[5])), "taxed":"" }) 
            subtotal += int(float(vals[5])) 
        
        tax_due = int(subtotal*gst_per/100)
        grand_total = subtotal + tax_due 
        
        # terms_data = get_terms_conditions(quotation_id)
        sample = { "company": 
                    { "name":Company_Name, 
                    "address":Company_Address, 
                    "phone": Company_Contact, 
                    "email": email_id
                    }, 
                "date": datetime.today().strftime("%d-%m-%Y"), 
                "quote_no": invoice_id, 
                "po_no": po_number,
                "valid_until": term_date,
                "prepared_by": "Admin", 
                "customer": 
                    { "name":party_name, 
                    "company":provider_name, 
                    "address":address, 
                    "phone":contact }, 
                "items":items, 
                "totals":
                    {"subtotal":subtotal,
                    "taxable":subtotal,
                    "tax_rate":gst_per,
                    "tax_due":tax_due,
                    "other":0,
                    "grand_total":grand_total},
                "terms": terms_data}
        if items != []:
            # pdf_path = r"D:\\ToolCosting\\Support Documents\\Tool_Quotation.pdf" 
            pdf_path = filedialog.asksaveasfilename(
                    defaultextension=".pdf",
                    filetypes=[("PDF files", "*.pdf")],
                    initialfile=f"{invoice_id}.pdf",   # Default file name
                    title="Save Quotation PDF",
                    parent=new_quot
                )
            
            messagebox.showinfo("Success",f"Invoice is generated successfully...", parent=new_quot) 
            date_tr = datetime.today().date()
            sql_update = f"UPDATE quotation_master SET invoice_id = {DATABASE_SYN}, invoice_tr_date = {DATABASE_SYN}, invoice_generated = {DATABASE_SYN} WHERE quotation_id = {DATABASE_SYN} AND login_id = {DATABASE_SYN}" 
            params = (invoice_id, date_tr, 'Y', quotation_id, login_id) 
            db_cursor.execute(sql_update, params) 
            #db_cursor.execute(sql_update)
            db_connection.commit()
            create_quotation_pdf(sample, pdf_path, "TAX INVOICE", new_quot) 
            # os.startfile(pdf_path) #txtSaveInfo['text'] = '' 
            trv_right.delete(*trv_right.get_children())
            trv_left.delete(*trv_left.get_children())
            On_Start_New_Quot()
    
    def generate_invoice_terms():
        global rules_page

        if trv.get_children():
            def on_ok_click():
                global rules_page   # IMPORTANT
                n1 = TxtRule.get(1.0, END).strip()
                terms_conditions = []
                if n1:                
                    terms_conditions = n1.split('\n')
                    
                generate_invoice(terms_conditions)

                rules_page.destroy()
                rules_page = None   # reset after close

            # ✅ Check if already open
            # if rules_page is not None and rules_page.winfo_exists():
            #     rules_page.lift()
            #     rules_page.focus_force()
            #     return

            def on_start_rules_page():
               TxtRule.insert(END, """Transport of meterial included/excluded in scope \nVehicle no. - XXXXXXXXXX""")

            # ✅ Create window only once
            rules_page = Toplevel(new_quot)
            rules_page.geometry("550x200+500+300")
            rules_page.title("Generating PDF")

            # ✅ Handle manual close (VERY IMPORTANT)
            def on_close():
                global rules_page
                rules_page.destroy()
                rules_page = None

            rules_page.protocol("WM_DELETE_WINDOW", on_close)

            LblRule = Label(rules_page, text="Terms & conditions", font=('Times New Roman', 18))
            LblRule.place(x=170, y=10)

            TxtRule = Text(rules_page, font=('Times New Roman', 14), width=55, height=4)
            TxtRule.place(x=20, y=50)

            BtnOk = Button(
                rules_page,
                text="OK",
                width=12,
                bg='green',
                fg='white',
                font=('Times New Roman', 12),
                command=on_ok_click
            )
            BtnOk.place(x=210, y=155)

            on_start_rules_page()

        else:
            messagebox.showerror("Error", "Please add some records to save.", parent=new_quot)
    
    
    def generate_invoice(terms):
        if not trv_right.get_children():
            messagebox.showerror("Error", "No items selected for invoice", parent=new_quot)
            return

        # ---- ASK FOR PO NUMBER ----
        po_number = simpledialog.askstring(
            "PO Number",
            "Enter Purchase Order (PO) Number:",
            parent=new_quot
        )
        
        # If user cancels or leaves empty
        if not po_number:
            messagebox.showwarning("Required", "PO Number is required to generate invoice", parent=new_quot)
            return
        
        inv_no = lblInvoiceNo['text'].split(": ")[1]
        quot_id = entQuotationID.get()
        date_tr = datetime.today().date()
        
        sql1 = f"SELECT COUNT(*) FROM invoice_master WHERE po_no = '{po_number}' and quot_id = '{quot_id}'"
        db_cursor.execute(sql1)
        data1 = db_cursor.fetchone()[0]
        if data1 > 0:
            messagebox.showerror("Error", f"PO No already exists for given QUOTATION NO : {quot_id}", parent=new_quot)
            return

        data = []
        terms_save = '\n'.join(terms)
        for item in trv_right.get_children():
            vals = trv_right.item(item, "values")
            data.append((inv_no, quot_id, vals[1], po_number, date_tr, terms_save, login_id))

        sql = """
        INSERT INTO invoice_master 
        (invoice_id, quot_id, part_no, po_no, date_tr, term_conditions, login_id)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """

        db_cursor.executemany(sql, data)
        db_connection.commit()

        messagebox.showinfo("Success", "Invoice generated successfully", parent=new_quot)
        Show_Invoice(po_number, terms)
        On_Start_New_Quot()
    # ---------------- UI ----------------
    new_quot = Toplevel(master)
    new_quot.title("New Invoice")
    new_quot.geometry("1050x550+300+120")
    new_quot.resizable(False, False)

    Label(new_quot, text="Create New Invoice",
        font=("Times New Roman", 24, "bold")).place(x=360, y=10)

    Label(new_quot, text="Quotation ID:",
        font=("Times New Roman", 16)).place(x=80, y=80)

    def only_int(new_value):
        return new_value.isdigit() or new_value == ""

    # vcmd = (new_quot.register(only_int), "%P")
    entQuotationID = AutocompleteCombobox(new_quot, font=("Times New Roman", 16), width=20)
    entQuotationID.place(x=230, y=80)
    entQuotationID.focus_set()

    Button(new_quot, text="Search", font=("Times New Roman", 14),
        bg="green", fg="white", command=search_quotation).place(x=500, y=78)

    lblInvoiceNo = Label(new_quot, text="Invoice No: ----",
                        font=("Times New Roman", 16, "bold"))
    lblInvoiceNo.place(x=700, y=80)

    cols = ("no", "part_no", "part_desc", "qty")

    trv_left = ttk.Treeview(new_quot, columns=cols, show="headings", height=15)
    trv_left.place(x=20, y=150, width=450)

    trv_right = ttk.Treeview(new_quot, columns=cols, show="headings", height=15)
    trv_right.place(x=570, y=150, width=450)

    for trv in (trv_left, trv_right):
        for c in cols:
            trv.heading(c, text=c.replace("_", " ").title())
        trv.column("no", width=40, anchor="center")
        trv.column("part_no", width=80, anchor="center")
        trv.column("part_desc", width=200)
        trv.column("qty", width=50, anchor="center")
        # trv.column("unit_price", width=70, anchor="e")
        # trv.column("total", width=70, anchor="e")

    Button(new_quot, text="→", font=("Arial", 18), width=3,
        command=move_right).place(x=490, y=220)

    Button(new_quot, text="←", font=("Arial", 18), width=3,
        command=move_left).place(x=490, y=270)

    Button(new_quot, text=">>", font=("Arial", 16, "bold"), width=3,
        command=move_all_right).place(x=490, y=320)

    Button(new_quot, text="<<", font=("Arial", 16, "bold"), width=3,
        command=move_all_left).place(x=490, y=370)

    Button(new_quot, text="Generate Invoice",
        font=("Times New Roman", 16, "bold"),
        bg="green", fg="white",
        command=generate_invoice_terms).place(x=440, y=500)

    On_Start_New_Quot()
    enable_esc_close(new_quot)
    return new_quot
