from reportlab.lib import colors

from reportlab.lib.units import mm

from reportlab.lib.styles import getSampleStyleSheet

from reportlab.platypus import (
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

# ==========================================================
# SOCIETY OS
# MAINTENANCE BILL TEMPLATE
# ==========================================================
#
# PURPOSE
# -------
# Canonical maintenance bill layout.
#
# THIS TEMPLATE:
#
# ✔ Receives hydrated payload only
# ✔ Performs ZERO calculations
# ✔ Performs ZERO ORM queries
# ✔ Performs ZERO business logic
# ✔ Renders approved Option-1 design
#
# ==========================================================


def render_maintenance_bill_story(payload):

    styles = getSampleStyleSheet()

    story = []

    # ======================================================
    # HEADER
    # ======================================================

    story.extend(
        _build_header(
            payload,
            styles,
        )
    )

    story.append(
        Spacer(
            1,
            4 * mm,
        )
    )

    # ======================================================
    # MEMBER + BILL DETAILS
    # ======================================================

    story.extend(
        _build_member_section(
            payload,
            styles,
        )
    )

    story.append(
        Spacer(
            1,
            4 * mm,
        )
    )

    # ======================================================
    # SPECIAL RECOVERIES
    # ======================================================

    story.extend(
        _build_special_recoveries(
            payload,
            styles,
        )
    )

    story.append(
        Spacer(
            1,
            4 * mm,
        )
    )

    # ======================================================
    # BILL BREAKDOWN + SUMMARY
    # ======================================================

    story.extend(
        _build_bill_section(
            payload,
            styles,
        )
    )

    story.append(
        Spacer(
            1,
            4 * mm,
        )
    )

    # ======================================================
    # ACCOUNT POSITION
    # ======================================================

    story.extend(
        _build_account_position(
            payload,
            styles,
        )
    )

    story.append(
        Spacer(
            1,
            4 * mm,
        )
    )

    # ======================================================
    # PAYMENT BLOCK
    # ======================================================

    story.extend(
        _build_payment_section(
            payload,
            styles,
        )
    )

    return story


# ==========================================================
# SECTION BUILDERS
# ==========================================================

def _build_header(
    payload,
    styles,
):

    society = payload.get(
        "society",
        {},
    )

    bill = payload.get(
        "bill",
        {},
    )

    society_name = society.get(
        "name",
        "-",
    )

    society_address = society.get(
        "address",
        "-",
    )

    society_id = society.get(
        "id",
        "-",
    )

    billing_month = bill.get(
        "billing_month_label",
        "-",
    )

    title_style = styles["Title"]

    normal_style = styles["BodyText"]

    left_block = [

        Paragraph(
            f"<b>{society_name}</b>",
            title_style,
        ),

        Paragraph(
            society_address,
            normal_style,
        ),

        Paragraph(
            f"<b>Society ID:</b> {society_id}",
            normal_style,
        ),
    ]

    right_block = [

        Paragraph(
            "<b>MAINTENANCE BILL</b>",
            title_style,
        ),

        Paragraph(
            billing_month,
            normal_style,
        ),
    ]

    table = Table(

        [
            [
                left_block,
                right_block,
            ]
        ],

        colWidths=[
            110 * mm,
            60 * mm,
        ],
    )

    table.setStyle(

        TableStyle(

            [

                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "TOP",
                ),

                (
                    "ALIGN",
                    (1, 0),
                    (1, 0),
                    "RIGHT",
                ),
            ]
        )
    )

    return [table]



