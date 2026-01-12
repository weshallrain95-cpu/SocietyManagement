from django.template.loader import render_to_string
from django.conf import settings
from pathlib import Path
from weasyprint import HTML


def generate_share_certificate_pdf(context, filename):
    html = render_to_string(
        "documents/share_certificate.html",
        context,
    )

    output_dir = Path(settings.MEDIA_ROOT) / "generated"
    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = output_dir / filename
    HTML(string=html).write_pdf(target=str(output_path))

    return output_path
