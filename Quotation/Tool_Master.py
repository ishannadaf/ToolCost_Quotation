from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from tkinter import simpledialog
from tkcalendar import DateEntry
from tkinter import filedialog
from openpyxl import load_workbook
from Database.connection import *
from pdf2image import convert_from_path
from PIL import Image, ImageTk
import tkinter as tk
from datetime import datetime, timedelta
from Quotation.Quotation_Master_PDF import create_quotation_pdf
import os
import re
import ast
import tkinter
import sys
import fitz


def get_poppler_path():
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, "poppler", "Library", "bin")
    else:
        return os.path.join(os.getcwd(), "poppler", "Library", "bin")


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

class ImageComboBox(tk.Frame):
    def __init__(self, master, items, command=None, width=20, **kwargs):
        super().__init__(master, **kwargs)
        self.items = items
        self.command = command
        self.selected_index = 0

        # ttk style for combobox look
        style = ttk.Style()
        style.configure("Custom.TButton",
                        relief="flat",
                        background="white",
                        anchor="w",
                        borderwidth=1)

        # Frame to mimic combobox field
        self.display_frame = tk.Frame(self, relief="solid", bd=1, bg="white")
        self.display_frame.pack(fill="x")

        # Label for image + text
        self.img_label = tk.Label(self.display_frame, bg="white")
        self.img_label.pack(side="left", padx=5, pady=2)

        self.text_label = tk.Label(self.display_frame, bg="white", anchor="w")
        self.text_label.pack(side="left", pady=2)

        # Arrow icon
        self.arrow_label = tk.Label(self.display_frame, text="▼", bg="white", font=("Arial", 8))
        self.arrow_label.pack(side="right", padx=5)

        # Bind click to dropdown
        self.display_frame.bind("<Button-1>", lambda e: self.show_dropdown())
        self.img_label.bind("<Button-1>", lambda e: self.show_dropdown())
        self.text_label.bind("<Button-1>", lambda e: self.show_dropdown())
        self.arrow_label.bind("<Button-1>", lambda e: self.show_dropdown())

        self.update_display()

    def set(self, value):
        # Find the index of the item with matching text
        for i, (text, img) in enumerate(self.items):
            if text == value:
                self.selected_index = i
                self.update_display()
                return
        raise ValueError(f"Value '{value}' not found in ImageComboBox items")
    def update_display(self):
        text, img = self.items[self.selected_index]
        self.img_label.config(image=img)
        self.text_label.config(text=text, font=("Times New Roman", 14))

    def show_dropdown(self):
        dropdown = tk.Toplevel(self)
        dropdown.wm_overrideredirect(True)
        dropdown.geometry(f"{self.winfo_width()}x{len(self.items)*60}+{self.winfo_rootx()}+{self.winfo_rooty()+self.winfo_height()}")

        for i, (text, img) in enumerate(self.items):
            btn = tk.Button(dropdown,
                            text=" " + text,
                            image=img,
                            compound="left",
                            anchor="w",
                            bg="white",
                            relief="flat",
                            font=('Times New Roman', 14),
                            command=lambda idx=i, win=dropdown: self.select(idx, win))
            btn.pack(fill="x")

    def select(self, index, win):
        self.selected_index = index
        self.update_display()
        if self.command:
            self.command(self.items[index][0])
        win.destroy()
    
    def get(self):
        return self.items[self.selected_index][0]
    
class MachiningList(tk.Frame):
    def __init__(self, master, machines, *args, **kwargs):
        super().__init__(master, *args, **kwargs)

        self.entries = {}  # store references for later (check, entry, etc.)
        lbl_lst = ['Name', 'Lbl. Price', 'Cust. price', 'Unit', 'Hours']
        
        lbl_1 = tk.Label(self, text=lbl_lst[0], font=("Arial", 12))
        lbl_1.grid(row=0, column=0, padx=5, pady=3)

        lbl_2 = tk.Label(self, text=lbl_lst[1], font=("Arial", 12))
        lbl_2.grid(row=0, column=1, padx=5, pady=3)

        lbl_3 = tk.Label(self, text=lbl_lst[2], font=("Arial", 12))
        lbl_3.grid(row=0, column=2, padx=5, pady=3)

        lbl_4 = tk.Label(self, text=lbl_lst[3], font=("Arial", 12))
        lbl_4.grid(row=0, column=3, padx=5, pady=3)
        
        lbl_5 = tk.Label(self, text=lbl_lst[4], font=("Arial", 12))
        lbl_5.grid(row=0, column=3, padx=5, pady=3)
            
        for i, (mid, name, rate, unit) in enumerate(machines):
            var_chk = tk.BooleanVar()
            chk = tk.Checkbutton(self, text=name, variable=var_chk, font=("Arial", 12))
            chk.grid(row=i+1, column=0, sticky="w", padx=5, pady=3)

            lbl_rate = tk.Label(self, text=f"Rs. {rate}", font=("Arial", 12))
            lbl_rate.grid(row=i+1, column=1, padx=5, pady=3)
            
            lbl_rate_cust = tk.Entry(self, width=6, font=("Arial", 12), justify='center')
            lbl_rate_cust.grid(row=i+1, column=2, padx=5, pady=3)
            lbl_rate_cust.delete(0, END)
            lbl_rate_cust.insert(0,str(rate))

            lbl_unit = tk.Label(self, text=unit, font=("Arial", 12))
            lbl_unit.grid(row=i+1, column=3, padx=5, pady=3)
            
            entry_hours = tk.Entry(self, width=6, font=("Arial", 12), justify='center')
            entry_hours.grid(row=i+1, column=4, padx=5, pady=3)
            entry_hours.delete(0, END)
            entry_hours.insert(0, "1")
            # store references
            self.entries[mid] = {
                "check": var_chk,
                "hours_entry": entry_hours,   # store the widget, not its value
                "cust_rate_entry": lbl_rate_cust, 
                "rate": rate,
                "unit": unit,
                "name": name
            }

    def get_selected(self):
        """Return selected machines with qty/time and cost"""
        result = []
        for mid, widgets in self.entries.items():
            if widgets["check"].get():
                result.append({
                    "id": mid,
                    "name": widgets["name"],
                    "rate": widgets["rate"],
                    "cust_rate": widgets["cust_rate_entry"].get(),   # fetch live value
                    "unit": widgets["unit"],
                    "hours": widgets["hours_entry"].get()            # fetch live value
                })
        return result
    
def open_term_condition():
    global open_windows

    key = "term_condition"

    if key in open_windows:
        win = open_windows[key]
        if win.winfo_exists():
            win.lift()
            win.focus_force()
            return

    win = Toplevel()
    win.title("Terms & Conditions")

    open_windows[key] = win

    def on_close():
        if key in open_windows:
            del open_windows[key]
        win.destroy()

    win.protocol("WM_DELETE_WINDOW", on_close)


rules_page = None

