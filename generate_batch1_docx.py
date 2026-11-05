import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

def set_cell_margins(cell, top=120, bottom=120, left=180, right=180):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('w:top', top), ('w:bottom', bottom), ('w:left', left), ('w:right', right)]:
        node = OxmlElement(m)
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def set_cell_borders(cell, top="single", bottom="single", left="single", right="single", sz="4", color="auto"):
    tcPr = cell._tc.get_or_add_tcPr()
    tcBorders = OxmlElement('w:tcBorders')
    borders = {'top': top, 'bottom': bottom, 'left': left, 'right': right}
    for border_name, border_style in borders.items():
        if border_style:
            b_el = OxmlElement(f'w:{border_name}')
            b_el.set(qn('w:val'), border_style)
            b_el.set(qn('w:sz'), sz)
            b_el.set(qn('w:space'), '0')
            b_el.set(qn('w:color'), color)
            tcBorders.append(b_el)
        else:
            b_el = OxmlElement(f'w:{border_name}')
            b_el.set(qn('w:val'), 'none')
            tcBorders.append(b_el)
    tcPr.append(tcBorders)

def add_footer_page_number(footer_para):
    footer_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = footer_para.add_run()
    fldChar1 = OxmlElement('w:fldChar')
    fldChar1.set(qn('w:fldCharType'), 'begin')
    instrText = OxmlElement('w:instrText')
    instrText.set(qn('xml:space'), 'preserve')
    instrText.text = "PAGE"
    fldChar2 = OxmlElement('w:fldChar')
    fldChar2.set(qn('w:fldCharType'), 'separate')
    fldChar3 = OxmlElement('w:fldChar')
    fldChar3.set(qn('w:fldCharType'), 'end')
    run._r.append(fldChar1)
    run._r.append(instrText)
    run._r.append(fldChar2)
    run._r.append(fldChar3)
    run.font.name = 'Times New Roman'
    run.font.size = Pt(14)

def format_paragraph(p, space_before=0, space_after=0, line_spacing=1.5, alignment=WD_ALIGN_PARAGRAPH.LEFT):
    p.paragraph_format.space_before = Pt(space_before)
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.line_spacing = line_spacing
    p.alignment = alignment

doc = docx.Document()

# Configure default Normal style
style = doc.styles['Normal']
font = style.font
font.name = 'Times New Roman'
font.size = Pt(14)
font.color.rgb = RGBColor(0, 0, 0)

# Section 1: Cover Page (No Page Number)
sec1 = doc.sections[0]
sec1.page_width = Inches(8.27)
sec1.page_height = Inches(11.69)
sec1.top_margin = Inches(0.8)
sec1.bottom_margin = Inches(0.6)
sec1.left_margin = Inches(1.1)
sec1.right_margin = Inches(1.0)
sec1.different_first_page_header_footer = True

# --- COVER PAGE ---
p = doc.add_paragraph()
format_paragraph(p, space_before=0, space_after=2, line_spacing=1.15, alignment=WD_ALIGN_PARAGRAPH.CENTER)
r = p.add_run("COIMBATORE INSTITUTE OF ENGINEERING AND TECHNOLOGY")
r.bold = True
r.font.size = Pt(15)

p = doc.add_paragraph()
format_paragraph(p, space_before=0, space_after=2, line_spacing=1.15, alignment=WD_ALIGN_PARAGRAPH.CENTER)
r = p.add_run("(Autonomous Institution Affiliated to Anna University, Chennai & Approved by AICTE, New Delhi)")
r.font.size = Pt(11)

p = doc.add_paragraph()
format_paragraph(p, space_before=0, space_after=18, line_spacing=1.15, alignment=WD_ALIGN_PARAGRAPH.CENTER)
r = p.add_run("COIMBATORE – 641 109")
r.bold = True
r.font.size = Pt(13)

p = doc.add_paragraph()
format_paragraph(p, space_before=16, space_after=16, line_spacing=1.3, alignment=WD_ALIGN_PARAGRAPH.CENTER)
r = p.add_run("AETHEROPS: AN AUTOMATED MULTI-TENANT CLOUD ARCHITECTURE SYNTHESIS AND DEVOPS ORCHESTRATION PLATFORM")
r.bold = True
r.font.size = Pt(18)

p = doc.add_paragraph()
format_paragraph(p, space_before=10, space_after=6, line_spacing=1.15, alignment=WD_ALIGN_PARAGRAPH.CENTER)
r = p.add_run("A PROJECT REPORT")
r.bold = True
r.font.size = Pt(14)

p = doc.add_paragraph()
format_paragraph(p, space_before=6, space_after=10, line_spacing=1.15, alignment=WD_ALIGN_PARAGRAPH.CENTER)
r = p.add_run("Submitted by")
r.font.size = Pt(14)

p = doc.add_paragraph()
format_paragraph(p, space_before=4, space_after=14, line_spacing=1.25, alignment=WD_ALIGN_PARAGRAPH.CENTER)
students = [
    ("NEDUNCHELIYAN N", "71052302070"),
    ("PRATHAP G", "71052302076"),
    ("RENO ACDEN R", "71052302083"),
    ("SANJEEV C S", "71052201403")
]
for name, reg in students:
    r = p.add_run(f"{name} ({reg})\n")
    r.bold = True
    r.font.size = Pt(16)

p = doc.add_paragraph()
format_paragraph(p, space_before=8, space_after=4, line_spacing=1.15, alignment=WD_ALIGN_PARAGRAPH.CENTER)
r = p.add_run("in partial fulfillment for the award of the degree\nof\n")
r.font.size = Pt(13)
r = p.add_run("BACHELOR OF ENGINEERING\n")
r.bold = True
r.font.size = Pt(15)
r = p.add_run("in\n")
r.font.size = Pt(13)
r = p.add_run("COMPUTER SCIENCE AND ENGINEERING")
r.bold = True
r.font.size = Pt(15)

p = doc.add_paragraph()
format_paragraph(p, space_before=18, space_after=2, line_spacing=1.15, alignment=WD_ALIGN_PARAGRAPH.CENTER)
r = p.add_run("DEPARTMENT OF COMPUTER SCIENCE AND ENGINEERING\n")
r.bold = True
r.font.size = Pt(14)
r = p.add_run("COIMBATORE INSTITUTE OF ENGINEERING AND TECHNOLOGY\n")
r.bold = True
r.font.size = Pt(14)
r = p.add_run("(Autonomous Institution Affiliated to Anna University, Chennai)\n")
r.font.size = Pt(11)
r = p.add_run("COIMBATORE – 641 109\n")
r.bold = True
r.font.size = Pt(13)
r = p.add_run("MAY 2026")
r.bold = True
r.font.size = Pt(14)

