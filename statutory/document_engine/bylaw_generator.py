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
        reg_no = society_data.get("registration_number")
        if reg_no:
            lines.append(f"Registration Number: {reg_no}")
        else:
            lines.append("Registration Status: Under Registration")
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

                text = clause.legal_text
                title = clause.title.strip().lower()

                # 🔥 GOVERNANCE INJECTION (FINAL)

                if title == "entrance fee and share capital":
                    text += f"\n\nEntrance fee shall be Rs. {hooks.get('entrance_fee')} payable at the time of admission."
                    text += f"\nEach share shall have a face value of Rs. {hooks.get('share_value')} and each member shall subscribe to a minimum of {hooks.get('minimum_shares_per_member')} shares."

                elif title == "levy of maintenance charges":
                    basis_map = {
                        "flat_area": "based on flat area (sq. ft.)",
                        "equal": "equally among all members",
                        "hybrid": "as decided by the General Body",
                    }
                    basis = basis_map.get(hooks.get("maintenance_charge_basis"))
                    text += f"\n\nMaintenance charges shall be levied {basis}."

                elif title == "interest on arrears":
                    text += f"\n\nInterest at the rate of {hooks.get('late_payment_interest_percent')}% per annum shall be charged on arrears."

                elif title == "sinking fund":
                    text += f"\n\nMembers shall contribute {hooks.get('sinking_fund_percent')}% towards the sinking fund."

                elif title == "levy of non-occupancy charges":
                    text += f"\n\nNon-occupancy charges shall be {hooks.get('non_occupancy_charge_percent')}% of the service charges."

                lines.append(text)

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
