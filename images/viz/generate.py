#!/usr/bin/env python3
"""dplyr verb diagram SVGs, layout v2: pill on top, tables below, notes inside canvas."""
import os
from math import log

OUT = "/home/alper/Documents/YTU/DERSLER/2025BAHAR/MBG4181-veri-analizi/repo/images/viz"
os.makedirs(OUT, exist_ok=True)

INK, HEADER, ROW_A, ROW_B = "#1E293B", "#222B57", "#FFFFFF", "#F1F5F9"
RED, RED_BG = "#DC2626", "#FEF2F2"
NEW_FG = "#B45309"
GRP = {"drug": "#BFDBFE", "ctrl": "#FDE68A"}
GRP_EDGE = {"drug": "#3B82F6", "ctrl": "#D97706"}
FONT = "Helvetica, Arial, sans-serif"
MONO = "SFMono-Regular, Consolas, Menlo, monospace"

ROWS = [("TP53","drug",300), ("BRCA1","ctrl",100), ("EGFR","drug",450),
        ("MYC","ctrl",250), ("GAPDH","drug",450), ("ACTB","ctrl",250)]
ROW_H, HDR_H, TOP = 30, 34, 104
COLS3 = [("gene",110), ("condition",118), ("expr",72)]
COLS2 = [("gene",110), ("expr",72)]

def esc(s): return str(s).replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")

def table(x, y, cols, rows, row_style=None, cell_style=None, row_h=ROW_H, hdr_style=None):
    w = sum(cw for _, cw in cols); h = HDR_H + row_h*len(rows); p = []
    p.append(f'<rect x="{x}" y="{y}" width="{w}" height="{HDR_H}" fill="{HEADER}"/>')
    cx = x
    for ci, (lab, cw) in enumerate(cols):
        hfill = hdr_style(ci) if hdr_style else "#FFFFFF"
        p.append(f'<text x="{cx+10}" y="{y+22}" font-size="15" font-weight="bold" fill="{hfill}">{esc(lab)}</text>')
        cx += cw
    for ri, row in enumerate(rows):
        ry = y + HDR_H + ri*row_h
        cs = row_style(row, ri) if row_style else {}
        fill, op = cs.get("fill", ROW_A if ri%2==0 else ROW_B), cs.get("opacity", 1.0)
        g0, g1 = (f'<g opacity="{op}">', '</g>') if op < 1 else ("", "")
        if g0: p.append(g0)
        p.append(f'<rect x="{x}" y="{ry}" width="{w}" height="{row_h}" fill="{fill}"/>')
        cx = x
        for ci, ((lab, cw), val) in enumerate(zip(cols, row)):
            tc, tf, tw = INK, FONT, "normal"
            if cell_style: tc, tf, tw = cell_style(row, ci, tc, tf, tw)
            p.append(f'<text x="{cx+10}" y="{ry+20}" font-family="{tf}" font-size="15" fill="{tc}" font-weight="{tw}">{esc(val)}</text>')
            cx += cw
        if g1: p.append(g1)
    return "\n".join(p), w, HDR_H + row_h*len(rows)

def pill(cx, y, code, size=16):
    w = len(code)*(size*0.58) + 30
    return (f'<rect x="{cx-w/2}" y="{y}" width="{w}" height="34" rx="17" fill="{HEADER}"/>'
            f'<text x="{cx}" y="{y+22}" text-anchor="middle" font-family="{MONO}" font-size="{size}" fill="#FFFFFF">{esc(code)}</text>')

def codecard(cx, y, lines, size=15):
    w = max(len(l) for l in lines)*(size*0.58) + 26
    h = len(lines)*22 + 14
    p = [f'<rect x="{cx-w/2}" y="{y}" width="{w}" height="{h}" rx="8" fill="{ROW_B}"/>']
    for i, l in enumerate(lines):
        p.append(f'<text x="{cx}" y="{y+24+i*22}" text-anchor="middle" font-family="{MONO}" font-size="{size}" fill="{INK}">{esc(l)}</text>')
    return "\n".join(p)