# --- SECTION 2: PRELIMINARY PAGES (ROMAN NUMERALS STARTING AT 'ii') ---
sec2 = doc.add_section()
sec2.page_width = Inches(8.27)
sec2.page_height = Inches(11.69)
sec2.top_margin = Inches(0.8)
sec2.bottom_margin = Inches(0.6)
sec2.left_margin = Inches(1.1)
sec2.right_margin = Inches(1.0)
sec2.header.is_linked_to_previous = False
sec2.footer.is_linked_to_previous = False

sectPr = sec2._sectPr
pgNumType = OxmlElement('w:pgNumType')
pgNumType.set(qn('w:fmt'), 'roman')
pgNumType.set(qn('w:start'), '2')
sectPr.append(pgNumType)

add_footer_page_number(sec2.footer.paragraphs[0])

# --- TITLE PAGE (Page ii) ---
p = doc.add_paragraph()
format_paragraph(p, space_before=0, space_after=2, line_spacing=1.15, alignment=WD_ALIGN_PARAGRAPH.CENTER)
r = p.add_run("COIMBATORE INSTITUTE OF ENGINEERING AND TECHNOLOGY")
r.bold = True
r.font.size = Pt(15)

p = doc.add_paragraph()
format_paragraph(p, space_before=0, space_after=2, line_spacing=1.15, alignment=WD_ALIGN_PARAGRAPH.CENTER)
r = p.add_run("(Autonomous Institution Affiliated to Anna University, Chennai & Approved by AICTE, New Delhi)")
r.font.size = Pt(11)

p = doc.add_paragraph()
format_paragraph(p, space_before=0, space_after=18, line_spacing=1.15, alignment=WD_ALIGN_PARAGRAPH.CENTER)
r = p.add_run("COIMBATORE – 641 109")
r.bold = True
r.font.size = Pt(13)

p = doc.add_paragraph()
format_paragraph(p, space_before=16, space_after=16, line_spacing=1.3, alignment=WD_ALIGN_PARAGRAPH.CENTER)
r = p.add_run("AETHEROPS: AN AUTOMATED MULTI-TENANT CLOUD ARCHITECTURE SYNTHESIS AND DEVOPS ORCHESTRATION PLATFORM")
r.bold = True
r.font.size = Pt(18)

p = doc.add_paragraph()
format_paragraph(p, space_before=10, space_after=6, line_spacing=1.15, alignment=WD_ALIGN_PARAGRAPH.CENTER)
r = p.add_run("A PROJECT REPORT")
r.bold = True
r.font.size = Pt(14)

p = doc.add_paragraph()
format_paragraph(p, space_before=6, space_after=10, line_spacing=1.15, alignment=WD_ALIGN_PARAGRAPH.CENTER)
r = p.add_run("Submitted by")
r.font.size = Pt(14)

p = doc.add_paragraph()
format_paragraph(p, space_before=4, space_after=14, line_spacing=1.25, alignment=WD_ALIGN_PARAGRAPH.CENTER)
for name, reg in students:
    r = p.add_run(f"{name} ({reg})\n")
    r.bold = True
    r.font.size = Pt(16)

p = doc.add_paragraph()
format_paragraph(p, space_before=8, space_after=4, line_spacing=1.15, alignment=WD_ALIGN_PARAGRAPH.CENTER)
r = p.add_run("in partial fulfillment for the award of the degree\nof\n")
r.font.size = Pt(13)
r = p.add_run("BACHELOR OF ENGINEERING\n")
r.bold = True
r.font.size = Pt(15)
r = p.add_run("in\n")
r.font.size = Pt(13)
r = p.add_run("COMPUTER SCIENCE AND ENGINEERING")
r.bold = True
r.font.size = Pt(15)

p = doc.add_paragraph()
format_paragraph(p, space_before=18, space_after=2, line_spacing=1.15, alignment=WD_ALIGN_PARAGRAPH.CENTER)
r = p.add_run("DEPARTMENT OF COMPUTER SCIENCE AND ENGINEERING\n")
r.bold = True
r.font.size = Pt(14)
r = p.add_run("COIMBATORE INSTITUTE OF ENGINEERING AND TECHNOLOGY\n")
r.bold = True
r.font.size = Pt(14)
r = p.add_run("(Autonomous Institution Affiliated to Anna University, Chennai)\n")
r.font.size = Pt(11)
r = p.add_run("COIMBATORE – 641 109\n")
r.bold = True
r.font.size = Pt(13)
r = p.add_run("MAY 2026")
r.bold = True
r.font.size = Pt(14)

doc.add_page_break()

# --- BONAFIDE CERTIFICATE (Page iii) ---
p = doc.add_paragraph()
format_paragraph(p, space_before=0, space_after=2, line_spacing=1.15, alignment=WD_ALIGN_PARAGRAPH.CENTER)
r = p.add_run("COIMBATORE INSTITUTE OF ENGINEERING AND TECHNOLOGY")
r.bold = True
r.font.size = Pt(15)

p = doc.add_paragraph()
format_paragraph(p, space_before=0, space_after=2, line_spacing=1.15, alignment=WD_ALIGN_PARAGRAPH.CENTER)
r = p.add_run("(Autonomous Institution Affiliated to Anna University, Chennai & Approved by AICTE, New Delhi)")
r.font.size = Pt(11)

p = doc.add_paragraph()
format_paragraph(p, space_before=0, space_after=8, line_spacing=1.15, alignment=WD_ALIGN_PARAGRAPH.CENTER)
r = p.add_run("COIMBATORE – 641 109\nDEPARTMENT OF COMPUTER SCIENCE AND ENGINEERING")
r.bold = True
r.font.size = Pt(13)

p = doc.add_paragraph()
format_paragraph(p, space_before=12, space_after=14, line_spacing=1.15, alignment=WD_ALIGN_PARAGRAPH.CENTER)
r = p.add_run("BONAFIDE CERTIFICATE")
r.bold = True
r.underline = True
r.font.size = Pt(14)

