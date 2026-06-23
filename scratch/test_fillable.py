from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Flowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
import os

class FlowableTextField(Flowable):
    def __init__(self, name, width=100, height=15):
        super().__init__()
        self.name = name
        self.width = width
        self.height = height

    def wrap(self, availWidth, availHeight):
        return self.width, self.height

    def draw(self):
        self.canv.saveState()
        # Draw AcroForm text field relative to the current flowable position
        form = self.canv.acroForm
        form.textfield(
            name=self.name,
            x=0, y=0,
            width=self.width,
            height=self.height,
            relative=True
        )
        self.canv.restoreState()

if __name__ == "__main__":
    pdf_path = "scratch/test_fillable.pdf"
    doc = SimpleDocTemplate(pdf_path, pagesize=A4)
    story = []
    
    styles = getSampleStyleSheet()
    
    # Table containing a label and the fillable field
    data = [
        [Paragraph("Name:", styles["Normal"]), FlowableTextField("student_name", width=120, height=15)],
        [Paragraph("School:", styles["Normal"]), FlowableTextField("school_name", width=120, height=15)],
    ]
    
    t = Table(data, colWidths=[30*mm, 130*mm], rowHeights=[20, 20])
    t.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.black),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    
    story.append(t)
    doc.build(story)
    print(f"Generated test PDF: {pdf_path}")
