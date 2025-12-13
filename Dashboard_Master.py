from tkinter import *
from PIL import ImageTk, Image
import tkinter as tk
from tkinter import font
from Database.connection import *
import os
import sys
import ctypes
from Generate_Key.Generate_Licence import Frm_Generate_Licence

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

def Frm_Master_Dashboard(login_id):
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
            ("Generate Licence", lambda: Frm_Generate_Licence(dash_screen, login_id)),
        ]
        popup_menu_for(widget or master_btn, entries)

    def open_report(evt=None, widget=None):
        """Quotation → New, History, Reports ▶ (Machining, All Report)"""
        btn = widget or quotation_btn

        # Main popup menu for "Quotation"
        popup = tk.Menu(dash_screen, tearoff=0, font=menu_item_font)

        # 1) Normal items
        popup.add_command(
            label="History",
            command=lambda: print("Done")#Frm_Quot_History(dash_screen, login_id)
        )
        # popup.add_command(
        #     label="Total",
        #     command=lambda: Frm_Generate_Licence(dash_screen, login_id)
        # )
        
        # Show the popup under the Quotation button
        x = btn.winfo_rootx()
        y = btn.winfo_rooty() + btn.winfo_height()
        try:
            popup.tk_popup(x, y)
        finally:
            popup.grab_release()

    def open_help(evt=None, widget=None):
        entries = [
            ("Log out", lambda: dash_screen.quit()),
        ]
        popup_menu_for(widget or help_btn, entries)

    master_btn = tk.Button(
        top_frame, text="Master", font=heading_font, bg="#2c3e50", fg="white", bd=0,
        activebackground="#34495e", activeforeground="white",
        command=lambda: open_master(widget=master_btn)
    )
    master_btn.pack(side="left", padx=20)

    quotation_btn = tk.Button(
        top_frame, text="Report", font=heading_font, bg="#2c3e50", fg="white", bd=0,
        activebackground="#34495e", activeforeground="white",
        command=lambda: open_report(widget=quotation_btn)
    )
    quotation_btn.pack(side="left", padx=20)

    help_btn = tk.Button(
        top_frame, text="Help", font=heading_font, bg="#2c3e50", fg="white", bd=0,
        activebackground="#34495e", activeforeground="white",
        command=lambda: open_help(widget=help_btn)
    )
    help_btn.pack(side="left", padx=20)

    # Optional: allow keyboard/menu mnemonics (Alt+M, Alt+Q, etc.)
    dash_screen.bind_all("<Alt-m>", lambda e: open_master(widget=master_btn))
    dash_screen.bind_all("<Alt-q>", lambda e: open_report(widget=quotation_btn))
    dash_screen.bind_all("<Alt-h>", lambda e: open_help(widget=help_btn))

    # ---------- Background image and canvas (kept from original) ----------
    screen_width = dash_screen.winfo_screenwidth()
    screen_height = dash_screen.winfo_screenheight()

    image1 = Image.open(r"D:\\ToolCosting\\Images\\background.jpg")
    resized_image = image1.resize((screen_width, screen_height), Image.Resampling.LANCZOS)
    img = ImageTk.PhotoImage(resized_image)

    canvas = tk.Canvas(dash_screen, width=screen_width, height=screen_height)
    canvas.pack(fill="both", expand=True)
    canvas.create_image(0, 0, anchor="nw", image=img)
    canvas.image = img  # keep reference so it isn't garbage-collected

    # Place the top_frame above the canvas (so it stays visible)
    top_frame.lift(canvas)
    top_frame.place(x=0, y=0, relwidth=1)

    on_start()
    dash_screen.mainloop()


# Example call for testing:
# Frm_Master_Dashboard(login_id=1)
