from tkinter import *
from PIL import ImageTk, Image
import tkinter as tk
from tkinter import font
from Masters.Account_Master import Frm_Account_Master
from Masters.Gst_Master import Frm_Gst_Percentage
from Masters.Profit_Percentage import Frm_Profit_Per_Master
from Masters.Raw_Material import Frm_Raw_Master
from Masters.Reset_Password import Frm_Reset_Password
from Quotation.NewInvoice import Frm_New_Invoice
from Quotation.Tool_Master import Frm_Tool_Master
from Database.connection import *
from Masters.Machining_Master import Frm_Machining_Master
from Masters.Firm_Master import Frm_Firm_Master
from Quotation.Quotation_Master_History import Frm_Quot_History
from Masters.Delivery_Master import Frm_Delivery_Master
from Reports.Gst_Report import Frm_GST_Report
from Reports.Invoice_History import Frm_Invoice_Report
from Reports.Machining_Report import Frm_Machining_Report
from Masters.Material_Master import Frm_material_master
import os
import sys
import ctypes
from tkinter import filedialog, messagebox
from openpyxl import Workbook
import subprocess
from Reports.Quotation_History import Frm_Quotation_Report
open_windows = {}
def resource_path(relative_path):
    """Get absolute path to resource (for PyInstaller compatibility)."""
    try:
        base_path = sys._MEIPASS  # PyInstaller temp folder
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

icon_path = resource_path(r"D:\\ToolCosting\\Images\\logo.ico")
try:
    myappid = 'MyCompany.MyApp.1.0'  # arbitrary string
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except Exception as e:
    print(e)

