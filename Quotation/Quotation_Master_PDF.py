from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import ast

# Register font
pdfmetrics.registerFont(TTFont('DejaVuSans', r"D:\\ToolCosting\\SupportFiles\\DejaVuSans.ttf"))
base_font = "DejaVuSans"
BLUE = colors.HexColor("#2F5597")

def currency(x): return f"{x:,.2f} rs."

def create_quotation_pdf(data, filename, pdf_type):
    if isinstance(data, str):
        data = ast.literal_eval(data)
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
    company_info = f"""{data['company']['address']}<br/>
Phone: {data['company']['phone']}<br/>
Prepared by: {data['prepared_by']}"""

    right_box = [
        ["DATE", data['date']],
        [f"{pdf_type.upper()} ID", data['quote_no']],
        ["VALID UNTIL", data['valid_until']]
    ]
    right_table = Table(right_box, colWidths=[35*mm,40*mm])
    right_table.setStyle(TableStyle([
        ("GRID",(0,0),(-1,-1),0.5,colors.black),
        ("ALIGN",(1,0),(1,-1),"CENTER")
    ]))

    header2 = Table([[Paragraph(company_info, small), right_table]], colWidths=[110*mm,55*mm])
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
    items = [["No","Description","Unit Price","Qty","Taxed","Total Amount"]]
    for row in data['items']:
        items.append([
            str(row['no']),
            row['part_desc'],
            currency(row['unit_price']),
            str(row['qty']),
            row.get("taxed",""),
            currency(row['total_price'])
        ])

    item_table = Table(items, colWidths=[15*mm,60*mm,25*mm,20*mm,20*mm,25*mm], repeatRows=1)
    item_table.setStyle(TableStyle([
        ("GRID",(0,0),(-1,-1),0.25,colors.black),
        ("BACKGROUND",(0,0),(-1,0),BLUE),
        ("TEXTCOLOR",(0,0),(-1,0),colors.white),
        ("ALIGN",(2,1),(-1,-1),"RIGHT"),
        ("FONTNAME",(0,0),(-1,-1),base_font),
        ("FONTSIZE",(0,0),(-1,-1),9)
    ]))
    elements.append(item_table)
    elements.append(Spacer(1,10))

    # --- TOTALS ---
    totals = [
        ["Subtotal", currency(data['totals']['subtotal'])],
        ["Taxable", currency(data['totals']['taxable'])],
        ["Tax rate", f"{data['totals']['tax_rate']}%"],
        ["Tax due", currency(data['totals']['tax_due'])],
        ["Other", currency(data['totals']['other'])],
        ["TOTAL", currency(data['totals']['grand_total'])]
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

    # --- FOOTER ---
    elements.append(Paragraph("Customer Acceptance (sign below):", small))
    elements.append(Spacer(1,20))
    elements.append(Paragraph("x ___________________________________________", normal))
    elements.append(Paragraph("Print Name:", normal))
    elements.append(Spacer(1,20))
    elements.append(Paragraph("<i>Thank You For Your Business!</i>", normal))

    doc.build(elements)


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