def arrow(x1, y, x2):
    return (f'<line x1="{x1}" y1="{y}" x2="{x2-12}" y2="{y}" stroke="{HEADER}" stroke-width="3"/>'
            f'<polygon points="{x2},{y} {x2-14},{y-7} {x2-14},{y+7}" fill="{HEADER}"/>')

def caption(x, y, text, anchor="start", fill="#64748B", size=14, italic="italic"):
    fi = f' font-style="{italic}"' if italic else ""
    return (f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-family="{FONT}" '
            f'font-size="{size}" fill="{fill}"{fi}>{esc(text)}</text>')

def svg(name, w, h, body):
    doc = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}">\n{body}\n</svg>'
    open(f"{OUT}/{name}.svg", "w").write(doc)
    print("wrote", name, w, h)

BOTTOM = TOP + HDR_H + ROW_H*6 + 40   # y of bottom note
H = BOTTOM + 46

# ---------- filter ----------
out = [r for r in ROWS if r[1]=="drug"]
b = [pill(380, 24, 'filter(condition == "drug")'),
     caption(40, 94, "input"), caption(410, 94, "result — rows satisfying the condition"),
     arrow(352, TOP+HDR_H+ROW_H*2+15, 400),
     table(40, TOP, COLS3, ROWS, row_style=lambda r, ri: {"opacity":.32} if r[1]!="drug" else {})[0],
     table(410, TOP, COLS3, out)[0],
     caption(40, BOTTOM, "dimmed rows simply do not flow on — the original data is never modified.", italic=None)]
svg("filter", 760, H, "\n".join(b))

# ---------- select ----------
b = [pill(360, 24, "select(gene, expr)"),
     caption(40, 94, "input"), caption(380, 94, "result — only the named columns"),
     arrow(352, TOP+HDR_H+ROW_H*2+15, 370),
     table(40, TOP, COLS3, ROWS, cell_style=lambda r, ci, tc, tf, tw: ("#94A3B8", tf, tw) if ci==1 else (tc, tf, tw))[0],
     table(380, TOP, COLS2, [(r[0], r[2]) for r in ROWS])[0],
     caption(40, BOTTOM, "select() works on column names — rows are untouched.", italic=None)]
svg("select", 700, H, "\n".join(b))

# ---------- mutate ----------
cols = COLS3 + [("log_expr", 96)]
rows = [(r[0], r[1], r[2], f"{log(r[2]):.2f}") for r in ROWS]
b = [pill(390, 24, "mutate(log_expr = log(expr))"),
     caption(40, 94, "input"), caption(410, 94, "result — new column added"),
     arrow(352, TOP+HDR_H+ROW_H*2+15, 400),
     table(40, TOP, COLS3, ROWS)[0],
     table(410, TOP, cols, rows, cell_style=lambda r, ci, tc, tf, tw: (NEW_FG, MONO, "bold") if ci==3 else (tc, tf, tw))[0],
     caption(40, BOTTOM, "mutate() keeps every existing column and computes the new one row by row.", italic=None)]
svg("mutate", 830, H, "\n".join(b))

# ---------- group_by + summarise ----------
b = [pill(390, 24, "group_by(condition) |> summarise(mean(expr))", size=15),
     caption(40, 94, "input — rows colored by group"), caption(440, 94, "result — one row per group"),
     arrow(352, TOP+HDR_H+ROW_H*2+15, 430),
     table(40, TOP, COLS3, ROWS,
           row_style=lambda r, ri: {"fill": GRP[r[1]]},
           cell_style=lambda r, ci, tc, tf, tw: (GRP_EDGE[r[1]], tf, "bold") if ci==1 else (tc, tf, tw))[0],
     table(440, TOP, [("condition",118), ("mean_expr",110)], [("drug",400), ("ctrl",200)],
           row_style=lambda r, ri: {"fill": GRP[r[0]]},
           cell_style=lambda r, ci, tc, tf, tw: (GRP_EDGE[r[0]], tf, "bold") if ci==0 else (tc, tf, tw))[0],
     caption(40, BOTTOM, "group_by() only tags rows; summarise() then collapses each group to a single number.", italic=None)]
svg("group-summarise", 760, H, "\n".join(b))