def Dashboard(login_id):
    def open_single_window(key, window_func, *args):

        global open_windows

        # Close all existing windows first
        for k, win in list(open_windows.items()):
            try:
                if win.winfo_exists():
                    win.destroy()
            except:
                pass

            del open_windows[k]

        # Open new window
        win = window_func(*args)
        open_windows[key] = win

        def on_close():
            try:
                del open_windows[key]
            except:
                pass
            win.destroy()

        win.protocol("WM_DELETE_WINDOW", on_close)

    
    def logout_app():
        dash_screen.destroy()
        #Main_Function()
    def download_excel():
        file_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx")],
            title="Save Excel File As",
            initialfile="sample.xlsx"
        )

        # If user cancels, file_path will be empty
        if not file_path:
            return

        try:
            # Create a new Excel workbook
            wb = Workbook()
            ws = wb.active
            ws.title = "Sheet1"

            # Add header row (fixed 4-5 columns)
            headers = ["Sr. No.", "Part No.", "Part Description", "QTY", "Unit Price", "Total Price"]
            ws.append(headers)
            
            sample_data = [
                
            ]

            # Add sample data to worksheet
            for row in sample_data:
                ws.append(row)

            wb.save(file_path)

            messagebox.showinfo("Success", f"Excel file created successfully:\n{file_path}")
            os.startfile(file_path)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create Excel file.\nError: {e}")
        
    def on_start():
        pass

    dash_screen = Tk()
    dash_screen.state("zoomed")
    dash_screen.title("Welcome To Tool Costing Master")
    try:
        dash_screen.iconbitmap(icon_path)
    except Exception:
        pass

    # ---------- Fonts ----------
    heading_font = font.Font(family="Times New Roman", size=18, weight="bold")
    menu_item_font = font.Font(family="Times New Roman", size=14, weight="bold")

    # ---------- Custom top bar (acts like menubar headings) ----------
    top_frame = tk.Frame(dash_screen, bg="#2c3e50", height=50)
    top_frame.pack(fill="x")

    # Utility to create and post a popup menu under a widget
    def popup_menu_for(widget, entries):
        # entries: list of tuples (label, command)
        popup = tk.Menu(dash_screen, tearoff=0, font=menu_item_font)
        for label, cmd in entries:
            if label == "---":   # simple separator marker
                popup.add_separator()
            else:
                popup.add_command(label=label, command=cmd)
        # compute position: under the widget
        x = widget.winfo_rootx()
        y = widget.winfo_rooty() + widget.winfo_height()
        try:
            popup.tk_popup(x, y)
        finally:
            popup.grab_release()

    # ---------- Heading button callbacks (show popups) ----------
    def open_master(evt=None, widget=None):
        entries = [
            ("Self Details", lambda: open_single_window("firm_master", Frm_Firm_Master,dash_screen, login_id, 2)),
            ("Customer Details", lambda: open_single_window("account_master", Frm_Account_Master, dash_screen, login_id)),
            ("Machining Library", lambda: open_single_window("Machining_Library", Frm_Machining_Master,dash_screen)),
            ("Material Details", lambda: open_single_window("material_master", Frm_material_master, dash_screen)),
            ("Percentage & Profit", lambda: open_single_window("percentage_profit", Frm_Profit_Per_Master, dash_screen)),
            ("Scrap Details", lambda: open_single_window("raw_master", Frm_Raw_Master, dash_screen)),
            ("GST Details", lambda: open_single_window("gst_master", Frm_Gst_Percentage, dash_screen))
        ]
        popup_menu_for(widget or master_btn, entries)

    def open_quotation(evt=None, widget=None):
        """Quotation → New, History, Reports ▶ (Machining, All Report)"""
        btn = widget or quotation_btn

        # Main popup menu for "Quotation"
        popup = tk.Menu(dash_screen, tearoff=0, font=menu_item_font)
        
        quot_menu = tk.Menu(popup, tearoff=0, font=menu_item_font)
        quot_menu.add_command(
            label="New",
            command=lambda: open_single_window("tool_master", Frm_Tool_Master, dash_screen, login_id)
        )
        
        # Attach submenu under "Reports"
        popup.add_cascade(label="Quotation", menu=quot_menu)
        
        quot_menu1 = tk.Menu(popup, tearoff=0, font=menu_item_font)
        quot_menu1.add_command(
            label="New",
            command=lambda: open_single_window("new_invoice", Frm_New_Invoice, dash_screen, login_id)
        )
        # quot_menu1.add_command(
        #     label="History",
        #     command=lambda: open_single_window("quot_history", Frm_Quot_History, dash_screen, login_id)
        # )
        
        # Attach submenu under "Reports"
        popup.add_cascade(label="Invoice", menu=quot_menu1)

        # 2) Submenu for "Reports"
        reports_menu = tk.Menu(popup, tearoff=0, font=menu_item_font)
        
        reports_menu.add_command(
            label="Quotation Report",
            command=lambda: open_single_window("quotation_report", Frm_Quotation_Report, dash_screen, login_id)
        )
        
        reports_menu.add_command(
            label="Invoice Report",
            command=lambda: open_single_window("invoice_report", Frm_Invoice_Report, dash_screen, login_id)
        )
        reports_menu.add_command(
            label="Machining",
            command=lambda: open_single_window("machining_report", Frm_Machining_Report, dash_screen, login_id)
        )
    
        reports_menu.add_command(
            label="GST File",
            command=lambda: open_single_window("gst_report", Frm_GST_Report, dash_screen, login_id)
        )
        
        reports_menu.add_command(
            label="Challan Report",
            command=lambda: open_single_window("delivery_master", Frm_Delivery_Master, dash_screen, login_id)
        )
        
        

        # Attach submenu under "Reports"
        popup.add_cascade(label="Reports", menu=reports_menu)
        
        search_menu = tk.Menu(popup, tearoff=0, font=menu_item_font)
        search_menu.add_command(
            label="Search Data",
            command=lambda: open_single_window("quot_history", Frm_Quot_History, dash_screen, login_id)
        )
        popup.add_cascade(label="Search", menu=search_menu)

        # Show the popup under the Quotation button
        x = btn.winfo_rootx()
        y = btn.winfo_rooty() + btn.winfo_height()
        try:
            popup.tk_popup(x, y)
        finally:
            popup.grab_release()

    def Backup_Data():
        
        # 🔧 CONFIG (change these)
        DB_USER = "root"
        DB_PASSWORD = "omicron"
        DB_NAME = "tool_management"
        
        # Fixed backup folder
        BACKUP_DIR = r"D:\\ToolCosting\\SupportFiles\\Backup"

        # Create folder if not exists
        os.makedirs(BACKUP_DIR, exist_ok=True)

        # File name with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = os.path.join(BACKUP_DIR, f"{DB_NAME}_{timestamp}.sql")
        mysqldump_path = r"C:\\Program Files\\MySQL\\MySQL Server 8.0\\bin\\mysqldump.exe"
        try:
            # 🔥 mysqldump command
            command = [
                mysqldump_path,
                "-u", DB_USER,
                f"-p{DB_PASSWORD}",
                "--databases", DB_NAME,              # includes CREATE DATABASE
                "--add-drop-database",
                "--add-drop-table",
                "--routines",
                "--events",
                "--triggers"
            ]

            # Write output to file
            with open(backup_file, "w", encoding="utf-8") as f:
                subprocess.run(command, stdout=f, check=True)
            messagebox.showinfo("Success", f"Backup successful: {backup_file}", parent=dash_screen)
            print(f"Backup successful: {backup_file}")

        except subprocess.CalledProcessError as e:
            messagebox.showerror("Error", f"Error while backup : {e}", parent=dash_screen)

    def open_help(evt=None, widget=None):
        entries = [
            ("Tool Excel", lambda: download_excel()),# replace with real function if any  
            ("Reset Password", lambda: open_single_window("reset_password", Frm_Reset_Password, dash_screen, login_id)),
            ("Backup", lambda: Backup_Data()),
            ("Log out", lambda: logout_app()),
        ]
        popup_menu_for(widget or help_btn, entries)

    # ---------- Menubar heading buttons ----------
    # Using flat buttons styled to look like a menubar
    master_btn = tk.Button(
        top_frame, text="Master", font=heading_font, bg="#2c3e50", fg="white", bd=0,
        activebackground="#34495e", activeforeground="white",
        command=lambda: open_master(widget=master_btn)
    )
    master_btn.pack(side="left", padx=20)

    quotation_btn = tk.Button(
        top_frame, text="Quotation", font=heading_font, bg="#2c3e50", fg="white", bd=0,
        activebackground="#34495e", activeforeground="white",
        command=lambda: open_quotation(widget=quotation_btn)
    )
    quotation_btn.pack(side="left", padx=20)

    # ❌ Removed separate Reports button

    help_btn = tk.Button(
        top_frame, text="Help", font=heading_font, bg="#2c3e50", fg="white", bd=0,
        activebackground="#34495e", activeforeground="white",
        command=lambda: open_help(widget=help_btn)
    )
    help_btn.pack(side="left", padx=20)
    
    child_window = None
    
    screen_width = dash_screen.winfo_screenwidth()
    screen_height = dash_screen.winfo_screenheight()

    image1 = Image.open(r"D:\\ToolCosting\\Images\\background.jpg")
    resized_image = image1.resize((screen_width, screen_height), Image.Resampling.LANCZOS)
    img = ImageTk.PhotoImage(resized_image)

    canvas = tk.Canvas(dash_screen, width=screen_width, height=screen_height)
    canvas.pack(fill="both", expand=True)
    canvas.create_image(0, 0, anchor="nw", image=img)
    canvas.image = img  # keep reference so it isn't garbage-collected

    top_frame.lift(canvas)
    top_frame.place(x=0, y=0, relwidth=1)

    on_start()
    dash_screen.mainloop()
