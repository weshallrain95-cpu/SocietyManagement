from bylaws.models import BylawChapter, BylawClause
import re

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

        # 🔥 FORCE SAME VALUES USED IN CLAUSES
        def get_value(key, fallback=None):
            val = hooks.get(key)
            return val if val is not None else fallback

        lines.append(f"Share Value: {get_value('share_value')}")
        lines.append(f"Minimum Shares Per Member: {get_value('minimum_shares_per_member')}")
        lines.append(f"Entrance Fee: {get_value('entrance_fee')}")
        lines.append(f"Maintenance Charge Basis: {get_value('maintenance_charge_basis')}")
        lines.append(f"Sinking Fund Percent: {get_value('sinking_fund_percent')}")
        lines.append(f"Repair Fund Percent: {get_value('repair_fund_percent')}")
        lines.append(f"Late Payment Interest Percent: {get_value('late_payment_interest_percent')}")
        lines.append(f"Non Occupancy Charge Percent: {get_value('non_occupancy_charge_percent')}")
        lines.append(f"Committee Size: {get_value('committee_size')}")
        lines.append(f"Committee Term Years: {get_value('committee_term_years')}")
        lines.append(f"Quorum General Body Percent: {get_value('quorum_general_body_percent')}")
        lines.append(f"Redevelopment Consent Percent: {get_value('redevelopment_consent_percent')}")

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

                # 🔥 GOVERNANCE INJECTION — FIXED (REPLACE NOT APPEND)

                
                if title == "entrance fee and share capital":
                    new_text = re.sub(
                        r"Entrance fee.*shares\.",
                        f"Entrance fee shall be Rs. {hooks.get('entrance_fee')} payable at the time of admission.\n"
                        f"Each share shall have a face value of Rs. {hooks.get('share_value')} and each member shall subscribe to a minimum of {hooks.get('minimum_shares_per_member')} shares.",
                        text,
                        flags=re.DOTALL,
                    )
                    text = new_text if new_text != text else text + "\n\n" + \
                        f"Entrance fee shall be Rs. {hooks.get('entrance_fee')} payable at the time of admission.\n" + \
                        f"Each share shall have a face value of Rs. {hooks.get('share_value')} and each member shall subscribe to a minimum of {hooks.get('minimum_shares_per_member')} shares."

                elif title in [
                    "intimation of tenant occupation",
                    "applicability of bye-laws to tenants",
                ]:
                    allowed = hooks.get("subletting_allowed")

                    if allowed == "no":
                        text += "\nSubletting of flats is not permitted without prior approval of the Society."
                    elif allowed == "yes":
                        text += "\nSubletting of flats is permitted subject to Society rules and intimation requirements."

                elif title == "transfer of shares and interest":
                    fee = hooks.get("transfer_fee")
                    if fee:
                        text += f"\nThe Society shall charge a transfer fee of Rs. {fee} as per applicable rules."

                elif title == "levy of non-occupancy charges":
                    if hooks.get("non_occupancy_mode") == "fixed_amount":
                        text = f"Non-occupancy charges shall be Rs. {hooks.get('non_occupancy_charge_fixed')} per month."
                    else:
                        text = f"Non-occupancy charges shall be {hooks.get('non_occupancy_charge_percent')}% of the service charges."

                elif title == "levy of maintenance charges":
                    basis_map = {
                        "flat_area": "based on flat area (sq. ft.)",
                        "equal": "equally among all members",
                        "hybrid": "as decided by the General Body",
                    }
                    basis = basis_map.get(hooks.get("maintenance_charge_basis"))

                    new_text = re.sub(
                        r"Maintenance charges.*\.",
                        f"Maintenance charges shall be levied {basis}.",
                        text,
                    )
                    text = new_text if new_text != text else text + "\n\n" + \
                        f"Maintenance charges shall be levied {basis}."


                elif title == "interest on arrears":
                    new_text = re.sub(
                        r"Interest.*\.",
                        f"Interest at the rate of {hooks.get('late_payment_interest_percent')}% per annum shall be charged on arrears.",
                        text,
                    )
                    text = new_text if new_text != text else text + "\n\n" + \
                        f"Interest at the rate of {hooks.get('late_payment_interest_percent')}% per annum shall be charged on arrears."


                elif title == "sinking fund":
                    new_text = re.sub(
                        r"Members shall contribute.*\.",
                        f"Members shall contribute {hooks.get('sinking_fund_percent')}% towards the sinking fund.",
                        text,
                    )
                    text = new_text if new_text != text else text + "\n\n" + \
                        f"Members shall contribute {hooks.get('sinking_fund_percent')}% towards the sinking fund."

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
