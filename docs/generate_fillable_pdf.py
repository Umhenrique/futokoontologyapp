# -*- coding: utf-8 -*-
"""
Generate a fillable PDF form (AcroForm) of the English Student Understanding / Support Sheet.
Maintains the exact 5-page layout and styling as the original reference format.
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

W, H = A4  # 595.27 x 841.89 points
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
PEACH = colors.HexColor("#FCE4D6")       # Peach row on monthly table
WARM_GREY = colors.HexColor("#F0EFEA")   # Table headers background
WHITE = colors.white
BLACK = colors.black

# ── Custom Paragraph Styles ──────────────────────────────────────────
def S(name, **kw):
    base = kw.pop("parent", "Normal")
    s = ParagraphStyle(name, parent=styles[base], **kw)
    return s

title_style   = S("Title3",   fontSize=11, fontName="Helvetica-Bold", leading=14, alignment=TA_CENTER, spaceAfter=2)
header_style  = S("Header3",  fontSize=8.5, leading=11, alignment=TA_CENTER)
normal_style  = S("Normal3",  fontSize=8,  leading=10)
small_style   = S("Small3",   fontSize=7,  leading=9)
section_style = S("Section3", fontSize=8.5, leading=11, fontName="Helvetica-Bold")
note_style    = S("Note3",    fontSize=6.5, leading=8.5, textColor=colors.grey)

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

class FlowableTextField(Flowable):
    """Draws an interactive AcroForm textfield relative to current coordinates."""
    def __init__(self, name, width, height, value="", multiline=False, fillColor=WHITE, fontSize=7.5):
        super().__init__()
        self.name = name
        self.width = width
        self.height = height
        self.value = value
        self.multiline = multiline
        self.fillColor = fillColor
        self.fontSize = fontSize

    def wrap(self, availWidth, availHeight):
        return self.width, self.height

    def draw(self):
        self.canv.saveState()
        form = self.canv.acroForm
        fieldFlags = 'multiline' if self.multiline else ''
        form.textfield(
            name=self.name,
            x=0, y=0,
            width=self.width,
            height=self.height,
            value=self.value,
            fillColor=self.fillColor,
            borderColor=colors.transparent,
            borderWidth=0,
            textColor=BLACK,
            fontSize=self.fontSize,
            fontName="Helvetica",
            relative=True,
            fieldFlags=fieldFlags,
            maxlen=2000 if self.multiline else 150
        )
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

# ── Main Document Builder ───────────────────────────────────────────
def build_fillable_doc():
    story = []

    # =========================================================================
    # PAGE 1: COVER PAGE
    # =========================================================================
    story.append(Spacer(1, 10))
    top_header = [
        ["", Paragraph("(Attachment 2)", S("TopR_F", fontSize=8, alignment=TA_RIGHT))],
        ["", Paragraph("HANDLE WITH CARE", S("HWC_Cover_F", fontSize=8.5, fontName="Helvetica-Bold", alignment=TA_CENTER))]
    ]
    top_header_t = Table(top_header, colWidths=[PAGE_W - 42*mm, 42*mm], rowHeights=[12, 18])
    top_header_t.setStyle(TableStyle([
        ("BOX", (1, 1), (1, 1), 1.2, BLACK),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN", (1, 1), (1, 1), "CENTER"),
    ]))
    story.append(top_header_t)
    story.append(Spacer(1, 40))

    story.append(Paragraph("Student Understanding / Support Sheet (Reference Format)", S("MTitle_F", fontSize=15, fontName="Helvetica-Bold", alignment=TA_CENTER)))
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

    # School Name Table
    story.append(Paragraph("Current enrolled school name or graduated school name", section_style))
    story.append(Spacer(1, 4))
    school_data = [
        [Paragraph("(Elementary)", normal_style), FlowableTextField("school_name_elementary", PAGE_W - 32*mm, 18, fillColor=CREAM)],
        [Paragraph("(Middle)", normal_style), FlowableTextField("school_name_middle", PAGE_W - 32*mm, 18, fillColor=CREAM)],
        [Paragraph("(High)", normal_style), FlowableTextField("school_name_high", PAGE_W - 32*mm, 18, fillColor=CREAM)],
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
        [Paragraph("(Reading / Furigana)", small_style), FlowableTextField("student_name_reading", PAGE_W - 42*mm, 12, fillColor=CREAM)],
        [Paragraph("Student Name", section_style), FlowableTextField("student_name", PAGE_W - 42*mm, 18, fillColor=CREAM)],
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

    # Classification number
    class_data = [
        ["", Paragraph("Classification Number", small_style), FlowableTextField("classification_number", 38*mm, 18, fillColor=CREAM)]
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

    # =========================================================================
    # PAGE 2: COMMON SHEET
    # =========================================================================
    story.append(Paragraph("Student Understanding / Support Sheet (Common Sheet)", title_style))
    story.append(Spacer(1, 2))

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
        [Paragraph("Created by &nbsp;", small_style), FlowableTextField("created_by_staff", 60*mm, 10, fillColor=WHITE),
         Paragraph("Added by &nbsp;", small_style), FlowableTextField("added_by_staff", 80*mm, 10, fillColor=WHITE)]
    ]
    added_info_t = Table(added_info, colWidths=[20*mm, 60*mm, 20*mm, 86*mm], rowHeights=[12])
    added_info_t.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
    ]))
    story.append(added_info_t)
    story.append(Spacer(1, 2))

    # Student Info Table
    student_data = [
        [Paragraph("(Student)<br/>Name", small_style), Paragraph("Gender", small_style), Paragraph("Date of Birth", small_style), Paragraph("Nationality *", small_style), Paragraph("Birthplace *", small_style)],
        [FlowableTextField("student_name", 48*mm, 18, fillColor=LIGHT_BLUE),
         FlowableTextField("gender", 14*mm, 18, fillColor=WHITE),
         FlowableTextField("dob", 48*mm, 18, fillColor=WHITE),
         FlowableTextField("nationality", 33*mm, 18, fillColor=WHITE),
         FlowableTextField("birthplace", 33*mm, 18, fillColor=WHITE)],
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
        [FlowableTextField("guardian_name", 48*mm, 18, fillColor=WHITE),
         FlowableTextField("guardian_relationship", 29*mm, 18, fillColor=WHITE),
         FlowableTextField("enrollment_date", 48*mm, 18, fillColor=WHITE),
         FlowableTextField("guardian_contact", 53*mm, 18, fillColor=WHITE)],
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
    abs_data.append([Paragraph("Fiscal Year", small_style)] + [FlowableTextField(f"abs_year_{g}", 9*mm, 9, fillColor=WHITE) for g in grades[1:]])
    abs_data.append([Paragraph("Grade", small_style)] + [Paragraph(g, small_style) for g in grades[1:]])
    for r_idx, r in enumerate(abs_rows):
        # We make the actual numeric cells fillable
        row_cells = [Paragraph(r, small_style)]
        for c_idx, g in enumerate(grades[1:]):
            f_name = f"abs_days_{r_idx}_{g}"
            # Use light blue for absent days row to match legend
            bg = LIGHT_BLUE if r_idx == 5 else WHITE
            row_cells.append(FlowableTextField(f_name, 9*mm, 9, fillColor=bg))
        abs_data.append(row_cells)

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

    # Basic Info Section
    story.append(Paragraph("Basic Information for Continuous Support", section_style))
    story.append(Paragraph("Special notes (student's strengths, assessment information, home situation, type/degree/diagnosis of disability, type and date of disability certificate *, learning history *, Japanese proficiency *, etc.)", note_style))
    story.append(Spacer(1, 1))
    basic_info_t = Table([[FlowableTextField("basic_info", PAGE_W - 4*mm, 22, multiline=True, fillColor=WHITE)]], colWidths=[PAGE_W], rowHeights=[26])
    basic_info_t.setStyle(get_table_style())
    story.append(basic_info_t)
    story.append(Spacer(1, 4))

    # Family Situation Section
    story.append(Paragraph("Family Situation", section_style))
    story.append(Paragraph("Special notes (developmental history, surrounding circumstances incl. family situation, changes since creation date, family composition *, language used at home *, etc.)", note_style))
    story.append(Spacer(1, 1))
    fam_t = Table([[FlowableTextField("family_situation", PAGE_W - 4*mm, 22, multiline=True, fillColor=WHITE)]], colWidths=[PAGE_W], rowHeights=[26])
    fam_t.setStyle(get_table_style())
    story.append(fam_t)
    story.append(Spacer(1, 4))

    # Remarks Section
    story.append(Paragraph("Remarks", section_style))
    story.append(Spacer(1, 1))
    rem_t = Table([[FlowableTextField("remarks_page2", PAGE_W - 4*mm, 16, multiline=True, fillColor=WHITE)]], colWidths=[PAGE_W], rowHeights=[20])
    rem_t.setStyle(get_table_style())
    story.append(rem_t)
    story.append(PageBreak())

    # =========================================================================
    # PAGE 3: GRADE-LEVEL SHEET A
    # =========================================================================
    story.append(Paragraph("Student Understanding / Support Sheet (Grade-Level Sheet A)", title_style))
    story.append(Spacer(1, 2))

    meta_data = [
        [Paragraph("Homeroom Teacher (Reading):", small_style), FlowableTextField("homeroom_teacher", 45*mm, 10, fillColor=LIGHT_BLUE),
         Paragraph("School Administrator:", small_style), FlowableTextField("administrator", 45*mm, 10, fillColor=LIGHT_BLUE)],
        [Paragraph("Date Created:", small_style), FlowableTextField("date_created", 45*mm, 10, fillColor=WHITE),
         Paragraph("Created by:", small_style), FlowableTextField("created_by", 45*mm, 10, fillColor=WHITE)],
        [Paragraph("Date Added (Added by):", small_style), FlowableTextField("date_added", 135*mm, 10, fillColor=WHITE), "", ""],
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

    # Student Info Table
    stu_data = [
        [Paragraph("Name (Reading)", small_style), Paragraph("Gender", small_style), Paragraph("School Name", small_style), Paragraph("Grade", small_style), Paragraph("Class", small_style)],
        [FlowableTextField("student_name", 58*mm, 18, fillColor=LIGHT_BLUE),
         FlowableTextField("gender", 14*mm, 18, fillColor=LIGHT_BLUE),
         FlowableTextField("school_name", 58*mm, 18, fillColor=WHITE),
         FlowableTextField("grade", 23*mm, 18, fillColor=WHITE),
         FlowableTextField("class_name", 23*mm, 18, fillColor=WHITE)],
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
        [Paragraph("Home School", small_style), FlowableTextField("school_support_content", 53*mm, 16, fillColor=WHITE), FlowableTextField("school_name", 43*mm, 16, fillColor=LIGHT_BLUE), FlowableTextField("school_phone", 34*mm, 16, fillColor=WHITE), FlowableTextField("school_contact", 28*mm, 16, fillColor=WHITE)],
        [Paragraph("Family", small_style), "", "", FlowableTextField("family_phone", 34*mm, 16, fillColor=LIGHT_BLUE), FlowableTextField("family_contact", 28*mm, 16, fillColor=LIGHT_BLUE)],
        [Paragraph("Welfare", small_style), FlowableTextField("welfare_support_content", 53*mm, 16, fillColor=WHITE), FlowableTextField("welfare_agency_name", 43*mm, 16, fillColor=WHITE), FlowableTextField("welfare_phone", 34*mm, 16, fillColor=WHITE), FlowableTextField("welfare_contact", 28*mm, 16, fillColor=WHITE)],
        [Paragraph("Medical", small_style), FlowableTextField("medical_support_content", 53*mm, 16, fillColor=WHITE), FlowableTextField("medical_agency_name", 43*mm, 16, fillColor=WHITE), FlowableTextField("medical_phone", 34*mm, 16, fillColor=WHITE), FlowableTextField("medical_contact", 28*mm, 16, fillColor=WHITE)],
        [Paragraph("Other", small_style), FlowableTextField("other_support_content", 53*mm, 16, fillColor=WHITE), FlowableTextField("support_facility", 43*mm, 16, fillColor=WHITE), FlowableTextField("other_phone", 34*mm, 16, fillColor=WHITE), FlowableTextField("other_contact", 28*mm, 16, fillColor=WHITE)],
    ]
    # Family row diagonal line placeholder
    sup_data[2][1] = DiagonalLine(100*mm, 20)

    sup_t = Table(sup_data, colWidths=[20*mm, 55*mm, 45*mm, 36*mm, 30*mm], rowHeights=[12]+[20]*5)
    sup_t.setStyle(get_table_style([
        ("BACKGROUND", (1, 0), (-1, 0), WARM_GREY),
        ("BACKGROUND", (0, 1), (0, -1), WARM_GREY),
        ("SPAN", (1, 2), (2, 2)), # merge main support and agency for family row
        ("BACKGROUND", (2, 1), (2, 1), LIGHT_BLUE),
        ("BACKGROUND", (3, 2), (4, 2), LIGHT_BLUE),
    ]))
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
    m_data.append([Paragraph("* Date Added →", small_style)] + [FlowableTextField(f"m_date_{m}", 9*mm, 8, fillColor=WHITE) for m in months[1:]])
    m_data.append([Paragraph("Month", small_style)] + [Paragraph(m, small_style) for m in months[1:]])
    
    # We make all cells in this table fillable
    for r_idx, r in enumerate(month_rows):
        row_cells = [Paragraph(r, small_style)]
        for c_idx, m in enumerate(months[1:]):
            f_name = f"m_abs_{r_idx}_{m}"
            bg = WHITE
            if r_idx == 5: bg = LIGHT_BLUE
            elif r_idx == 6: bg = PEACH
            elif r_idx >= 7: bg = LIGHT_BLUE
            
            # Highlight total columns
            if m == "Total":
                bg = LIGHT_BLUE
                # Let's map "absent_days" directly to the total absent days row 6 or 5 total!
                if r_idx == 6: # Absent Days row total
                    f_name = "absent_days"
                    
            row_cells.append(FlowableTextField(f_name, 9*mm, 8, fillColor=bg))
        m_data.append(row_cells)

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
    reasons_t = Table([[FlowableTextField("reasons_extended_absence", PAGE_W - 4*mm, 16, multiline=True, fillColor=WHITE)]], colWidths=[PAGE_W], rowHeights=[20])
    reasons_t.setStyle(get_table_style())
    story.append(reasons_t)
    story.append(Spacer(1, 4))

    # Handover Section
    story.append(Paragraph("Handover Notes for Next School Year (include episodes relevant to support/guidance, recorded from diverse perspectives)", section_style))
    story.append(Spacer(1, 1))
    handover_t = Table([[FlowableTextField("handover_notes", PAGE_W - 4*mm, 22, multiline=True, fillColor=WHITE)]], colWidths=[PAGE_W], rowHeights=[26])
    handover_t.setStyle(get_table_style())
    story.append(handover_t)
    story.append(PageBreak())

    # =========================================================================
    # PAGE 4: GRADE-LEVEL SHEET B
    # =========================================================================
    story.append(Paragraph("Student Understanding / Support Sheet (Grade-Level Sheet B)", title_style))
    story.append(Spacer(1, 2))

    metaB_data = [
        [Paragraph("Homeroom Teacher (Reading):", small_style), FlowableTextField("homeroom_teacher", 45*mm, 10, fillColor=LIGHT_BLUE),
         Paragraph("School Administrator:", small_style), FlowableTextField("administrator", 45*mm, 10, fillColor=LIGHT_BLUE)],
        [Paragraph("Date Created:", small_style), FlowableTextField("date_created", 45*mm, 10, fillColor=LIGHT_BLUE),
         Paragraph("Created by:", small_style), FlowableTextField("created_by", 45*mm, 10, fillColor=LIGHT_BLUE)],
        [Paragraph("Date Added (Added by):", small_style), FlowableTextField("date_added_b", 135*mm, 10, fillColor=WHITE), "", ""],
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

    # Student Info Table
    stuB_data = [
        [Paragraph("Name (Reading)", small_style), Paragraph("Gender", small_style), Paragraph("School Name", small_style), Paragraph("Grade", small_style), Paragraph("Class", small_style)],
        [FlowableTextField("student_name", 58*mm, 18, fillColor=LIGHT_BLUE),
         FlowableTextField("gender", 14*mm, 18, fillColor=LIGHT_BLUE),
         FlowableTextField("school_name", 58*mm, 18, fillColor=LIGHT_BLUE),
         FlowableTextField("grade", 23*mm, 18, fillColor=LIGHT_BLUE),
         FlowableTextField("class_name", 23*mm, 18, fillColor=LIGHT_BLUE)],
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
        [Paragraph("Student", small_style), FlowableTextField("student_current_situation", 81*mm, 31, multiline=True, fillColor=WHITE), FlowableTextField("student_future_wishes", 81*mm, 31, multiline=True, fillColor=WHITE)],
        [Paragraph("Guardian", small_style), FlowableTextField("guardian_current_situation", 81*mm, 31, multiline=True, fillColor=WHITE), FlowableTextField("guardian_future_wishes", 81*mm, 31, multiline=True, fillColor=WHITE)],
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
    goals_t = Table([[FlowableTextField("goals_for_year", PAGE_W - 4*mm, 16, multiline=True, fillColor=WHITE)]], colWidths=[PAGE_W], rowHeights=[20])
    goals_t.setStyle(get_table_style())
    story.append(goals_t)
    story.append(Spacer(1, 4))

    # Support Plan Table
    story.append(Paragraph("Individual Support Plan by Term", section_style))
    story.append(Spacer(1, 2))
    plan_data = [
        ["", "", Paragraph("Goal", small_style), Paragraph("Support Content", small_style), Paragraph("Progress / Evaluation", small_style)],
        ["", Paragraph("School", small_style), FlowableTextField("plan_goal_school_1", 43*mm, 15, fillColor=WHITE), FlowableTextField("plan_content_school_1", 58*mm, 15, fillColor=WHITE), FlowableTextField("plan_eval_school_1", 39*mm, 15, fillColor=WHITE)],
        ["", Paragraph("Related Agencies", small_style), FlowableTextField("plan_goal_agency_1", 43*mm, 15, fillColor=WHITE), FlowableTextField("plan_content_agency_1", 58*mm, 15, fillColor=WHITE), FlowableTextField("plan_eval_agency_1", 39*mm, 15, fillColor=WHITE)],
        ["", Paragraph("School", small_style), FlowableTextField("plan_goal_school_2", 43*mm, 15, fillColor=WHITE), FlowableTextField("plan_content_school_2", 58*mm, 15, fillColor=WHITE), FlowableTextField("plan_eval_school_2", 39*mm, 15, fillColor=WHITE)],
        ["", Paragraph("Related Agencies", small_style), FlowableTextField("plan_goal_agency_2", 43*mm, 15, fillColor=WHITE), FlowableTextField("plan_content_agency_2", 58*mm, 15, fillColor=WHITE), FlowableTextField("plan_eval_agency_2", 39*mm, 15, fillColor=WHITE)],
        ["", Paragraph("School", small_style), FlowableTextField("plan_goal_school_3", 43*mm, 15, fillColor=WHITE), FlowableTextField("plan_content_school_3", 58*mm, 15, fillColor=WHITE), FlowableTextField("plan_eval_school_3", 39*mm, 15, fillColor=WHITE)],
        ["", Paragraph("Related Agencies", small_style), FlowableTextField("plan_goal_agency_3", 43*mm, 15, fillColor=WHITE), FlowableTextField("plan_content_agency_3", 58*mm, 15, fillColor=WHITE), FlowableTextField("plan_eval_agency_3", 39*mm, 15, fillColor=WHITE)],
    ]
    # Vertical rotated labels
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

    # =========================================================================
    # PAGE 5: DISCUSSION SHEET
    # =========================================================================
    story.append(Paragraph("Student Understanding / Support Sheet (Discussion Sheet)", title_style))
    story.append(Spacer(1, 2))

    # Meta
    disc_meta = [
        [Paragraph("Recorder:", small_style), FlowableTextField("recorder_name", 60*mm, 10, fillColor=WHITE),
         Paragraph("Date:", small_style), FlowableTextField("discussion_date", 40*mm, 10, fillColor=WHITE)]
    ]
    disc_meta_t = Table(disc_meta, colWidths=[20*mm, 100*mm, 20*mm, 46*mm], rowHeights=[12])
    disc_meta_t.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
    ]))
    story.append(disc_meta_t)
    story.append(Spacer(1, 2))

    # Header Table
    disc_hdr = [
        [Paragraph("Grade", small_style), Paragraph("Class", small_style), Paragraph("Name", small_style), Paragraph("Participants / Agencies", small_style)],
        [FlowableTextField("grade", 18*mm, 15, fillColor=LIGHT_BLUE),
         FlowableTextField("class_name", 18*mm, 15, fillColor=LIGHT_BLUE),
         FlowableTextField("student_name", 48*mm, 15, fillColor=LIGHT_BLUE),
         FlowableTextField("discussion_participants", 94*mm, 15, fillColor=WHITE)],
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
        ("Student's Wishes", "student_wishes_disc", 22),
        ("Guardian's Wishes", "guardian_wishes_disc", 22),
        ("Information from Related Agencies", "agencies_info_disc", 22),
        ("Support Status", "support_status_disc", 10),
    ]
    for label, field_id, h in sections:
        story.append(Paragraph(label, section_style))
        story.append(Spacer(1, 1))
        sec_t = Table([[FlowableTextField(field_id, PAGE_W - 4*mm, h - 4, multiline=True, fillColor=WHITE)]], colWidths=[PAGE_W], rowHeights=[h])
        sec_t.setStyle(get_table_style())
        story.append(sec_t)
        story.append(Spacer(1, 4))

    # Goal block under Support Status
    goal_data = [
        [Paragraph("Goal", small_style), FlowableTextField("discussion_goal", PAGE_W - 24*mm, 12, fillColor=WHITE)]
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
        ["", FlowableTextField("role_agency_1", 44*mm, 12, fillColor=WHITE), FlowableTextField("role_goal_1", 63*mm, 12, fillColor=WHITE), FlowableTextField("role_eval_1", 63*mm, 12, fillColor=WHITE)],
        ["", FlowableTextField("role_agency_2", 44*mm, 12, fillColor=WHITE), FlowableTextField("role_goal_2", 63*mm, 12, fillColor=WHITE), FlowableTextField("role_eval_2", 63*mm, 12, fillColor=WHITE)],
        ["", FlowableTextField("role_agency_3", 44*mm, 12, fillColor=WHITE), FlowableTextField("role_goal_3", 63*mm, 12, fillColor=WHITE), FlowableTextField("role_eval_3", 63*mm, 12, fillColor=WHITE)],
        ["", FlowableTextField("role_agency_4", 44*mm, 12, fillColor=WHITE), FlowableTextField("role_goal_4", 63*mm, 12, fillColor=WHITE), FlowableTextField("role_eval_4", 63*mm, 12, fillColor=WHITE)],
        ["", FlowableTextField("role_agency_5", 44*mm, 12, fillColor=WHITE), FlowableTextField("role_goal_5", 63*mm, 12, fillColor=WHITE), FlowableTextField("role_eval_5", 63*mm, 12, fillColor=WHITE)],
        ["", FlowableTextField("role_agency_6", 44*mm, 12, fillColor=WHITE), FlowableTextField("role_goal_6", 63*mm, 12, fillColor=WHITE), FlowableTextField("role_eval_6", 63*mm, 12, fillColor=WHITE)],
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
    conf_t = Table([[FlowableTextField("confirmations_disc", PAGE_W - 4*mm, 16, multiline=True, fillColor=WHITE)]], colWidths=[PAGE_W], rowHeights=[20])
    conf_t.setStyle(get_table_style())
    story.append(conf_t)
    story.append(Spacer(1, 4))

    # Special Notes Section
    story.append(Paragraph("Special Notes", section_style))
    story.append(Spacer(1, 1))
    spec_t = Table([[FlowableTextField("special_notes_disc", PAGE_W - 4*mm, 16, multiline=True, fillColor=WHITE)]], colWidths=[PAGE_W], rowHeights=[20])
    spec_t.setStyle(get_table_style())
    story.append(spec_t)

    return story

if __name__ == "__main__":
    out_dir = os.path.dirname(os.path.abspath(__file__))
    out_path = os.path.join(out_dir, "Student Understanding Model Sheet - Fillable (English).pdf")
    
    doc = SimpleDocTemplate(
        out_path,
        pagesize=A4,
        leftMargin=12*mm,
        rightMargin=12*mm,
        topMargin=12*mm,
        bottomMargin=12*mm
    )
    
    doc.build(build_fillable_doc())
    print(f"Successfully generated: {out_path}")
