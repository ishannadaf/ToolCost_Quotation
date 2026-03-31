from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from tkinter import *
import ast
from tkinter import messagebox
# Register font
pdfmetrics.registerFont(TTFont('DejaVuSans', r"D:\\ToolCosting\\SupportFiles\\DejaVuSans.ttf"))
base_font = "DejaVuSans"
BLUE = colors.HexColor("#2F5597")
import os

def create_quotation_pdf(data, filename, pdf_type, master):
    messagebox.showinfo("Info", f"Opening your {pdf_type}...Click Ok.", parent=master)
    
    if isinstance(data, str):
        data = ast.literal_eval(data)
    
    po_no = ''
    if data['po_no'] == '':
        po_no = '--'
    else:
        po_no = data['po_no']
    #print("PO NUMBER:", data['po_no'])
    doc = SimpleDocTemplate(filename, pagesize=A4,
                            leftMargin=20*mm, rightMargin=20*mm,
                            topMargin=15*mm, bottomMargin=15*mm)
    styles = getSampleStyleSheet()
    normal = styles['Normal']; normal.fontName = base_font; normal.fontSize = 10
    small = ParagraphStyle("small", parent=normal, fontSize=9)

    elements = []

    # --- HEADER ---
    company_style = ParagraphStyle(
        "company_style",
        parent=normal,
        fontName=base_font,
        fontSize=16,          # <-- Bigger size
        leading=18,
        spaceAfter=6
    )

    header_table = Table([
        [Paragraph(f"<b>{data['company']['name']}</b>", company_style),
        Paragraph(f"<b><font color='#2F5597' size=16>{pdf_type}</font></b>", normal)]
    ], colWidths=[120*mm, 60*mm])
    header_table.setStyle(TableStyle([("VALIGN",(0,0),(-1,-1),"MIDDLE")]))
    elements.append(header_table)
    elements.append(Spacer(1,8))

    # --- Company Info & Quote Info ---
    
    address = data['company']['address'].replace("\n", " ")

    if len(address) > 50:
        split_index = address.rfind(" ", 0, 50)
        if split_index == -1:
            split_index = 50
        address = address[:split_index] + "<br/>" + address[split_index+1:]
    company_info = f"""
        {address}<br/>
        Phone : {data['company']['phone']}<br/>
        <br/>
        """

    right_box = [
        ["DATE", data['date']],
        [f"{pdf_type.upper()} ID", data['quote_no']],
        ["PO NUMBER", po_no],
        ["VALID UNTIL", data['valid_until']]
    ]
    right_table = Table(right_box, colWidths=[35*mm,40*mm])
    right_table.setStyle(TableStyle([
        ("GRID",(0,0),(-1,-1),0.5,colors.black),
        ("ALIGN",(1,0),(1,-1),"CENTER")
    ]))
    
    right_wrapper = Table([[right_table]], colWidths=[55*mm])
    right_wrapper.setStyle(TableStyle([
        ("ALIGN", (0,0), (-1,-1), "RIGHT")
    ]))

    header2 = Table(
        [[Paragraph(company_info, small), right_wrapper]],
        colWidths=[110*mm, 55*mm],
        hAlign="LEFT"
    )

    header2.setStyle(TableStyle([
        ("VALIGN", (0,0), (-1,-1), "TOP"),
        ("LEFTPADDING", (0,0), (-1,-1), 5),
        ("RIGHTPADDING", (0,0), (-1,-1), 5),
        ("ALIGN", (1,0), (1,0), "RIGHT"),  # ⭐ Push right table properly
    ]))
    elements.append(header2)
    elements.append(Spacer(1,10))

    # --- CUSTOMER SECTION ---
    cust = data['customer']
    cust_table = Table([
        [Paragraph("<b><font color='white'>CUSTOMER</font></b>", normal)],
        [Paragraph(f"{cust['name']}<br/>{cust['company']}<br/>{cust['address']}<br/>{cust['phone']}", normal)]
    ], colWidths=[165*mm])
    cust_table.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,0),BLUE),
        ("TEXTCOLOR",(0,0),(-1,0),colors.white),
        ("BOX",(0,0),(-1,-1),0.5,colors.black)
    ]))
    elements.append(cust_table)
    elements.append(Spacer(1,10))

    # --- ITEMS TABLE ---
    items = [["No","Description","Price (Rs.)","Qty","Total Amount (Rs.)"]]
    for row in data['items']:
        items.append([
            str(row['no']),
            row['part_desc'],
            str(row['unit_price']),
            str(row['qty']),
            # row.get("taxed",""),
            str(row['total_price'])
        ])

    item_table = Table(items, colWidths=[15*mm,70*mm,25*mm,20*mm,35*mm], repeatRows=1)
    item_table.setStyle(TableStyle([
        ("GRID",(0,0),(-1,-1),0.25,colors.black),
        ("BACKGROUND",(0,0),(-1,0),BLUE),
        ("TEXTCOLOR",(0,0),(-1,0),colors.white),
        ("ALIGN",(2,1),(-1,-1),"RIGHT"),
        ("ALIGN",(3,0),(3,-1),"CENTER"),
        ("FONTNAME",(0,0),(-1,-1),base_font),
        ("FONTSIZE",(0,0),(-1,-1),9)
    ]))
    elements.append(item_table)
    elements.append(Spacer(1,10))

    # --- TOTALS ---
    totals = [
        ["Subtotal (Rs.)", str(data['totals']['subtotal'])],
        ["Tax rate (%)", f"{data['totals']['tax_rate']}"],
        ["Tax due (Rs.)", str(data['totals']['tax_due'])],
        ["TOTAL (Rs.)", str(data['totals']['grand_total'])]
    ]
    total_table = Table(totals, colWidths=[50*mm,35*mm], hAlign="RIGHT")
    total_table.setStyle(TableStyle([
        ("GRID",(0,0),(-1,-1),0.25,colors.black),
        ("ALIGN",(1,0),(1,-1),"RIGHT"),
        ("BACKGROUND",(0,-1),(-1,-1),BLUE),
        ("TEXTCOLOR",(0,-1),(-1,-1),colors.white),
        ("FONTNAME",(0,0),(-1,-1),base_font),
        ("FONTSIZE",(0,0),(-1,-1),9)
    ]))
    elements.append(total_table)
    elements.append(Spacer(1,15))

    # --- TERMS ---
    terms_table = Table([
        [Paragraph("<b><font color='white'>TERMS AND CONDITIONS</font></b>", normal)],
        [Paragraph("<br/>".join(data['terms']), small)]
    ], colWidths=[165*mm])
    terms_table.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,0),BLUE),
        ("TEXTCOLOR",(0,0),(-1,0),colors.white),
        ("BOX",(0,0),(-1,-1),0.5,colors.black)
    ]))
    elements.append(terms_table)
    elements.append(Spacer(1,15))

    elements.append(Paragraph("Regards,", small))
    elements.append(Spacer(1,20))
    elements.append(Paragraph(data['company']['name'], normal))

    # --- FOOTER ---
    # elements.append(Paragraph("Customer Acceptance (sign below):", small))
    # elements.append(Spacer(1,20))
    # elements.append(Paragraph("x ___________________________________________", normal))
    # elements.append(Paragraph("Print Name:", normal))
    # elements.append(Spacer(1,20))
    # elements.append(Paragraph("<i>Thank You For Your Business!</i>", normal))

    doc.build(elements)
    
    os.startfile(r"D:\\ToolCosting\\Support Documents\\Tool_Quotation.pdf")

