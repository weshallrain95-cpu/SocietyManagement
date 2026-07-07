from io import BytesIO

import qrcode

from reportlab.lib.utils import ImageReader


def build_upi_uri(
    *,
    upi_id,
    payee_name,
    amount,
    transaction_note,
):
    """
    Build a standards-compliant UPI payment URI.
    """

    return (
        "upi://pay?"
        f"pa={upi_id}"
        f"&pn={payee_name}"
        f"&am={amount}"
        "&cu=INR"
        f"&tn={transaction_note}"
    )


def generate_upi_qr_image(
    *,
    upi_id,
    payee_name,
    amount,
    transaction_note,
):
    """
    Generate a QR image suitable for embedding
    directly into ReportLab PDFs.
    """

    uri = build_upi_uri(
        upi_id=upi_id,
        payee_name=payee_name,
        amount=amount,
        transaction_note=transaction_note,
    )

    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=8,
        border=2,
    )

    qr.add_data(uri)
    qr.make(fit=True)

    image = qr.make_image(
        fill_color="black",
        back_color="white",
    )

    buffer = BytesIO()

    image.save(
        buffer,
        format="PNG",
    )

    buffer.seek(0)

    return buffer