# Double line spacing as per CIET rule
p = doc.add_paragraph()
format_paragraph(p, space_before=6, space_after=14, line_spacing=2.0, alignment=WD_ALIGN_PARAGRAPH.JUSTIFY)
r = p.add_run("Certified that this project report titled ")
r.font.size = Pt(14)
r = p.add_run("“AETHEROPS: AN AUTOMATED MULTI-TENANT CLOUD ARCHITECTURE SYNTHESIS AND DEVOPS ORCHESTRATION PLATFORM”")
r.bold = True
r.font.size = Pt(14)
r = p.add_run(" is the bonafide work of ")
r.font.size = Pt(14)
r = p.add_run("NEDUNCHELIYAN N (71052302070), PRATHAP G (71052302076), RENO ACDEN R (71052302083), and SANJEEV C S (71052201403)")
r.bold = True
r.font.size = Pt(14)
r = p.add_run(" who carried out the project work under my supervision.")
r.font.size = Pt(14)

# Student Table
table = doc.add_table(rows=5, cols=4)
table.alignment = WD_TABLE_ALIGNMENT.CENTER
headers = ["S.No.", "Register Number", "Name of the Candidate", "Signature"]
widths = [Inches(0.6), Inches(1.8), Inches(2.3), Inches(1.4)]

hdr_cells = table.rows[0].cells
for i, title in enumerate(headers):
    hdr_cells[i].text = title
    p = hdr_cells[i].paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.runs[0].font.name = 'Times New Roman'
    p.runs[0].font.size = Pt(12)
    p.runs[0].font.bold = True
    set_cell_margins(hdr_cells[i], top=100, bottom=100, left=100, right=100)
    set_cell_borders(hdr_cells[i], top="single", bottom="single", left="single", right="single")

candidates = [
    ("1", "71052302070", "NEDUNCHELIYAN N"),
    ("2", "71052302076", "PRATHAP G"),
    ("3", "71052302083", "RENO ACDEN R"),
    ("4", "71052201403", "SANJEEV C S")
]

for row_idx, (sno, reg, name) in enumerate(candidates, start=1):
    row_cells = table.rows[row_idx].cells
    row_cells[0].text = sno
    row_cells[1].text = reg
    row_cells[2].text = name
    row_cells[3].text = ""
    for col_idx in range(4):
        p = row_cells[col_idx].paragraphs[0]
        if col_idx in [0, 1]:
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        elif col_idx == 2:
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        if len(p.runs) > 0:
            p.runs[0].font.name = 'Times New Roman'
            p.runs[0].font.size = Pt(12)
        set_cell_margins(row_cells[col_idx], top=80, bottom=80, left=80, right=80)
        set_cell_borders(row_cells[col_idx], top="single", bottom="single", left="single", right="single")

p_space = doc.add_paragraph()
format_paragraph(p_space, space_before=16, space_after=0, line_spacing=1.0)

# Signatures: HOD and Supervisor (adhering strictly to supervisor title rule)
sig_table = doc.add_table(rows=1, cols=2)
sig_table.alignment = WD_TABLE_ALIGNMENT.CENTER
c_left = sig_table.rows[0].cells[0]
c_right = sig_table.rows[0].cells[1]
c_left.width = Inches(3.1)
c_right.width = Inches(3.1)
set_cell_borders(c_left, top=None, bottom=None, left=None, right=None)
set_cell_borders(c_right, top=None, bottom=None, left=None, right=None)

p_left = c_left.paragraphs[0]
format_paragraph(p_left, space_before=0, space_after=2, line_spacing=1.15, alignment=WD_ALIGN_PARAGRAPH.LEFT)
p_left.add_run("SIGNATURE\n\n\n\n").bold = True
r = p_left.add_run("Dr. K. PUSHPALATHA, M.E., Ph.D.,\n")
r.bold = True
r.font.size = Pt(13)
r = p_left.add_run("HEAD OF THE DEPARTMENT\n")
r.bold = True
r.font.size = Pt(13)
r = p_left.add_run("Professor and Head\nDepartment of Computer Science\nand Engineering\nCoimbatore Institute of Engineering\nand Technology\nCoimbatore – 641 109")
r.font.size = Pt(12)

p_right = c_right.paragraphs[0]
format_paragraph(p_right, space_before=0, space_after=2, line_spacing=1.15, alignment=WD_ALIGN_PARAGRAPH.RIGHT)
p_right.add_run("SIGNATURE\n\n\n\n").bold = True
r = p_right.add_run("Ms. M. ABIRAMI, M.E.,\n")
r.bold = True
r.font.size = Pt(13)
# Supervisor Title Rule: SUPERVISOR typed in capital letters directly between name and academic designation, omitting administrative titles
r = p_right.add_run("SUPERVISOR\n")
r.bold = True
r.font.size = Pt(13)
r = p_right.add_run("Professor\nDepartment of Computer Science\nand Engineering\nCoimbatore Institute of Engineering\nand Technology\nCoimbatore – 641 109")
r.font.size = Pt(12)

# Viva-Voce
p = doc.add_paragraph()
format_paragraph(p, space_before=18, space_after=14, line_spacing=1.3, alignment=WD_ALIGN_PARAGRAPH.JUSTIFY)
r = p.add_run("Submitted for the Anna University Project Viva-Voce Examination held on ____________________")
r.font.size = Pt(13)

viva_table = doc.add_table(rows=1, cols=2)
viva_table.alignment = WD_TABLE_ALIGNMENT.CENTER
v_left = viva_table.rows[0].cells[0]
v_right = viva_table.rows[0].cells[1]
v_left.width = Inches(3.1)
v_right.width = Inches(3.1)
set_cell_borders(v_left, top=None, bottom=None, left=None, right=None)
set_cell_borders(v_right, top=None, bottom=None, left=None, right=None)

pv_left = v_left.paragraphs[0]
format_paragraph(pv_left, space_before=16, space_after=0, line_spacing=1.15, alignment=WD_ALIGN_PARAGRAPH.LEFT)
pv_left.add_run("INTERNAL EXAMINER").bold = True

pv_right = v_right.paragraphs[0]
format_paragraph(pv_right, space_before=16, space_after=0, line_spacing=1.15, alignment=WD_ALIGN_PARAGRAPH.RIGHT)
pv_right.add_run("EXTERNAL EXAMINER").bold = True

doc.add_page_break()

# --- CERTIFICATE OF EVALUATION (Page iv) ---
p = doc.add_paragraph()
format_paragraph(p, space_before=0, space_after=2, line_spacing=1.15, alignment=WD_ALIGN_PARAGRAPH.CENTER)
r = p.add_run("COIMBATORE INSTITUTE OF ENGINEERING AND TECHNOLOGY")
r.bold = True
r.font.size = Pt(15)

