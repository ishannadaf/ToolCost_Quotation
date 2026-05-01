from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from tkinter import *
from tkinter import messagebox
import ast
import os
from num2words import num2words
from Database.connection import *
# Register font
pdfmetrics.registerFont(TTFont('DejaVuSans', r"D:\\ToolCosting\\SupportFiles\\DejaVuSans.ttf"))
base_font = "DejaVuSans"
BLUE = colors.HexColor("#2F5597")

from reportlab.pdfgen import canvas


def Fetch_Bank_GST():
    sql1 = "SELECT firm_bank_name, firm_bank_acc, firm_bank_ifsc, firm_gst FROM firm_master"
    db_cursor.execute(sql1)
    data = db_cursor.fetchall()
    
    return data[0][0], data[0][1], data[0][2], data[0][3]



class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pages = []

    def showPage(self):
        self.pages.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        total_pages = len(self.pages)

        for page in self.pages:
            self.__dict__.update(page)

            # ✅ Draw footer ONLY on last page
            if self._pageNumber == total_pages:
                self.draw_footer()

            super().showPage()

        super().save()

    def draw_footer(self):
        x = 20 * mm
        y = 20 * mm

        self.setFont("DejaVuSans", 10)
        self.drawString(x, y + 12, "Regards,")
        self.drawString(x, y, self.company_name)

def draw_footer_last(canvas, doc):
    if canvas.getPageNumber() == doc.page_count:
        canvas.saveState()

        x = 20 * mm
        y = 20 * mm

        canvas.setFont("DejaVuSans", 10)
        canvas.drawString(x, y + 12, "Regards,")
        canvas.drawString(x, y, doc.company_name)

        canvas.restoreState()

