from reportlab.lib import colors

from reportlab.lib.units import mm

from reportlab.lib.styles import getSampleStyleSheet

from reportlab.platypus import (
    Paragraph,
    Table,
    TableStyle,
    Image,
)


def _zone(
    label,
    width,
    height,
    style,
):

    table = Table(

        [[
            Paragraph(
                label,
                style,
            )
        ]],

        colWidths=[
            width
        ],

        rowHeights=[
            height
        ],
    )

    table.setStyle(

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
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "MIDDLE",
                ),

                (
                    "ALIGN",
                    (0, 0),
                    (-1, -1),
                    "CENTER",
                ),
            ]
        )
    )

    return table


def render_maintenance_bill_story(payload):

    styles = getSampleStyleSheet()

    zone_style = styles["BodyText"]

    story = []

    # =====================================================
    # HEADER
    # =====================================================

    society = payload.get(
        "society",
        {},
    )

    bill = payload.get(
        "bill",
        {},
    )

    month_badge = Table(

        [[

            Paragraph(

                f"""
                <font
                    size="8"
                    color="#7A4D00"
                >
                For the Month of
                <b>{bill.get('billing_month_label', '-')}</b>
                </font>
                """,

                styles["BodyText"],
            )

        ]],

        colWidths=[
            42 * mm
        ],
    )
    month_badge.setStyle(

        TableStyle(

            [

                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, -1),
                    colors.HexColor("#F8E8D5"),
                ),

                (
                    "BOX",
                    (0, 0),
                    (-1, -1),
                    0.4,
                    colors.HexColor("#E4B87C"),
                ),

                (
                    "ALIGN",
                    (0, 0),
                    (-1, -1),
                    "CENTER",
                ),

                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    4,
                ),

                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    4,
                ),
            ]
        )
    )
    header_table = Table(

        [

            [

                Paragraph(

                    f"""
                    <font size="14">
                    <b>{society.get('name', '-')}</b>
                    </font>

                    <br/>

                    <font size="8">
                    {society.get('address', '-')}
                    </font>

                    <br/>

                    <font size="8">
                    Society ID: {society.get('id', '-')}
                    </font>
                    """,

                    styles["BodyText"],
                ),

                Paragraph(

                    f"""
                    <font
                        size="11"
                        color="#D08A3C"
                    >
                    <b>MAINTENANCE BILL</b>
                    </font>

                    <br/><br/>

                    <font
                        size="8"
                        color="#7A4D00"
                    >
                    For the Month of
                    {bill.get('billing_month_label', '-')}
                    </font>
                    """,

                    styles["BodyText"],
                ),
            ]
        ],

        colWidths=[
            135 * mm,
            55 * mm,
        ],

    )

    header_table.setStyle(

        TableStyle(

            [

                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "MIDDLE",
                ),

                (
                    "ALIGN",
                    (1, 0),
                    (1, 0),
                    "CENTER",
                ),
            ]
        )
    )

    story.append(
        header_table
    )
    story.append(
        Table(
            [[""]],
            rowHeights=[2 * mm],
        )
    )

    # =====================================================
    # MEMBER + BILL
    # =====================================================

    member = payload.get(
        "member",
        {},
    )

    bill = payload.get(
        "bill",
        {},
    )

    member_data = [

        [
            Paragraph(
                '<font size="8" color="#666666"><b>MEMBER & PROPERTY DETAILS</b></font>',
                styles["BodyText"],
            ),
        ],

        [
            f"Member: {member.get('member_name', '-')}",
        ],

        [
            f"Flat: {member.get('flat_number', '-')}",
        ],

        [
            f"Wing: {member.get('wing', '-')}",
        ],

        [
            f"Floor: {member.get('floor', '-')}",
        ],

        [
            f"Area: {member.get('area', '-')}",
        ],

        [
            f"Occupancy: {member.get('occupancy_status', '-')}",
        ],
    ]

    member_table = Table(

        member_data,

        colWidths=[
            90 * mm,
        ],
    )

    member_table.setStyle(

        TableStyle(

            [
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "TOP",
                ),

                (
                    "FONTSIZE",
                    (0, 1),
                    (-1, -1),
                    7,
                ),

                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    1,
                ),

                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    1,
                ),
            ]
        )
    )

    bill_data = [

        [
            Paragraph(
                '<font size="8" color="#666666"><b>BILL INFORMATION</b></font>',
                styles["BodyText"],
            ),
        ],

        [
            f"Bill No: {bill.get('bill_number', '-')}",
        ],

        [
            f"Bill Date: {bill.get('bill_date', '-')}",
        ],

        [
            f"Due Date: {bill.get('due_date', '-')}",
        ],

        [
            f"Billing Period: {bill.get('billing_period', '-')}",
        ],

        [
            f"Category: {bill.get('bill_category', '-')}",
        ],

        [
            f"Days: {bill.get('days_in_period', '-')}",
        ],
    ]

    bill_table = Table(

        bill_data,

        colWidths=[
            90 * mm,
        ],
    )

    bill_table.setStyle(

        TableStyle(

            [
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "TOP",
                ),

                (
                    "FONTSIZE",
                    (0, 1),
                    (-1, -1),
                    7,
                ),

                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    1,
                ),

                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    1,
                ),
            ]
        )
    )

    member_bill = Table(

        [

            [
                member_table,
                bill_table,
            ]
        ],

        colWidths=[
            95 * mm,
            95 * mm,
        ],

    )

    member_bill.setStyle(

        TableStyle(

            [

                (
                    "BOX",
                    (0, 0),
                    (-1, -1),
                    0.6,
                    colors.HexColor("#D6D6D6"),
                ),

                (
                    "LINEAFTER",
                    (0, 0),
                    (0, 0),
                    0.6,
                    colors.HexColor("#E0B57A"),
                ),

                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "TOP",
                ),

                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    8,
                ),

                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    8,
                ),

                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    2,
                ),

                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    2,
                ),
            ]
        )
    )

    story.append(member_bill)

    # =====================================================
    # RECOVERIES
    # =====================================================

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

    non_occ_panel = [

        [
            Paragraph(
                '<font color="#777777" size="7"><b>NON OCCUPANCY</b></font>',
                styles["BodyText"],
            )
        ],

        [
            Paragraph(
                "Applicable",
                styles["BodyText"],
            )
        ],

        [
            Paragraph(
                f'<font size="9"><b>₹ {non_occupancy_amount}</b></font>',
                styles["BodyText"],
            )
        ],
    ]

    non_occ_table = Table(
        non_occ_panel,
        colWidths=[43 * mm],
    )

    non_occ_table.setStyle(

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

    parking_data = [

        [
            "Vehicle",
            "Qty",
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

            "Total",
            "",
            "",
            str(parking_total),
        ]
    )

    parking_table = Table(

    parking_data,

        colWidths=[
            25 * mm,
            15 * mm,
            20 * mm,
            20 * mm,
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
                    colors.lightgrey,
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
                (
                    "FONTSIZE",
                    (0, 0),
                    (-1, -1),
                    6,
                ),

                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    1,
                ),

                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    1,
                ),
            ]
        )
    )

    parking_panel = Table(

        [

            [
                Paragraph(
                    '<font color="#777777" size="7"><b>PARKING RECOVERY</b></font>',
                    styles["BodyText"],
                )
            ],

            [
                parking_table
            ],
        ],

        colWidths=[
            93 * mm
        ],
    )

    total_panel = Table(

        [

            [
                Paragraph(
                    '<font color="#777777" size="7"><b>TOTAL RECOVERY</b></font>',
                    styles["BodyText"],
                )
            ],

            [
                Paragraph(
                    f'<font size="10"><b>₹ {total_special}</b></font>',
                    styles["BodyText"],
                )
            ],
        ],

        colWidths=[
            48 * mm
        ],
    )

    total_panel.setStyle(

        TableStyle(

            [

            ]
        )
    )

    recoveries = Table(

        [

            [

                non_occ_table,

                parking_panel,

                total_panel,
            ]
        ],

        colWidths=[

            45 * mm,

            95 * mm,

            50 * mm,
        ],
    )

    recoveries.setStyle(

        TableStyle(

            [

                (
                    "BOX",
                    (0, 0),
                    (-1, -1),
                    0.6,
                    colors.HexColor("#D6D6D6"),
                ),

                (
                    "LINEAFTER",
                    (0, 0),
                    (0, 0),
                    0.3,
                    colors.HexColor("#E6E6E6"),
                ),

                (
                    "LINEAFTER",
                    (1, 0),
                    (1, 0),
                    0.3,
                    colors.HexColor("#E6E6E6"),
                ),

                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "TOP",
                ),

                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    6,
                ),

                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    6,
                ),

                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    2,
                ),

                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    2,
                ),
            ]
        )
    )

    story.append(
        recoveries
    )

    # =====================================================
    # SUMMARY RAIL
    # =====================================================

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

                f"{float(row.get('amount', 0)):,.2f}",
            ]
        )

    breakdown_table = Table(

        bill_data,

        colWidths=[
            8 * mm,
            68 * mm,
            28 * mm,
            14 * mm,
            16 * mm,
        ]
    )

    breakdown_table.setStyle(

        TableStyle(

            [

                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.25,
                    colors.lightgrey,
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
                    "FONTSIZE",
                    (0, 0),
                    (-1, -1),
                    7,
                ),
            ]
        )
    )

    
    due_date = bill.get(
        "due_date",
        "-",
    )
    
    summary_rail = Table(

        [

            [
                Paragraph(
                    "<b>SUMMARY</b>",
                    styles["BodyText"],
                )
            ],

            [
                Paragraph(
                    f"""
                    Core Charges<br/>
                    ₹ {float(summary.get('core_maintenance_total', 0)):,.2f}
                    """,
                    styles["BodyText"],
                )
            ],

            [
                Paragraph(
                    f"""
                    Special Recovery<br/>
                    ₹ {float(summary.get('special_recovery_total', 0)):,.2f}
                    """,
                    styles["BodyText"],
                )
            ],

            [
                Paragraph(
                    f"""
                    Gross Amount<br/>
                    ₹ {float(summary.get('gross_bill_amount', 0)):,.2f}
                    """,
                    styles["BodyText"],
                )
            ],

            [
                Paragraph(

                    f"""
                    <font size="8">
                    Due Date
                    </font>
                    <br/>
                    <b>{due_date}</b>
                    """,

                    styles["BodyText"],
                )
            ],
        ],

        colWidths=[
            42 * mm
        ],
    )

    summary_rail.setStyle(

        TableStyle(

            [

                (
                    "BOX",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.HexColor("#D6D6D6"),
                ),

                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.HexColor("#D6D6D6"),
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

    breakdown_panel = Table(

        [

            [
                Paragraph(
                    "<b>BILL BREAKDOWN</b>",
                    styles["Heading3"],
                )
            ],

            [
                breakdown_table
            ],
        ],

        colWidths=[
            148 * mm
        ],
    )

    main_content = Table(

        [

            [

                breakdown_panel,

                summary_rail,
            ]
        ],

        colWidths=[

            145 * mm,

            45 * mm,
        ],
    )

    main_content.setStyle(

        TableStyle(

            [

                (
                    "BOX",
                    (0, 0),
                    (-1, -1),
                    0.6,
                    colors.HexColor("#D6D6D6"),
                ),

                (
                    "LINEAFTER",
                    (0, 0),
                    (0, 0),
                    0.3,
                    colors.HexColor("#E6E6E6"),
                ),

                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "TOP",
                ),

                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    6,
                ),

                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    6,
                ),
            ]
        )
    )

    story.append(
        main_content
    )

    # =====================================================
    # ACCOUNT + NOTES
    # =====================================================

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
        
        [
            "Net Payable",
            account.get(
                "net_payable",
                "0.00",
            ),
        ],
    ]


    account_table = Table(

        account_data,

        colWidths=[
            42 * mm,
            20 * mm,
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
                    colors.lightgrey,
                ),

                (
                    "FONTSIZE",
                    (0, 0),
                    (-1, -1),
                    7,
                ),
            ]
        )
    )

    notes = [

        "Please make the payment before the due date to avoid late fee.",

        "This is a system generated bill and does not require a signature.",

        "For any queries, please contact the society office.",
    ]

    notes_rows = [

        [
            Paragraph(
                '<font color="#777777"><b>NOTES</b></font>',
                styles["BodyText"],
            )
        ]
    ]

    for note in notes:

        notes_rows.append(

            [
                Paragraph(
                    f"• {note}",
                    styles["BodyText"],
                )
            ]
        )

    notes_table = Table(

        notes_rows,

        colWidths=[
            118 * mm
        ],
    )

    notes_table.setStyle(

        TableStyle(

            [

                (
                    "FONTSIZE",
                    (0, 0),
                    (-1, -1),
                    7,
                ),
            ]
        )
    )

    account_panel = Table(

        [

            [
                Paragraph(
                    "<b>ACCOUNT POSITION</b>",
                    styles["BodyText"],
                )
            ],

            [
                account_table
            ],
        ],

        colWidths=[
            67 * mm
        ],
    )

    notes_panel = Table(

        [

            [
                notes_table
            ]
        ],

        colWidths=[
            123 * mm
        ],
    )

    account_notes = Table(

        [

            [

                account_panel,

                notes_panel,
            ]
        ],

        colWidths=[

            67 * mm,

            123 * mm,
        ],
    )

    account_notes.setStyle(

        TableStyle(

            [

                (
                    "BOX",
                    (0, 0),
                    (-1, -1),
                    0.6,
                    colors.HexColor("#D6D6D6"),
                ),

                (
                    "LINEAFTER",
                    (0, 0),
                    (0, 0),
                    0.3,
                    colors.HexColor("#E6E6E6"),
                ),

                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "TOP",
                ),

                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    6,
                ),

                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    6,
                ),
            ]
        )
    )

    story.append(
        account_notes
    )

    # =====================================================
    # PAYMENT
    # =====================================================

    payment_info = payload.get(
        "payment",
        {},
    )

    bank_name = payment_info.get(
        "bank_name",
        "Not Configured",
    )

    account_number = payment_info.get(
        "account_number",
        "Not Configured",
    )

    ifsc = payment_info.get(
        "ifsc",
        "Not Configured",
    )

    upi_id = payment_info.get(
        "upi_id",
        "Not Configured",
    )

    qr_image = payment_info.get(
        "qr_image",
    )

    qr_panel = Table(

        [

            [
                Paragraph(
                    '<font size="7" color="#777777"><b>QR PAYMENT</b></font>',
                    styles["BodyText"],
                )
            ],

            [
                Image(
                    qr_image,
                    width=32 * mm,
                    height=32 * mm,
                )
                if qr_image
                else
                Paragraph(
                    """
                    <font size="6">
                    QR Not Configured

                    <br/>

                    Use Bank Transfer
                    </font>
                    """,
                    styles["BodyText"],
                )
            ],
        ],

        colWidths=[
            45 * mm
        ],
    )

    bank_panel = Table(

        [

            [
                Paragraph(
                    '<font size="7" color="#777777"><b>BANK TRANSFER</b></font>',
                    styles["BodyText"],
                )
            ],

            [
                Paragraph(
                    f'<font size="6">Bank Name: {bank_name}</font>',
                    styles["BodyText"],
                )
            ],

            [
                Paragraph(
                    f'<font size="6">Account No: {account_number}</font>',
                    styles["BodyText"],
                )
            ],

            [
                Paragraph(
                    f'<font size="6">IFSC: {ifsc}</font>',
                    styles["BodyText"],
                )
            ],

            [
                Paragraph(
                    f'<font size="6">UPI ID: {upi_id}</font>',
                    styles["BodyText"],
                )
            ],
        ],

        colWidths=[
            95 * mm
        ],

        rowHeights=[
            4 * mm,
            3 * mm,
            3 * mm,
            3 * mm,
            3 * mm,
        ],
    )

    other_panel = Table(

        [

            [
                Paragraph(
                    '<font size="7" color="#777777"><b>OTHER MODES</b></font>',
                    styles["BodyText"],
                )
            ],

            [
                Paragraph(

                    """
                    <font size="6">

                    Cheque / DD

                    <br/>

                    Society Office

                    <br/>

                    Treasurer

                    </font>
                    """,

                    styles["BodyText"],
                )
            ],
        ],

        colWidths=[
            45 * mm
        ],
    )

    payment = Table(

        [

            [

                qr_panel,

                bank_panel,

                other_panel,
            ]
        ],

        colWidths=[

            45 * mm,

            100 * mm,

            45 * mm,
        ],
    )

    payment.setStyle(

        TableStyle(

            [

                (
                    "BOX",
                    (0, 0),
                    (-1, -1),
                    0.6,
                    colors.HexColor("#D6D6D6"),
                ),

                (
                    "LINEAFTER",
                    (0, 0),
                    (0, 0),
                    0.3,
                    colors.HexColor("#E6E6E6"),
                ),

                (
                    "LINEAFTER",
                    (1, 0),
                    (1, 0),
                    0.3,
                    colors.HexColor("#E6E6E6"),
                ),

                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "TOP",
                ),

                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    2,
                ),

                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    2,
                ),
            ]
        )
    )

    story.append(
        payment
    )

    footer = Table(

        [[

            Paragraph(

                """
                Thank you for being a valued member of the society.
                """,

                styles["BodyText"],
            )

        ]],

        colWidths=[
            190 * mm
        ],
    )

    footer.setStyle(

        TableStyle(

            [

                (
                    "ALIGN",
                    (0, 0),
                    (-1, -1),
                    "CENTER",
                ),

                (
                    "TEXTCOLOR",
                    (0, 0),
                    (-1, -1),
                    colors.grey,
                ),

                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    4,
                ),
            ]
        )
    )

    story.append(
        footer
    )

    return story