p = doc.add_paragraph()
format_paragraph(p, space_before=0, space_after=2, line_spacing=1.15, alignment=WD_ALIGN_PARAGRAPH.CENTER)
r = p.add_run("(Autonomous Institution Affiliated to Anna University, Chennai & Approved by AICTE, New Delhi)")
r.font.size = Pt(11)

p = doc.add_paragraph()
format_paragraph(p, space_before=0, space_after=8, line_spacing=1.15, alignment=WD_ALIGN_PARAGRAPH.CENTER)
r = p.add_run("COIMBATORE – 641 109\nDEPARTMENT OF COMPUTER SCIENCE AND ENGINEERING")
r.bold = True
r.font.size = Pt(13)

p = doc.add_paragraph()
format_paragraph(p, space_before=12, space_after=14, line_spacing=1.15, alignment=WD_ALIGN_PARAGRAPH.CENTER)
r = p.add_run("CERTIFICATE OF EVALUATION")
r.bold = True
r.underline = True
r.font.size = Pt(14)

p = doc.add_paragraph()
format_paragraph(p, space_before=4, space_after=10, line_spacing=2.0, alignment=WD_ALIGN_PARAGRAPH.LEFT)
r = p.add_run("Name of the College : ")
r.bold = True
p.add_run("Coimbatore Institute of Engineering and Technology\n")
r = p.add_run("Degree & Branch      : ")
r.bold = True
p.add_run("Bachelor of Engineering in Computer Science and Engineering\n")
r = p.add_run("Title of the Project  : ")
r.bold = True
p.add_run("AETHEROPS: AN AUTOMATED MULTI-TENANT CLOUD ARCHITECTURE SYNTHESIS AND DEVOPS ORCHESTRATION PLATFORM")

# Candidates Table
p = doc.add_paragraph()
format_paragraph(p, space_before=6, space_after=12, line_spacing=2.0, alignment=WD_ALIGN_PARAGRAPH.JUSTIFY)
p.add_run("The project report submitted by the following candidates in partial fulfillment of the requirements for the award of the degree of ")
p.add_run("Bachelor of Engineering in Computer Science and Engineering").bold = True
p.add_run(" of Anna University, Chennai has been evaluated by the committee and found satisfactory.")

eval_table = doc.add_table(rows=6, cols=3)
eval_table.alignment = WD_TABLE_ALIGNMENT.CENTER
headers_eval = ["Evaluation Component / Rubrics", "Maximum Marks", "Marks Awarded"]
hdr_eval_cells = eval_table.rows[0].cells
for i, title in enumerate(headers_eval):
    hdr_eval_cells[i].text = title
    p = hdr_eval_cells[i].paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.runs[0].font.name = 'Times New Roman'
    p.runs[0].font.size = Pt(12)
    p.runs[0].font.bold = True
    set_cell_margins(hdr_eval_cells[i], top=100, bottom=100, left=100, right=100)
    set_cell_borders(hdr_eval_cells[i], top="single", bottom="single", left="single", right="single")

rubrics = [
    ("1. Problem Identification, Literature Survey & Objectives", "20", ""),
    ("2. Architectural Design, Methodology & Technology Stack", "25", ""),
    ("3. Microservices Implementation & Quality of Engineering", "25", ""),
    ("4. Testing, System Validation, Security & Results", "15", ""),
    ("5. Project Documentation, Viva-Voce & Technical Defense", "15", "")
]
for idx, (comp, max_m, act_m) in enumerate(rubrics, start=1):
    row_cells = eval_table.rows[idx].cells
    row_cells[0].text = comp
    row_cells[1].text = max_m
    row_cells[2].text = act_m
    p0 = row_cells[0].paragraphs[0]
    p0.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p1 = row_cells[1].paragraphs[0]
    p1.alignment = WD_ALIGN_PARAGRAPH.CENTER
    for c_i in range(3):
        if len(row_cells[c_i].paragraphs[0].runs) > 0:
            row_cells[c_i].paragraphs[0].runs[0].font.name = 'Times New Roman'
            row_cells[c_i].paragraphs[0].runs[0].font.size = Pt(12)
        set_cell_margins(row_cells[c_i], top=80, bottom=80, left=80, right=80)
        set_cell_borders(row_cells[c_i], top="single", bottom="single", left="single", right="single")

p_space = doc.add_paragraph()
format_paragraph(p_space, space_before=16, space_after=0, line_spacing=1.0)

eval_sig_table = doc.add_table(rows=2, cols=2)
eval_sig_table.alignment = WD_TABLE_ALIGNMENT.CENTER
for r_i in range(2):
    for c_i in range(2):
        set_cell_borders(eval_sig_table.rows[r_i].cells[c_i], top=None, bottom=None, left=None, right=None)

c00 = eval_sig_table.rows[0].cells[0]
c01 = eval_sig_table.rows[0].cells[1]
p = c00.paragraphs[0]
format_paragraph(p, space_before=0, space_after=2, line_spacing=1.15, alignment=WD_ALIGN_PARAGRAPH.LEFT)
p.add_run("PROJECT COORDINATOR\n\n\n").bold = True
r = p.add_run("Ms. M. PUSHPALATHA, M.E.,\n")
r.bold = True
r.font.size = Pt(13)
r = p.add_run("Associate Professor\nDepartment of CSE, CIET")
r.font.size = Pt(12)

p = c01.paragraphs[0]
format_paragraph(p, space_before=0, space_after=2, line_spacing=1.15, alignment=WD_ALIGN_PARAGRAPH.RIGHT)
p.add_run("HEAD OF THE DEPARTMENT\n\n\n").bold = True
r = p.add_run("Dr. K. PUSHPALATHA, M.E., Ph.D.,\n")
r.bold = True
r.font.size = Pt(13)
r = p.add_run("Professor & Head\nDepartment of CSE, CIET")
r.font.size = Pt(12)

c10 = eval_sig_table.rows[1].cells[0]
c11 = eval_sig_table.rows[1].cells[1]
p = c10.paragraphs[0]
format_paragraph(p, space_before=18, space_after=0, line_spacing=1.15, alignment=WD_ALIGN_PARAGRAPH.LEFT)
p.add_run("INTERNAL EXAMINER").bold = True

p = c11.paragraphs[0]
format_paragraph(p, space_before=18, space_after=0, line_spacing=1.15, alignment=WD_ALIGN_PARAGRAPH.RIGHT)
p.add_run("EXTERNAL EXAMINER").bold = True