def _build_member_section(
    payload,
    styles,
):

    member = payload.get(
        "member",
        {},
    )

    bill = payload.get(
        "bill",
        {},
    )

    left_data = [

        [
            Paragraph(
                "<b>MEMBER & PROPERTY DETAILS</b>",
                styles["Heading4"],
            ),
            "",
        ],

        [
            "Member Name",
            member.get(
                "member_name",
                "-",
            ),
        ],

        [
            "Flat / Unit No.",
            member.get(
                "flat_number",
                "-",
            ),
        ],

        [
            "Wing / Block",
            member.get(
                "wing",
                "-",
            ),
        ],

        [
            "Floor",
            member.get(
                "floor",
                "-",
            ),
        ],

        [
            "Area",
            member.get(
                "area",
                "-",
            ),
        ],

        [
            "Occupancy Status",
            member.get(
                "occupancy_status",
                "-",
            ),
        ],
    ]

    right_data = [

        [
            Paragraph(
                "<b>BILL INFORMATION</b>",
                styles["Heading4"],
            ),
            "",
        ],

        [
            "Bill No.",
            bill.get(
                "bill_number",
                "-",
            ),
        ],

        [
            "Bill Date",
            bill.get(
                "bill_date",
                "-",
            ),
        ],

        [
            "Due Date",
            bill.get(
                "due_date",
                "-",
            ),
        ],

        [
            "Billing Period",
            bill.get(
                "billing_period",
                "-",
            ),
        ],

        [
            "Bill Category",
            bill.get(
                "bill_category",
                "Monthly Maintenance",
            ),
        ],

        [
            "Days In Period",
            bill.get(
                "days_in_period",
                "-",
            ),
        ],
    ]

    left_table = Table(
        left_data,
        colWidths=[
            35 * mm,
            55 * mm,
        ],
    )

    right_table = Table(
        right_data,
        colWidths=[
            35 * mm,
            55 * mm,
        ],
    )

    left_table.setStyle(

        TableStyle(

            [

                (
                    "SPAN",
                    (0, 0),
                    (1, 0),
                ),

                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, 0),
                    8,
                ),
            ]
        )
    )

    right_table.setStyle(

        TableStyle(

            [

                (
                    "SPAN",
                    (0, 0),
                    (1, 0),
                ),

                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, 0),
                    8,
                ),
            ]
        )
    )

    wrapper = Table(

        [
            [
                left_table,
                right_table,
            ]
        ],

        colWidths=[
            95 * mm,
            95 * mm,
        ],
    )

    wrapper.setStyle(

        TableStyle(

            [

                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "TOP",
                ),
            ]
        )
    )

    return [wrapper]


def _build_special_recoveries(
    payload,
    styles,
):

    special = payload.get(
        "special_recoveries",
        {},
    )

    non_occupancy_amount = special.get(
        "non_occupancy_amount",
        "0.00",
    )

    parking_total = special.get(
        "parking_total",
        "0.00",
    )

    parking_rows = special.get(
        "parking_rows",
        [],
    )

    total_special = special.get(
        "total_special_recovery",
        "0.00",
    )

    parking_data = [

        [
            "Vehicle Type",
            "Quantity",
            "Rate",
            "Amount",
        ]
    ]

    for row in parking_rows:

        parking_data.append(

            [

                row.get(
                    "vehicle_type",
                    "-",
                ),

                str(
                    row.get(
                        "quantity",
                        0,
                    )
                ),

                str(
                    row.get(
                        "rate",
                        "0.00",
                    )
                ),

                str(
                    row.get(
                        "amount",
                        "0.00",
                    )
                ),
            ]
        )

    parking_data.append(

        [

            "Total Parking Recovery",
            "",
            "",
            str(
                parking_total
            ),
        ]
    )

    parking_table = Table(

        parking_data,

        colWidths=[
            35 * mm,
            20 * mm,
            20 * mm,
            25 * mm,
        ],
    )

    parking_table.setStyle(

        TableStyle(

            [

                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.25,
                    colors.grey,
                ),

                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.whitesmoke,
                ),

                (
                    "FONTNAME",
                    (0, 0),
                    (-1, 0),
                    "Helvetica-Bold",
                ),

                (
                    "FONTNAME",
                    (0, -1),
                    (-1, -1),
                    "Helvetica-Bold",
                ),
            ]
        )
    )

    left_panel = [

        Paragraph(
            "<b>SPECIAL RECOVERIES</b>",
            styles["Heading4"],
        ),

        Spacer(
            1,
            2 * mm,
        ),

        Paragraph(
            "Additional recoveries applicable for this bill",
            styles["BodyText"],
        ),

        Spacer(
            1,
            4 * mm,
        ),

        Paragraph(
            "<b>NON OCCUPANCY CHARGES</b>",
            styles["BodyText"],
        ),

        Paragraph(
            f"₹ {non_occupancy_amount}",
            styles["Heading3"],
        ),
    ]

    right_panel = [

        Paragraph(
            "<b>PARKING RECOVERY (As Per Parking Contract)</b>",
            styles["BodyText"],
        ),

        Spacer(
            1,
            2 * mm,
        ),

        parking_table,
    ]

    total_panel = [

        Paragraph(
            "<b>TOTAL SPECIAL RECOVERY</b>",
            styles["BodyText"],
        ),

        Spacer(
            1,
            5 * mm,
        ),

        Paragraph(
            f"₹ {total_special}",
            styles["Heading2"],
        ),
    ]

    wrapper = Table(

        [

            [
                left_panel,
                right_panel,
                total_panel,
            ]
        ],

        colWidths=[
            55 * mm,
            85 * mm,
            40 * mm,
        ],
    )

    wrapper.setStyle(

        TableStyle(

            [

                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "TOP",
                ),

                (
                    "BOX",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.lightgrey,
                ),
            ]
        )
    )

    return [wrapper]


