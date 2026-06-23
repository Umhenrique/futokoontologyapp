# -*- coding: utf-8 -*-
"""
Generate English translations of the Japanese student understanding/support sheets.
Maintains the exact 5-page form structure and visual layout as the originals.
Uses English placeholders instead of Japanese glyphs to avoid rendering bugs.
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Flowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
import os

W, H = A4  # A4 size: 595.27 x 841.89 points
PAGE_W = W - 24*mm  # Margins: 12mm on each side. Usable width: 186mm
grades = ["Yr", "E1", "E2", "E3", "E4", "E5", "E6", "M1", "M2", "M3", "H1", "H2", "H3", "H4"]

# Global table column widths
abs_col_widths = [56*mm] + [10*mm]*13
plan_col_widths = [20*mm, 20*mm, 45*mm, 60*mm, 41*mm]
role_col_widths = [10*mm, 46*mm, 65*mm, 65*mm]

styles = getSampleStyleSheet()

# ── Colors ──────────────────────────────────────────────────────────
CREAM = colors.HexColor("#FFFDE0")       # Legend/input fields color on page 1
LIGHT_BLUE = colors.HexColor("#E1ECF7")  # Auto-populated fields background
PEACH = colors.HexColor("#FCE4D6")       # Page 2/3 peach row
WARM_GREY = colors.HexColor("#F0EFEA")   # Table headers background
WHITE = colors.white
BLACK = colors.black

# ── Custom Paragraph Styles ──────────────────────────────────────────
def S(name, **kw):
    base = kw.pop("parent", "Normal")
    s = ParagraphStyle(name, parent=styles[base], **kw)
    return s

title_style   = S("Title2",   fontSize=11, fontName="Helvetica-Bold", leading=14, alignment=TA_CENTER, spaceAfter=2)
header_style  = S("Header2",  fontSize=8.5, leading=11, alignment=TA_CENTER)
normal_style  = S("Normal2",  fontSize=8,  leading=10)
small_style   = S("Small2",   fontSize=7,  leading=9)
section_style = S("Section2", fontSize=8.5, leading=11, fontName="Helvetica-Bold")
note_style    = S("Note2",    fontSize=6.5, leading=8.5, textColor=colors.grey)

# ── Custom Flowables ───────────────────────────────────────────────
class DiagonalLine(Flowable):
    """Draws a diagonal line from bottom-left to top-right of a merged cell."""
    def __init__(self, w, h):
        super().__init__()
        self.w = w
        self.h = h

    def wrap(self, availWidth, availHeight):
        return self.w, self.h

    def draw(self):
        self.canv.saveState()
        self.canv.setStrokeColor(BLACK)
        self.canv.setLineWidth(0.5)
        self.canv.line(0, 0, self.w, self.h)
        self.canv.restoreState()

class RotatedText(Flowable):
    """Draws rotated text centered in a cell."""
    def __init__(self, text, style, w, h):
        super().__init__()
        self.text = text
        self.style = style
        self.w = w
        self.h = h

    def wrap(self, availWidth, availHeight):
        return self.w, self.h

    def draw(self):
        self.canv.saveState()
        self.canv.setFont(self.style.fontName, self.style.fontSize)
        self.canv.setFillColor(self.style.textColor or BLACK)
        self.canv.translate(self.w / 2.0 + 2, self.h / 2.0)
        self.canv.rotate(-90)
        self.canv.drawCentredString(0, -2, self.text)
        self.canv.restoreState()

# ── Table Styles Helper ──────────────────────────────────────────────
def get_table_style(extra_commands=None):
    ts = [
        ("GRID", (0, 0), (-1, -1), 0.5, BLACK),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("LEFTPADDING", (0, 0), (-1, -1), 2),
        ("RIGHTPADDING", (0, 0), (-1, -1), 2),
        ("TOPPADDING", (0, 0), (-1, -1), 2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
    ]
    if extra_commands:
        ts.extend(extra_commands)
    return TableStyle(ts)

# ════════════════════════════════════════════════════════════════════════════
#  DOCUMENT 1 – "Student Understanding Model Sheet"
# ════════════════════════════════════════════════════════════════════════════

def build_doc1():
    story = []

    # ── Page 1: Cover Page ──────────────────────────────────────────────────
    story.append(Spacer(1, 10))
    top_header = [
        ["", Paragraph("(Attachment 2)", S("TopR", fontSize=8, alignment=TA_RIGHT))],
        ["", Paragraph("HANDLE WITH CARE", S("HWC_Cover", fontSize=8.5, fontName="Helvetica-Bold", alignment=TA_CENTER))]
    ]
    top_header_t = Table(top_header, colWidths=[PAGE_W - 42*mm, 42*mm], rowHeights=[12, 18])
    top_header_t.setStyle(TableStyle([
        ("BOX", (1, 1), (1, 1), 1.2, BLACK),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN", (1, 1), (1, 1), "CENTER"),
    ]))
    story.append(top_header_t)
    story.append(Spacer(1, 40))

    # Main Title
    story.append(Paragraph("Student Understanding / Support Sheet (Reference Format)", S("MTitle", fontSize=15, fontName="Helvetica-Bold", alignment=TA_CENTER)))
    story.append(Spacer(1, 40))

    # Legend
    legend_data = [
        ["", Paragraph("is automatically filled by pre-recorded content", small_style)]
    ]
    legend_t = Table(legend_data, colWidths=[12*mm, PAGE_W - 12*mm], rowHeights=[10])
    legend_t.setStyle(TableStyle([
        ("BOX", (0, 0), (0, 0), 0.5, BLACK),
        ("BACKGROUND", (0, 0), (0, 0), LIGHT_BLUE),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    story.append(legend_t)
    story.append(Spacer(1, 20))

    # School Name Table (Horizontal lines only, cream inputs)
    story.append(Paragraph("Current enrolled school name or graduated school name", section_style))
    story.append(Spacer(1, 4))
    school_data = [
        [Paragraph("(Elementary)", normal_style), ""],
        [Paragraph("(Middle)", normal_style), ""],
        [Paragraph("(High)", normal_style), ""],
    ]
    school_t = Table(school_data, colWidths=[30*mm, PAGE_W - 30*mm], rowHeights=[22]*3)
    school_t.setStyle(TableStyle([
        ("LINEABOVE", (0, 0), (-1, 0), 0.5, BLACK),
        ("LINEBELOW", (0, 0), (-1, -1), 0.5, BLACK),
        ("BACKGROUND", (1, 0), (1, -1), CREAM),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(school_t)
    story.append(Spacer(1, 25))

    # Name block
    name_data = [
        [Paragraph("(Reading / Furigana)", small_style), ""],
        [Paragraph("Student Name", section_style), ""],
    ]
    name_t = Table(name_data, colWidths=[40*mm, PAGE_W - 40*mm], rowHeights=[14, 24])
    name_t.setStyle(TableStyle([
        ("LINEABOVE", (0, 0), (-1, 0), 0.5, BLACK),
        ("LINEBELOW", (0, 0), (-1, -1), 0.5, BLACK),
        ("BACKGROUND", (1, 0), (1, -1), CREAM),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(name_t)
    story.append(Spacer(1, 40))

    # Classification number (Bottom right)
    class_data = [
        ["", Paragraph("Classification Number", small_style), ""]
    ]
    class_t = Table(class_data, colWidths=[PAGE_W - 80*mm, 40*mm, 40*mm], rowHeights=[20])
    class_t.setStyle(TableStyle([
        ("LINEABOVE", (1, 0), (2, 0), 0.5, BLACK),
        ("LINEBELOW", (1, 0), (2, 0), 0.5, BLACK),
        ("BACKGROUND", (2, 0), (2, 0), CREAM),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN", (1, 0), (1, 0), "RIGHT"),
    ]))
    story.append(class_t)
    story.append(PageBreak())

    # ── Page 2: Common Sheet ────────────────────────────────────────────────
    story.append(Paragraph("Student Understanding / Support Sheet (Common Sheet)", title_style))
    story.append(Spacer(1, 2))

    # Meta text above tables
    meta_info = [
        [Paragraph("Date Created: Year &nbsp; &nbsp; &nbsp; &nbsp; Month &nbsp; &nbsp; Day &nbsp; &nbsp;", small_style),
         Paragraph("* Fields marked * are to be filled in when necessary for students with disabilities, foreign students, etc.", note_style)]
    ]
    meta_info_t = Table(meta_info, colWidths=[70*mm, PAGE_W - 70*mm])
    meta_info_t.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
        ("ALIGN", (1, 0), (1, 0), "RIGHT"),
    ]))
    story.append(meta_info_t)
    story.append(Spacer(1, 2))

    # Created/Added by row
    added_info = [
        [Paragraph("Created by &nbsp; Staff A &nbsp; &nbsp; &nbsp; Added by &nbsp; Staff A / Staff B / ...", small_style)]
    ]
    added_info_t = Table(added_info, colWidths=[PAGE_W])
    added_info_t.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
    ]))
    story.append(added_info_t)
    story.append(Spacer(1, 2))

    # Student Info Table
    student_data = [
        [Paragraph("(Student)<br/>Name", small_style), Paragraph("Gender", small_style), Paragraph("Date of Birth", small_style), Paragraph("Nationality *", small_style), Paragraph("Birthplace *", small_style)],
        [Paragraph("<b>(Reading)</b><br/>0", normal_style), Paragraph("0", normal_style), Paragraph("YYYY &nbsp; &nbsp; &nbsp; / &nbsp; &nbsp; MM &nbsp; &nbsp; / &nbsp; &nbsp; DD", small_style), "", ""],
    ]
    student_t = Table(student_data, colWidths=[50*mm, 16*mm, 50*mm, 35*mm, 35*mm], rowHeights=[14, 22])
    student_t.setStyle(get_table_style([
        ("BACKGROUND", (0, 0), (-1, 0), WARM_GREY),
        ("BACKGROUND", (0, 1), (0, 1), LIGHT_BLUE),
    ]))
    story.append(student_t)
    story.append(Spacer(1, 2))

    # Guardian Info Table
    guardian_data = [
        [Paragraph("(Guardian)<br/>Name", small_style), Paragraph("Relationship *", small_style), Paragraph("School Enrollment Date *", small_style), Paragraph("Contact", small_style)],
        [Paragraph("<b>(Reading)</b><br/>", normal_style), "", Paragraph("YYYY &nbsp; &nbsp; &nbsp; / &nbsp; &nbsp; MM &nbsp; &nbsp; / &nbsp; &nbsp; DD", small_style), ""],
    ]
    guardian_t = Table(guardian_data, colWidths=[50*mm, 31*mm, 50*mm, 55*mm], rowHeights=[14, 22])
    guardian_t.setStyle(get_table_style([
        ("BACKGROUND", (0, 0), (-1, 0), WARM_GREY),
    ]))
    story.append(guardian_t)
    story.append(Spacer(1, 4))

    # Absence Days Table
    story.append(Paragraph("Absence Days by Grade Level &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Added: &nbsp; MM / DD", section_style))
    story.append(Spacer(1, 2))

    grades = ["Yr", "E1", "E2", "E3", "E4", "E5", "E6", "M1", "M2", "M3", "H1", "H2", "H3", "H4"]
    abs_rows = [
        "Days Required to Attend",
        "Days Attended",
        "Attended (Separate Room)",
        "Late Arrivals",
        "Early Departures",
        "Absent Days",
        "Recorded as Attended (Official Register)",
        "① Educational Support Center",
        "② Board of Education Agency (excl. ①)",
        "③ Child Guidance / Welfare Office",
        "④ Public Health / Mental Health Center",
        "⑤ Hospital / Clinic",
        "⑥ Private Organization / Facility",
        "⑦ Other Agencies",
        "⑧ Use of IT / Online Learning",
    ]

    abs_data = []
    # Row 0: Fiscal Year label (empty cols for values)
    abs_data.append([Paragraph("Fiscal Year", small_style)] + [""]*13)
    # Row 1: Grade label + grade values
    abs_data.append([Paragraph("Grade", small_style)] + [Paragraph(g, small_style) for g in grades[1:]])
    # Other rows
    for r in abs_rows:
        abs_data.append([Paragraph(r, small_style)] + [""]*13)

    abs_t = Table(abs_data, colWidths=abs_col_widths, rowHeights=[11]*17)
    abs_t.setStyle(get_table_style([
        ("BACKGROUND", (0, 0), (-1, 0), WARM_GREY),
        ("BACKGROUND", (0, 1), (-1, 1), WARM_GREY),
        ("BACKGROUND", (0, 2), (0, 6), WARM_GREY),
        ("BACKGROUND", (0, 7), (-1, 7), LIGHT_BLUE), # Absent Days row
        ("BACKGROUND", (0, 8), (0, 16), LIGHT_BLUE), # Official attendance sub-labels
        ("ALIGN", (0, 0), (0, -1), "LEFT"),
        # Dotted lines inside the official attendance block
        ("LINEBELOW", (0, 9), (-1, 15), 0.5, BLACK, 0, (1, 2)),
    ]))
    story.append(abs_t)
    story.append(Spacer(1, 4))

    # Basic Info Section (Set height on Table, not dynamic text)
    story.append(Paragraph("Basic Information for Continuous Support", section_style))
    story.append(Paragraph("Special notes (student's strengths, assessment information, home situation, type/degree/diagnosis of disability, type and date of disability certificate *, learning history *, Japanese proficiency *, etc.)", note_style))
    story.append(Spacer(1, 1))
    basic_info_t = Table([[""]], colWidths=[PAGE_W], rowHeights=[26])
    basic_info_t.setStyle(get_table_style())
    story.append(basic_info_t)
    story.append(Spacer(1, 4))

    # Family Situation Section
    story.append(Paragraph("Family Situation", section_style))
    story.append(Paragraph("Special notes (developmental history, surrounding circumstances incl. family situation, changes since creation date, family composition *, language used at home *, etc.)", note_style))
    story.append(Spacer(1, 1))
    fam_t = Table([[""]], colWidths=[PAGE_W], rowHeights=[26])
    fam_t.setStyle(get_table_style())
    story.append(fam_t)
    story.append(Spacer(1, 4))

    # Remarks Section
    story.append(Paragraph("Remarks", section_style))
    story.append(Spacer(1, 1))
    rem_t = Table([[""]], colWidths=[PAGE_W], rowHeights=[20])
    rem_t.setStyle(get_table_style())
    story.append(rem_t)
    story.append(PageBreak())

    # ── Page 3: Grade-Level Sheet A ─────────────────────────────────────────
    story.append(Paragraph("Student Understanding / Support Sheet (Grade-Level Sheet A)", title_style))
    story.append(Spacer(1, 2))

    # Meta Info
    meta_data = [
        [Paragraph("Homeroom Teacher (Reading):", small_style), "", Paragraph("School Administrator:", small_style), ""],
        [Paragraph("Date Created:", small_style), "", Paragraph("Created by:", small_style), ""],
        [Paragraph("Date Added (Added by):", small_style), "", "", ""],
    ]
    meta_t = Table(meta_data, colWidths=[45*mm, 48*mm, 45*mm, 48*mm], rowHeights=[12, 12, 12])
    meta_t.setStyle(get_table_style([
        ("BACKGROUND", (0, 0), (0, 2), WARM_GREY),
        ("BACKGROUND", (2, 0), (2, 1), WARM_GREY),
        ("BACKGROUND", (1, 0), (1, 1), LIGHT_BLUE),
        ("BACKGROUND", (3, 0), (3, 1), LIGHT_BLUE),
        ("SPAN", (1, 2), (3, 2)),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
    ]))
    story.append(meta_t)
    story.append(Spacer(1, 4))

    # Student Info Table (Page 3)
    stu_data = [
        [Paragraph("Name (Reading)", small_style), Paragraph("Gender", small_style), Paragraph("School Name", small_style), Paragraph("Grade", small_style), Paragraph("Class", small_style)],
        [Paragraph("( &nbsp; &nbsp; &nbsp; 0 &nbsp; &nbsp; &nbsp; )<br/>0", normal_style), Paragraph("0", normal_style), "", "", ""],
    ]
    stu_t = Table(stu_data, colWidths=[60*mm, 16*mm, 60*mm, 25*mm, 25*mm], rowHeights=[12, 20])
    stu_t.setStyle(get_table_style([
        ("BACKGROUND", (0, 0), (-1, 0), WARM_GREY),
        ("BACKGROUND", (0, 1), (1, 1), LIGHT_BLUE),
    ]))
    story.append(stu_t)
    story.append(Spacer(1, 4))

    # Support Agencies Table
    story.append(Paragraph("Support Agencies (In-school / External)", section_style))
    story.append(Spacer(1, 2))
    sup_data = [
        ["", Paragraph("Main Support Content", small_style), Paragraph("Agency Name", small_style), Paragraph("Phone Number", small_style), Paragraph("Contact Person", small_style)],
        [Paragraph("Home School", small_style), "", "0", "", ""],
        [Paragraph("Family", small_style), "", "", "0", "0"],
        [Paragraph("Welfare", small_style), "", "", "", ""],
        [Paragraph("Medical", small_style), "", "", "", ""],
        [Paragraph("Other", small_style), "", "", "", ""],
    ]
    sup_t = Table(sup_data, colWidths=[20*mm, 55*mm, 45*mm, 36*mm, 30*mm], rowHeights=[12]+[20]*5)
    sup_t.setStyle(get_table_style([
        ("BACKGROUND", (1, 0), (-1, 0), WARM_GREY),
        ("BACKGROUND", (0, 1), (0, -1), WARM_GREY),
        ("SPAN", (1, 2), (2, 2)), # merge main support and agency for family row
        ("BACKGROUND", (2, 1), (2, 1), LIGHT_BLUE),
        ("BACKGROUND", (3, 2), (4, 2), LIGHT_BLUE),
    ]))
    # Add diagonal line in the merged cell of the family row (Row 2, spanning Col 1 and 2)
    sup_t.setStyle(TableStyle([
        ("ALIGN", (1, 2), (2, 2), "CENTER"),
        ("VALIGN", (1, 2), (2, 2), "MIDDLE"),
    ]))
    # Let reportlab build the flowable inside the cell
    sup_data[2][1] = DiagonalLine(100*mm, 20)
    story.append(sup_t)
    story.append(Spacer(1, 4))

    # Monthly Absence Table
    story.append(Paragraph("Monthly Absence Record &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; * Date Added →", section_style))
    story.append(Spacer(1, 2))

    months = ["Month", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec", "Jan", "Feb", "Mar", "Total"]
    month_rows = [
        "Days Required to Attend",
        "Days Attended",
        "Attended (Separate Room)",
        "Late Arrivals",
        "Early Departures",
        "Cumulative Absent Days",
        "Absent Days (incl. official attendance)",
        "Recorded as Attended (Official Register)",
        "① Educational Support Center",
        "② Board of Education Agency (excl. ①)",
        "③ Child Guidance / Welfare Office",
        "④ Public Health / Mental Health Center",
        "⑤ Hospital / Clinic",
        "⑥ Private Organization / Facility",
        "⑦ Other Agencies",
        "⑧ Use of IT / Online Learning",
    ]
    m_data = []
    # Row 0: ※ Date Added row
    m_data.append([Paragraph("* Date Added →", small_style)] + [""]*13)
    # Row 1: Month header
    m_data.append([Paragraph("Month", small_style)] + [Paragraph(m, small_style) for m in months[1:]])
    # Data rows
    for r in month_rows:
        m_data.append([Paragraph(r, small_style)] + [""]*13)

    m_t = Table(m_data, colWidths=abs_col_widths, rowHeights=[10]*18)
    m_t.setStyle(get_table_style([
        ("BACKGROUND", (0, 0), (-1, 0), WARM_GREY),
        ("BACKGROUND", (0, 1), (-1, 1), WARM_GREY),
        ("BACKGROUND", (0, 2), (0, 6), WARM_GREY),
        ("BACKGROUND", (0, 7), (-1, 7), LIGHT_BLUE), # Cumulative Absent Days
        ("BACKGROUND", (0, 8), (-1, 8), PEACH),      # Absent Days (incl. official attendance)
        ("BACKGROUND", (0, 9), (0, 17), LIGHT_BLUE), # Official attendance sub-labels
        ("BACKGROUND", (-1, 2), (-1, -1), LIGHT_BLUE), # Total column is light blue
        ("ALIGN", (0, 0), (0, -1), "LEFT"),
        ("LINEBELOW", (0, 10), (-1, 16), 0.5, BLACK, 0, (1, 2)),
    ]))
    # Fill in "0" values in the Cumulative Absent Days row for the Model sheet
    for c in range(1, 13):
        m_data[7][c] = Paragraph("0", small_style)
    # Put empty "0" in the last column cells
    for r in range(2, 18):
        m_data[r][13] = Paragraph("0", small_style)
    story.append(m_t)
    story.append(Spacer(1, 4))

    # Reasons Section
    story.append(Paragraph("Reasons for Extended Absence / Continued School Refusal / etc.", section_style))
    story.append(Spacer(1, 1))
    reasons_t = Table([[""]], colWidths=[PAGE_W], rowHeights=[20])
    reasons_t.setStyle(get_table_style())
    story.append(reasons_t)
    story.append(Spacer(1, 4))

    # Handover Section
    story.append(Paragraph("Handover Notes for Next School Year (include episodes relevant to support/guidance, recorded from diverse perspectives)", section_style))
    story.append(Spacer(1, 1))
    handover_t = Table([[""]], colWidths=[PAGE_W], rowHeights=[26])
    handover_t.setStyle(get_table_style())
    story.append(handover_t)
    story.append(PageBreak())

    # ── Page 4: Grade-Level Sheet B ─────────────────────────────────────────
    story.append(Paragraph("Student Understanding / Support Sheet (Grade-Level Sheet B)", title_style))
    story.append(Spacer(1, 2))

    # Meta Table (same as Page 3 but labeled B sheet)
    metaB_data = [
        [Paragraph("Homeroom Teacher (Reading):", small_style), "0", Paragraph("School Administrator:", small_style), "0"],
        [Paragraph("Date Created:", small_style), "0", Paragraph("Created by:", small_style), "0"],
        [Paragraph("Date Added (Added by):", small_style), "", "", ""],
    ]
    metaB_t = Table(metaB_data, colWidths=[45*mm, 48*mm, 45*mm, 48*mm], rowHeights=[12, 12, 12])
    metaB_t.setStyle(get_table_style([
        ("BACKGROUND", (0, 0), (0, 2), WARM_GREY),
        ("BACKGROUND", (2, 0), (2, 1), WARM_GREY),
        ("BACKGROUND", (1, 0), (1, 1), LIGHT_BLUE),
        ("BACKGROUND", (3, 0), (3, 1), LIGHT_BLUE),
        ("SPAN", (1, 2), (3, 2)),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
    ]))
    story.append(metaB_t)
    story.append(Spacer(1, 4))

    # Student Info Table (Page 4)
    stuB_data = [
        [Paragraph("Name (Reading)", small_style), Paragraph("Gender", small_style), Paragraph("School Name", small_style), Paragraph("Grade", small_style), Paragraph("Class", small_style)],
        [Paragraph("( &nbsp; &nbsp; &nbsp; 0 &nbsp; &nbsp; &nbsp; )<br/>0", normal_style), Paragraph("0", normal_style), "0", "0", "0"],
    ]
    stuB_t = Table(stuB_data, colWidths=[60*mm, 16*mm, 60*mm, 25*mm, 25*mm], rowHeights=[12, 20])
    stuB_t.setStyle(get_table_style([
        ("BACKGROUND", (0, 0), (-1, 0), WARM_GREY),
        ("BACKGROUND", (0, 1), (-1, 1), LIGHT_BLUE),
    ]))
    story.append(stuB_t)
    story.append(Spacer(1, 4))

    # Wishes Table
    story.append(Paragraph("Current Situation and Wishes of Student / Guardian", section_style))
    story.append(Spacer(1, 2))
    wishes_data = [
        ["", Paragraph("Current Situation", small_style), Paragraph("Future Wishes (incl. career path)", small_style)],
        [Paragraph("Student", small_style), "", ""],
        [Paragraph("Guardian", small_style), "", ""],
    ]
    wishes_t = Table(wishes_data, colWidths=[20*mm, 83*mm, 83*mm], rowHeights=[12, 35, 35])
    wishes_t.setStyle(get_table_style([
        ("BACKGROUND", (1, 0), (-1, 0), WARM_GREY),
        ("BACKGROUND", (0, 1), (0, -1), WARM_GREY),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
    ]))
    story.append(wishes_t)
    story.append(Spacer(1, 4))

    # Goals Section
    story.append(Paragraph("Goals for This School Year", section_style))
    story.append(Spacer(1, 1))
    goals_t = Table([[""]], colWidths=[PAGE_W], rowHeights=[20])
    goals_t.setStyle(get_table_style())
    story.append(goals_t)
    story.append(Spacer(1, 4))

    # Support Plan Table
    story.append(Paragraph("Individual Support Plan by Term", section_style))
    story.append(Spacer(1, 2))
    plan_data = [
        ["", "", Paragraph("Goal", small_style), Paragraph("Support Content", small_style), Paragraph("Progress / Evaluation", small_style)],
        ["", Paragraph("School", small_style), "", "", ""],
        ["", Paragraph("Related Agencies", small_style), "", "", ""],
        ["", Paragraph("School", small_style), "", "", ""],
        ["", Paragraph("Related Agencies", small_style), "", "", ""],
        ["", Paragraph("School", small_style), "", "", ""],
        ["", Paragraph("Related Agencies", small_style), "", "", ""],
    ]
    # Set custom vertical term labels inside Flowables to rotate them nicely
    plan_col_widths = [20*mm, 20*mm, 45*mm, 60*mm, 41*mm]
    plan_data[1][0] = RotatedText("1st Term", small_style, 20*mm, 36)
    plan_data[3][0] = RotatedText("2nd Term", small_style, 20*mm, 36)
    plan_data[5][0] = RotatedText("3rd Term", small_style, 20*mm, 36)

    plan_t = Table(plan_data, colWidths=plan_col_widths, rowHeights=[12]+[18]*6)
    plan_t.setStyle(get_table_style([
        ("BACKGROUND", (2, 0), (-1, 0), WARM_GREY),
        ("BACKGROUND", (0, 1), (1, -1), WARM_GREY),
        ("SPAN", (0, 1), (0, 2)),
        ("SPAN", (0, 3), (0, 4)),
        ("SPAN", (0, 5), (0, 6)),
    ]))
    story.append(plan_t)
    story.append(PageBreak())

    # ── Page 5: Discussion Sheet ─────────────────────────────────────────────
    story.append(Paragraph("Student Understanding / Support Sheet (Discussion Sheet)", title_style))
    story.append(Spacer(1, 2))

    # Info above table
    disc_meta = [
        [Paragraph("Recorder: &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Student Guidance Coordinator:", small_style),
         Paragraph("Date: YYYY &nbsp; &nbsp; &nbsp; / &nbsp; &nbsp; MM &nbsp; &nbsp; / &nbsp; &nbsp; DD", small_style)]
    ]
    disc_meta_t = Table(disc_meta, colWidths=[120*mm, PAGE_W - 120*mm])
    disc_meta_t.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN", (1, 0), (1, 0), "RIGHT"),
    ]))
    story.append(disc_meta_t)
    story.append(Spacer(1, 2))

    # Header Table
    disc_hdr = [
        [Paragraph("Grade", small_style), Paragraph("Class", small_style), Paragraph("Name", small_style), Paragraph("Participants / Agencies", small_style)],
        ["0", "0", "0", ""],
    ]
    disc_hdr_t = Table(disc_hdr, colWidths=[20*mm, 20*mm, 50*mm, 96*mm], rowHeights=[12, 18])
    disc_hdr_t.setStyle(get_table_style([
        ("BACKGROUND", (0, 0), (-1, 0), WARM_GREY),
        ("BACKGROUND", (0, 1), (2, 1), LIGHT_BLUE),
    ]))
    story.append(disc_hdr_t)
    story.append(Spacer(1, 4))

    # Sections
    sections = [
        ("Student's Wishes", 22),
        ("Guardian's Wishes", 22),
        ("Information from Related Agencies", 22),
        ("Support Status", 10), # Will put the Goal and Role Allocation tables below
    ]
    for label, h in sections:
        story.append(Paragraph(label, section_style))
        story.append(Spacer(1, 1))
        sec_t = Table([[""]], colWidths=[PAGE_W], rowHeights=[h])
        sec_t.setStyle(get_table_style())
        story.append(sec_t)
        story.append(Spacer(1, 4))

    # Goal block under Support Status
    goal_data = [
        [Paragraph("Goal", small_style), ""]
    ]
    goal_t = Table(goal_data, colWidths=[20*mm, PAGE_W - 20*mm], rowHeights=[16])
    goal_t.setStyle(get_table_style([
        ("BACKGROUND", (0, 0), (0, 0), WARM_GREY),
        ("ALIGN", (0, 0), (0, 0), "CENTER"),
    ]))
    story.append(goal_t)
    story.append(Spacer(1, 2))

    # Role Allocation table
    role_data = [
        ["", Paragraph("Agency / Division", small_style), Paragraph("Short-Term Goal &nbsp; &nbsp; MM / DD", small_style), Paragraph("Progress / Evaluation &nbsp; &nbsp; MM / DD", small_style)],
        ["", "", "", ""],
        ["", "", "", ""],
        ["", "", "", ""],
        ["", "", "", ""],
        ["", "", "", ""],
        ["", "", "", ""],
    ]
    role_data[1][0] = RotatedText("Role Allocation", small_style, 10*mm, 70)

    role_t = Table(role_data, colWidths=role_col_widths, rowHeights=[12]+[15]*6)
    role_t.setStyle(get_table_style([
        ("BACKGROUND", (1, 0), (-1, 0), WARM_GREY),
        ("BACKGROUND", (0, 1), (0, -1), WARM_GREY),
        ("SPAN", (0, 1), (0, -1)),
    ]))
    story.append(role_t)
    story.append(Spacer(1, 4))

    # Confirmations Section
    story.append(Paragraph("Confirmations / Agreed Matters", section_style))
    story.append(Spacer(1, 1))
    conf_t = Table([[""]], colWidths=[PAGE_W], rowHeights=[20])
    conf_t.setStyle(get_table_style())
    story.append(conf_t)
    story.append(Spacer(1, 4))

    # Special Notes Section
    story.append(Paragraph("Special Notes", section_style))
    story.append(Spacer(1, 1))
    spec_t = Table([[""]], colWidths=[PAGE_W], rowHeights=[20])
    spec_t.setStyle(get_table_style())
    story.append(spec_t)

    return story


# ════════════════════════════════════════════════════════════════════════════
#  DOCUMENT 2 – "Student Understanding and Support Sheet (Example Form)"
# ════════════════════════════════════════════════════════════════════════════

def build_doc2():
    story = []

    # ── Page 1: Cover Page ──────────────────────────────────────────────────
    story.append(Spacer(1, 10))
    top_header = [
        ["", Paragraph("(Attachment 2)", S("TopR2", fontSize=8, alignment=TA_RIGHT))],
        ["", Paragraph("HANDLE WITH CARE", S("HWC_Cover2", fontSize=8.5, fontName="Helvetica-Bold", alignment=TA_CENTER))]
    ]
    top_header_t = Table(top_header, colWidths=[PAGE_W - 42*mm, 42*mm], rowHeights=[12, 18])
    top_header_t.setStyle(TableStyle([
        ("BOX", (1, 1), (1, 1), 1.2, BLACK),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN", (1, 1), (1, 1), "CENTER"),
    ]))
    story.append(top_header_t)
    story.append(Spacer(1, 40))

    # Main Title
    story.append(Paragraph("Student Understanding / Support Sheet (Reference Format)", S("MTitle2", fontSize=15, fontName="Helvetica-Bold", alignment=TA_CENTER)))
    story.append(Spacer(1, 40))

    # Legend
    legend_data = [
        ["", Paragraph("is automatically filled by pre-recorded content", small_style)]
    ]
    legend_t = Table(legend_data, colWidths=[12*mm, PAGE_W - 12*mm], rowHeights=[10])
    legend_t.setStyle(TableStyle([
        ("BOX", (0, 0), (0, 0), 0.5, BLACK),
        ("BACKGROUND", (0, 0), (0, 0), LIGHT_BLUE),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    story.append(legend_t)
    story.append(Spacer(1, 20))

    # School Name Table (Example values pre-filled)
    story.append(Paragraph("Current enrolled school name or graduated school name", section_style))
    story.append(Spacer(1, 4))
    school_data = [
        [Paragraph("(Elementary)", normal_style), Paragraph("Oak Elementary School", normal_style)],
        [Paragraph("(Middle)", normal_style), Paragraph("Oak Middle School", normal_style)],
        [Paragraph("(High)", normal_style), ""],
    ]
    school_t = Table(school_data, colWidths=[30*mm, PAGE_W - 30*mm], rowHeights=[22]*3)
    school_t.setStyle(TableStyle([
        ("LINEABOVE", (0, 0), (-1, 0), 0.5, BLACK),
        ("LINEBELOW", (0, 0), (-1, -1), 0.5, BLACK),
        ("BACKGROUND", (1, 0), (1, -1), CREAM),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(school_t)
    story.append(Spacer(1, 25))

    # Name block (Example value pre-filled)
    name_data = [
        [Paragraph("(Reading / Furigana)", small_style), Paragraph("DOE, John", normal_style)],
        [Paragraph("Student Name", section_style), Paragraph("John Doe", normal_style)],
    ]
    name_t = Table(name_data, colWidths=[40*mm, PAGE_W - 40*mm], rowHeights=[14, 24])
    name_t.setStyle(TableStyle([
        ("LINEABOVE", (0, 0), (-1, 0), 0.5, BLACK),
        ("LINEBELOW", (0, 0), (-1, -1), 0.5, BLACK),
        ("BACKGROUND", (1, 0), (1, -1), CREAM),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(name_t)
    story.append(Spacer(1, 40))

    # Classification number (Example value pre-filled)
    class_data = [
        ["", Paragraph("Classification Number", small_style), Paragraph("0001", normal_style)]
    ]
    class_t = Table(class_data, colWidths=[PAGE_W - 80*mm, 40*mm, 40*mm], rowHeights=[20])
    class_t.setStyle(TableStyle([
        ("LINEABOVE", (1, 0), (2, 0), 0.5, BLACK),
        ("LINEBELOW", (1, 0), (2, 0), 0.5, BLACK),
        ("BACKGROUND", (2, 0), (2, 0), CREAM),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN", (1, 0), (1, 0), "RIGHT"),
    ]))
    story.append(class_t)
    story.append(PageBreak())

    # ── Page 2: Common Sheet ────────────────────────────────────────────────
    story.append(Paragraph("Student Understanding / Support Sheet (Common Sheet)", title_style))
    story.append(Spacer(1, 2))

    # Meta text above tables
    meta_info = [
        [Paragraph("Date Created: Year &nbsp; <b>2025</b> &nbsp; Month &nbsp; <b>10</b> &nbsp; Day &nbsp; <b>15</b> &nbsp; &nbsp;", small_style),
         Paragraph("* Fields marked * are to be filled in when necessary for students with disabilities, foreign students, etc.", note_style)]
    ]
    meta_info_t = Table(meta_info, colWidths=[70*mm, PAGE_W - 70*mm])
    meta_info_t.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
        ("ALIGN", (1, 0), (1, 0), "RIGHT"),
    ]))
    story.append(meta_info_t)
    story.append(Spacer(1, 2))

    # Created/Added by row
    added_info = [
        [Paragraph("Created by &nbsp; Staff A &nbsp; &nbsp; &nbsp; Added by &nbsp; Staff A / Staff B / ...", small_style)]
    ]
    added_info_t = Table(added_info, colWidths=[PAGE_W])
    added_info_t.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
    ]))
    story.append(added_info_t)
    story.append(Spacer(1, 2))

    # Student Info Table
    student_data = [
        [Paragraph("(Student)<br/>Name", small_style), Paragraph("Gender", small_style), Paragraph("Date of Birth", small_style), Paragraph("Nationality *", small_style), Paragraph("Birthplace *", small_style)],
        [Paragraph("<b>(Reading)</b> &nbsp; DOE, John<br/>John Doe", normal_style), Paragraph("Male", normal_style), Paragraph("2013 / 04 / 12", normal_style), "Japan", "Tokyo"],
    ]
    student_t = Table(student_data, colWidths=[50*mm, 16*mm, 50*mm, 35*mm, 35*mm], rowHeights=[14, 22])
    student_t.setStyle(get_table_style([
        ("BACKGROUND", (0, 0), (-1, 0), WARM_GREY),
        ("BACKGROUND", (0, 1), (0, 1), LIGHT_BLUE),
    ]))
    story.append(student_t)
    story.append(Spacer(1, 2))

    # Guardian Info Table
    guardian_data = [
        [Paragraph("(Guardian)<br/>Name", small_style), Paragraph("Relationship *", small_style), Paragraph("School Enrollment Date *", small_style), Paragraph("Contact", small_style)],
        [Paragraph("<b>(Reading)</b> &nbsp; DOE, Jane<br/>Jane Doe", normal_style), Paragraph("Mother", normal_style), Paragraph("2020 / 04 / 01", normal_style), Paragraph("000-0000-0000", normal_style)],
    ]
    guardian_t = Table(guardian_data, colWidths=[50*mm, 31*mm, 50*mm, 55*mm], rowHeights=[14, 22])
    guardian_t.setStyle(get_table_style([
        ("BACKGROUND", (0, 0), (-1, 0), WARM_GREY),
    ]))
    story.append(guardian_t)
    story.append(Spacer(1, 4))

    # Absence Days Table
    story.append(Paragraph("Absence Days by Grade Level &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Added: &nbsp; 10 / 15", section_style))
    story.append(Spacer(1, 2))

    abs_rows_data = [
        ("Days Required to Attend", ["200","200","200","200","200","200","","","","","","","",""]),
        ("Days Attended",            ["195","188","150","100","80","60","","","","","","","",""]),
        ("Attended (Separate Room)", ["","","","","5","10","","","","","","","",""]),
        ("Late Arrivals",            ["2","3","5","10","15","20","","","","","","","",""]),
        ("Early Departures",         ["1","2","3","5","8","10","","","","","","","",""]),
        ("Absent Days",              ["5","12","50","100","120","140","","","","","","","",""]),
        ("Recorded as Attended (Official Register)", ["","","","","","","","","","","","","",""]),
        ("① Educational Support Center", ["","","","","","","","","","","","","",""]),
        ("② Board of Education Agency (excl. ①)", ["","","","","","","","","","","","","",""]),
        ("③ Child Guidance / Welfare Office", ["","","","","","","","","","","","","",""]),
        ("④ Public Health / Mental Health Center", ["","","","","","","","","","","","","",""]),
        ("⑤ Hospital / Clinic", ["","","","","","","","","","","","","",""]),
        ("⑥ Private Organization / Facility", ["","","","","","","","","","","","","",""]),
        ("⑦ Other Agencies", ["","","","","","","","","","","","","",""]),
        ("⑧ Use of IT / Online Learning", ["","","","","","","","","","","","","",""]),
    ]

    abs_data = []
    abs_data.append([Paragraph("Fiscal Year", small_style)] + [""]*13)
    abs_data.append([Paragraph("Grade", small_style)] + [Paragraph(g, small_style) for g in grades[1:]])
    for label, vals in abs_rows_data:
        abs_data.append([Paragraph(label, small_style)] + [Paragraph(v, small_style) for v in vals])

    abs_t = Table(abs_data, colWidths=abs_col_widths, rowHeights=[11]*17)
    abs_t.setStyle(get_table_style([
        ("BACKGROUND", (0, 0), (-1, 0), WARM_GREY),
        ("BACKGROUND", (0, 1), (-1, 1), WARM_GREY),
        ("BACKGROUND", (0, 2), (0, 6), WARM_GREY),
        ("BACKGROUND", (0, 7), (-1, 7), LIGHT_BLUE), # Absent Days row
        ("BACKGROUND", (0, 8), (0, 16), LIGHT_BLUE), # Official attendance sub-labels
        ("ALIGN", (0, 0), (0, -1), "LEFT"),
        ("LINEBELOW", (0, 9), (-1, 15), 0.5, BLACK, 0, (1, 2)),
    ]))
    story.append(abs_t)
    story.append(Spacer(1, 4))

    # Basic Info Section (Dynamic height)
    story.append(Paragraph("Basic Information for Continuous Support", section_style))
    story.append(Paragraph("Special notes (student's strengths, assessment information, home situation, type/degree/diagnosis of disability, type and date of disability certificate *, learning history *, Japanese proficiency *, etc.)", note_style))
    story.append(Spacer(1, 1))
    basic_text = Paragraph(
        "<b>Student's strengths:</b> Earnest and straightforward character. Enjoys drawing.<br/>"
        "<b>Assessment:</b> School refusal tendencies observed since 4th grade. Anxiety reported.<br/>"
        "<b>Disability / Diagnosis:</b> None.", normal_style
    )
    basic_info_t = Table([[basic_text]], colWidths=[PAGE_W], rowHeights=None)
    basic_info_t.setStyle(get_table_style([
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(basic_info_t)
    story.append(Spacer(1, 4))

    # Family Situation Section
    story.append(Paragraph("Family Situation", section_style))
    story.append(Paragraph("Special notes (developmental history, surrounding circumstances incl. family situation, changes since creation date, family composition *, language used at home *, etc.)", note_style))
    story.append(Spacer(1, 1))
    fam_text = Paragraph(
        "Lives with parents and one younger sibling. Father works long hours and is rarely home. "
        "Mother is the primary caregiver and is supportive. Home language: Japanese.", normal_style
    )
    fam_t = Table([[fam_text]], colWidths=[PAGE_W], rowHeights=None)
    fam_t.setStyle(get_table_style([
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(fam_t)
    story.append(Spacer(1, 4))

    # Remarks Section
    story.append(Paragraph("Remarks", section_style))
    story.append(Spacer(1, 1))
    rem_t = Table([[""]], colWidths=[PAGE_W], rowHeights=[20])
    rem_t.setStyle(get_table_style())
    story.append(rem_t)
    story.append(PageBreak())

    # ── Page 3: Grade-Level Sheet A ─────────────────────────────────────────
    story.append(Paragraph("Student Understanding / Support Sheet (Grade-Level Sheet A)", title_style))
    story.append(Spacer(1, 2))

    # Meta Info
    meta_data = [
        [Paragraph("Homeroom Teacher (Reading):", small_style), Paragraph("Teacher A", normal_style), Paragraph("School Administrator:", small_style), Paragraph("Principal A", normal_style)],
        [Paragraph("Date Created:", small_style), Paragraph("2025 / 10 / 15", normal_style), Paragraph("Created by:", small_style), Paragraph("Teacher A", normal_style)],
        [Paragraph("Date Added (Added by):", small_style), Paragraph("Staff A / Staff B", normal_style), "", ""],
    ]
    meta_t = Table(meta_data, colWidths=[45*mm, 48*mm, 45*mm, 48*mm], rowHeights=[12, 12, 12])
    meta_t.setStyle(get_table_style([
        ("BACKGROUND", (0, 0), (0, 2), WARM_GREY),
        ("BACKGROUND", (2, 0), (2, 1), WARM_GREY),
        ("BACKGROUND", (1, 0), (1, 1), LIGHT_BLUE),
        ("BACKGROUND", (3, 0), (3, 1), LIGHT_BLUE),
        ("SPAN", (1, 2), (3, 2)),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
    ]))
    story.append(meta_t)
    story.append(Spacer(1, 4))

    # Student Info Table (Page 3)
    stu_data = [
        [Paragraph("Name (Reading)", small_style), Paragraph("Gender", small_style), Paragraph("School Name", small_style), Paragraph("Grade", small_style), Paragraph("Class", small_style)],
        [Paragraph("( DOE, John )<br/>John Doe", normal_style), Paragraph("Male", normal_style), Paragraph("Oak Elementary", normal_style), Paragraph("6th", normal_style), Paragraph("Class 2", normal_style)],
    ]
    stu_t = Table(stu_data, colWidths=[60*mm, 16*mm, 60*mm, 25*mm, 25*mm], rowHeights=[12, 20])
    stu_t.setStyle(get_table_style([
        ("BACKGROUND", (0, 0), (-1, 0), WARM_GREY),
        ("BACKGROUND", (0, 1), (-1, 1), LIGHT_BLUE),
    ]))
    story.append(stu_t)
    story.append(Spacer(1, 4))

    # Support Agencies Table
    story.append(Paragraph("Support Agencies (In-school / External)", section_style))
    story.append(Spacer(1, 2))
    sup_data = [
        ["", Paragraph("Main Support Content", small_style), Paragraph("Agency Name", small_style), Paragraph("Phone Number", small_style), Paragraph("Contact Person", small_style)],
        [Paragraph("Home School", small_style), Paragraph("Homeroom guidance", normal_style), Paragraph("Oak Elementary School", normal_style), Paragraph("000-000-0000", normal_style), Paragraph("Teacher A", normal_style)],
        [Paragraph("Family", small_style), "", "", Paragraph("000-0000-0000", normal_style), ""],
        [Paragraph("Welfare", small_style), "", "", "", ""],
        [Paragraph("Medical", small_style), "", "", "", ""],
        [Paragraph("Other", small_style), Paragraph("Educational Support Center", normal_style), Paragraph("Oak Support Center", normal_style), Paragraph("000-000-0000", normal_style), Paragraph("Counsellor A", normal_style)],
    ]
    sup_t = Table(sup_data, colWidths=[20*mm, 55*mm, 45*mm, 36*mm, 30*mm], rowHeights=[12]+[20]*5)
    sup_t.setStyle(get_table_style([
        ("BACKGROUND", (1, 0), (-1, 0), WARM_GREY),
        ("BACKGROUND", (0, 1), (0, -1), WARM_GREY),
        ("SPAN", (1, 2), (2, 2)), # merge main support and agency for family row
        ("BACKGROUND", (2, 1), (2, 1), LIGHT_BLUE),
        ("BACKGROUND", (3, 2), (4, 2), LIGHT_BLUE),
        ("ALIGN", (1, 1), (-1, -1), "LEFT"),
    ]))
    # Draw diagonal line in merged cell
    sup_data[2][1] = DiagonalLine(100*mm, 20)
    story.append(sup_t)
    story.append(Spacer(1, 4))

    # Monthly Absence Table
    story.append(Paragraph("Monthly Absence Record &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; * Date Added → &nbsp; 10 / 15", section_style))
    story.append(Spacer(1, 2))

    months = ["Month", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec", "Jan", "Feb", "Mar", "Total"]
    month_rows_ex = [
        ("Days Required to Attend",             ["21","20","21","20","0","20","21","20","22","20","19","21","205"]),
        ("Days Attended",                        ["5", "3", "2", "1","0","2", "1", "0","1", "2", "1", "2", "20"]),
        ("Attended (Separate Room)",             ["3", "2", "1","0","0","1","1","0","0","0","0","0","8"]),
        ("Late Arrivals",                        ["2","1","0","0","0","0","0","0","0","0","0","0","3"]),
        ("Early Departures",                     ["1","0","0","0","0","0","0","0","0","0","0","0","1"]),
        ("Cumulative Absent Days",               ["16","33","52","71","71","89","109","129","150","168","186","205","—"]),
        ("Absent Days (incl. official attend.)", ["16","17","19","19","0","18","20","20","21","18","18","19","185"]),
        ("Recorded as Attended (Official Reg.)",["0","0","0","0","0","0","0","0","0","0","0","0","0"]),
        ("① Educational Support Center",        ["0","0","0","0","0","0","0","0","0","0","0","0","0"]),
        ("② Board of Education Agency",         ["0","0","0","0","0","0","0","0","0","0","0","0","0"]),
        ("③ Child Guidance / Welfare Office",   ["0","0","0","0","0","0","0","0","0","0","0","0","0"]),
        ("④ Public Health Center",              ["0","0","0","0","0","0","0","0","0","0","0","0","0"]),
        ("⑤ Hospital / Clinic",                ["0","0","0","0","0","0","0","0","0","0","0","0","0"]),
        ("⑥ Private Organization / Facility",   ["0","0","0","0","0","0","0","0","0","0","0","0","0"]),
        ("⑦ Other Agencies",                   ["0","0","0","0","0","0","0","0","0","0","0","0","0"]),
        ("⑧ Use of IT / Online Learning",      ["0","0","0","0","0","0","0","0","0","0","0","0","0"]),
    ]

    m_data = []
    m_data.append([Paragraph("* Date Added →", small_style)] + [""]*13)
    m_data.append([Paragraph("Month", small_style)] + [Paragraph(m, small_style) for m in months[1:]])
    for label, vals in month_rows_ex:
        m_data.append([Paragraph(label, small_style)] + [Paragraph(v, small_style) for v in vals])

    m_t = Table(m_data, colWidths=abs_col_widths, rowHeights=[10]*18)
    m_t.setStyle(get_table_style([
        ("BACKGROUND", (0, 0), (-1, 0), WARM_GREY),
        ("BACKGROUND", (0, 1), (-1, 1), WARM_GREY),
        ("BACKGROUND", (0, 2), (0, 6), WARM_GREY),
        ("BACKGROUND", (0, 7), (-1, 7), LIGHT_BLUE), # Cumulative Absent Days
        ("BACKGROUND", (0, 8), (-1, 8), PEACH),      # Absent Days (incl. official attendance)
        ("BACKGROUND", (0, 9), (0, 17), LIGHT_BLUE), # Official attendance sub-labels
        ("BACKGROUND", (-1, 2), (-1, -1), LIGHT_BLUE), # Total column is light blue
        ("ALIGN", (0, 0), (0, -1), "LEFT"),
        ("LINEBELOW", (0, 10), (-1, 16), 0.5, BLACK, 0, (1, 2)),
    ]))
    story.append(m_t)
    story.append(Spacer(1, 4))

    # Reasons Section
    story.append(Paragraph("Reasons for Extended Absence / Continued School Refusal / etc.", section_style))
    story.append(Spacer(1, 1))
    reasons_val = Paragraph("School refusal. Reports feeling anxious about peer relationships. Observed since 4th grade.", normal_style)
    reasons_t = Table([[reasons_val]], colWidths=[PAGE_W], rowHeights=None)
    reasons_t.setStyle(get_table_style([
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(reasons_t)
    story.append(Spacer(1, 4))

    # Handover Section
    story.append(Paragraph("Handover Notes for Next School Year", section_style))
    story.append(Spacer(1, 1))
    handover_val = Paragraph("Continue regular contact with parents. Coordinate with the Educational Support Center. Encourage gradual re-integration via the separate room.", normal_style)
    handover_t = Table([[handover_val]], colWidths=[PAGE_W], rowHeights=None)
    handover_t.setStyle(get_table_style([
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(handover_t)
    story.append(PageBreak())

    # ── Page 4: Grade-Level Sheet B ─────────────────────────────────────────
    story.append(Paragraph("Student Understanding / Support Sheet (Grade-Level Sheet B)", title_style))
    story.append(Spacer(1, 2))

    # Meta Table (same as Page 3 but labeled B sheet)
    metaB_data = [
        [Paragraph("Homeroom Teacher (Reading):", small_style), Paragraph("Teacher A", normal_style), Paragraph("School Administrator:", small_style), Paragraph("Principal A", normal_style)],
        [Paragraph("Date Created:", small_style), Paragraph("2025 / 10 / 15", normal_style), Paragraph("Created by:", small_style), Paragraph("Teacher A", normal_style)],
        [Paragraph("Date Added (Added by):", small_style), Paragraph("Staff A / Staff B", normal_style), "", ""],
    ]
    metaB_t = Table(metaB_data, colWidths=[45*mm, 48*mm, 45*mm, 48*mm], rowHeights=[12, 12, 12])
    metaB_t.setStyle(get_table_style([
        ("BACKGROUND", (0, 0), (0, 2), WARM_GREY),
        ("BACKGROUND", (2, 0), (2, 1), WARM_GREY),
        ("BACKGROUND", (1, 0), (1, 1), LIGHT_BLUE),
        ("BACKGROUND", (3, 0), (3, 1), LIGHT_BLUE),
        ("SPAN", (1, 2), (3, 2)),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
    ]))
    story.append(metaB_t)
    story.append(Spacer(1, 4))

    # Student Info Table (Page 4)
    stuB_data = [
        [Paragraph("Name (Reading)", small_style), Paragraph("Gender", small_style), Paragraph("School Name", small_style), Paragraph("Grade", small_style), Paragraph("Class", small_style)],
        [Paragraph("( DOE, John )<br/>John Doe", normal_style), Paragraph("Male", normal_style), Paragraph("Oak Elementary", normal_style), Paragraph("6th", normal_style), Paragraph("Class 2", normal_style)],
    ]
    stuB_t = Table(stuB_data, colWidths=[60*mm, 16*mm, 60*mm, 25*mm, 25*mm], rowHeights=[12, 20])
    stuB_t.setStyle(get_table_style([
        ("BACKGROUND", (0, 0), (-1, 0), WARM_GREY),
        ("BACKGROUND", (0, 1), (-1, 1), LIGHT_BLUE),
    ]))
    story.append(stuB_t)
    story.append(Spacer(1, 4))

    # Wishes Table
    story.append(Paragraph("Current Situation and Wishes of Student / Guardian", section_style))
    story.append(Spacer(1, 2))
    wishes_data = [
        ["", Paragraph("Current Situation", small_style), Paragraph("Future Wishes (incl. career path)", small_style)],
        [Paragraph("Student", small_style), Paragraph("Wants to go to school but feels anxious.", normal_style), Paragraph("Wants to attend middle school normally.", normal_style)],
        [Paragraph("Guardian", small_style), Paragraph("Would like son to gradually re-engage with school.", normal_style), Paragraph("Hopes he can attend a regular high school.", normal_style)],
    ]
    wishes_t = Table(wishes_data, colWidths=[20*mm, 83*mm, 83*mm], rowHeights=[12, 35, 35])
    wishes_t.setStyle(get_table_style([
        ("BACKGROUND", (1, 0), (-1, 0), WARM_GREY),
        ("BACKGROUND", (0, 1), (0, -1), WARM_GREY),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
    ]))
    story.append(wishes_t)
    story.append(Spacer(1, 4))

    # Goals Section
    story.append(Paragraph("Goals for This School Year", section_style))
    story.append(Spacer(1, 1))
    goals_val = Paragraph("Increase attendance by utilizing the separate room and building a trusting relationship.", normal_style)
    goals_t = Table([[goals_val]], colWidths=[PAGE_W], rowHeights=None)
    goals_t.setStyle(get_table_style([
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(goals_t)
    story.append(Spacer(1, 4))

    # Support Plan Table
    story.append(Paragraph("Individual Support Plan by Term", section_style))
    story.append(Spacer(1, 2))
    plan_data = [
        ["", "", Paragraph("Goal", small_style), Paragraph("Support Content", small_style), Paragraph("Progress / Evaluation", small_style)],
        ["", Paragraph("School", small_style), Paragraph("Visit separate room at least 3x/week", normal_style), Paragraph("Daily check-in call by homeroom teacher; separate room available", normal_style), ""],
        ["", Paragraph("Related Agencies", small_style), Paragraph("Coordinate with Support Center", normal_style), Paragraph("Weekly check-in with Support Center counsellor", normal_style), ""],
        ["", Paragraph("School", small_style), Paragraph("Attend at least one regular class per week", normal_style), Paragraph("Gradual re-integration plan with class teacher", normal_style), ""],
        ["", Paragraph("Related Agencies", small_style), Paragraph("Continue counselling", normal_style), Paragraph("Bi-weekly family meeting", normal_style), ""],
        ["", Paragraph("School", small_style), Paragraph("Maintain attendance rhythm", normal_style), Paragraph("Celebrate progress; prepare transition plan", normal_style), ""],
        ["", Paragraph("Related Agencies", small_style), Paragraph("Handover to middle school", normal_style), Paragraph("Joint meeting with middle school counsellor", normal_style), ""],
    ]
    plan_data[1][0] = RotatedText("1st Term", small_style, 20*mm, 36)
    plan_data[3][0] = RotatedText("2nd Term", small_style, 20*mm, 36)
    plan_data[5][0] = RotatedText("3rd Term", small_style, 20*mm, 36)

    plan_t = Table(plan_data, colWidths=plan_col_widths, rowHeights=[12]+[18]*6)
    plan_t.setStyle(get_table_style([
        ("BACKGROUND", (2, 0), (-1, 0), WARM_GREY),
        ("BACKGROUND", (0, 1), (1, -1), WARM_GREY),
        ("SPAN", (0, 1), (0, 2)),
        ("SPAN", (0, 3), (0, 4)),
        ("SPAN", (0, 5), (0, 6)),
        ("ALIGN", (2, 1), (-1, -1), "LEFT"),
    ]))
    story.append(plan_t)
    story.append(PageBreak())

    # ── Page 5: Discussion Sheet ─────────────────────────────────────────────
    story.append(Paragraph("Student Understanding / Support Sheet (Discussion Sheet)", title_style))
    story.append(Spacer(1, 2))

    # Info above table
    disc_meta = [
        [Paragraph("Recorder: &nbsp; <b>Staff A (homeroom teacher)</b> &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Student Guidance Coordinator: &nbsp; <b>Staff B</b>", small_style),
         Paragraph("Date: &nbsp; <b>2025 / 10 / 15</b>", small_style)]
    ]
    disc_meta_t = Table(disc_meta, colWidths=[120*mm, PAGE_W - 120*mm])
    disc_meta_t.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN", (1, 0), (1, 0), "RIGHT"),
    ]))
    story.append(disc_meta_t)
    story.append(Spacer(1, 2))

    # Header Table
    disc_hdr = [
        [Paragraph("Grade", small_style), Paragraph("Class", small_style), Paragraph("Name", small_style), Paragraph("Participants / Agencies", small_style)],
        [Paragraph("6th", normal_style), Paragraph("Class 2", normal_style), Paragraph("John Doe", normal_style), Paragraph("Homeroom teacher, guidance coordinator, Support Center counsellor, parent", normal_style)],
    ]
    disc_hdr_t = Table(disc_hdr, colWidths=[20*mm, 20*mm, 50*mm, 96*mm], rowHeights=[12, 18])
    disc_hdr_t.setStyle(get_table_style([
        ("BACKGROUND", (0, 0), (-1, 0), WARM_GREY),
        ("BACKGROUND", (0, 1), (2, 1), LIGHT_BLUE),
        ("ALIGN", (3, 1), (3, 1), "LEFT"),
    ]))
    story.append(disc_hdr_t)
    story.append(Spacer(1, 4))

    # Sections (Set heights to None for auto-size, no overflow/overlap)
    # Note: Page 5 of Document 2 in original was empty, but since we are generating an example form,
    # we include example values, and set height to None to auto-expand to fit the dynamic text.
    sections_data = [
        ("Student's Wishes", Paragraph("Wants to go to school but feels scared when he thinks about it.", normal_style)),
        ("Guardian's Wishes", Paragraph("Would like the school and Support Center to work together to help son feel safe at school.", normal_style)),
        ("Information from Related Agencies", Paragraph("Support Center counsellor reports: Student is gradually opening up; recommends slow, pressure-free re-integration.", normal_style)),
        ("Support Status", Paragraph("Homeroom teacher calls daily. Support Center provides weekly counselling. Parents attend monthly meetings.", normal_style)),
    ]
    for label, val in sections_data:
        story.append(Paragraph(label, section_style))
        story.append(Spacer(1, 1))
        sec_t = Table([[val]], colWidths=[PAGE_W], rowHeights=None)
        sec_t.setStyle(get_table_style([
            ("ALIGN", (0, 0), (-1, -1), "LEFT"),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("TOPPADDING", (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ]))
        story.append(sec_t)
        story.append(Spacer(1, 4))

    # Goal block under Support Status
    goal_data = [
        [Paragraph("Goal", small_style), Paragraph("Re-establish normal school attendance and routines.", normal_style)]
    ]
    goal_t = Table(goal_data, colWidths=[20*mm, PAGE_W - 20*mm], rowHeights=[16])
    goal_t.setStyle(get_table_style([
        ("BACKGROUND", (0, 0), (0, 0), WARM_GREY),
        ("ALIGN", (0, 0), (0, 0), "CENTER"),
        ("ALIGN", (1, 0), (1, 0), "LEFT"),
    ]))
    story.append(goal_t)
    story.append(Spacer(1, 2))

    # Role Allocation table
    role_data = [
        ["", Paragraph("Agency / Division", small_style), Paragraph("Short-Term Goal &nbsp; &nbsp; MM / DD", small_style), Paragraph("Progress / Evaluation &nbsp; &nbsp; MM / DD", small_style)],
        ["", Paragraph("Home School (homeroom)", normal_style), Paragraph("Daily check-in; invite to separate room", normal_style), ""],
        ["", Paragraph("Support Center", normal_style), Paragraph("Weekly counselling session", normal_style), ""],
        ["", Paragraph("Family", normal_style), Paragraph("Encourage attendance in a low-pressure way", normal_style), ""],
        ["", "", "", ""],
        ["", "", "", ""],
        ["", "", "", ""],
    ]
    role_data[1][0] = RotatedText("Role Allocation", small_style, 10*mm, 70)

    role_t = Table(role_data, colWidths=role_col_widths, rowHeights=[12]+[15]*6)
    role_t.setStyle(get_table_style([
        ("BACKGROUND", (1, 0), (-1, 0), WARM_GREY),
        ("BACKGROUND", (0, 1), (0, -1), WARM_GREY),
        ("SPAN", (0, 1), (0, -1)),
        ("ALIGN", (1, 1), (-1, -1), "LEFT"),
    ]))
    story.append(role_t)
    story.append(Spacer(1, 4))

    # Confirmations Section
    story.append(Paragraph("Confirmations / Agreed Matters", section_style))
    story.append(Spacer(1, 1))
    conf_val = Paragraph("All parties agreed to meet monthly and share updates via a shared record sheet.", normal_style)
    conf_t = Table([[conf_val]], colWidths=[PAGE_W], rowHeights=None)
    conf_t.setStyle(get_table_style([
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    story.append(conf_t)
    story.append(Spacer(1, 4))

    # Special Notes Section
    story.append(Paragraph("Special Notes", section_style))
    story.append(Spacer(1, 1))
    spec_val = Paragraph("Next meeting scheduled for November 12, 2025.", normal_style)
    spec_t = Table([[spec_val]], colWidths=[PAGE_W], rowHeights=None)
    spec_t.setStyle(get_table_style([
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    story.append(spec_t)

    return story


# ════════════════════════════════════════════════════════════════════════════
#  Main Execution
# ════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    out_dir = os.path.dirname(os.path.abspath(__file__))

    out1 = os.path.join(out_dir, "Student Understanding Model Sheet (English).pdf")
    doc1 = SimpleDocTemplate(out1, pagesize=A4,
                             leftMargin=12*mm, rightMargin=12*mm,
                             topMargin=12*mm, bottomMargin=12*mm)
    doc1.build(build_doc1())
    print(f"Created: {out1}")

    out2 = os.path.join(out_dir, "Student Understanding and Support Sheet - Example Form (English).pdf")
    doc2 = SimpleDocTemplate(out2, pagesize=A4,
                             leftMargin=12*mm, rightMargin=12*mm,
                             topMargin=12*mm, bottomMargin=12*mm)
    doc2.build(build_doc2())
    print(f"Created: {out2}")