doc.add_page_break()

# --- ACKNOWLEDGEMENT (Page v) ---
p = doc.add_paragraph()
format_paragraph(p, space_before=0, space_after=14, line_spacing=1.15, alignment=WD_ALIGN_PARAGRAPH.CENTER)
r = p.add_run("ACKNOWLEDGEMENT")
r.bold = True
r.underline = True
r.font.size = Pt(14)

ack_paragraphs = [
    ("First and foremost, we express our profound gratitude to our esteemed Director, ",
     "Dr. K. A. Chinnaraju, MBA., Ph.D.",
     ", for his inspiring administrative patronage, academic vision, and for establishing world-class computational and laboratory infrastructure at Coimbatore Institute of Engineering and Technology, which made the conception and execution of this project possible."),
    
    ("We extend our heartfelt thanks and profound indebtedness to our respected Principal, ",
     "Dr. K. Manikanda Subramanian, M.E., Ph.D.",
     ", for his constant academic encouragement, infrastructural guidance, and unceasing motivation toward engineering rigor and scholarly research excellence."),
    
    ("We place on record our deep sense of gratitude and sincere indebtedness to ",
     "Dr. K. Pushpalatha, M.E., Ph.D.",
     ", Professor and Head of the Department of Computer Science and Engineering, for her invaluable technical counsel, persistent encouragement, intellectual stimulation, and continuous institutional support provided throughout the lifecycle of this project."),
    
    ("We convey our earnest appreciation and gratitude to our Project Coordinator, ",
     "Ms. M. Pushpalatha, M.E.",
     ", Associate Professor, Department of Computer Science and Engineering, for her meticulous scheduling, rigorous progress evaluations, and constructive critiques during every technical review milestone."),
    
    ("We express our deepest gratitude and indebtedness to our Project Supervisor, ",
     "Ms. M. Abirami, M.E.",
     ", Professor, Department of Computer Science and Engineering, for her exceptional scholarly mentorship, sharp architectural feedback, unwavering patience, and invaluable technical guidance from inception to production deployment."),
    
    ("We express our sincere appreciation to all the faculty members, technical supporting staff, and system administrators of the Department of Computer Science and Engineering for their generous cooperation, technical assistance, and continuous goodwill."),
    
    ("Finally, we express our warmest love, gratitude, and eternal indebtedness to our beloved parents, family members, and friends for their enduring patience, sacrifices, moral encouragement, and emotional sustenance throughout our undergraduate study.",
     "", "")
]

for p_text in ack_paragraphs:
    p = doc.add_paragraph()
    format_paragraph(p, space_before=6, space_after=8, line_spacing=1.5, alignment=WD_ALIGN_PARAGRAPH.JUSTIFY)
    p.add_run(p_text[0]).font.size = Pt(14)
    if p_text[1]:
        r = p.add_run(p_text[1])
        r.bold = True
        r.font.size = Pt(14)
    if p_text[2]:
        p.add_run(p_text[2]).font.size = Pt(14)

p = doc.add_paragraph()
format_paragraph(p, space_before=16, space_after=2, line_spacing=1.15, alignment=WD_ALIGN_PARAGRAPH.RIGHT)
r = p.add_run("NEDUNCHELIYAN N (71052302070)\nPRATHAP G (71052302076)\nRENO ACDEN R (71052302083)\nSANJEEV C S (71052201403)\n")
r.bold = True
r.font.size = Pt(14)

doc.add_page_break()

# --- ABSTRACT (Page vi) ---
p = doc.add_paragraph()
format_paragraph(p, space_before=0, space_after=14, line_spacing=1.15, alignment=WD_ALIGN_PARAGRAPH.CENTER)
r = p.add_run("ABSTRACT")
r.bold = True
r.underline = True
r.font.size = Pt(14)

# Abstract is strictly double spaced as per CIET rules
abstract_p1 = (
    "The escalating complexity of modern multi-cloud software deployments and distributed microservices architectures has "
    "rendered traditional manual infrastructure provisioning error-prone, insecure, and economically unsustainable. Cloud "
    "misconfigurations account for the vast majority of critical cloud security breaches, while disparate DevOps toolchains create "
    "an operational disconnect between static application semantics and production cloud topologies. This project presents AetherOps, "
    "an automated multi-tenant cloud architecture synthesis, Infrastructure as Code (IaC) generation, and DevOps orchestration "
    "platform engineered to overcome these industry-wide limitations."
)

abstract_p2 = (
    "AetherOps is architected as a fleet of 12 decoupled microservices coordinated through an asynchronous API Gateway and a reactive "
    "single-page dashboard. The platform incorporates an Abstract Syntax Tree (AST) static code analyzer that autonomously interrogates "
    "arbitrary software repositories to extract runtime requirements, port exposures, database dependencies, and network topologies. A "
    "deterministic requirements profiling engine reconciles these discovered profiles against a regional catalog spanning 39 Amazon "
    "Web Services (AWS) regions to compute optimal compute, memory, and storage resource allocations. The architectural synthesizer "
    "transforms these requirements into a formal Directed Acyclic Graph (DAG) with deterministic coordinate geometry, visualized on an "
    "interactive canvas. An automated compiler subsequently synthesizes modular HashiCorp Terraform manifests enforcing zero-trust "
    "security postures and least-privilege IAM policies. Multi-tenant workspace isolation is enforced at the database layer using "
    "UUIDv4 tenancy scoping, Role-Based Access Control (RBAC), and AES-256-GCM envelope encryption for cloud credentials and OAuth secrets. "
    "Continuous FinOps cost arbitrage, automated CIS Benchmark compliance scanning, and Prometheus observability guarantee ongoing "
    "governance. Empirical validation demonstrates that AetherOps reduces end-to-end cloud provisioning time from multiple days to under "
    "4 minutes, achieves 100% compliance on automated CIS security baselines, eliminates cloud configuration drift, and reduces cloud compute "
    "expenditure by up to 34% through algorithmic rightsizing."
)

p = doc.add_paragraph()
format_paragraph(p, space_before=4, space_after=10, line_spacing=2.0, alignment=WD_ALIGN_PARAGRAPH.JUSTIFY)
p.add_run(abstract_p1).font.size = Pt(14)

p = doc.add_paragraph()
format_paragraph(p, space_before=4, space_after=10, line_spacing=2.0, alignment=WD_ALIGN_PARAGRAPH.JUSTIFY)
p.add_run(abstract_p2).font.size = Pt(14)

