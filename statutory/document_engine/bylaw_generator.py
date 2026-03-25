from bylaws.models import BylawChapter, BylawClause


class BylawDocumentGenerator:

    @staticmethod
    def generate(society_data: dict, hooks: dict):

        lines = []

        # ---------------------------------------------------
        # HEADER
        # ---------------------------------------------------

        lines.append("BYE-LAWS")
        lines.append("")
        lines.append("OF")
        lines.append("")
        lines.append(society_data["society_name"])
        lines.append("")
        lines.append("Registered under the Maharashtra Cooperative Societies Act, 1960")
        lines.append("")
        lines.append(f"Registration Number: {society_data['registration_number']}")
        lines.append(f"Address: {society_data['registered_address']}")
        lines.append(f"District: {society_data['district']}")
        lines.append(f"Adopted on: {society_data['adoption_date']}")
        lines.append("")
        lines.append("=" * 60)
        lines.append("")

        # ---------------------------------------------------
        # GOVERNANCE PARAMETERS
        # ---------------------------------------------------

        lines.append("GOVERNANCE PARAMETERS")
        lines.append("")

        for key, value in hooks.items():
            label = key.replace("_", " ").title()
            lines.append(f"{label}: {value}")

        lines.append("")
        lines.append("=" * 60)
        lines.append("")

        # ---------------------------------------------------
        # LEGAL DEFINITIONS SECTION
        # ---------------------------------------------------

        lines.append("LEGAL DEFINITIONS")
        lines.append("-" * 60)
        lines.append("")

        definition_clauses = BylawClause.objects.filter(
            title__icontains="definition"
        ).order_by("sequence_order")

        for clause in definition_clauses:
            lines.append(f"{clause.title}")
            lines.append("")
            lines.append(clause.legal_text)
            lines.append("")

        lines.append("=" * 60)
        lines.append("")

        # ---------------------------------------------------
        # BY-LAW CANON
        # ---------------------------------------------------

        chapters = BylawChapter.objects.order_by("sequence_order")

        bylaw_counter = 1

        for chapter in chapters:

            lines.append("")
            lines.append(f"CHAPTER: {chapter.title}")
            lines.append("-" * 60)

            clauses = BylawClause.objects.filter(
                chapter=chapter
            ).order_by("sequence_order")

            for clause in clauses:

                lines.append("")
                lines.append(f"BYE-LAW {bylaw_counter}: {clause.title}")
                lines.append("")
                lines.append(clause.legal_text)

                bylaw_counter += 1

        # ---------------------------------------------------
        # SIGNATURE PAGE
        # ---------------------------------------------------

        lines.append("")
        lines.append("=" * 60)
        lines.append("")
        lines.append("CERTIFICATION")
        lines.append("")

        lines.append(
            f"Certified that the above Bye-laws were adopted in the first "
            f"general meeting of the promoters of "
            f"{society_data['society_name']}."
        )

        lines.append("")
        lines.append("Date: __________________________")
        lines.append("Place: _________________________")
        lines.append("")
        lines.append("Chief Promoter Signature:")
        lines.append("_______________________________")
        lines.append("")
        lines.append("Secretary Signature:")
        lines.append("_______________________________")
        lines.append("")
        lines.append("Promoter Members:")
        lines.append("")

        for i in range(1, 11):
            lines.append(f"{i}. _______________________________")

        lines.append("")
        lines.append("=" * 60)

        return "\n".join(lines)
