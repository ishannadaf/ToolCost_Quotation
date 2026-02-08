from tkinter import *
import tkinter.ttk as ttk
from tkcalendar import DateEntry
from datetime import datetime, timedelta
from Database.connection import *
from tkinter import messagebox
from Quotation.Quotation_Master_PDF import create_quotation_pdf
import os

def Frm_Quot_History(master, login_id):
    def Search_Records():
        
        n1 = TxtSearch.get()
        n2 = TxtSearchBy.get()
        n3 = TxtCustomerS.get()
        if n1 == "Quotation":
            if n2 == "Quotation No":
                sql1 = f"SELECT qm.quotation_id, qm.provider_name, qm.date_tr_quot, qm.invoice_tr_date, am.party_name, qm.invoice_id FROM quotation_master qm INNER JOIN account_master am on qm.cust_id = am.id WHERE qm.quotation_id = '{n3}'"
            else:
                sql1 = f"""SELECT qm.quotation_id, qm.provider_name, qm.date_tr_quot, qm.invoice_tr_date, 
                am.party_name, qm.invoice_id FROM quotation_master qm INNER JOIN account_master am on qm.cust_id = am.id 
                    INNER JOIN quotation_master_details qmd on qmd.Quotation_Id = qm.quotation_id
                    WHERE qmd.part_no = '{n3}'"""
        if n1 == "Invoice":
            if n2 == "Invoice No":
                sql1 = f"SELECT qm.quotation_id, qm.provider_name, qm.date_tr_quot, qm.invoice_tr_date, am.party_name, qm.invoice_id FROM quotation_master qm INNER JOIN account_master am on qm.cust_id = am.id WHERE qm.invoice_id = '{n3}' and invoice_generated = 'Y'"
            else:
                sql1 = f"""SELECT qm.quotation_id, qm.provider_name, qm.date_tr_quot, qm.invoice_tr_date, 
                am.party_name, qm.invoice_id FROM quotation_master qm INNER JOIN account_master am on qm.cust_id = am.id 
                    INNER JOIN quotation_master_details qmd on qmd.Quotation_Id = qm.quotation_id
                    WHERE qmd.part_no = '{n3}'"""
        db_cursor.execute(sql1)
        data1 = db_cursor.fetchall()
        trv_1.delete(*trv_1.get_children())
        date1 = datetime.strptime(TxtDate_1.get(),'%d-%m-%Y').strftime('%Y-%m-%d')
        gst_per = "SELECT gst_per FROM gst_percentage_table WHERE id = 1"
        db_cursor.execute(gst_per)
        gst_per = db_cursor.fetchone()[0]
        if data1 != []:
            name = data1[0][4]
            cnt1 = 1
            for i in data1:
                sql2 = f"SELECT * FROM quotation_master_details WHERE Quotation_Id = {DATABASE_SYN}"
                db_cursor.execute(sql2, (i[0],))
                data2 = db_cursor.fetchall()
                sample = {}
                if data2 != []:
                    for j in data2:
                        sql3 = f"SELECT * FROM quotation_master_details_machining_details WHERE Quotation_Id = {DATABASE_SYN} AND part_no_id = {DATABASE_SYN} AND date_tr = {DATABASE_SYN}"
                        db_cursor.execute(sql3, (j[0], j[2], j[15]))
                        data3 = db_cursor.fetchall()
                        
                        Company_Name, Company_Address, Company_Contact = Get_Firm_Details()
                        sql_basics = f"SELECT * FROM account_master WHERE party_name = {DATABASE_SYN}"
                        db_cursor.execute(sql_basics, (name,))
                        data_basics = db_cursor.fetchall()

                        items = []
                        subtotal = 0
                        cnt = 1
                        for child in data2:
                            items.append({
                                "no": cnt,
                                "part_desc": child[3],
                                "qty": int(child[4]),
                                "unit_price": float(child[14]),
                                "total_price": float(child[15]),
                                "taxed":""
                            })
                            cnt += 1
                            subtotal += float(child[15])
                        tax_due = round(subtotal*18/100,2)
                        grand_total = subtotal + tax_due
                        
                        sample = {
                            "company": {
                                "name":Company_Name,
                                "address":Company_Address,
                                "phone": Company_Contact
                            },
                            "date": datetime.today().strftime("%d-%m-%Y"),
                            "quote_no": i[0] if n1 == "Quotation" else i[5],
                            "valid_until": (i[2] + timedelta(days=30)).strftime('%d-%m-%Y'),
                            "prepared_by": "Admin",
                            "customer": {
                                "name":name,
                                "company":i[1],
                                "address":data_basics[0][4],
                                "phone":data_basics[0][3]
                            },
                            "items":items,
                            "totals":{"subtotal":subtotal,"taxable":subtotal,"tax_rate":gst_per,"tax_due":tax_due,"other":0,"grand_total":grand_total},
                            "terms":[
                                "1. Customer will be billed after indicating acceptance of this quote",
                                "2. Payment will be due prior to delivery of service and goods",
                                "3. Please fax or mail the signed price quote to the address above"
                            ]
                        }

                trv_1.insert("", 'end', text=str(cnt1), values=(str(i[0]), str(i[4]), str(i[1]), str(i[2].date()), str(i[3]), sample))
                cnt1 += 1

    def Get_Firm_Details():
        sql1 = f"SELECT firm_name, firm_address, firm_contact FROM firm_master where login_id = {DATABASE_SYN}"
        db_cursor.execute(sql1, (login_id,))
        data1 = db_cursor.fetchall()
        return data1[0][0], data1[0][1], data1[0][2]
    
    def show_selected_record(event):
        for selection in trv_1.selection():
            item = trv_1.item(selection)
        i1 = item["values"]
        
        sample = i1[-1]
        msg = messagebox.askyesno("Question","You want to open this quotation ?", parent=tool_master_history)
        if msg:
            n1 = TxtSearch.get().upper()
            create_quotation_pdf(sample, r"D:\\ToolCosting\\Support Documents\\Tool_Quotation.pdf", n1)
            messagebox.showinfo("Info", "Opening your Quotation...Click Ok.", parent=tool_master_history)
            os.startfile(r"D:\\ToolCosting\\Support Documents\\Tool_Quotation.pdf")
        
    def On_Start_tab2():
        sql1 = f"SELECT party_name FROM account_master WHERE login_id = {DATABASE_SYN}"
        db_cursor.execute(sql1, (login_id,))
        data1 = db_cursor.fetchall()
        party_lst = ['Select']
        if db_cursor.rowcount != 0:
            for party_name in data1:
                party_lst.append(party_name[0])
        
            TxtCustomerS['values'] = party_lst
            TxtCustomerS.current(0)
            TxtCustomerS['completevalues']=party_lst
        
        
    tool_master_history = Toplevel(master)
    tool_master_history.title("Quotation Master History")
    tool_master_history.geometry("900x600+300+150")
    
    LblHead = Label(tool_master_history, text='Quotation Master History', font=('Times New Roman', 22, 'bold'), fg='Purple')
    LblHead.place(x=300, y=10)
    
    Frm1 = LabelFrame(tool_master_history, text="")
    Frm1.place(x=15, y=80, width=870, height=120)
    answer = StringVar()
    LblSearch = Label(Frm1, text='Search', font=('Times New Roman', 17))
    LblSearch.place(x=10, y=10)
    TxtSearch = ttk.Combobox(Frm1, width=12, justify='center', values=('Quotation','Invoice'), font=('Times New Roman', 17), state="readonly")
    TxtSearch.place(x=100, y=10)
    TxtSearch.current(0)
    LblSearchBy = Label(Frm1, text='         By', font=('Times New Roman', 17))
    LblSearchBy.place(x=260, y=10)
    TxtSearchBy = ttk.Combobox(Frm1, width=12, justify='center', values=('Quotation No','Part No'), font=('Times New Roman', 17), state="readonly")
    TxtSearchBy.place(x=380, y=10)
    TxtSearchBy.current(0)

    LblCust = Label(Frm1, text="Quotation No :", font=('Times New Roman', 17))
    LblCust.place(x=50, y=60)
    TxtCustomerS = Entry(Frm1, width=26, font=('Times New Roman', 17), justify='center')
    TxtCustomerS.place(x=210, y=60)
    #TxtCustomerS._open_dropdown()

    LblDate = Label(Frm1, text="Date :", font=('Times New Roman', 16))
    LblDate.place(x=650, y=10)
    TxtDate_1 = DateEntry(Frm1, width=10, font=('Times New Roman', 16), borderwidth=2, date_pattern="dd-mm-yyyy")
    TxtDate_1.place(x=720, y=10)

    BtnSearch = Button(Frm1, text='Search', font=('Times New Roman', 14), width=16, bg='green', fg='white', command=Search_Records)
    BtnSearch.place(x=670, y=60)

    scrolly=Scrollbar(tool_master_history , orient=VERTICAL)

    trv_1=ttk.Treeview(tool_master_history , columns=("quot_id" , "cust_name" , "prov_name", "date_tr_quot", "date_tr_invoice") , yscrollcommand=scrolly.set )#, xscrollcommand=scrollx.set
    scrolly.place(x=1070, y=210, height=360)
    scrolly.config(command=trv_1.yview)

    trv_1.heading("quot_id" , text="Quotation no")
    trv_1.heading("cust_name" , text="Customer Name")
    trv_1.heading("prov_name", text="Provider Name")
    trv_1.heading("date_tr_quot" , text="Quotation Date")
    trv_1.heading("date_tr_invoice" , text="Invoice Date")

    #trv_1.heading("Provider" , text="Provider")

    trv_1["show"]="headings"

    trv_1.column("quot_id" , width=70, anchor='center')
    trv_1.column("cust_name" , width=200, anchor='center')
    trv_1.column("prov_name", width=100, anchor='center')
    trv_1.column("date_tr_quot" , width=150, anchor='center')
    trv_1.column("date_tr_invoice" , width=150, anchor='center')

    trv_1.place(x=15, y=260, width=870, height=330)
    trv_1.bind("<Double-1>", show_selected_record)
    # On_Start_tab2()
    
    def f1(event):
        if TxtSearch.get() == 'Quotation':
            TxtSearchBy['values'] = ('Quotation No', 'Part No')
        else:
            TxtSearchBy['values'] = ('Invoice No', 'Part No')
        TxtSearchBy.focus()
        TxtSearchBy.event_generate("<Down>")
    def f2(event):
        n1 = TxtSearchBy.get()
        LblCust['text'] = f'{n1}: '
        TxtCustomerS.focus()

    TxtSearch.bind("<<ComboboxSelected>>", f1)
    TxtSearchBy.bind("<<ComboboxSelected>>", f2)
    tool_master_history.bind("<Escape>", lambda e: tool_master_history.destroy())
    # tool_master_history.mainloop()
    return tool_master_history
    
# Frm_Quot_History(1,1)