# ---------- clean ----------
rows_in = [("TP53","drug",300), ("BRCA1","Drug",100), ("EGFR","drug",450),
           ("EGFR","drug",450), ("MYC","ctrl","NA"), ("ACTB","ctrl",250)]
def cs_clean(r, ci, tc, tf, tw):
    if ci==1 and r[1]=="Drug": return (RED, tf, "bold")
    if r[0]=="EGFR": return (RED, tf, "bold")
    if ci==2 and r[2]=="NA": return (RED, tf, "bold")
    return (tc, tf, tw)
out = [("TP53","drug",300), ("BRCA1","drug",100), ("EGFR","drug",450), ("ACTB","ctrl",250)]
b = [codecard(390, 14, ["distinct() |> ",
                        "mutate(condition = tolower(condition)) |> drop_na()"]),
     caption(40, 94, "raw data — three classic problems"), caption(440, 94, "clean data"),
     arrow(352, TOP+HDR_H+ROW_H*2+15, 430),
     table(40, TOP, COLS3, rows_in, cell_style=cs_clean)[0],
     table(440, TOP, COLS3, out)[0],
     caption(40, BOTTOM-20, "red: duplicate row · inconsistent label · missing value", fill=RED, size=13),
     caption(40, BOTTOM+6, "real data arrives dirty. Cleaning is step one — and because it is a script,", italic=None),
     caption(40, BOTTOM+28, "not a series of clicks, it is repeatable.", italic=None)]
svg("clean", 800, H+6, "\n".join(b))

# ---------- untidy shapes ----------
LRED = "#FCA5A5"   # light red readable on navy header
def checkmark(txt, x, y): return caption(x, y, txt, fill="#15803D")

b = []
# panel A: one variable spread across columns (the classic expression matrix)
colsA = [("sample",64), ("TP53",76), ("BRCA1",80), ("EGFR",76)]
rowsA = [("s1",300,100,450), ("s2",320,110,470)]
b.append(caption(40, 30, "✗ untidy — the variable gene is hiding in the column names", fill=RED))
b.append(table(40, 44, colsA, rowsA,
               hdr_style=lambda ci: LRED if ci>=1 else "#FFFFFF")[0])
b.append(pill(188, 152, "pivot_longer(cols = TP53:EGFR)", size=13))
b.append(f'<line x1="188" y1="196" x2="188" y2="244" stroke="{HEADER}" stroke-width="3"/>'
         f'<polygon points="188,256 181,242 195,242" fill="{HEADER}"/>')
b.append(caption(188, 268, "gene and expr become columns", anchor="middle"))
b.append(table(40, 278, [("sample",70), ("gene",84), ("expr",64)],
               [("s1","TP53",300), ("s1","BRCA1",100), ("s2","TP53",320), ("s2","BRCA1",110)])[0])
b.append(checkmark("✓ tidy — one row per gene per sample", 40, 452))

# panel B: two variables stuffed into one column
b.append(caption(480, 30, "✗ untidy — two variables in one column", fill=RED))
b.append(table(480, 44, [("sample",124), ("expr",70)],
               [("ctrl_rep1",300), ("ctrl_rep2",320), ("drug_rep1",450)],
               cell_style=lambda r, ci, tc, tf, tw: (RED, tf, "bold") if ci==0 else (tc, tf, tw))[0])
b.append(codecard(575, 178, ["separate(sample,", '  into = c("condition", "replicate"))'], size=13))
b.append(f'<line x1="575" y1="238" x2="575" y2="246" stroke="{HEADER}" stroke-width="3"/>'
         f'<polygon points="575,258 568,244 582,244" fill="{HEADER}"/>')
b.append(caption(575, 268, "the sample label splits into two columns", anchor="middle"))
b.append(table(480, 278, [("condition",100), ("replicate",96), ("expr",64)],
               [("ctrl",1,300), ("ctrl",2,320), ("drug",1,450)])[0])
b.append(checkmark("✓ tidy — every variable its own column", 480, 424))
svg("untidy", 880, 470, "\n".join(b))

# ---------- reproducibility: Excel vs script ----------
GREEN = "#15803D"
b = []
b.append(f'<line x1="488" y1="26" x2="488" y2="410" stroke="#CBD5E1" stroke-width="2" stroke-dasharray="6 6"/>')