p = doc.add_paragraph()
format_paragraph(p, space_before=8, space_after=0, line_spacing=1.5, alignment=WD_ALIGN_PARAGRAPH.LEFT)
r = p.add_run("Keywords: ")
r.bold = True
r.font.size = Pt(14)
p.add_run("Cloud Infrastructure Automation, Infrastructure as Code (IaC), Multi-Tenant Microservices, Directed Acyclic Graph (DAG), FinOps Arbitrage, Envelope Encryption, Static AST Analysis.").font.size = Pt(14)

doc.add_page_break()

# --- TABLE OF CONTENTS (Pages vii - ix) ---
p = doc.add_paragraph()
format_paragraph(p, space_before=0, space_after=14, line_spacing=1.15, alignment=WD_ALIGN_PARAGRAPH.CENTER)
r = p.add_run("TABLE OF CONTENTS")
r.bold = True
r.underline = True
r.font.size = Pt(14)

# Note: Exclude Title Page and Bonafide Certificate per CIET rules!
toc_items = [
    ("", "CERTIFICATE OF EVALUATION", "iv", True, 0),
    ("", "ACKNOWLEDGEMENT", "v", True, 0),
    ("", "ABSTRACT", "vi", True, 0),
    ("", "LIST OF TABLES", "x", True, 0),
    ("", "LIST OF FIGURES", "xi", True, 0),
    ("", "LIST OF SYMBOLS, ABBREVIATIONS AND NOMENCLATURE", "xii", True, 0),
    ("1", "INTRODUCTION", "1", True, 0),
    ("1.1", "General", "1", False, 1),
    ("1.2", "Background", "3", False, 1),
    ("1.3", "Problem Statement", "5", False, 1),
    ("1.4", "Objectives of the Project", "7", False, 1),
    ("1.5", "Scope of the Project", "8", False, 1),
    ("1.6", "Feasibility Study", "10", False, 1),
    ("1.6.1", "Technical Feasibility", "10", False, 2),
    ("1.6.2", "Economic Feasibility", "11", False, 2),
    ("1.6.3", "Operational Feasibility", "12", False, 2),
    ("1.7", "Software Development Methodology", "13", False, 1),
    ("1.8", "Risk Management", "15", False, 1),
    ("2", "LITERATURE REVIEW", "17", True, 0),
    ("2.1", "Introduction", "17", False, 1),
    ("2.2", "Overview of Existing Systems", "18", False, 1),
    ("2.3", "System Comparison", "21", False, 1),
    ("2.4", "Existing Framework Limitations vs Proposed Approach", "23", False, 1),
    ("2.5", "Access Control & Governance Model", "25", False, 1),
    ("2.6", "UI/UX Principles & Technology Stack Architecture", "27", False, 1),
    ("2.7", "Security Mechanisms", "29", False, 1),
    ("3", "SYSTEM ANALYSIS AND DESIGN", "32", True, 0),
    ("3.1", "Introduction", "32", False, 1),
    ("3.2", "Existing System Analysis & Current Workflow", "33", False, 1),
    ("3.3", "Proposed System Architecture", "35", False, 1),
    ("3.3.1", "Presentation Layer", "35", False, 2),
    ("3.3.2", "Application & Orchestration Layer", "36", False, 2),
    ("3.3.3", "Data & Edge Infrastructure Layer", "37", False, 2),
    ("3.4", "System Modeling Diagrams", "38", False, 1),
    ("3.4.1", "System Architecture Blueprint", "38", False, 2),
    ("3.4.2", "Sequence Flow Diagram", "40", False, 2),
    ("3.4.3", "Database Schema & ER Design", "42", False, 2),
    ("3.5", "Use Case Analysis", "44", False, 1),
    ("3.6", "API / Interface Design Specification", "46", False, 1),
    ("3.7", "Non-Functional Requirements", "48", False, 1),
    ("3.8", "System Requirements", "50", False, 1),
    ("4", "SYSTEM IMPLEMENTATION", "52", True, 0),
    ("4.1", "Introduction", "52", False, 1),
    ("4.2", "Development Environment Setup", "53", False, 1),
    ("4.3", "Backend / Core Engine Implementation Details", "55", False, 1),
    ("4.3.1", "Workspace & Microservices Topology", "55", False, 2),
    ("4.3.2", "Connection Pooling & Data Brokers", "56", False, 2),
    ("4.3.3", "Authentication & Security Middleware", "57", False, 2),
    ("4.4", "Frontend / Dashboard Implementation", "59", False, 1),
    ("4.5", "Implementation Challenges and Solutions", "61", False, 1),
    ("4.6", "Deployment Strategy Considerations", "63", False, 1),
    ("5", "RESULTS AND DISCUSSION", "65", True, 0),
    ("5.1", "Introduction", "65", False, 1),
    ("5.2", "System Output Screens", "66", False, 1),
    ("5.3", "Comprehensive Testing", "70", False, 1),
    ("5.3.1", "Unit & Integration Testing", "70", False, 2),
    ("5.3.2", "Security Penetration & RBAC Testing", "71", False, 2),
    ("5.3.3", "Load & Performance Testing", "72", False, 2),
    ("5.3.4", "Functional Test Cases", "73", False, 2),
    ("5.4", "User Acceptance Testing", "76", False, 1),
    ("5.5", "Comparison with Existing Methods", "78", False, 1),
    ("6", "CONCLUSION", "81", True, 0),
    ("6.1", "Summary of Work", "81", False, 1),
    ("6.2", "Achievements", "82", False, 1),
    ("6.3", "Limitations", "83", False, 1),
    ("6.4", "Conclusion", "84", False, 1),
    ("7", "FUTURE SCOPE", "85", True, 0),
    ("7.1", "Introduction", "85", False, 1),
    ("7.2", "Advanced AI & Automation Integrations", "86", False, 1),
    ("7.3", "Expanded Engagement & Platform Features", "88", False, 1),
    ("", "APPENDICES", "90", True, 0),
    ("APPENDIX 1", "CORE SOURCE CODE MODULES", "90", True, 1),
    ("", "REFERENCES", "102", True, 0),
    ("", "CONFERENCE CERTIFICATE", "106", True, 0)
]

# Create a clean TOC table with dotted leaders
toc_table = doc.add_table(rows=len(toc_items) + 1, cols=3)
toc_table.alignment = WD_TABLE_ALIGNMENT.CENTER
toc_widths = [Inches(1.1), Inches(4.3), Inches(0.8)]