def Frm_Tool_Master(master, login_id):
    def enable_esc_close(window):
        #print(window)
        def _close(event=None):
            window.grab_release()
            window.destroy()
            return "break"   # ⛔ STOP event propagation
        window.bind("<Escape>", _close)
    #============================================================================================
    #                           Quotation Form
    #============================================================================================
    def Frm_Quotation_Master(master, input_data, customer, provider, login_id):
        data_update = None
        machining_list_update_master = None
        if len(input_data)>6 and isinstance(input_data[6], str):
            data_update = ast.literal_eval(input_data[6])
      
        def preset_data(data_update):
            global machining_list_update_master
            if data_update['material']:
                material = data_update['material']
                unit_measurement = data_update['unit_measurement']
                shape = data_update['shape']
                width = data_update['width']
                length = data_update['length']
                thickness = data_update['thickness']
                unit_weight = data_update['unit_weight']
                unit_price = data_update['unit_price']
                rmc = data_update['rmc']
                profit_per = data_update['profit_per']
                scrab_per = data_update['scrab_per']
                machining_lst = data_update['machining_lst']
                machining_list_update_master = machining_lst
                TxtMaterial.set(material)
                TxtUnit.set(unit_measurement)
                TxtShape.set(shape)
                
                TxtWidth.delete(0, END)
                TxtLength.delete(0, END)
                TxtThickNess.delete(0, END)
                TxtProfit.delete(0, END)
                
                LblUnitWeight.place(x=150, y=5)
                TxtUnitWeight.place(x=140, y=30)
                LblRMC.place(x=450, y=5)
                TxtRMC.place(x=440, y=30)
                LblWeld.place_forget()
                TxtWeld.place_forget()
                LblSRST.place_forget()
                TxtSRST.place_forget()
                
                TxtWidth['state'] = 'normal'
                TxtLength['state'] = 'normal'
                TxtThickNess['state'] = 'normal'
                LblLength['text'] = 'Length'
                
                val = TxtShape.get()
                if val == "Rectangle":
                    TxtWidth['state'] = 'normal'
                    TxtLength['state'] = 'normal'
                    TxtThickNess['state'] = 'normal'
                    LblThickNess['text'] = 'Thickness'
                    LblLength['text'] = 'Length'
                elif val == 'Hexagon':
                    TxtWidth['state'] = 'disabled'
                    TxtLength['state'] = 'normal'
                    TxtThickNess['state'] = 'normal'
                    LblThickNess['text'] = 'Flat'
                elif val == 'Circle':
                    TxtWidth['state'] = 'disabled'
                    TxtLength['state'] = 'normal'
                    TxtThickNess['state'] = 'normal'
                    LblThickNess['text'] = 'Diameter'
                    LblLength['text'] = 'Length'
                elif val == 'Fabrication':
                    TxtWidth['state'] = 'disabled'
                    TxtLength['state'] = 'normal'
                    TxtThickNess['state'] = 'disabled'
                    LblLength['text'] = 'Fab. Weight'
                    
                    LblUnitWeight.place(x=330, y=5)
                    TxtUnitWeight.place(x=320, y=30)
                    
                    LblRMC.place(x=550, y=5)
                    TxtRMC.place(x=540, y=30)
                    
                    LblWeld.place(x=50, y=5)
                    TxtWeld.place(x=40, y=30)
                    
                    LblSRST.place(x=180, y=5)
                    TxtSRST.place(x=170, y=30)
                    
                    TxtWeld.delete(0, END)
                    TxtSRST.delete(0, END)
                    
                    TxtWeld.insert(0, thickness)
                    TxtSRST.insert(0, width)
                
                try:
                    TxtWidth.insert(0, width)
                except:
                    pass
                try:
                    TxtLength.insert(0, length)
                except:
                    pass
                try:
                    TxtThickNess.insert(0, thickness)
                except:
                    pass
                
                TxtProfit.delete(0, END)
                TxtProfit.insert(0, str(profit_per))
                TxtScrabPer.delete(0, END)
                TxtScrabPer.insert(0, str(scrab_per))
                TxtUnitWeight['text'] = str(unit_weight)
                LblTotalToolCost['text'] = str(unit_price) + ' Rs.'
                TxtRMC['text'] = rmc
                cnt = 1
                total_sum = 0
                s1 = ''
                # s2 = ''
                
                s11 = ''
                for key, item in machining_lst.items():
                    if cnt == 3:
                        s1 += '\n'
                        s11 += '\n'
                        cnt = 1
                    if cnt == 2:
                        s1 += "\t"
                        s11 += "\t"
                    sum1 = round(float(item.get("cust_rate"))*float(item.get("total_hr")), 2)
                    total_sum += sum1
                    s1 += key + ' : ' + str(sum1) + ' rs.'
                    s11 += key + ' : ' + str(sum1) + ' rs.' + ',' + str(item.get("total_hr")) + ',' + str(item.get("cust_rate"))
                    cnt += 1
                s2.set(s11)
                # s3 = s1.split(',')[0]
                ListMachiningCost['text'] = s1
                ListMachiningCostTotal['text'] = 'Total Cost\n'+str(total_sum)+' Rs.'
                f1_function()

            else:
                material = TxtMaterial.current(0)
                unit_measurement = TxtUnit.current(0)
            
        def Get_Raw_Cost(name):
            
            sql1 = f"""SELECT price FROM raw_cost WHERE name = {DATABASE_SYN} AND cust_id IN ('{var_cust_id.get()}', 0) ORDER BY 
                        CASE 
                            WHEN cust_id = '{var_cust_id.get()}' THEN 1
                            ELSE 2
                        END
                        LIMIT 1"""
            db_cursor.execute(sql1,(name,))
            data1 = db_cursor.fetchall()
            if data1 != []:
                return data1[0][0]
            else:
                return 0
            
        def get_machines_from_db():
            
            sql1 = f"""SELECT 
                        g.id,
                        g.name,
                        COALESCE(c.price, g.price) AS rate,
                        COALESCE(c.cust_id, g.cust_id) AS cust_id
                    FROM machining_master g
                    LEFT JOIN machining_master c
                        ON g.name = c.name
                        AND c.cust_id = '{var_cust_id.get()}'
                    WHERE g.cust_id = 0;"""
            
            db_cursor.execute(sql1)
            data1 = db_cursor.fetchall()
            lst_machining = []
            if db_cursor.rowcount != 0:
                cnt = 1
                for i in data1:
                    lst_machining.append([i[0], i[1], i[2], 'Hr'])
                    cnt += 1
            
            return lst_machining

        def add_machining_cost():
            
            root = Toplevel(quotation_master)
            root.title("Machining Details")
            root.grab_set()
            machines = get_machines_from_db()
            machining_list = MachiningList(root, machines)
            machining_list.pack(padx=10, pady=10)
            
            text_value = s2.get()
            
            entries = re.split(r'[\t\n]+', text_value)

            names_in_text = set()
            for entry in entries:
                entry = entry.strip()
                if not entry:
                    continue

                parts = entry.split(',')

                main_part = parts[0].strip()

                hours = parts[1].strip() if len(parts) > 1 else "0"
                cust_rate = parts[2].strip() if len(parts) > 2 else "0"

                # Extract name
                name = main_part.split(':', 1)[0].strip()

                if name:
                    for mid, widgets in machining_list.entries.items():
                        if widgets["name"].lower() == name.lower():
                            widgets["check"].set(True)

                            # Set hours
                            widgets["hours_entry"].delete(0, "end")
                            widgets["hours_entry"].insert(0, hours)

                            # Set customer rate (if you have separate entry box)
                            widgets["cust_rate_entry"].delete(0, "end")
                            widgets["cust_rate_entry"].insert(0, cust_rate)

            def submit():
                global selected_machining_list
                selected_machining_list = machining_list.get_selected()
                s1 = ""
                cnt = 1
                total_sum = 0
                for item in selected_machining_list:
                    if cnt == 3:
                        s1 += '\n'
                        cnt = 1
                    if cnt == 2:
                        s1 += "\t"
                    sum1 = round(float(item.get("cust_rate"))*float(item.get("hours")), 2)
                    total_sum += sum1 
                    s1 += item.get("name") + ' : ' + str(sum1) + ' rs.'
                    cnt += 1
                ListMachiningCost['text'] = s1
                ListMachiningCostTotal['text'] = 'Total Cost\n'+str(total_sum)+' Rs.'
                root.destroy()
            BtnSubmit = tk.Button(root, text="Submit", font=('Times New Roman', 12), width=12, bg='green', fg='white', command=submit)
            BtnSubmit.pack(pady=10)
            
            enable_esc_close(root)
            return root
            # root.mainloop()
        
        def open_pdf():
            file_path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")], parent=quotation_master)
            if not file_path:
                return

            doc = fitz.open(file_path)
            
            # pages = convert_from_path(pdf_path, dpi=150, first_page=1, last_page=1, poppler_path=poppler_path)
            # pdf_image = pages[0]
            pdf_image = doc.load_page(0)
            pix = pdf_image.get_pixmap(matrix=fitz.Matrix(1.5, 1.5))
            # pdf_image.thumbnail((300, 500), Image.Resampling.LANCZOS)
            # img_tk = ImageTk.PhotoImage(pdf_image)
            # preview_label.config(image=img_tk)
            # preview_label.image = img_tk
            
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            img.thumbnail((300, 500), Image.Resampling.LANCZOS)
            full_img.set(file_path)
            img_tk = ImageTk.PhotoImage(img)
            preview_label.config(image=img_tk)
            preview_label.image = img_tk
            
            sql1 = f"UPDATE account_master SET pdf_path = '{file_path}' where party_name = '{TxtCustomer.get()}'"
            db_cursor.execute(sql1)
            db_connection.commit()
            
        
        def clear_data_Quo():
            TxtNo.delete(0, END)
            TxtPartNo.delete(0, END)
            TxtPartDesc.delete(0, END)
        
        def On_Start_Quo():
            TxtCustomer.insert(0, customer)
            TxtProv.insert(0, provider)
            
            sql1 = "SELECT ID FROM account_master WHERE party_name = %s and login_id = %s"
            db_cursor.execute(sql1, (customer, login_id))
            data1 = db_cursor.fetchall()
            var_cust_id.set(data1[0][0])
            
            clear_data_Quo()
            TxtNo.insert(0, input_data[0])
            TxtPartNo.insert(0, input_data[1])
            TxtPartDesc.insert(0, input_data[2])
            
            TxtNo['state'] = 'disabled'
            TxtPartNo['state'] = 'disabled'
            TxtPartDesc['state'] = 'disabled'
            
            sql1 = f"""
            SELECT 
                    g.name
                FROM material_master g
                LEFT JOIN material_master c
                    ON g.name = c.name
                    AND c.cust_id = '{var_cust_id.get()}'
                    AND c.login_id = {DATABASE_SYN}
                WHERE g.login_id = {DATABASE_SYN}
                AND g.cust_id = 0;
            
            """
            #sql1 = f"SELECT name FROM material_master WHERE login_id = {DATABASE_SYN} and cust_id = '{var_cust_id.get()}'"
            db_cursor.execute(sql1, (login_id, login_id))
            data1 = db_cursor.fetchall()
            if db_cursor.rowcount != 0:
                lst_material = []
                for i in data1:
                    lst_material.append(i[0])
                TxtMaterial['values'] = lst_material
                TxtMaterial.current(0)
            #Get_Raw_Cost(TxtMaterial.get())
            # if len(input_data) > 6:
            #     TxtMaterial.set()
            rawAmt = Get_Raw_Cost(TxtMaterial.get())
            TxtScrabCost['text'] = str(rawAmt) + ' Rs.'
            TxtCustomer['state'] = "readonly"
            TxtProv["state"] = "readonly"
            
            sql_pdf_path = f"SELECT pdf_path FROM account_master WHERE id = {DATABASE_SYN}"
            db_cursor.execute(sql_pdf_path, (var_cust_id.get(),))
            data_pdf_path = db_cursor.fetchall()
            pdf_path = None
            if data_pdf_path != [] and data_pdf_path[0][0] is not None:
                pdf_path = data_pdf_path[0][0]
            
            if pdf_path:
                try:
                    # poppler_path = get_poppler_path()
                    doc = fitz.open(pdf_path)
                    
                    # pages = convert_from_path(pdf_path, dpi=150, first_page=1, last_page=1, poppler_path=poppler_path)
                    # pdf_image = pages[0]
                    pdf_image = doc.load_page(0)
                    pix = pdf_image.get_pixmap(matrix=fitz.Matrix(1.5, 1.5))
                    
                    # pdf_image.thumbnail((300, 500), Image.Resampling.LANCZOS)
                    # img_tk = ImageTk.PhotoImage(pdf_image)
                    # preview_label.config(image=img_tk)
                    # preview_label.image = img_tk
                    
                    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                    img.thumbnail((300, 500), Image.Resampling.LANCZOS)
                    full_img.set(pdf_path)
                    img_tk = ImageTk.PhotoImage(img)
                    preview_label.config(image=img_tk)
                    preview_label.image = img_tk
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to load PDF preview: {str(e)}", parent=quotation_master)
                # else:
                #     messagebox.showwarning("Warning", "PDF path exists in database but file not found.", parent=quotation_master)
            
            sql_per_profit = f"SELECT profit_per, scrab_per FROM profit_percentage_master WHERE cust_id = '{var_cust_id.get()}'"
            db_cursor.execute(sql_per_profit)
            data_per_profit = db_cursor.fetchall()
            TxtProfit.delete(0, END)
            TxtScrabPer.delete(0, END)
            if data_per_profit != []:
                TxtProfit.insert(0, str(data_per_profit[0][0]))
                TxtScrabPer.insert(0, str(data_per_profit[0][1]))
            
        def validate_number(P):
            if P == "": 
                return True
            try:
                float(P)
                return True
            except ValueError:
                return False
        
        
        
        def CalculateTotalCost():
            if TxtScrabPer.get() != '':
                if TxtProfit.get() != '':
                    BtnSaveAndCalculate['state'] = 'normal'
                    weight = float(TxtUnitWeight['text'].split(' ')[0])
                    rmc_amt = float(TxtRMC['text'])
                    try:
                        TxtMachiningCost = float(ListMachiningCostTotal['text'].split()[2])
                    except:
                        TxtMachiningCost = 0.0
                    total_cost = round(rmc_amt+TxtMachiningCost, 2)
                    #raw_amt = Get_Raw_Cost(TxtMaterial.get())
                    raw_cost = float(TxtScrabTotal['text'].split(' ')[0])
                    profit_per = TxtProfit.get()
                    var_percentage.set(profit_per)
                    total_cost = round(total_cost - raw_cost, 2)
                    total_cost = round(total_cost + total_cost*float(profit_per) / 100)
                    LblTotalToolCost['text'] = str(total_cost) + ' Rs.'
                else:
                    messagebox.showerror("Error", "Please enter Profit %.", parent=quotation_master)
                    TxtProfit.focus()
            else:
                messagebox.showerror("Error", "Please enter scrap %.", parent=quotation_master)
                TxtScrabPer.focus()
                
        def Save_Changed_Unit_Price():
            global selected_machining_list
            selected_item = trv.focus()
            unit_price = float(LblTotalToolCost['text'].split()[0])
            machining_lst = {}
            
            if selected_machining_list:
                for item in selected_machining_list:
                    machining_lst[item['name']] = {
                        "machining_name" : item['name'],
                        "lbl_rate": item['rate'],
                        "cust_rate": item['cust_rate'],
                        "total_hr": item['hours'],
                    }
            elif data_update and (data_update['machining_lst']):
                # print(data_update['machining_lst'])
                for name, item in data_update['machining_lst'].items():
                    machining_lst[name] = {
                        "machining_name": item['machining_name'],
                        "lbl_rate": item['lbl_rate'],
                        "cust_rate": item['cust_rate'],
                        "total_hr": item['total_hr'],
                    }
            data1 = {
                "material" : TxtMaterial.get(),
                "unit_measurement" : TxtUnit.get(),
                "shape" : TxtShape.get(),
                "width" : TxtWidth.get() if TxtShape.get() != 'Fabrication' else TxtSRST.get(),
                "length" : TxtLength.get(),
                "thickness" : TxtThickNess.get() if TxtShape.get() != 'Fabrication' else TxtWeld.get(),
                "unit_weight" : TxtUnitWeight['text'].split(' ')[0],
                "unit_price" : unit_price,
                "rmc" : TxtRMC["text"],
                "profit_per" : TxtProfit.get(),
                "scrab_per" : TxtScrabPer.get(),
                "machining_lst" : machining_lst
            }
            new_values = [input_data[0], input_data[1], input_data[2], input_data[3], str(unit_price), str(round(float(unit_price*int(input_data[3])),2)), data1]
            trv.item(selected_item, values=new_values)
            
            selected_machining_list = None
            var_cust_id.set('')
            s2.set('')
            quotation_master.destroy()
            
        def check_shape(val):
            TxtWidth.delete(0, END)
            TxtLength.delete(0, END)
            TxtThickNess.delete(0, END)
            LblTotalToolCost['text'] = '0.0'
            ListMachiningCost['text'] = ''
            TxtRMC['text'] = '0.0'
            TxtUnitWeight['text'] = '0.0'
            ListMachiningCostTotal['text'] = 'Total Cost'
            
            LblUnitWeight.place(x=150, y=5)
            TxtUnitWeight.place(x=140, y=30)
            LblRMC.place(x=450, y=5)
            TxtRMC.place(x=440, y=30)
            LblWeld.place_forget()
            TxtWeld.place_forget()
            LblSRST.place_forget()
            TxtSRST.place_forget()
            
            if val == "Rectangle":
                TxtWidth['state'] = 'normal'
                TxtLength['state'] = 'normal'
                TxtThickNess['state'] = 'normal'
                LblThickNess['text'] = 'Thickness'
                LblLength['text'] = 'Length'
            if val == 'Hexagon':
                TxtWidth['state'] = 'disabled'
                TxtLength['state'] = 'normal'
                TxtThickNess['state'] = 'normal'
                LblThickNess['text'] = 'Flat'
            if val == 'Circle':
                TxtWidth['state'] = 'disabled'
                TxtLength['state'] = 'normal'
                TxtThickNess['state'] = 'normal'
                LblThickNess['text'] = 'Diameter'
                LblLength['text'] = 'Length'
            if val == 'Fabrication':
                TxtWidth['state'] = 'disabled'
                TxtLength['state'] = 'normal'
                TxtThickNess['state'] = 'disabled'
                LblLength['text'] = 'Fab. Weight'
                
                LblUnitWeight.place(x=330, y=5)
                TxtUnitWeight.place(x=320, y=30)
                
                LblRMC.place(x=550, y=5)
                TxtRMC.place(x=540, y=30)
                
                LblWeld.place(x=50, y=5)
                TxtWeld.place(x=40, y=30)
                
                LblSRST.place(x=180, y=5)
                TxtSRST.place(x=170, y=30)

        quotation_master = Toplevel(tool_master)
        quotation_master.title("Quotation Master")
        quotation_master.geometry("1100x750+175+20")
        quotation_master.grab_set()
        
        global selected_machining_list
        selected_machining_list = None
        vcmd = (quotation_master.register(validate_number), "%P")
        LblHead = Label(quotation_master, text="Quotation Master", font=('Times New Roman', 20, 'bold'))
        LblHead.place(x=470, y=10)
        
        Frm1 = LabelFrame(quotation_master, text="")
        Frm1.place(x=15, y=70, width=1070, height=60)
        
        Frm2 = LabelFrame(quotation_master, text="")
        Frm2.place(x=15, y=140, width=700, height=200)
        Frm3 = LabelFrame(quotation_master, text="")
        Frm3.place(x=725, y=140, width=360, height=410)
        Frm4 = LabelFrame(quotation_master, text="Material Sizes")
        Frm4.place(x=15, y=350, width=700, height=200)
        
        btn_open = tk.Button(Frm3, text="Open PDF", command=open_pdf)
        btn_open.place(x=20, y=5)
        preview_label = tk.Label(Frm3)
        preview_label.place(x=20, y=30)
        
        Frm5 = LabelFrame(Frm4, text="")
        Frm5.place(x=10, y=85, width=680, height=70)
        
        Frm6 = LabelFrame(quotation_master, text="Machining Cost")
        Frm6.place(x=15, y=560, width=630, height=120)
        
        Frm8 = LabelFrame(quotation_master, text="Scrap Percentage")
        Frm8.place(x=655, y=560, width=210, height=120)
        
        Frm9 = LabelFrame(quotation_master, text="Profit %")
        Frm9.place(x=875, y=560, width=210, height=55)
        
        LblProfit = Label(Frm9, text='Profit (%)', font=('Times New Roman', 12))
        LblProfit.grid(column=0, row=0, padx=10)#place(x=10, y=5)
        TxtProfit = Entry(Frm9, validate="key", font=('Times New Roman', 12), validatecommand=vcmd, width=8, justify='center')
        TxtProfit.grid(column=1, row=0, padx=10)#place(x=)
        
        Frm7 = LabelFrame(quotation_master, text="Final Amount")
        Frm7.place(x=875, y=625, width=210, height=55)
        
        LblTotalToolCost = Label(Frm7, text='0.0', font=('Times New Roman', 20, 'bold'))
        LblTotalToolCost.pack()#place(x=30, y=20)
        
        LblCust = Label(Frm1, text="Customer Name :", font=('Times New Roman', 14))
        LblCust.place(x=20, y=10)
        TxtCustomer = Entry(Frm1, width=30, font=('Times New Roman', 14), justify='center')
        TxtCustomer.place(x=160, y=10)
        
        LblProv = Label(Frm1, text="Provider :", font=('Times New Roman', 14))
        LblProv.place(x=480, y=10)
        TxtProv = Entry(Frm1, width=20, font=('Times New Roman', 14), justify='center')
        TxtProv.place(x=570, y=10)
        
        LblDate = Label(Frm1, text="Date :", font=('Times New Roman', 14))
        LblDate.place(x=860, y=10)
        TxtDate = DateEntry(Frm1, width=12, font=('Times New Roman', 14), borderwidth=2, date_pattern="dd-mm-yyyy", state="readonly")
        TxtDate.place(x=920, y=10)
        
        LblNo = Label(Frm2, text='No.', font=('Times New Roman', 16))
        LblNo.place(x=10, y=5)
        TxtNo = Entry(Frm2, font=('Times New Roman', 16), width=8, justify='center')
        TxtNo.place(x=10, y=50)
        
        LblPartNo = Label(Frm2, text='Part Number', font=('Times New Roman', 16))
        LblPartNo.place(x=140, y=5)
        TxtPartNo = Entry(Frm2, font=('Times New Roman', 16), width=14, justify='center')
        TxtPartNo.place(x=140, y=50)
        
        LblPartDesc = Label(Frm2, text='Part Description', font=('Times New Roman', 16))
        LblPartDesc.place(x=330, y=5)
        TxtPartDesc = Entry(Frm2, font=('Times New Roman', 16), width=32, justify='center')
        TxtPartDesc.place(x=330, y=50)
        
        LblMaterial = Label(Frm2, text='Select Material', font=('Times New Roman', 16))
        LblMaterial.place(x=10, y=95)
        TxtMaterial = ttk.Combobox(Frm2, font=('Times New Roman', 16), state='readonly', width=15, justify='center')
        TxtMaterial.place(x=10, y=140)
        
        LblUnit = Label(Frm2, text='Unit of Measure', font=('Times New Roman', 16))
        LblUnit.place(x=240, y=95)
        TxtUnit = ttk.Combobox(Frm2, font=('Times New Roman', 16), state='readonly', values=('mm', 'cm', 'inch'), justify='center', width=15)
        TxtUnit.place(x=240, y=140)
        TxtUnit.current(0)
        
        
        rect_img = ImageTk.PhotoImage(Image.open(r"D:\\ToolCosting\\Images\\\\rectangle.png").resize((50, 20), Image.Resampling.LANCZOS))
        circle_img = ImageTk.PhotoImage(Image.open(r"D:\\ToolCosting\\Images\\circle.png").resize((50, 20), Image.Resampling.LANCZOS))
        tri_img = ImageTk.PhotoImage(Image.open(r"D:\\ToolCosting\\Images\\hexagon.png").resize((50, 20), Image.Resampling.LANCZOS))
        fabrication_img = ImageTk.PhotoImage(Image.open(r"D:\\ToolCosting\\Images\\hexagon.png").resize((50, 20), Image.Resampling.LANCZOS))
        items = [
            ("Rectangle", rect_img),
            ("Circle", circle_img),
            ("Hexagon", tri_img),
            ("Fabrication", fabrication_img)
        ]
        
        LblShape = Label(Frm2, text='Select Shape', font=('Times New Roman', 16))
        LblShape.place(x=470, y=95)
        TxtShape = ImageComboBox(Frm2, items, command=lambda val: check_shape(val))
        TxtShape.place(x=460, y=140)

        LblThickNess = Label(Frm4, text='Thickness', font=('Times New Roman', 16))
        LblThickNess.place(x=10, y=5)
        TxtThickNess = Entry(Frm4, validate="key", validatecommand=vcmd, font=('Times New Roman', 16), width=16, justify='center')
        TxtThickNess.place(x=10, y=40)
        
        LblWidth = Label(Frm4, text='Width', font=('Times New Roman', 16))
        LblWidth.place(x=230, y=5)
        TxtWidth = Entry(Frm4, validate="key", validatecommand=vcmd, font=('Times New Roman', 16), width=16, justify='center')
        TxtWidth.place(x=230, y=40)
        
        LblLength = Label(Frm4, text='Length', font=('Times New Roman', 16))
        LblLength.place(x=450, y=5)
        TxtLength = Entry(Frm4, validate="key", validatecommand=vcmd, font=('Times New Roman', 16), width=16, justify='center')
        TxtLength.place(x=450, y=40)
        
        LblWeld = Label(Frm5, text='Welding', font=('Times New Roman', 14))
        TxtWeld = Entry(Frm5, width=8, font=('Times New Roman', 18), justify='center')
        
        LblSRST = Label(Frm5, text='SRST', font=('Times New Roman', 14))
        TxtSRST = Entry(Frm5, width=8, font=('Times New Roman', 18), justify='center')
        
                
        LblUnitWeight = Label(Frm5, text='Unit Weight', font=('Times New Roman', 14))
        LblUnitWeight.place(x=150, y=5)
        TxtUnitWeight = Label(Frm5, text='0.00 Kgs', font=('Times New Roman', 18))
        TxtUnitWeight.place(x=140, y=30)
        
        LblRMC = Label(Frm5, text='RMC', font=('Times New Roman', 14))
        LblRMC.place(x=450, y=5)
        TxtRMC = Label(Frm5, text='0.0', font=('Times New Roman', 18))
        TxtRMC.place(x=440, y=30)
        
        BtnAddMachining = Button(Frm6, text='Add \nMachining', font=('Times New Roman', 10), height=3, width=14, bg='green', fg='white', command=add_machining_cost)
        BtnAddMachining.place(x=10, y=10)
        
        ListMachiningCost = Label(Frm6, text='', font=('Times New Roman', 12))
        ListMachiningCost.place(x=130, y=10)
        
        LblScrabCost = Label(Frm8, text='Scrap Rate : ', font=('Times New Roman', 12))
        LblScrabCost.place(x=10, y=5)
        TxtScrabCost = Label(Frm8, text='50 Rs.', font=('Times New Roman', 12, 'bold'))
        TxtScrabCost.place(x=100, y=5)
        
        LblScrabPer = Label(Frm8, text='Scrap % : ', font=('Times New Roman', 12))
        LblScrabPer.place(x=10, y=35)
        TxtScrabPer = Entry(Frm8, font=('Times New Roman', 12, 'bold'), width=6, justify='center')
        TxtScrabPer.place(x=100, y=35)
        
        LblScrabTotal = Label(Frm8, text='Total : ', font=('Times New Roman', 12))
        LblScrabTotal.place(x=10, y=70)
        TxtScrabTotal = Label(Frm8, text = '0.0 Rs.', font=('Times New Roman', 13, 'bold'), width=8)
        TxtScrabTotal.place(x=100, y=70)
        
        
        ListMachiningCostTotal = Label(Frm6, text='Total Cost', font=('Times New Roman', 12, 'bold'))
        ListMachiningCostTotal.place(x=510, y=20)
        
        BtnPrevious = Button(quotation_master, text='<- Previous', font=('Times New Roman', 12), width=12, bg='green', fg='white', command=quotation_master.destroy)
        BtnPrevious.place(x=15, y=690)
        
        # BtnReset = Button(quotation_master, text='Reset', font=('Times New Roman', 12), width=12, bg='red', fg='white', command=Reset_Form)
        # BtnReset.place(x=430, y=680)
        BtnCalculate = Button(quotation_master, text='Calculate', font=('Times New Roman', 12), width=18, bg='green', fg='white', command=CalculateTotalCost)
        BtnCalculate.place(x=450, y=690)
        
        BtnSaveAndCalculate = Button(quotation_master, state='disabled', text='Save & Continue', font=('Times New Roman', 14), bg='green', fg='white', width=30, command=Save_Changed_Unit_Price)
        BtnSaveAndCalculate.place(x=740, y=690)
        
        def f1_function():
            if TxtScrabPer.get() == '':
                scrab_per = 0
            else:
                scrab_per = float(TxtScrabPer.get())
            width = TxtWidth.get() or '0'
            length = TxtLength.get() or '0'
            thickness = TxtThickNess.get() or '0'
            
            material = TxtMaterial.get()
            
            TxtScrabCost['text'] = str(Get_Raw_Cost(material)) + ' Rs.'
            
            sql1 = f"""SELECT 
                        COALESCE(c.density, g.density) AS density,
                        COALESCE(c.rate, g.rate) AS rate
                    FROM material_master g
                    LEFT JOIN material_master c
                        ON g.name = c.name
                        AND c.cust_id = '{var_cust_id.get()}'
                        AND c.login_id = {DATABASE_SYN}
                    WHERE g.login_id = {DATABASE_SYN}
                    AND g.name = '{material}'
                    AND g.cust_id = 0
                    LIMIT 1;"""
            db_cursor.execute(sql1,(login_id, login_id))
            density_rate = db_cursor.fetchall()
            shape = TxtShape.get()
            conversion_factor = TxtUnit.get()

            if conversion_factor == 'mm':
                width = float(width)
                length = float(length)
                thickness = float(thickness)
            if conversion_factor == 'cm':
                width = float(width) * 10
                length = float(length) * 10
                thickness = float(thickness) * 10
            if conversion_factor == 'inch':
                width = float(width) * 25.4
                length = float(length) * 25.4
                thickness = float(thickness) * 25.4
            flag = False
            if shape == 'Rectangle':
                volume = ((float(width) * float(length) * float(thickness)* float(density_rate[0][0]))/1000000000)
                flag = True
            if shape == 'Hexagon':
                volume = (2.598076 * (float(thickness)/1.73205)**2 * float(length) * float(density_rate[0][0])/1000000000)
                flag = True
            if shape == 'Circle':
                volume = (3.141592 * (float(thickness)**2)/4 * float(length) * float(density_rate[0][0])/1000000000)
                flag = True
            if shape == 'Fabrication':
                volume = round((float(length)), 1)
                #TxtLength.delete(0, END)
                #TxtLength.insert(0, str(volume))
                flag = True
            if flag:
                unit_weight = round(volume, 1)
                TxtUnitWeight['text'] = str(unit_weight) + '  Kgs'
                if shape == 'Fabrication':
                    try:
                        weld = float(TxtWeld.get())
                        srst = float(TxtSRST.get())
                    except:
                        weld = 0
                        srst = 0
                    if weld and srst:
                        TxtRMC['text'] = round((volume * float(density_rate[0][1])) + (weld * float(length)) + (srst * float(length)), 1)
                else:
                    TxtRMC['text'] = round(volume * float(density_rate[0][1]), 1)

                weight = float(TxtUnitWeight['text'].split(' ')[0])
                scrab_cost = float(TxtScrabCost['text'].split(' ')[0])
                scrab = TxtScrabPer.get()
                # if scrab_cost == 0.0:
                #     TxtScrabPer.delete(0, END)
                #     TxtScrabPer.insert(0, '0')
                #     scrab = 0
                # if scrab == 0:
                #     scrab = 0
                scrab_amt = round(scrab_per * weight * scrab_cost/100, 2)
                
                TxtScrabTotal['text'] = str(scrab_amt) + ' Rs.'

            else:
                TxtUnitWeight['text'] = str(0.0) + '  Kgs'
                volume = 0
                TxtRMC['text'] = round(volume * float(density_rate[0][1]), 1)
                TxtScrabTotal['text'] = '0.0 Rs.'

        
        
        def f1(event):
            f1_function()
            
        def f22(event):
            TxtLength.delete(0, END)
            TxtWidth.delete(0, END)
            TxtThickNess.delete(0, END)
            LblTotalToolCost['text'] = ''
            ListMachiningCost['text'] = ''
            ListMachiningCostTotal['text'] = ''
        
        def f11(event):
            TxtLength.focus()
        
        def f12(event):
            TxtThickNess.focus()
        
        def f111(evevnt):
            # profit = 
            scrab_cost = float(TxtScrabCost['text'].split(' ')[0])
            scrab = TxtScrabPer.get()
            if scrab == '':
                scrab = 1
            if scrab_cost == 0.0:
                TxtScrabPer.delete(0, END)
                TxtScrabPer.insert(0, '0')
                scrab = 0
            if scrab == 0:
                scrab = 1
            scrab_per = float(scrab)
            weight = float(TxtUnitWeight['text'].split(' ')[0])
            scrab_amt = round(scrab_per * weight * scrab_cost/100, 2)
            
            TxtScrabTotal['text'] = str(scrab_amt) + ' Rs.'
        
        def f13(event):
            TxtWidth.focus()
        
        def open_image_window(pdf_path):
            if not pdf_path:
                messagebox.showwarning("Warning", "No PDF available for preview.", parent=quotation_master)
                return

            try:
                os.startfile(pdf_path)  # Open PDF with default viewer
                # doc = fitz.open(pdf_path)
                # page = doc.load_page(0)
                # pix = page.get_pixmap(matrix=fitz.Matrix(1.3,1.3))

                # img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

                # # 🔥 Create window
                # img_window = Toplevel(quotation_master)
                # img_window.title("PDF Preview")
                # img_window.geometry("900x700")  # fixed window size (important)

                # # 🔥 Canvas
                # canvas = tk.Canvas(img_window)
                # canvas.pack(side="left", fill="both", expand=True)

                # # 🔥 Scrollbars
                # v_scroll = tk.Scrollbar(img_window, orient="vertical", command=canvas.yview)
                # v_scroll.pack(side="right", fill="y")

                # h_scroll = tk.Scrollbar(img_window, orient="horizontal", command=canvas.xview)
                # h_scroll.pack(side="bottom", fill="x")

                # canvas.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)

                # # 🔥 Image
                # img_tk = ImageTk.PhotoImage(img)
                # canvas.create_image(0, 0, anchor="nw", image=img_tk)
                # canvas.image = img_tk  # prevent garbage collection

                # # 🔥 Scroll region
                # canvas.config(scrollregion=canvas.bbox("all"))

                # # 🔥 Mouse drag (move image)
                # def on_click(event):
                #     canvas.scan_mark(event.x, event.y)

                # def on_drag(event):
                #     canvas.scan_dragto(event.x, event.y, gain=1)

                # canvas.bind("<ButtonPress-1>", on_click)
                # canvas.bind("<B1-Motion>", on_drag)

                # # 🔥 Mouse wheel scroll
                # canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))

                # enable_esc_close(img_window)

            except Exception as e:
                messagebox.showerror("Error", f"Failed to open PDF preview: {str(e)}", parent=quotation_master)
        full_img = StringVar()
        TxtWidth.bind('<KeyRelease>', f1)
        TxtLength.bind('<KeyRelease>',f1)
        TxtThickNess.bind('<KeyRelease>',f1)
        TxtWeld.bind('<KeyRelease>',f1)
        TxtSRST.bind('<KeyRelease>',f1)
        TxtThickNess.bind('<Return>',f13)
        TxtWidth.bind('<Return>', f11)

        TxtMaterial.bind('<<ComboboxSelected>>', f1)
        TxtUnit.bind('<<ComboboxSelected>>',f1)
        TxtScrabPer.bind('<KeyRelease>', f111)
        preview_label.bind('<Button-1>', lambda e: open_image_window(full_img.get()))
        
        On_Start_Quo()
        if data_update:
            preset_data(data_update)
        
               
        enable_esc_close(quotation_master)

        return quotation_master
        # quotation_master.mainloop()
    
    def Open_File():
        try:
            file_path = filedialog.askopenfilename(
                title="Select an Excel File",
                filetypes=(("Excel Files", "*.xlsx;*.xls"), ("All Files", "*.*")),
                parent=tool_master
            )
            if file_path:
                wb = load_workbook(file_path, data_only=True)
                sheet = wb.active  # get active sheet
                trv.delete(*trv.get_children())
                unit_price = 0.0
                total_price = 0.0
                for i, row in enumerate(sheet.iter_rows(values_only=True)):
                    if i == 0:
                        continue
                    trv.insert("", 'end', text=str(row[0]), values=(str(row[0]), str(row[1]), row[2], row[3], unit_price if not row[4] else row[4], total_price if not row[5] else row[5]))
                On_Start_Tool_Master()
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open file: {str(e)}", parent=tool_master)
    def clear_data():
        TxtNo.delete(0, END)
        TxtPartDesc.delete(0, END)
        TxtQty.delete(0, END)
        TxtNo.focus()
        trv.delete(*trv.get_children())
    
    def On_Start_Tool_Master():
        #clear_data()
        BtnSave['state'] = 'normal'
        BtnSave['text'] = 'Save'
        var_quot.set('')
        TxtNo.delete(0, END)
        TxtPartDesc.delete(0, END)
        TxtQty.delete(0, END)
        TxtNo.focus()
        for item in trv.get_children():
            vals = trv.item(item)["values"]
            if vals[4] != '0.0' and vals[5] != '0.0':
                BtnShowQuotation['state'] = 'normal'
                break

    def add_entry_manual():
        no = TxtNo.get()
        part_name = TxtPartDesc.get()
        qty = TxtQty.get()
        cnt = 1
        if BtnSave['state'] != 'normal':
           BtnSave['state'] = 'normal'
           trv.delete(*trv.get_children())
        for item in trv.get_children():
            cnt += 1
        
        if no != '' and part_name != '' and qty != '':
            trv.insert("", 'end', text=str(cnt), values=(str(cnt), str(no), part_name, qty, '0.0', '0.0'))
            #clear_data()
        
        if BtnSave['state'] == 'disabled':
            BtnSave['text'] = 'Save'
            BtnSave['state'] = 'normal'
        
        TxtNo.delete(0, END)
        TxtPartDesc.delete(0, END)
        TxtQty.delete(0, END)
        TxtNo.focus()
    
    def delete_selected():
        """Delete selected row(s) from Treeview"""
        selected_items = trv.selection()  # get selected rows
        
        for item in selected_items:
            trv.delete(item)
        
        rows = []
        for item in trv.get_children():
            row = trv.item(item, "values")
            rows.append(list(row))
        
        trv.delete(*trv.get_children())
        cnt = 1
        for row in rows:
            trv.insert("", 'end', text=str(cnt), values=(str(cnt), str(row[1]), row[2], row[3], row[4], row[5], row[6]))
            cnt += 1

    def show_selected_record(event):
        for selection in trv.selection():
            item = trv.item(selection)
        i1 = item["values"]
        Frm_Quotation_Master(tool_master, i1, TxtCustomer1.get(), TxtProv.get(), login_id)

    def Show_Quotation_Pdf(no):
        po_number = None
        if txtSaveInfo['text'] == 'Done':
            if no == 2:
                po_number = simpledialog.askstring(
                    "PO Number",
                    "Enter Purchase Order (PO) Number:",
                    parent=tool_master
                )

                # If user cancels or leaves empty
                if not po_number:
                    messagebox.showwarning("Required", "PO Number is required to generate invoice", parent=tool_master)
                    return
            Company_Name, Company_Contact, Company_Address, email_id = Get_Firm_Details(login_id)
            customer_name = TxtCustomer1.get()
            party_name, contact, address, mid = Customer_Details(customer_name, login_id)
            provider_name = TxtProv.get()
            term_date = (datetime.today() + timedelta(days=30)).strftime('%d-%m-%Y')
            items = []
            quotation_id = var_quot.get()
            if no == 2:
                invoice_id = Invoice_Id_Funct(login_id)
            subtotal = 0
            
            gst_per = "SELECT gst_per FROM gst_percentage_table WHERE id = 1"
            db_cursor.execute(gst_per)
            gst_per = int(db_cursor.fetchone()[0])
            data = []
            cnt1 = 1
            
            terms_data = get_terms_conditions(quotation_id)
            
            for child in trv.get_children():
                vals = trv.item(child)["values"]
                items.append({
                    "no": vals[1],
                    "part_desc": vals[2],
                    "qty": int(vals[3]),
                    "unit_price": int(float(vals[4])),
                    "total_price": int(float(vals[5])),
                    "taxed":""
                })
                #data.append((invoice_id, quotation_id, vals[0], po_no, date_tr, login_id))
                subtotal += int(float(vals[5]))
            tax_due = int(subtotal*gst_per/100)
            grand_total = int(subtotal + tax_due)
            sample = {
                "company": {
                    "name":Company_Name,
                    "address":Company_Address,
                    "phone": Company_Contact,
                    "email": email_id
                },
                "date": datetime.today().strftime("%d-%m-%Y"),
                "quote_no": quotation_id if no == 1 else invoice_id,
                "po_no": "--" if no ==1 else po_number,
                "valid_until": term_date,
                "prepared_by": "Admin",
                "customer": {
                    "name":party_name,
                    "company":provider_name,
                    "address":address,
                    "phone":contact
                },
                "items":items,
                "totals":{"subtotal":subtotal,"tax_rate":int(gst_per),"tax_due":tax_due,"other":0,"grand_total":grand_total},
                "terms":terms_data
            }

            if items != []:
                # pdf_path = r"D:\\ToolCosting\\Support Documents\\Tool_Quotation.pdf"
                pdf_name = quotation_id if no == 1 else invoice_id
                pdf_path = filedialog.asksaveasfilename(
                    defaultextension=".pdf",
                    filetypes=[("PDF files", "*.pdf")],
                    initialfile=f"{pdf_name}.pdf",   # Default file name
                    title="Save PDF",
                    parent=tool_master
                )
                if no == 1:
                    #messagebox.showinfo("Success",f"QUOTATION is generated successfully...", parent=tool_master)
                    create_quotation_pdf(sample, pdf_path, "QUOTATION", tool_master)
                elif no == 2:
                    # po_number = simpledialog.askstring(
                    #     "PO Number",
                    #     "Enter Purchase Order (PO) Number:",
                    #     parent=tool_master
                    # )

                    # # If user cancels or leaves empty
                    # if not po_number:
                    #     messagebox.showwarning("Required", "PO Number is required to generate invoice", parent=tool_master)
                    #     return
                    #messagebox.showinfo("Success",f"Invoice is generated successfully...", parent=tool_master)
                    date_tr = datetime.today().date()
                    sql_update = f"UPDATE quotation_master SET invoice_id = {DATABASE_SYN}, invoice_tr_date = {DATABASE_SYN}, invoice_generated = {DATABASE_SYN} WHERE quotation_id = {DATABASE_SYN} AND login_id = {DATABASE_SYN}"
                    params = (invoice_id, date_tr, 'Y', var_quot.get(), login_id)
                    db_cursor.execute(sql_update, params)
                    
                    sql_new = "INSERT INTO invoice_master (invoice_id, quot_id, part_no, po_no, date_tr, login_id) VALUES (%s, %s, %s, %s, %s, %s)"
                    db_cursor.executemany(sql_new, [(invoice_id, var_quot.get(), trv.item(child)["values"][1], po_number, date_tr, login_id) for child in trv.get_children()])
                    
                    db_connection.commit()
                    var_quot.set('')
                    create_quotation_pdf(sample, pdf_path, "TAX INVOICE", tool_master)

                os.startfile(pdf_path)
                #txtSaveInfo['text'] = ''
                #trv.delete(*trv.get_children())
            else:
                messagebox.showerror("Error","Please fill the records to generate quotation/invoice.", parent=tool_master)
        else:
            messagebox.showerror("Error", "Please save/update first.",parent = tool_master)

    def save_quotation():
        global rules_page

        if trv.get_children():
            def on_ok_click():
                global rules_page   # IMPORTANT
                n1 = TxtRule.get(1.0, END).strip()
                terms_conditions = []
                if n1:                
                    terms_conditions = n1.split('\n')
                    
                Save_Data_Quotation(terms_conditions)

                rules_page.destroy()
                rules_page = None   # reset after close

            # ✅ Check if already open
            # if rules_page is not None and rules_page.winfo_exists():
            #     rules_page.lift()
            #     rules_page.focus_force()
            #     return

            def on_start_rules_page():
                terms_conditions = get_terms_conditions(var_quot.get())
                TxtRule.delete(1.0, END)

                if terms_conditions:
                    str_rules = "\n".join(terms_conditions)
                    TxtRule.insert(END, str_rules)
                else:
                    TxtRule.insert(END, """1) Customer will be billed after acceptance of this quote.\n2) Quotation will be valid for next 30 days.\n3) Please mail signed copy of quotation to company mail ID.\n4) Payment terms - 50% Advance and 50% plus GST payable within 45 days from date of invoice.\n5) Delivery time - 30 days.""")

            # ✅ Create window only once
            rules_page = Toplevel(tool_master)
            rules_page.geometry("550x250+500+300")
            rules_page.title("Generating PDF")

            # ✅ Handle manual close (VERY IMPORTANT)
            def on_close():
                global rules_page
                rules_page.destroy()
                rules_page = None

            rules_page.protocol("WM_DELETE_WINDOW", on_close)

            LblRule = Label(rules_page, text="Terms & conditions", font=('Times New Roman', 18))
            LblRule.place(x=170, y=20)

            TxtRule = Text(rules_page, font=('Times New Roman', 14), width=55, height=7)
            TxtRule.place(x=20, y=60)

            BtnOk = Button(
                rules_page,
                text="OK",
                width=12,
                bg='green',
                fg='white',
                font=('Times New Roman', 12),
                command=on_ok_click
            )
            BtnOk.place(x=170, y=210)

            on_start_rules_page()

        else:
            messagebox.showerror("Error", "Please add some records to save.", parent=tool_master)
    
    def Save_Data_Quotation(terms_conditions):
    
        customer_name = TxtCustomer1.get()
        party_name, contact, address, mid = Customer_Details(customer_name, login_id)
        provider_name = TxtProv.get()
        if BtnSave['text'].lower() == 'save':
            quotation_id = Quotation_Id_Funct(login_id)
        else:
            quotation_id = var_quot.get()
        date_tr_quot = datetime.now().date()

        cnt = 0
        flag = False
        for child in trv.get_children():
            vals = trv.item(child)["values"]
            if int(float(vals[4])) != 0 and int(float(vals[5])) != 0:
                flag = True
            else:
                flag = False
                break
        
        #if flag:
        # else:
        #     table_names = ['quotation_master_details_machining_details_u', 'quotation_master_details_u', 'quotation_master_u']
        flag2 = True
        if not flag:
            msg1 = messagebox.askyesno("Warning", "All part's are not updated. Do you want to continue?.\nYou have to update the quotation from UPDATE tab.", parent=tool_master)
            if msg1:
                flag2 = True
            else:
                flag2 = False
        if flag2:
            qmd_items = []
            qmd_items_update = []
            qmdmd_item = []
            qmdmd_item_update = []
            for child in trv.get_children():
                vals = trv.item(child)["values"]
                part_no = vals[1]
                part_desc = vals[2]
                part_qty = int(vals[3])
                unit_price = round(float(vals[4]), 2)
                total_price = round(float(vals[5]), 2)
                if len(vals)>6 and ast.literal_eval(vals[6]):
                    str_json = ast.literal_eval(vals[6])
                    material = str_json["material"]
                    unit_measurement = str_json["unit_measurement"]
                    shape = str_json["shape"]
                    try:
                        width = float(str_json["width"])
                    except:
                        width = 0 
                    try:
                        Length = float(str_json["length"])
                    except:
                        Length = 0
                    try:
                        Thickness = float(str_json["thickness"])
                    except:
                        Thickness = 0
                    try:
                        Rmc = float(str_json["rmc"])
                    except:
                        Rmc = 0
                    try:
                        profit_per = var_percentage.get()
                    except:
                        profit_per = 0
                    try:
                        scrab_per = float(str_json["scrab_per"])
                    except:
                        scrab_per = 0
                    try:
                        Weight = float(str_json["unit_weight"])
                    except:
                        Weight = 0
                    try:
                        machining_lst = str_json["machining_lst"]
                    except:
                        machining_lst = {}
                    
                else:
                    material = ''
                    unit_measurement = ''
                    shape = ''
                    width = 0
                    Length = 0
                    Thickness = 0
                    Rmc = 0
                    profit_per = 0
                    scrab_per = 0
                    Weight = 0
                    machining_lst = {}
                if machining_lst:
                    for key, item in machining_lst.items():
                        qmdmd_item.append([quotation_id, part_no, item['machining_name'], item['lbl_rate'], item['cust_rate'], item['total_hr'], date_tr_quot, login_id])
                        qmdmd_item_update.append([part_no, item['machining_name'], item['lbl_rate'], item['cust_rate'], item['total_hr'], date_tr_quot, login_id, var_quot.get()])
                qmd_items.append([quotation_id, part_no, part_desc, part_qty, material, unit_measurement, shape, width, Length, Thickness, Weight, Rmc, profit_per, scrab_per, unit_price, total_price, date_tr_quot, login_id])
                qmd_items_update.append([part_no, part_desc, part_qty, material, unit_measurement, shape, width, Length, Thickness, Weight, Rmc, profit_per, scrab_per, unit_price, total_price, date_tr_quot, login_id, var_quot.get()])
            if qmdmd_item != []:
                if BtnSave['text'] == 'UPDATE':
                    sql_update = f"DELETE FROM quotation_master_details_machining_details WHERE login_id = '{login_id}' AND Quotation_Id = '{var_quot.get()}'"
                    db_cursor.execute(sql_update)
                #elif BtnSave['text'] == 'SAVE':
                sql1 = f"INSERT INTO quotation_master_details_machining_details (Quotation_Id, part_no_id, machining_name, lbl_rate, cust_rate, total_hr, date_tr, login_id) VALUES ({DATABASE_SYN}, {DATABASE_SYN}, {DATABASE_SYN}, {DATABASE_SYN}, {DATABASE_SYN}, {DATABASE_SYN}, {DATABASE_SYN}, {DATABASE_SYN})"
                db_cursor.executemany(sql1, qmdmd_item)

            if BtnSave['text'] == 'UPDATE':
                sql_delete = f"DELETE FROM quotation_master_details WHERE login_id = '{login_id}' AND Quotation_Id = '{var_quot.get()}'"
                db_cursor.execute(sql_delete)
            #elif BtnSave['text'] == 'SAVE':
            sql2 = f"INSERT INTO quotation_master_details (Quotation_Id, part_no, part_desc, part_qty, material, unit_measurement, shape, width, length_part, thickness, unit_weight, rmc, profit_per, scrab_per, unit_price, total_price, date_tr, login_id) VALUES ({DATABASE_SYN}, {DATABASE_SYN}, {DATABASE_SYN}, {DATABASE_SYN}, {DATABASE_SYN}, {DATABASE_SYN}, {DATABASE_SYN}, {DATABASE_SYN}, {DATABASE_SYN}, {DATABASE_SYN}, {DATABASE_SYN}, {DATABASE_SYN}, {DATABASE_SYN}, {DATABASE_SYN}, {DATABASE_SYN}, {DATABASE_SYN}, {DATABASE_SYN}, {DATABASE_SYN})"
            db_cursor.executemany(sql2, qmd_items)
            
            if BtnSave['text'] == 'UPDATE':
                sql_delete = f"DELETE FROM quotation_master WHERE login_id = '{login_id}' AND quotation_id = '{var_quot.get()}'"
                db_cursor.execute(sql_delete)

            #if BtnSave['text'] == 'SAVE':    
            sql3 = f"INSERT INTO quotation_master (quotation_id, cust_id, cust_name, provider_name, date_tr_quot, invoice_generated, login_id, terms_conditions) VALUES ({DATABASE_SYN}, {DATABASE_SYN}, {DATABASE_SYN}, {DATABASE_SYN}, {DATABASE_SYN}, {DATABASE_SYN}, {DATABASE_SYN}, {DATABASE_SYN})"
            db_cursor.execute(sql3, (quotation_id, mid, party_name, provider_name, date_tr_quot, 'N', login_id, '\n'.join(terms_conditions)))
            db_connection.commit()
            
            messagebox.showinfo("Success", "Data saved successfully.",parent=tool_master)
            BtnSave['text'] = 'Save'
            txtSaveInfo['text'] = ''
            if flag:
                txtSaveInfo['text'] = 'Done'
                var_quot.set(quotation_id)
            else:
                reset_form_quot_unsaved_data()
            BtnSave['state'] = 'disabled'    

    def only_int(new_value):
        return new_value.isdigit() or new_value == ""

    def show_selected_record_update(event):
        for selection in trv_1History.selection():
            item = trv_1History.item(selection)
        i1 = item["values"]
        BtnSave['state'] = 'normal'
        BtnSave['text'] = 'UPDATE'
        qid = str(i1[0]).zfill(9)   # '71225001' -> '071225001'
        var_quot.set(qid)
        TxtCustomer1.set(i1[1])
        TxtProv.set(i1[2])
        try:
            TxtDate.set_date(datetime.strptime(i1[3], "%Y-%m-%d").date())
        except:
            TxtDate.set_date(datetime.strptime(i1[3], "%Y-%m-%d %H:%M:%S").date())
        if isinstance(i1[5], str):
            data = ast.literal_eval(i1[5])
        trv.delete(*trv.get_children())
        cnt1 = 1
        for quot_id, quot_details in data.items():
            for part_id, part_details in quot_details.items():
                machining_details = {
                    'material' : part_details['material'],
                    'unit_measurement' : part_details['unit_measurement'],
                    'shape' : part_details['shape'],
                    'width' : part_details['width'],
                    'length' : part_details['length'],
                    'thickness' : part_details['thickness'],
                    'unit_weight' : part_details['unit_weight'],
                    'rmc' : part_details['rmc'],
                    'profit_per' : part_details['profit_per'],
                    'scrab_per' : part_details['scrab_per'],
                    'unit_price' : part_details['unit_price'],
                    'machining_lst' : part_details['lst']
                }
                trv.insert("", 'end', text=str(cnt1), values=(str(cnt1), str(part_id), str(part_details["part_desc"]), str(part_details["qty"]), str(part_details["unit_price"]), str(part_details["total_price"]), machining_details))
                cnt1 += 1
        notebook.select(tab1)
    party_dict = {}
    def On_Start_tab2():
        sql1 = f"SELECT party_name, provider_names FROM account_master WHERE login_id = {DATABASE_SYN}"
        db_cursor.execute(sql1, (login_id,))
        data1 = db_cursor.fetchall()
        party_lst = []
        if db_cursor.rowcount != 0:
            for party_name in data1:
                party_lst.append(party_name[0])
                party_dict[party_name[0]] = [x.strip() for x in party_name[1].split(',')]

            TxtCustomer1.set_completion_list(party_lst)
            if party_lst:
                TxtCustomer1.current(0)
            TxtCustomerSHistory.set_completion_list(party_lst)
            if party_lst:
                TxtCustomerSHistory.current(0)
            
            TxtProv['values'] = party_dict[TxtCustomer1.get()]
            if TxtProv['values']:
                TxtProv.current(0)

    def Search_Records():
        trv_1History.delete(*trv_1History.get_children())
        name = TxtCustomerSHistory.get()
        if name != '' and name != 'Select':
            sql1 = f"SELECT quotation_id, provider_name, date_tr_quot, invoice_tr_date, cust_name FROM quotation_master WHERE cust_name = {DATABASE_SYN}"
            db_cursor.execute(sql1, (name,))
        data1 = db_cursor.fetchall()
        if data1 != []:
            cnt1 = 1
            for i in data1:
                sql2 = f"SELECT * FROM quotation_master_details WHERE Quotation_Id = {DATABASE_SYN}"
                db_cursor.execute(sql2, (i[0],))
                data2 = db_cursor.fetchall()
                all_items = {}
                items = {}
                if data2 != []:
                    cnt = 1
                    for child in data2:
                        part_items = {}
                        sql3 = f"SELECT * FROM quotation_master_details_machining_details WHERE Quotation_Id = '{child[1]}' AND part_no_id = '{child[2]}' AND date_tr = '{child[17]}'"
                        db_cursor.execute(sql3)
                        data3 = db_cursor.fetchall()
                        items[child[2]] = {
                            "no" : cnt,
                            "part_desc" : child[3],
                            "qty" : int(child[4]),
                            "material" : child[5],
                            "unit_measurement" : child[6],
                            "shape" : child[7],
                            "width" : child[8],
                            "length" : child[9],
                            "thickness" : child[10],
                            "unit_weight" : child[11],
                            "rmc" : child[12],
                            "profit_per" : child[13],
                            "scrab_per" : child[14],
                            "unit_price" : child[15],
                            "total_price" : child[16]
                            }

                        lst = {}
                        if data3 != []:
                            for item in data3:
                                lst[item[3]] = {
                                    "machining_name" : item[3],
                                    "lbl_rate" : item[4],
                                    "cust_rate" : item[5],
                                    "total_hr" : item[6],
                                    "date_tr" : str(item[7])                            
                                }
                                
                        items[child[2]]["lst"] = lst
                        cnt += 1
                    all_items[i[0]] = items
                dt1 = i[2]
                dt2 = i[3]
                if dt1:
                    try:
                        dt1 = str(dt1.date())
                    except:
                        pass
                if dt2:
                    try:
                        dt2 = str(dt2.date())
                    except:
                        pass
                trv_1History.insert("", 'end', text=str(cnt1), values=(str(i[0]), str(i[4]), str(i[1]), dt1, dt2, all_items))
                cnt1 += 1
    
    def reset_form_quot_unsaved_data():
        trv.delete(*trv.get_children())
        TxtNo.delete(0, END)
        TxtPartDesc.delete(0, END)
        TxtQty.delete(0, END)
        TxtNo.focus()
        var_quot.set('')
        txtSaveInfo['text'] = ''
    
    def reset_form_quot():
        msg = messagebox.askquestion("Warning", "Do you want to reset form?",parent=tool_master)
        if msg:
            trv.delete(*trv.get_children())
            BtnSave['state'] = 'normal'
            BtnSave['text'] = 'SAVE'
            TxtNo.delete(0, END)
            TxtPartDesc.delete(0, END)
            TxtQty.delete(0, END)
            TxtNo.focus()
            var_quot.set('')
            txtSaveInfo['text'] = ''
            
        
    #=============================================================================================
    #                                   Tab 1
    #=============================================================================================            
    tool_master = Toplevel(master)
    tool_master.title("Tool Master")
    tool_master.geometry("1100x680+175+70")
    tool_master.resizable(False, False)
    tool_master.grab_set()
    s = ttk.Style()
    s.configure('TNotebook.Tab',font=('Times New Roman',14))
    var_percentage = tk.IntVar()
    notebook = ttk.Notebook(tool_master)
    notebook.pack(expand=True, fill="both")
    var_cache = {}
    tab1 = ttk.Frame(notebook)
    tab2 = ttk.Frame(notebook)

    notebook.add(tab1, text="                  New Tools               ")
    notebook.add(tab2, text="                  Update                ")
    
    LblCust = Label(tab1, text="Customer Name :", font=('Times New Roman', 14))
    LblCust.place(x=20, y=25)
    TxtCustomer1 = AutocompleteCombobox(tab1, width=30, font=('Times New Roman', 14), state='readonly')
    TxtCustomer1.place(x=180, y=25)
    
    LblProv = Label(tab1, text="Provider :", font=('Times New Roman', 14))
    LblProv.place(x=510, y=25)
    TxtProv = ttk.Combobox(tab1, width=20, font=('Times New Roman', 14), state='readonly')
    TxtProv.place(x=620, y=25)
    
    LblDate = Label(tab1, text="Date :", font=('Times New Roman', 14))
    LblDate.place(x=860, y=25)
    TxtDate = DateEntry(tab1, width=12, font=('Times New Roman', 14), borderwidth=2, date_pattern="dd-mm-yyyy", state='readonly')
    TxtDate.place(x=930, y=25)
    
    Frm1 = LabelFrame(tab1, text="")
    Frm1.place(x=15, y=80, width=840, height=110)
    Frm2 = LabelFrame(tab1, text="", font=('Times New Roman', 12))
    Frm2.place(x=870, y=80, width=200, height=110)
    
    LblNo = Label(Frm1, text='Part Number', font=('Times New Roman', 16))
    LblNo.place(x=10, y=5)
    TxtNo = Entry(Frm1, font=('Times New Roman', 16), width=14, justify='center')
    TxtNo.place(x=10, y=50)
    
    LblPartDesc = Label(Frm1, text='Part Description', font=('Times New Roman', 16))
    LblPartDesc.place(x=200, y=5)
    TxtPartDesc = Entry(Frm1, font=('Times New Roman', 16), width=32, justify='center')
    TxtPartDesc.place(x=200, y=50)
    
    LblQty = Label(Frm1, text='Qty', font=('Times New Roman', 16))
    LblQty.place(x=580, y=5)
    vcmd = (tool_master.register(only_int), "%P")
    TxtQty = Entry(Frm1, font=('Times New Roman', 16), width=12,validate="key", validatecommand=vcmd, justify='center')
    TxtQty.place(x=580, y=50)
    
    BtnAdd = Button(Frm1, text='Add', font=('Times New Roman', 12), width=9, bg='green', fg='white', command=add_entry_manual)
    BtnAdd.place(x=730, y=47)
    
    LblExcel = Label(Frm2, text='Select Excel', font=('Times New Roman', 16))
    LblExcel.place(x=10, y=5)
    BtnExcel = Button(Frm2, text='Open Excel', font=('Times New Roman', 16), width=12, bg='green', fg='white', command=Open_File)
    BtnExcel.place(x=10, y=50)

    scrolly=Scrollbar(tab1 , orient=VERTICAL)
    
    trv=ttk.Treeview(tab1 , columns=("no" , "part_no" , "part_desc", "qty", "unit_price", "total_price") , yscrollcommand=scrolly.set )#, xscrollcommand=scrollx.set
    scrolly.place(x=1070, y=210, height=360)
    scrolly.config(command=trv.yview)

    trv.heading("no" , text="No.")
    trv.heading("part_no" , text="Part No")
    trv.heading("part_desc" , text="Part Description")
    trv.heading("qty" , text="Qty.")
    trv.heading("unit_price" , text="Price (Rs.)")
    trv.heading("total_price" , text="Total Price (Rs.)")
    
    #trv.heading("Provider" , text="Provider")
    
    trv["show"]="headings"

    trv.column("no" , width=70, anchor='center')
    trv.column("part_no" , width=300, anchor='center')
    trv.column("part_desc" , width=200, anchor='center')
    trv.column("qty" , width=100, anchor='center')
    trv.column("unit_price" , width=100, anchor='center')
    trv.column("total_price" , width=100, anchor='center')
    #trv.column("Provider" , width=100, anchor='center')
    
    trv.place(x=15, y=210, width=1050, height=360)
    
    txtSaveInfo = Label(tool_master, text='')
    txtSaveInfo.place(x=1500, y=10)
    
    Frm3 = LabelFrame(tab1, text="", font=('Times New Roman', 12))
    Frm3.place(x=160, y=585, width=570, height=50)
    
    BtnSave = Button(Frm3, text='SAVE', font=('Times New Roman', 12), width=14, bg='green', fg='white', command=save_quotation)
    BtnSave.place(x=50, y=5)
    BtnDelete = Button(Frm3, text='DELETE', font=('Times New Roman', 12), width=14, bg='brown', fg='white', command=delete_selected)
    BtnDelete.place(x=210, y=5)
    BtnReset = Button(Frm3, text='RESET', font=('Times New Roman', 12), width=14, bg='blue', fg='white', command=reset_form_quot)
    BtnReset.place(x=370, y=5)
    # BtnExit = Button(Frm3, text='EXIT', font=('Times New Roman', 12), width=13, bg='red', fg='white',command=tool_master.destroy)
    # BtnExit.place(x=430, y=5)
    
    BtnShowQuotation = Button(tab1, text='Show Preview Quotation', font=('Times New Roman', 16), width=22, fg='white', bg='green', command= lambda x = 1:Show_Quotation_Pdf(x))   
    BtnShowQuotation.place(x=780, y=590)
    # BtnShowInvoice = Button(tab1, text='Generate Invoice', font=('Times New Roman', 14), width=20, fg='white', bg='green', command= lambda x = 2:Show_Quotation_Pdf(x))
    # BtnShowInvoice.place(x=850, y=590)
    
    
    def f1(event):
        cust = TxtCustomer1.get()
        TxtProv['values'] = party_dict[cust]
        TxtProv.current(0)
        TxtProv.focus()
        # TxtProv.delete(0, END)
        # TxtProv.event_generate('<Down>')
    
    def f2(event):
        if TxtNo.get() != '':
            TxtPartDesc.focus()
    
    def f3(event):
        if TxtPartDesc.get() != '':
            TxtQty.focus()
    
    def f4(event):
        if TxtQty.get() != '':
            add_entry_manual()
    
    def f5(event):
        TxtNo.focus()
    
    def f6(event):
        cust = TxtCustomer1.get()
        TxtProv['values'] = party_dict[cust]
        TxtProv.current(0)
        TxtProv.focus()

    TxtCustomer1.bind("<<ComboboxSelected>>", f1)
    TxtCustomer1.bind("<Return>", f1)
    # TxtCustomer1.bind("<FocusOut>", f1)
    # TxtProv.bind("<FocusIn>", f6)
    TxtProv.bind("<<ComboboxSelected>>", f5)
    TxtNo.bind('<Return>', f2)
    TxtPartDesc.bind('<Return>', f3)
    TxtQty.bind('<Return>', f4)
    
    trv.bind("<Double-1>", show_selected_record)

    #=======================================================================================================
    #                                           Tab 2
    #=======================================================================================================

    LblHeadHistory = Label(tab2, text='Quotation Master Update', font=('Times New Roman', 24, 'bold'), fg='Purple')
    LblHeadHistory.place(x=350, y=10)
    var_quot = StringVar()
    var_cust_id = IntVar()
    s2 = StringVar()
    Frm1History = LabelFrame(tab2, text="")
    Frm1History.place(x=15, y=80, width=1070, height=60)

    LblCustHistory = Label(Frm1History, text="Customer Name :", font=('Times New Roman', 15))
    LblCustHistory.place(x=110, y=10)
    TxtCustomerSHistory = AutocompleteCombobox(Frm1History, width=30, font=('Times New Roman', 15))
    TxtCustomerSHistory.place(x=270, y=10)
    #TxtCustomerS._open_dropdown()

    LblDateHistory = Label(Frm1History, text="Date :", font=('Times New Roman', 14))
    LblDateHistory.place(x=750, y=10)
    TxtDate_1History = DateEntry(Frm1History, width=12, font=('Times New Roman', 14), borderwidth=2, date_pattern="dd-mm-yyyy")
    TxtDate_1History.place(x=820, y=10)

    BtnSearchHistory = Button(Frm1History, text='Search', font=('Times New Roman', 12), width=12, bg='green', fg='white', command=Search_Records)
    BtnSearchHistory.place(x=620, y=10)

    # scrollyhistory=Scrollbar(tab2 , orient=VERTICAL)

    trv_1History=ttk.Treeview(tab2 , columns=("quot_id" , "cust_name" , "prov_name", "date_tr_quot", "date_tr_invoice") , yscrollcommand=scrolly.set )#, xscrollcommand=scrollx.set
    # scrollyhistory.place(x=1070, y=80, height=360)
    # scrollyhistory.config(command=trv_1History.yview)

    trv_1History.heading("quot_id" , text="Quotation no")
    trv_1History.heading("cust_name" , text="Customer Name")
    trv_1History.heading("prov_name", text="Provider Name")
    trv_1History.heading("date_tr_quot" , text="Quotation Date")
    trv_1History.heading("date_tr_invoice" , text="Invoice Date")

    trv_1History["show"]="headings"

    trv_1History.column("quot_id" , width=70, anchor='center')
    trv_1History.column("cust_name" , width=200, anchor='center')
    trv_1History.column("prov_name", width=100, anchor='center')
    trv_1History.column("date_tr_quot" , width=150, anchor='center')
    trv_1History.column("date_tr_invoice" , width=150, anchor='center')

    trv_1History.place(x=15, y=160, width=1070, height=370)
    trv_1History.bind("<Double-1>", show_selected_record_update)
    On_Start_tab2()
    # tool_master_history.mainloop()
    
    On_Start_Tool_Master()
    enable_esc_close(tool_master)
    tool_master.mainloop()
    return tool_master
    
# Frm_Tool_Master(1, 1)