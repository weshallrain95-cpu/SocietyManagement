import os

from django.conf import settings

from reportlab.platypus import (
    SimpleDocTemplate,
)

from reportlab.lib.units import mm

from statutory.document_engine.templates.maintenance_bill_template_v2 import (
    render_maintenance_bill_story,
)

from society.finance.maintenance.maintenance_bill_preview_context import (
    build_preview_bill_payload,
)


class MaintenanceBillArtifactGenerator:

    @staticmethod
    def generate(
        society,
        simulation,
        preview_flat,
    ):

        payload = (
            build_preview_bill_payload(
                society=society,
                simulation=simulation,
                preview_flat=preview_flat,
            )
        )


        folder = os.path.join(
            settings.MEDIA_ROOT,
            "maintenance_preview_artifacts",
        )

        os.makedirs(
            folder,
            exist_ok=True,
        )

        filename = (
            f"maintenance_preview_"
            f"{society.id}.pdf"
        )

        filepath = os.path.join(
            folder,
            filename,
        )

        document = SimpleDocTemplate(
            filepath,

            leftMargin=8 * mm,
            rightMargin=8 * mm,

            topMargin=8 * mm,
            bottomMargin=8 * mm,
        )

        story = (
            render_maintenance_bill_story(
                payload
            )
        )

        document.build(
            story
        )

        return filepath