# Header
h_cells = toc_table.rows[0].cells
h_cells[0].text = "CHAPTER NO."
h_cells[1].text = "TITLE"
h_cells[2].text = "PAGE NO."
for i in range(3):
    p = h_cells[i].paragraphs[0]
    p.runs[0].font.name = 'Times New Roman'
    p.runs[0].font.size = Pt(12)
    p.runs[0].font.bold = True
    if i == 2 or i == 0:
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    else:
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    set_cell_margins(h_cells[i], top=80, bottom=80, left=60, right=60)
    set_cell_borders(h_cells[i], top="single", bottom="single", left=None, right=None)

for idx, (num, title, pg, is_bold, indent_lvl) in enumerate(toc_items, start=1):
    row_cells = toc_table.rows[idx].cells
    row_cells[0].text = num
    indent_space = "    " * indent_lvl
    row_cells[1].text = f"{indent_space}{title}"
    row_cells[2].text = pg
    
    p0 = row_cells[0].paragraphs[0]
    p0.alignment = WD_ALIGN_PARAGRAPH.LEFT
    if len(p0.runs) > 0:
        p0.runs[0].font.name = 'Times New Roman'
        p0.runs[0].font.size = Pt(11)
        p0.runs[0].font.bold = is_bold
        
    p1 = row_cells[1].paragraphs[0]
    p1.alignment = WD_ALIGN_PARAGRAPH.LEFT
    if len(p1.runs) > 0:
        p1.runs[0].font.name = 'Times New Roman'
        p1.runs[0].font.size = Pt(11)
        p1.runs[0].font.bold = is_bold
        
    p2 = row_cells[2].paragraphs[0]
    p2.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    if len(p2.runs) > 0:
        p2.runs[0].font.name = 'Times New Roman'
        p2.runs[0].font.size = Pt(11)
        p2.runs[0].font.bold = is_bold
        
    for c_i in range(3):
        set_cell_margins(row_cells[c_i], top=40, bottom=40, left=60, right=60)
        set_cell_borders(row_cells[c_i], top=None, bottom=None, left=None, right=None)

doc.add_page_break()

# --- LIST OF TABLES (Page x) ---
p = doc.add_paragraph()
format_paragraph(p, space_before=0, space_after=14, line_spacing=1.15, alignment=WD_ALIGN_PARAGRAPH.CENTER)
r = p.add_run("LIST OF TABLES")
r.bold = True
r.underline = True
r.font.size = Pt(14)

tables_data = [
    ("Table 2.1", "Comparison of Proposed System vs Existing Systems across Architectural Parameters", "22"),
    ("Table 2.2", "Security Features Implemented in the System", "30"),
    ("Table 3.1", "Comprehensive API Endpoints and Data Channels", "47"),
    ("Table 3.2", "Hardware and Software Requirements Specification", "51"),
    ("Table 4.1", "Implementation Challenges, Technical Impacts, and Mitigations", "62"),
    ("Table 5.1", "Functional Test Cases and System Validation", "74"),
    ("Table 5.2", "User Acceptance Testing Results Summary", "77"),
    ("Table 5.3", "Comparative Analysis of Proposed System vs Existing Cloud Provisioning Methods", "79")
]

lot_table = doc.add_table(rows=len(tables_data) + 1, cols=3)
lot_table.alignment = WD_TABLE_ALIGNMENT.CENTER
h_lot = lot_table.rows[0].cells
h_lot[0].text = "TABLE NO."
h_lot[1].text = "TITLE"
h_lot[2].text = "PAGE NO."
for i in range(3):
    p = h_lot[i].paragraphs[0]
    p.runs[0].font.name = 'Times New Roman'
    p.runs[0].font.size = Pt(12)
    p.runs[0].font.bold = True
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER if (i == 0 or i == 2) else WD_ALIGN_PARAGRAPH.LEFT
    set_cell_margins(h_lot[i], top=80, bottom=80, left=60, right=60)
    set_cell_borders(h_lot[i], top="single", bottom="single", left=None, right=None)

for idx, (t_no, t_title, t_pg) in enumerate(tables_data, start=1):
    r_cells = lot_table.rows[idx].cells
    r_cells[0].text = t_no
    r_cells[1].text = t_title
    r_cells[2].text = t_pg
    for c_i in range(3):
        p = r_cells[c_i].paragraphs[0]
        p.runs[0].font.name = 'Times New Roman'
        p.runs[0].font.size = Pt(11)
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER if c_i == 0 else (WD_ALIGN_PARAGRAPH.RIGHT if c_i == 2 else WD_ALIGN_PARAGRAPH.LEFT)
        set_cell_margins(r_cells[c_i], top=60, bottom=60, left=60, right=60)
        set_cell_borders(r_cells[c_i], top=None, bottom=None, left=None, right=None)

doc.add_page_break()

# --- LIST OF FIGURES (Page xi) ---
p = doc.add_paragraph()
format_paragraph(p, space_before=0, space_after=14, line_spacing=1.15, alignment=WD_ALIGN_PARAGRAPH.CENTER)
r = p.add_run("LIST OF FIGURES")
r.bold = True
r.underline = True
r.font.size = Pt(14)

figures_data = [
    ("Figure 2.1", "Multi-Tenant Role-Based Access Control (RBAC) and Governance Model", "26"),
    ("Figure 2.2", "Technology Stack Architecture and Layered Service Blueprint", "28"),
    ("Figure 3.4.1", "Microservices System Architecture and Inter-Service Communication Topology", "39"),
    ("Figure 3.4.2", "End-to-End Infrastructure Synthesis and Deployment Sequence Diagram", "41"),
    ("Figure 3.4.3", "Entity-Relationship (ER) Schema for Multi-Tenant Workspaces and Cloud Credentials", "43"),
    ("Figure 5.1", "Authentication and Multi-Tenant Workspace Selection View", "66"),
    ("Figure 5.2", "Project and Environment Lifecycle Management Dashboard", "67"),
    ("Figure 5.3", "Static Repository Analysis and Sizing Engine Output View", "68"),
    ("Figure 5.4", "Interactive React Flow DAG Architecture Designer Canvas", "68"),
    ("Figure 5.5", "Synthesized Infrastructure as Code (Terraform) and Compliance Audit View", "69"),
    ("Figure 5.6", "Cloud Deployer Execution Engine and Real-Time Observability Dashboard", "70")
]