def create_quotation_pdf(data, filename, pdf_type, master):
    messagebox.showinfo("Info", f"Opening your {pdf_type}...Click Ok.", parent=master)

    if isinstance(data, str):
        data = ast.literal_eval(data)

    po_no = data['po_no'] if data['po_no'] else "--"

    doc = SimpleDocTemplate(
        filename,
        pagesize=A4,
        leftMargin=15 * mm,
        rightMargin=15 * mm,
        topMargin=15 * mm,
        bottomMargin=20 * mm
    )

    styles = getSampleStyleSheet()
    normal = styles['Normal']
    normal.fontName = base_font
    normal.fontSize = 10

    small = ParagraphStyle("small", parent=normal, fontSize=9)

    elements = []

    # ================= HEADER =================
    company_style = ParagraphStyle(
        "company_style",
        parent=normal,
        fontName=base_font,
        fontSize=16,
        leading=18
    )

    # Company info formatting
    address = data['company']['address'].replace("\n", " ")

    if len(address) > 50:
        split_index = address.rfind(" ", 0, 50)
        if split_index == -1:
            split_index = 50
        address = address[:split_index] + "<br/>" + address[split_index + 1:]

    company_info = f"""
        {address}<br/>
        Phone : {data['company']['phone']}<br/>
        Email : {data['company']['email']}
    """

    # Right box
    right_box = [
        ["DATE", data['date']],
        [f"{pdf_type.upper()} ID", data['quote_no']],
        ["PO NUMBER", po_no],
        ["VALID UNTIL", data['valid_until']]
    ]

    right_table = Table(right_box, colWidths=[35 * mm, 40 * mm])
    right_table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
        ("ALIGN", (1, 0), (1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE")
    ]))

    # 🔥 FINAL HEADER (MERGED TABLE)
    header_full = Table([
        [
            Paragraph(f"<b>{data['company']['name']}</b>", company_style),
            Paragraph(
                f"<para alignment='right'><b><font color='#2F5597' size=16>{pdf_type}</font></b></para>",
                normal
            )
        ],
        [
            Paragraph(company_info, small),
            right_table
        ]
    ], colWidths=[120 * mm, 55 * mm])

    header_full.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("ALIGN", (1, 0), (1, 0), "RIGHT"),
            ("ALIGN", (1, 1), (1, 1), "RIGHT"),

            # Keep horizontal tight
            ("LEFTPADDING", (0, 0), (-1, -1), 0),
            ("RIGHTPADDING", (0, 0), (-1, -1), 0),

            # 👇 Add ONLY vertical breathing space
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]))

    elements.append(header_full)
    elements.append(Spacer(1, 12))

    # ================= CUSTOMER =================
    cust = data['customer']
    cust_table = Table([
        [Paragraph("<b><font color='white'>CUSTOMER</font></b>", normal)] if pdf_type != 'TAX INVOICE' else [Paragraph("<b><font color='white'>BILL TO</font></b>", normal)],
        [Paragraph(f"{cust['name']}<br/>{cust['company']}<br/>{cust['address']}<br/>{cust['phone']}", normal)]
    ], colWidths=[175 * mm])

    cust_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), BLUE),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.black)
    ]))

    elements.append(cust_table)
    elements.append(Spacer(1, 10))

    # ================= ITEMS =================
    items = [["Sr.No.", "Part No", "Description", "Price (Rs.)", "Qty", "Total Amount (Rs.)"]]
    cnt = 1
    for row in data['items']:
        items.append([
            str(cnt),
            str(row['no']) ,#if len(str(row['no'])) < 19 else str(row['no'])[:19]+'\n'+str(row['no'])[19:]
            row['part_desc'] if len(str(row['part_desc'])) < 26 else str(row['part_desc'])[:26]+'\n'+str(row['part_desc'])[26:],
            str(row['unit_price']),
            str(row['qty']),
            str(row['total_price'])
        ])
        cnt += 1

    item_table = Table(items, colWidths=[17 * mm, 58 * mm, 30 * mm, 23 * mm, 15 * mm, 32 * mm], repeatRows=1)

    item_table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.25, colors.black),
        ("BACKGROUND", (0, 0), (-1, 0), BLUE),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),

        # ✅ Header center
        ("ALIGN", (0, 0), (-1, 0), "CENTER"),

        # ✅ Sr.No
        ("ALIGN", (0, 1), (0, -1), "CENTER"),

        # ✅ Part No
        ("ALIGN", (1, 1), (1, -1), "CENTER"),

        # 🔥 IMPORTANT: Description LEFT
        ("ALIGN", (2, 1), (2, -1), "LEFT"),

        # ✅ Price & Total RIGHT
        ("ALIGN", (3, 1), (3, -1), "RIGHT"),
        ("ALIGN", (5, 1), (5, -1), "RIGHT"),

        # ✅ Qty CENTER
        ("ALIGN", (4, 1), (4, -1), "CENTER"),

        ("FONTNAME", (0, 0), (-1, -1), base_font),
        ("FONTSIZE", (0, 0), (-1, -1), 9)
    ]))

    elements.append(item_table)
    elements.append(Spacer(1, 10))

    # ================= TOTAL =================
    totals = [
        ["Subtotal (Rs.)", str(data['totals']['subtotal'])],
        ["Tax rate (%)", f"{data['totals']['tax_rate']}"],
        ["Tax due (Rs.)", str(data['totals']['tax_due'])],
        ["TOTAL (Rs.)", str(data['totals']['grand_total'])]
    ]

    total_table = Table(totals, colWidths=[40 * mm, 35 * mm], hAlign="RIGHT")

    total_table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.25, colors.black),
        ("ALIGN", (1, 0), (1, -1), "RIGHT"),
        ("BACKGROUND", (0, -1), (-1, -1), BLUE),
        ("TEXTCOLOR", (0, -1), (-1, -1), colors.white),
        ("FONTNAME", (0, 0), (-1, -1), base_font),
        ("FONTSIZE", (0, 0), (-1, -1), 9)
    ]))
    
    elements.append(KeepTogether([
            total_table,
            Spacer(1, 15)
        ]))
    
    amount_words = num2words(
        data['totals']['grand_total'],
        lang='en_IN'
    ).title() + " Rs. Only"
    
    amount_table = Table([
        [Paragraph("<b><font color='white'>TOTAL AMOUNT (IN WORDS)</font></b>", normal)],
        [Paragraph(amount_words, small)]
    ], colWidths=[175 * mm])

    amount_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), BLUE),   # Blue header
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.black)
    ]))

    elements.append(amount_table)
    elements.append(Spacer(1, 15))

    # ================= TERMS =================

    if pdf_type != "TAX INVOICE":

        # ================= TERMS HEADER =================

        terms_header = Table([
            [Paragraph("<b><font color='white'>TERMS AND CONDITIONS</font></b>", normal)]
        ], colWidths=[175 * mm])

        terms_header.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), BLUE),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("BOX", (0, 0), (-1, -1), 0.5, colors.black),
        ]))

        elements.append(terms_header)

        # ================= TERMS BODY =================

        terms_body = "<br/>".join(data['terms'])

        terms_paragraph = Paragraph(terms_body, small)

        terms_body_table = Table([
            [terms_paragraph]
        ], colWidths=[175 * mm])

        terms_body_table.setStyle(TableStyle([
            ("BOX", (0, 0), (-1, -1), 0.5, colors.black),

            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ]))

        elements.append(terms_body_table)
        elements.append(Spacer(1, 15))

    else:

        # ================= PAY TO =================

        firm_bank_name, firm_bank_acc, firm_bank_ifsc, firm_gst = Fetch_Bank_GST()

        pay_body = "<br/>".join([
            f"{data['company']['name']}",
            f"<br/><b>Bank Name:</b> {firm_bank_name}",
            f"<b>Account No:</b> {firm_bank_acc}",
            f"<b>IFSC Code:</b> {firm_bank_ifsc}",
            f"<b>GST No:</b> {firm_gst}",
        ])

        pay_table = Table([
            [Paragraph("<b><font color='white'>PAY TO</font></b>", normal)],
            [Paragraph(pay_body, small)]
        ], colWidths=[175 * mm])

        pay_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), BLUE),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("BOX", (0, 0), (-1, -1), 0.5, colors.black),

            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ]))

        elements.append(KeepTogether([
            pay_table,
            Spacer(1, 10),
        ]))

        # ================= TERMS HEADER =================

        terms_header = Table([
            [Paragraph("<b><font color='white'>TERMS AND CONDITIONS</font></b>", normal)]
        ], colWidths=[175 * mm])

        terms_header.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), BLUE),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("BOX", (0, 0), (-1, -1), 0.5, colors.black),
        ]))

        elements.append(terms_header)

        # ================= TERMS BODY =================

        terms_body = "<br/>".join(data['terms'])

        terms_paragraph = Paragraph(terms_body, small)

        terms_body_table = Table([
            [terms_paragraph]
        ], colWidths=[175 * mm])

        terms_body_table.setStyle(TableStyle([
            ("BOX", (0, 0), (-1, -1), 0.5, colors.black),

            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ]))

        elements.append(terms_body_table)
        elements.append(Spacer(1, 15))

    # ================= BOTTOM ALIGN =================
    
    doc.company_name = data['company']['name']
    # ================= BUILD =================
    def set_canvas_data(canvas, doc):
        canvas.company_name = doc.company_name
    doc.build(
            elements,
            onFirstPage=set_canvas_data,
            onLaterPages=set_canvas_data,
            canvasmaker=NumberedCanvas
        )

    os.startfile(filename)