def _build_bill_section(
    payload,
    styles,
):

    charges = payload.get(
        "charges",
        [],
    )

    summary = payload.get(
        "summary",
        {},
    )

    bill_data = [

        [
            "#",
            "Nature Of Charges",
            "Basis",
            "Rate",
            "Amount",
        ]
    ]

    for index, row in enumerate(
        charges,
        start=1,
    ):

        bill_data.append(

            [

                str(index),

                row.get(
                    "name",
                    "-",
                ),

                row.get(
                    "basis",
                    "-",
                ),

                str(
                    row.get(
                        "rate",
                        "0.00",
                    )
                ),

                str(
                    row.get(
                        "amount",
                        "0.00",
                    )
                ),
            ]
        )

    bill_table = Table(

        bill_data,

        colWidths=[
            10 * mm,
            65 * mm,
            35 * mm,
            25 * mm,
            30 * mm,
        ],
    )

    bill_table.setStyle(

        TableStyle(

            [

                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.25,
                    colors.grey,
                ),

                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.whitesmoke,
                ),

                (
                    "FONTNAME",
                    (0, 0),
                    (-1, 0),
                    "Helvetica-Bold",
                ),

                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "MIDDLE",
                ),
            ]
        )
    )

    summary_data = [

        [
            "Core Maintenance Charges",
            summary.get(
                "core_maintenance_total",
                "0.00",
            ),
        ],

        [
            "Special Recoveries",
            summary.get(
                "special_recovery_total",
                "0.00",
            ),
        ],

        [
            "Gross Bill Amount",
            summary.get(
                "gross_bill_amount",
                "0.00",
            ),
        ],
    ]

    summary_table = Table(

        summary_data,

        colWidths=[
            55 * mm,
            35 * mm,
        ],
    )

    summary_table.setStyle(

        TableStyle(

            [

                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.25,
                    colors.grey,
                ),

                (
                    "FONTNAME",
                    (0, 0),
                    (-1, -1),
                    "Helvetica-Bold",
                ),
            ]
        )
    )

    wrapper = [

        Paragraph(
            "<b>BILL BREAKDOWN</b>",
            styles["Heading4"],
        ),

        Spacer(
            1,
            2 * mm,
        ),

        bill_table,

        Spacer(
            1,
            4 * mm,
        ),

        Paragraph(
            "<b>BILL SUMMARY</b>",
            styles["Heading4"],
        ),

        Spacer(
            1,
            2 * mm,
        ),

        summary_table,
    ]

    return wrapper


