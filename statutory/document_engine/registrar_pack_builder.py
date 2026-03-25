import os
import zipfile

from django.conf import settings

from statutory.models import SocietyLegalDocument


class RegistrarPackBuilder:

    REQUIRED_ARTIFACTS = [
        "REGISTRAR_SUBMISSION_LETTER_MH",
        "FORM_A_MH",
        "BYLAW_DRAFT_MH",
        "PROVISIONAL_COMMITTEE_RESOLUTION_MH",
        "FIRST_GENERAL_MEETING_MINUTES_MH",
        "PROMOTER_CONSENT_LETTER_MH",
        "BUILDER_DOCUMENT_NOTICE_MH",
        "BANK_ACCOUNT_LETTER_MH",
    ]

    ORDERED_FILES = [
        "REGISTRAR_SUBMISSION_LETTER_MH",
        "FORM_A_MH",
        "BYLAW_DRAFT_MH",
        "PROVISIONAL_COMMITTEE_RESOLUTION_MH",
        "FIRST_GENERAL_MEETING_MINUTES_MH",
        "PROMOTER_CONSENT_LETTER_MH",
        "BUILDER_DOCUMENT_NOTICE_MH",
        "BANK_ACCOUNT_LETTER_MH",
    ]

    @staticmethod
    def validate_pack(society):

        missing = []

        for code in RegistrarPackBuilder.REQUIRED_ARTIFACTS:

            exists = SocietyLegalDocument.objects.filter(
                society=society,
                template__artifact_code=code
            ).exists()

            if not exists:
                missing.append(code)

        if missing:
            raise ValueError(
                f"Registrar pack cannot be built. Missing artifacts: {missing}"
            )

    @staticmethod
    def collect_documents(society):

        documents = {}

        for code in RegistrarPackBuilder.ORDERED_FILES:

            doc = SocietyLegalDocument.objects.get(
                society=society,
                template__artifact_code=code
            )

            documents[code] = doc

        return documents

    @staticmethod
    def build_zip_pack(society):

        RegistrarPackBuilder.validate_pack(society)

        docs = RegistrarPackBuilder.collect_documents(society)

        # Correct directory
        pack_dir = os.path.join(settings.MEDIA_ROOT, "legal_documents")

        os.makedirs(pack_dir, exist_ok=True)

        zip_name = f"registrar_pack_society_{society.id}.zip"

        zip_path = os.path.join(pack_dir, zip_name)

        with zipfile.ZipFile(zip_path, "w") as z:

            for code in RegistrarPackBuilder.ORDERED_FILES:

                doc = docs[code]

                file_path = doc.file.path
                filename = os.path.basename(file_path)

                z.write(file_path, filename)

        return zip_path