# -------------------------------
# SAMPLE DATA FOR TESTING
# -------------------------------
# if __name__ == "__main__":
#     sample = {
#         "company": {
#             "name":"Ghatage Patil Industries",
#             "address":"123 Street, Bangalore",
#             "website":"somedomain.com",
#             "phone":"000-000-0000",
#             "fax":"000-000-0000"
#         },
#         "date": datetime.today().strftime("%d-%m-%Y"),
#         "quote_no": "Q-2025-002",
#         "customer_id": "CUST-101",
#         "valid_until": "14-10-2025",
#         "prepared_by": "Sales Team",
#         "customer": {
#             "name":"Client Y",
#             "company":"ABC Ltd.",
#             "address":"45 Market Road",
#             "city":"City, ST ZIP",
#             "phone":"999-999-9999"
#         },
#         "items":[
#             {"no":1,"part_desc":"This is 1st Part","qty":1,"unit_price":644.75,"total_price":644.75,"taxed":""},
#             {"no":2,"part_desc":"This is 2nd Part","qty":2,"unit_price":5984.38,"total_price":11968.76,"taxed":"X"}
#         ],
#         "totals":{"subtotal":12613.51,"taxable":11968.76,"tax_rate":18.0,"tax_due":2270.43,"other":0,"grand_total":14883.94},
#         "terms":[
#             "1. Customer will be billed after indicating acceptance of this quote",
#             "2. Payment will be due prior to delivery of service and goods",
#             "3. Please fax or mail the signed price quote to the address above"
#         ]
#     }

#     create_exact_quotation(sample,"quotation_test.pdf")
#     print("Quotation PDF generated: quotation_test.pdf")