lof_table = doc.add_table(rows=len(figures_data) + 1, cols=3)
lof_table.alignment = WD_TABLE_ALIGNMENT.CENTER
h_lof = lof_table.rows[0].cells
h_lof[0].text = "FIGURE NO."
h_lof[1].text = "TITLE"
h_lof[2].text = "PAGE NO."
for i in range(3):
    p = h_lof[i].paragraphs[0]
    p.runs[0].font.name = 'Times New Roman'
    p.runs[0].font.size = Pt(12)
    p.runs[0].font.bold = True
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER if (i == 0 or i == 2) else WD_ALIGN_PARAGRAPH.LEFT
    set_cell_margins(h_lof[i], top=80, bottom=80, left=60, right=60)
    set_cell_borders(h_lof[i], top="single", bottom="single", left=None, right=None)

for idx, (f_no, f_title, f_pg) in enumerate(figures_data, start=1):
    r_cells = lof_table.rows[idx].cells
    r_cells[0].text = f_no
    r_cells[1].text = f_title
    r_cells[2].text = f_pg
    for c_i in range(3):
        p = r_cells[c_i].paragraphs[0]
        p.runs[0].font.name = 'Times New Roman'
        p.runs[0].font.size = Pt(11)
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER if c_i == 0 else (WD_ALIGN_PARAGRAPH.RIGHT if c_i == 2 else WD_ALIGN_PARAGRAPH.LEFT)
        set_cell_margins(r_cells[c_i], top=60, bottom=60, left=60, right=60)
        set_cell_borders(r_cells[c_i], top=None, bottom=None, left=None, right=None)

doc.add_page_break()

# --- LIST OF SYMBOLS, ABBREVIATIONS AND NOMENCLATURE (Page xii) ---
p = doc.add_paragraph()
format_paragraph(p, space_before=0, space_after=14, line_spacing=1.15, alignment=WD_ALIGN_PARAGRAPH.CENTER)
r = p.add_run("LIST OF SYMBOLS, ABBREVIATIONS AND NOMENCLATURE")
r.bold = True
r.underline = True
r.font.size = Pt(14)

abbr_data = [
    ("AES", "Advanced Encryption Standard"),
    ("API", "Application Programming Interface"),
    ("APM", "Application Performance Monitoring"),
    ("ARN", "Amazon Resource Name"),
    ("AST", "Abstract Syntax Tree"),
    ("AWS", "Amazon Web Services"),
    ("CI/CD", "Continuous Integration and Continuous Deployment"),
    ("CIDR", "Classless Inter-Domain Routing"),
    ("CIS", "Center for Internet Security"),
    ("CORS", "Cross-Origin Resource Sharing"),
    ("CPU", "Central Processing Unit"),
    ("CSP", "Cloud Service Provider"),
    ("DAG", "Directed Acyclic Graph"),
    ("DB", "Database"),
    ("DNS", "Domain Name System"),
    ("EC2", "Elastic Compute Cloud"),
    ("ECS", "Elastic Container Service"),
    ("EKS", "Elastic Kubernetes Service"),
    ("ER", "Entity Relationship"),
    ("GCM", "Galois/Counter Mode"),
    ("GitOps", "Git-centric Operations and Declarative Infrastructure"),
    ("HMAC", "Hash-based Message Authentication Code"),
    ("HOD", "Head of the Department"),
    ("HTTP", "Hypertext Transfer Protocol"),
    ("HTTPS", "Hypertext Transfer Protocol Secure"),
    ("IaC", "Infrastructure as Code"),
    ("IAM", "Identity and Access Management"),
    ("IOPS", "Input/Output Operations Per Second"),
    ("JSON", "JavaScript Object Notation"),
    ("JWT", "JSON Web Token"),
    ("K8s", "Kubernetes"),
    ("LLM", "Large Language Model"),
    ("MTBF", "Mean Time Between Failures"),
    ("MTTD", "Mean Time To Detect"),
    ("MTTR", "Mean Time To Recover"),
    ("OAuth", "Open Authorization"),
    ("OIDC", "OpenID Connect"),
    ("ORM", "Object-Relational Mapping"),
    ("OS", "Operating System"),
    ("RBAC", "Role-Based Access Control"),
    ("REST", "Representational State Transfer"),
    ("S3", "Simple Storage Service"),
    ("SDK", "Software Development Kit"),
    ("SLA", "Service Level Agreement"),
    ("SPA", "Single Page Application"),
    ("SQL", "Structured Query Language"),
    ("SSL", "Secure Sockets Layer"),
    ("TLS", "Transport Layer Security"),
    ("UI/UX", "User Interface / User Experience"),
    ("URI", "Uniform Resource Identifier"),
    ("UUID", "Universally Unique Identifier"),
    ("VPC", "Virtual Private Cloud")
]

# Sort strictly alphabetically
abbr_data.sort(key=lambda x: x[0].upper())

abbr_table = doc.add_table(rows=len(abbr_data) + 1, cols=2)
abbr_table.alignment = WD_TABLE_ALIGNMENT.CENTER
h_abbr = abbr_table.rows[0].cells
h_abbr[0].text = "ABBREVIATION / SYMBOL"
h_abbr[1].text = "EXPANSION / NOMENCLATURE"
for i in range(2):
    p = h_abbr[i].paragraphs[0]
    p.runs[0].font.name = 'Times New Roman'
    p.runs[0].font.size = Pt(12)
    p.runs[0].font.bold = True
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER if i == 0 else WD_ALIGN_PARAGRAPH.LEFT
    set_cell_margins(h_abbr[i], top=80, bottom=80, left=60, right=60)
    set_cell_borders(h_abbr[i], top="single", bottom="single", left=None, right=None)

for idx, (abbr, desc) in enumerate(abbr_data, start=1):
    r_cells = abbr_table.rows[idx].cells
    r_cells[0].text = abbr
    r_cells[1].text = desc
    for c_i in range(2):
        p = r_cells[c_i].paragraphs[0]
        p.runs[0].font.name = 'Times New Roman'
        p.runs[0].font.size = Pt(11)
        p.runs[0].font.bold = (c_i == 0)
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER if c_i == 0 else WD_ALIGN_PARAGRAPH.LEFT
        set_cell_margins(r_cells[c_i], top=50, bottom=50, left=60, right=60)
        set_cell_borders(r_cells[c_i], top=None, bottom=None, left=None, right=None)

output_filename = "CIET_CSE_AetherOps_Project_Report.docx"
doc.save(output_filename)
print(f"Report Batch 1 generated successfully: {output_filename}")