def _build_account_position(
    payload,
    styles,
):

    account = payload.get(
        "account_position",
        {},
    )

    account_data = [

        [
            "Previous Outstanding",
            account.get(
                "previous_outstanding",
                "0.00",
            ),
        ],

        [
            "Advance Balance",
            account.get(
                "advance_balance",
                "0.00",
            ),
        ],

        [
            "Interest Levied",
            account.get(
                "interest_levied",
                "0.00",
            ),
        ],

        [
            "Penalty Levied",
            account.get(
                "penalty_levied",
                "0.00",
            ),
        ],

        [
            "Recovery Charges",
            account.get(
                "recovery_charges",
                "0.00",
            ),
        ],

        [
            "Net Adjustment",
            account.get(
                "net_adjustment",
                "0.00",
            ),
        ],
    ]

    account_table = Table(

        account_data,

        colWidths=[
            70 * mm,
            40 * mm,
        ],
    )

    account_table.setStyle(

        TableStyle(

            [

                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.25,
                    colors.grey,
                ),

                (
                    "FONTNAME",
                    (0, -1),
                    (-1, -1),
                    "Helvetica-Bold",
                ),

                (
                    "BACKGROUND",
                    (0, -1),
                    (-1, -1),
                    colors.whitesmoke,
                ),
            ]
        )
    )

    net_payable = account.get(
        "net_payable",
        "0.00",
    )

    payable_table = Table(

        [

            [
                "NET PAYABLE",
                f"₹ {net_payable}",
            ]
        ],

        colWidths=[
            90 * mm,
            50 * mm,
        ],
    )

    payable_table.setStyle(

        TableStyle(

            [

                (
                    "BOX",
                    (0, 0),
                    (-1, -1),
                    1,
                    colors.black,
                ),

                (
                    "FONTNAME",
                    (0, 0),
                    (-1, -1),
                    "Helvetica-Bold",
                ),

                (
                    "FONTSIZE",
                    (0, 0),
                    (-1, -1),
                    12,
                ),

                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, -1),
                    colors.whitesmoke,
                ),
            ]
        )
    )

    return [

        Paragraph(
            "<b>ACCOUNT POSITION</b>",
            styles["Heading4"],
        ),

        Spacer(
            1,
            2 * mm,
        ),

        account_table,

        Spacer(
            1,
            4 * mm,
        ),

        payable_table,
    ]


def _build_payment_section(
    payload,
    styles,
):

    payment = payload.get(
        "payment",
        {},
    )

    notes = payload.get(
        "notes",
        [],
    )

    payment_data = [

        [
            "Bank Name",
            payment.get(
                "bank_name",
                "-",
            ),
        ],

        [
            "Account Number",
            payment.get(
                "account_number",
                "-",
            ),
        ],

        [
            "IFSC",
            payment.get(
                "ifsc",
                "-",
            ),
        ],

        [
            "UPI ID",
            payment.get(
                "upi_id",
                "-",
            ),
        ],
    ]

    payment_table = Table(

        payment_data,

        colWidths=[
            40 * mm,
            90 * mm,
        ],
    )

    payment_table.setStyle(

        TableStyle(

            [

                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.25,
                    colors.grey,
                ),

                (
                    "BACKGROUND",
                    (0, 0),
                    (0, -1),
                    colors.whitesmoke,
                ),

                (
                    "FONTNAME",
                    (0, 0),
                    (0, -1),
                    "Helvetica-Bold",
                ),
            ]
        )
    )

    story = [

        Paragraph(
            "<b>PAYMENT OPTIONS</b>",
            styles["Heading4"],
        ),

        Spacer(
            1,
            2 * mm,
        ),

        payment_table,
    ]

    if notes:

        story.extend(

            [

                Spacer(
                    1,
                    4 * mm,
                ),

                Paragraph(
                    "<b>NOTES</b>",
                    styles["Heading4"],
                ),
            ]
        )

        note_rows = []

        for note in notes:

            note_rows.append(

                [
                    f"• {note}"
                ]
            )

        notes_table = Table(

            note_rows,

            colWidths=[
                150 * mm,
            ],
        )

        notes_table.setStyle(

            TableStyle(

                [

                    (
                        "GRID",
                        (0, 0),
                        (-1, -1),
                        0.25,
                        colors.lightgrey,
                    ),
                ]
            )
        )

        story.append(
            notes_table
        )

    story.extend(

        [

            Spacer(
                1,
                6 * mm,
            ),

            Paragraph(
                "Generated by SocietyOS",
                styles["BodyText"],
            ),
        ]
    )

    return story