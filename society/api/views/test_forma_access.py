# society/api/views/test_forma_access.py

from rest_framework.decorators import api_view
from rest_framework.response import Response
import os

@api_view(["GET"])
def test_forma_access(request):
    society_id = request.GET.get("society_id")

    base_dir = "media/legal_documents"

    # find FORM A file for this society
    files = [
        f for f in os.listdir(base_dir)
        if f.startswith(f"FORM_A_MH_{society_id}")
    ]

    if not files:
        return Response({"error": "FORM A not found"})

    file_path = os.path.join(base_dir, files[0])

    # 🔥 TRY READING FILE
    with open(file_path, "r") as f:
        content = f.read()
        # 🔥 EXTRACT PROJECT NAME

        project_name = ""

        lines = content.split("\n")

        for i, line in enumerate(lines):
            if "NAME OF THE PROPOSED SOCIETY" in line:

                # 🔥 scan forward to find actual value
                for j in range(i + 1, len(lines)):
                    candidate = lines[j].strip()

                    if candidate and "----" not in candidate:
                        project_name = candidate
                        break

                break

        chief_promoter_name = ""

        for i, line in enumerate(lines):
            if "CHIEF PROMOTER DETAILS" in line:

                # scan forward to find "Name:"
                for j in range(i + 1, len(lines)):
                    candidate = lines[j].strip()

                    if candidate.startswith("Name:"):
                        chief_promoter_name = candidate.replace("Name:", "").strip()
                        break

                break

        meeting_date = ""

        for i, line in enumerate(lines):
            if "FIRST PROMOTERS MEETING" in line:

                for j in range(i + 1, len(lines)):
                    candidate = lines[j].strip()

                    if candidate.startswith("Date:"):
                        meeting_date = candidate.replace("Date:", "").strip()
                        break

                break

        committee_members = []

        capture = False

        for line in lines:
            clean = line.strip()

            # start capturing after header
            if "LIST OF PROMOTER MEMBERS" in clean:
                capture = True
                continue

            # skip header lines
            if capture and (
                "Sr. No." in clean
                or "----" in clean
                or clean == ""
            ):
                continue

            # stop if section ends
            if capture and clean.startswith("ENCLOSURES"):
                break

            if capture:
                parts = [p.strip() for p in clean.split("|")]

                if len(parts) >= 3:
                    sr_no = parts[0]
                    name = parts[1]

                    # extract flat number from address
                    address = parts[2]
                    flat_number = ""

                    if "Flat" in address:
                        flat_number = address.split(",")[0].replace("Flat", "").strip()

                    committee_members.append({
                        "sr_no": int(sr_no),
                        "name": name,
                        "flat_number": flat_number
                    })

            meeting_place = ""

            for i, line in enumerate(lines):
                if line.strip().startswith("Place:"):
                    meeting_place = line.replace("Place:", "").strip()
                    break

            project_address = ""

            for i, line in enumerate(lines):
                if "ADDRESS OF THE PROPOSED SOCIETY" in line:

                    # scan forward to first valid value
                    for j in range(i + 1, len(lines)):
                        candidate = lines[j].strip()

                        if candidate and "----" not in candidate:
                            project_address = candidate
                            break

                    break

        bank_name = ""
        bank_branch = ""

        for i, line in enumerate(lines):
            if "BANK ACCOUNT DETAILS" in line:

                for j in range(i + 1, len(lines)):
                    candidate = lines[j].strip()

                    if not candidate or "----" in candidate:
                        continue

                    if candidate.startswith("Bank Name:"):
                        bank_name = candidate.replace("Bank Name:", "").strip()

                    elif candidate.startswith("Branch:"):
                        bank_branch = candidate.replace("Branch:", "").strip()
                        break

                break                        

        registrar_office = ""

        for i, line in enumerate(lines):
            if line.strip() == "TO":

                # scan forward to find registrar line
                for j in range(i + 1, len(lines)):
                    candidate = lines[j].strip()

                    if not candidate or "----" in candidate:
                        continue

                    # first meaningful line = registrar designation
                    if "Registrar" in candidate:
                        next_line = ""

                        # try to capture next line (district)
                        if j + 1 < len(lines):
                            next_line = lines[j + 1].strip()

                        registrar_office = f"{candidate} {next_line}".strip()
                        break

                break



    return Response({
        "file_found": file_path,
        "project_name": project_name,
        "project_address": project_address,
        "registrar_office": registrar_office,
        "chief_promoter_name": chief_promoter_name,
        "bank_name": bank_name,
        "bank_branch": bank_branch,
        "meeting_date": meeting_date,
        "meeting_place": meeting_place,
        "committee_members": committee_members,
        "preview": content[:200],
    })