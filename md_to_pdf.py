import os
import re
from fpdf import FPDF

MD_FILE = "2026.04.24_파이썬_기초_사용법.md"

script_dir = os.path.dirname(os.path.abspath(__file__))
md_path = os.path.join(script_dir, MD_FILE)
pdf_path = os.path.join(script_dir, MD_FILE.replace(".md", ".pdf"))

FONT_REGULAR = "C:/Windows/Fonts/malgun.ttf"
FONT_BOLD    = "C:/Windows/Fonts/malgunbd.ttf"
FONT_MONO    = "C:/Windows/Fonts/malgun.ttf"

with open(md_path, encoding="utf-8") as f:
    lines = f.readlines()


class PDF(FPDF):
    def header(self):
        pass

    def footer(self):
        self.set_y(-12)
        self.set_font("regular", size=8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, str(self.page_no()), align="C")


pdf = PDF(format="A4")
pdf.set_margins(20, 20, 20)
pdf.set_auto_page_break(auto=True, margin=20)

pdf.add_font("regular", style="",  fname=FONT_REGULAR)
pdf.add_font("regular", style="B", fname=FONT_BOLD) # for fpdf2 table headers
pdf.add_font("bold",    style="",  fname=FONT_BOLD)
pdf.add_font("mono",    style="",  fname=FONT_MONO)

pdf.add_page()

def set_regular(size=11): pdf.set_font("regular", size=size); pdf.set_text_color(34, 34, 34)
def set_bold(size=11):    pdf.set_font("bold",    size=size); pdf.set_text_color(34, 34, 34)
def set_mono(size=9):     pdf.set_font("mono",    size=size); pdf.set_text_color(34, 34, 34)

def render_inline(text, base_size=11):
    """굵은 글씨(**text**)와 인라인 코드(`code`), 링크([text](url))를 처리해서 출력"""
    text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)  # [텍스트](링크) → 텍스트만
    parts = re.split(r'(\*\*.*?\*\*|`[^`]+`)', text)
    for part in parts:
        if part.startswith("**") and part.endswith("**"):
            set_bold(base_size)
            pdf.write(6, part[2:-2])
        elif part.startswith("`") and part.endswith("`"):
            set_mono(base_size - 1)
            pdf.set_fill_color(244, 244, 244)
            pdf.write(6, part[1:-1])
        else:
            set_regular(base_size)
            pdf.write(6, part)

def render_hr():
    pdf.ln(3)
    pdf.set_draw_color(200, 200, 200)
    pdf.line(pdf.get_x(), pdf.get_y(), pdf.get_x() + 170, pdf.get_y())
    pdf.ln(5)

def render_blockquote(text):
    pdf.set_fill_color(250, 250, 250)
    pdf.set_draw_color(170, 170, 170)
    x = pdf.get_x()
    pdf.set_x(x + 4)
    set_regular(10)
    pdf.set_text_color(85, 85, 85)
    pdf.multi_cell(160, 6, text.lstrip("> ").strip(), border="L", fill=True, padding=(2, 4, 2, 6))
    pdf.ln(1)

def render_table(table_lines):
    rows = []
    for row in table_lines:
        if re.match(r"^\|[-| :]+\|$", row.strip()):
            continue
        cells = [c.strip() for c in row.strip().strip("|").split("|")]
        rows.append(cells)
    if not rows:
        return

    col_count = max(len(row) for row in rows)
    # 빈 칸을 채워 길이가 일정하도록 맞춤
    for i in range(len(rows)):
        while len(rows[i]) < col_count:
            rows[i].append("")

    col_lengths = [0] * col_count
    for row in rows:
        for j, cell in enumerate(row):
            # 대략적인 글자 길이 계산 (한글=2, 영문/공백=1)
            length = sum(2 if ord(c) > 127 else 1 for c in cell)
            if length > col_lengths[j]:
                col_lengths[j] = length
                
    total_len = sum(col_lengths)
    if total_len > 0:
        col_widths = tuple(170 * (l / total_len) for l in col_lengths)
    else:
        col_widths = tuple(170 / col_count for _ in range(col_count))

    pdf.set_draw_color(200, 200, 200)
    set_regular(9)
    
    with pdf.table(
        col_widths=col_widths,
        text_align="LEFT",
        first_row_as_headings=False,
        cell_fill_color=(255, 255, 255),
        cell_fill_mode="ROWS",
    ) as table:
        for i, data_row in enumerate(rows):
            row = table.row()
            for datum in data_row:
                # 마크다운 문법 정리 (**굵게**, `코드`, [링크](주소), <br> 줄바꿈)
                datum = re.sub(r"\*\*([^*]+)\*\*", r"\1", datum)
                datum = re.sub(r"`([^`]+)`", r"\1", datum)
                datum = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", datum)
                datum = re.sub(r"<br\s*/?>", "\n", datum, flags=re.IGNORECASE)

                if i == 0:
                    pdf.set_fill_color(240, 240, 240)
                    pdf.set_font("regular", "B", 9)
                else:
                    pdf.set_fill_color(255, 255, 255)
                    pdf.set_font("regular", "", 9)
                row.cell(datum)
    pdf.ln(3)