# LEFT: point-and-click
b.append(caption(40, 34, "✗ point-and-click — the steps leave no trace", fill=RED, size=22))
# excel-style grid: column letters + row numbers
gx, gy, cw, rh = 64, 54, 66, 28
letters = ["A", "B", "C", "D"]
b.append(f'<rect x="{gx}" y="{gy}" width="{cw*4}" height="24" fill="#E2E8F0"/>')
for j, L in enumerate(letters):
    b.append(f'<text x="{gx+j*cw+cw/2}" y="{gy+18}" text-anchor="middle" font-size="16" fill="#64748B">{L}</text>')
highlight = {(2, 3), (3, 3)}          # row, col index (yellow fills)
for i in range(4):
    ry = gy + 24 + i*rh
    b.append(f'<rect x="40" y="{ry}" width="24" height="{rh}" fill="#E2E8F0"/>')
    b.append(f'<text x="52" y="{ry+19}" text-anchor="middle" font-size="15" fill="#64748B">{i+1}</text>')
    for j in range(4):
        fill = "#FDE68A" if (i, j) in highlight else "#FFFFFF"
        b.append(f'<rect x="{gx+j*cw}" y="{ry}" width="{cw}" height="{rh}" fill="{fill}" stroke="#CBD5E1"/>')
        if (i, j) == (2, 3):
            b.append(f'<text x="{gx+j*cw+cw/2}" y="{ry+21}" text-anchor="middle" font-size="18" '
                     f'font-weight="bold" fill="{RED}">400</text>')
b.append(f'<polygon points="320,134 320,154 325,149 329,157 332,154 328,147 334,147" fill="#334155"/>')  # cursor on the 400 cell
for i, t in enumerate(["clicked", "dragged", "copied"]):
    cx0 = 102 + i*96
    b.append(f'<rect x="{cx0-48}" y="212" width="96" height="34" rx="17" fill="none" stroke="#94A3B8" stroke-dasharray="5 4"/>')
    b.append(f'<text x="{cx0}" y="235" text-anchor="middle" font-size="17" fill="#94A3B8">{t}</text>')
for i, fn in enumerate(["expr_analysis.xlsx", "expr_analysis_final.xlsx", "expr_analysis_final_v3_REAL.xlsx"]):
    b.append(f'<rect x="{40+i*16}" y="{256+i*34}" width="{384-i*16}" height="34" rx="8" fill="#F1F5F9" stroke="#CBD5E1"/>')
    b.append(f'<text x="{54+i*16}" y="{279+i*34}" font-family="{MONO}" font-size="17" fill="#64748B">{fn}</text>')
b.append(caption(40, 396, "rerunning = redoing every click by hand.", italic=None, size=18))
b.append(caption(40, 422, "nobody — not even you — knows what was done.", italic=None, size=18))

# RIGHT: a script
b.append(caption(526, 34, "✓ a script — the steps are the record", fill=GREEN, size=22))
b.append(codecard(738, 54, ['read_csv("expr.csv") |>',
                            '  filter(condition == "drug") |>',
                            '  summarise(mean(expr))'], size=20))
b.append(f'<line x1="738" y1="148" x2="738" y2="184" stroke="{HEADER}" stroke-width="3"/>'
         f'<polygon points="738,196 731,182 745,182" fill="{HEADER}"/>')
b.append(f'<rect x="664" y="210" width="148" height="72" rx="9" fill="{HEADER}"/>')
b.append(f'<text x="738" y="236" text-anchor="middle" font-size="17" fill="#94A3B8">mean_expr</text>')
b.append(f'<text x="738" y="272" text-anchor="middle" font-family="{MONO}" font-size="30" '
         f'font-weight="bold" fill="#FBBF24">400</text>')
b.append(caption(738, 320, "✓ same result on any machine — next year too", anchor="middle", fill=GREEN, italic=None, size=18))
b.append(caption(526, 396, "the script is the analysis: every step,", italic=None, size=18))
b.append(caption(526, 422, "re-executed identically with one command.", italic=None, size=18))
svg("reproducibility", 960, 446, "\n".join(b))
