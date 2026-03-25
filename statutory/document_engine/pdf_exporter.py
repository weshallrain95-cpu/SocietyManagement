from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.styles import ParagraphStyle


class LegalPDFExporter:

    @staticmethod
    def export(document_text: str, filename: str):

        styles = getSampleStyleSheet()

        body = ParagraphStyle(
            "body",
            parent=styles["Normal"],
            fontSize=11,
            leading=16,
        )

        title = ParagraphStyle(
            "title",
            parent=styles["Heading1"],
            fontSize=18,
            spaceAfter=20,
        )

        elements = []

        for line in document_text.split("\n"):

            if not line.strip():
                elements.append(Spacer(1, 8))
                continue

            if line.isupper():
                elements.append(Paragraph(line, title))
            else:
                elements.append(Paragraph(line, body))

        pdf = SimpleDocTemplate(
            filename,
            pagesize=A4,
            rightMargin=2 * cm,
            leftMargin=2 * cm,
            topMargin=2 * cm,
            bottomMargin=2 * cm,
        )

        pdf.build(elements)

        return filename
        