# ── 파싱 루프 ──────────────────────────────────────────────
i = 0
while i < len(lines):
    line = lines[i].rstrip("\n")
    stripped = line.strip()

    # 빈 줄
    if stripped == "":
        pdf.ln(3)
        i += 1
        continue

    # HR
    if re.match(r"^-{3,}$|^\*{3,}$|^_{3,}$", stripped):
        render_hr()
        i += 1
        continue

    # 제목
    if stripped.startswith("# ") and not stripped.startswith("## "):
        set_bold(18)
        pdf.set_text_color(20, 20, 20)
        pdf.multi_cell(0, 9, stripped[2:])
        render_hr()
        i += 1
        continue

    if stripped.startswith("## "):
        pdf.ln(4)
        set_bold(14)
        pdf.set_text_color(20, 20, 20)
        pdf.multi_cell(0, 8, stripped[3:])
        pdf.set_draw_color(200, 200, 200)
        pdf.line(pdf.get_x(), pdf.get_y(), pdf.get_x() + 170, pdf.get_y())
        pdf.ln(3)
        i += 1
        continue

    if stripped.startswith("### "):
        pdf.ln(2)
        set_bold(11)
        pdf.set_text_color(60, 60, 60)
        pdf.multi_cell(0, 7, stripped[4:])
        pdf.ln(1)
        i += 1
        continue

    # 테이블 (| 로 시작하는 연속 라인)
    if stripped.startswith("|"):
        table_lines = []
        while i < len(lines) and lines[i].strip().startswith("|"):
            table_lines.append(lines[i].strip())
            i += 1
        render_table(table_lines)
        continue

    # 코드 블록 (``` 으로 감싸인 것)
    if stripped.startswith("```"):
        code_lines = []
        i += 1
        while i < len(lines) and not lines[i].strip().startswith("```"):
            code_lines.append(lines[i].rstrip("\n"))
            i += 1
        i += 1  # 닫는 ``` 건너뜀

        pdf.set_fill_color(244, 244, 244)
        pdf.set_draw_color(180, 180, 180)
        pdf.set_x(pdf.get_x() + 2)
        set_mono(9)
        code_text = "\n".join(code_lines)
        pdf.multi_cell(166, 5.5, code_text, border=1, fill=True, padding=(3, 4, 3, 4))
        pdf.ln(3)
        continue

    # 인용구
    if stripped.startswith("> "):
        render_blockquote(stripped)
        i += 1
        continue

    # 목록 (- 또는 숫자.)
    if re.match(r"^[-*] ", stripped) or re.match(r"^\d+\. ", stripped):
        is_ordered = bool(re.match(r"^\d+\. ", stripped))
        bullet_text = re.sub(r"^[-*] |^\d+\. ", "", stripped)
        indent = (len(line) - len(line.lstrip()))
        x_offset = 5 + indent * 2

        set_regular(10)
        bullet = "•" if not is_ordered else re.match(r"^(\d+)\.", stripped).group(1) + "."
        pdf.set_x(pdf.get_x() + x_offset)
        pdf.cell(6, 6, bullet)
        render_inline(bullet_text, base_size=10)
        pdf.ln(6)
        i += 1
        continue

    # 일반 문단
    set_regular(10)
    pdf.set_x(pdf.get_x())
    render_inline(stripped, base_size=10)
    pdf.ln(6)
    i += 1

pdf.output(pdf_path)
print(f"PDF 생성 완료: {pdf_path}")
