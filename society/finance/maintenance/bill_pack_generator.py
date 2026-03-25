import os
import zipfile

from django.conf import settings

from society.finance.maintenance.bill_generator import generate_flat_bill_pdf


def generate_society_bill_zip(bill):

    folder = os.path.join(settings.MEDIA_ROOT, "maintenance_bills")
    os.makedirs(folder, exist_ok=True)

    pdf_paths = []

    for flat_bill in bill.flatmaintenancebill_set.all():

        path = generate_flat_bill_pdf(flat_bill)
        pdf_paths.append(path)

    zip_filename = f"{bill.society.id}_{bill.billing_month}_maintenance_bills.zip"
    zip_path = os.path.join(folder, zip_filename)

    with zipfile.ZipFile(zip_path, "w") as zipf:

        for pdf in pdf_paths:
            arcname = os.path.basename(pdf)
            zipf.write(pdf, arcname)

    return zip_path
    