import os
from django.conf import settings
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas


def generate_flat_bill_pdf(flat_bill):

    society = flat_bill.bill.society
    flat = flat_bill.flat
    month = flat_bill.bill.billing_month

    folder = os.path.join(settings.MEDIA_ROOT, "maintenance_bills")
    os.makedirs(folder, exist_ok=True)

    filename = f"{society.id}_{flat.id}_{month}.pdf"
    filepath = os.path.join(folder, filename)

    c = canvas.Canvas(filepath, pagesize=A4)

    y = 800

    # Society Header
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, y, society.name)

    y -= 40

    c.setFont("Helvetica", 11)
    c.drawString(50, y, f"Maintenance Bill")
    y -= 20

    c.drawString(50, y, f"Flat: {flat}")
    y -= 20

    c.drawString(50, y, f"Billing Month: {month}")

    y -= 40

    # Table Header
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "Charge")
    c.drawRightString(500, y, "Amount")

    y -= 10
    c.line(50, y, 500, y)

    y -= 25

    # Charge Lines
    c.setFont("Helvetica", 11)

    for line in flat_bill.lines.all():

        c.drawString(50, y, line.charge_name)
        c.drawRightString(500, y, f"{line.amount}")

        y -= 20

    # Non occupancy (if applicable)
    if flat_bill.non_occupancy_charge > 0:

        c.drawString(50, y, "Non Occupancy Charge")
        c.drawRightString(500, y, f"{flat_bill.non_occupancy_charge}")

        y -= 20

    y -= 10
    c.line(50, y, 500, y)

    y -= 25

    # Total
    c.setFont("Helvetica-Bold", 12)

    c.drawString(50, y, "Total Payable")
    c.drawRightString(500, y, f"{flat_bill.total_payable}")

    c.save()

    return filepath
    