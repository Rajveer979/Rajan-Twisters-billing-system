import streamlit as st
from google import genai
from google.genai import types
from fpdf import FPDF
from PIL import Image
import re
import io

# --- CONFIGURATION ---
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
except:
    API_KEY = "AIzaSyDxBT0LhrpISRJXd6Jv5hfiIaSmzUTBWKA"
client = genai.Client(api_key=API_KEY)
MODEL_ID = "gemini-3-flash-preview"

st.set_page_config(page_title="Rajan Twisters AI", layout="wide")

if 'manual_meters' not in st.session_state:
    st.session_state.manual_meters = ""

# --- 1. METER ENTRY ---
st.header("1. Meter Entry")
uploaded_file = st.file_uploader("Upload Meter Sheet", type=["jpg", "jpeg", "png"])

col_a, col_b = st.columns([1, 2])
with col_a:
    if uploaded_file and st.button("🚀 Scan Image"):
        with st.spinner("AI Scanning..."):
            try:
                img = Image.open(uploaded_file)
                if img.mode in ("RGBA", "P"): img = img.convert("RGB")
                img_byte_arr = io.BytesIO()
                img.save(img_byte_arr, format='JPEG', quality=80)
                prompt = "List all decimal numbers found, separated by commas. No text."
                response = client.models.generate_content(
                    model=MODEL_ID,
                    contents=[prompt, types.Part.from_bytes(data=img_byte_arr.getvalue(), mime_type='image/jpeg')]
                )
                raw_found = re.findall(r"\d+\.\d+", response.text)
                st.session_state.manual_meters = ", ".join(raw_found)
                st.success("Scan Complete!")
            except Exception:
                st.error("Server busy. Please enter values manually.")

with col_b:
    meter_input = st.text_area("Verify / Edit Meter Values:", value=st.session_state.manual_meters, height=150)
    st.session_state.manual_meters = meter_input

# Data Processing
try:
    final_weights = [float(x.strip()) for x in meter_input.replace('\n', ',').split(',') if x.strip()]
    final_weights.sort()
except ValueError:
    final_weights = []

# --- 2. BILLING DETAILS ---
if final_weights:
    st.divider()
    c1, c2 = st.columns(2)
    with c1:
        buyer = st.text_input("M/s.", "raj")
        address = st.text_area("Address", "192, hariom small scale Ind Society-1, bamroli, surat")
        gstin_buyer = st.text_input("GSTIN (Receiver)", "24AABCDE1234A1Z1")
    with c2:
        bill_no = st.text_input("BILL NO.", "2")
        ch_no = st.text_input("CH. NO.", "2")
        date = st.text_input("DATE", "07-03-2026")
        broker = st.text_input("BROKER", "sharma")
        rate = st.number_input("RATE", value=15.0)

    if st.button("📄 Generate Paper-Style PDF"):
        total_mtrs = sum(final_weights)
        taxable    = total_mtrs * rate
        cgst_val   = taxable * 0.025
        sgst_val   = taxable * 0.025
        igst_val   = 0.0
        grand_total = round(taxable + cgst_val + sgst_val)
        round_up    = round(grand_total - (taxable + cgst_val + sgst_val), 2)
        amt_rs      = int(taxable)
        amt_ps      = round((taxable - amt_rs) * 100)

        # ── Layout constants ──────────────────────────
        PAGE_W = 210
        M      = 8           # margin
        IW     = PAGE_W - 2*M  # inner width = 194mm

        # Table columns (sum = 194)
        C_DESC = 72
        C_PCS  = 20
        C_TOT  = 30
        C_RATE = 30
        C_AMT  = 30
        C_PS   = IW - C_DESC - C_PCS - C_TOT - C_RATE - C_AMT  # 12mm

        # Totals block aligns under C_RATE + C_AMT + C_PS
        TX     = M + C_DESC + C_PCS + C_TOT   # x-start of totals = 160mm
        TW     = C_RATE + C_AMT + C_PS        # total width = 72mm
        T_LBL  = 44                            # label cell width
        T_VAL  = TW - T_LBL                   # value cell width = 28mm

        # Left info block width = DESC+PCS+TOT
        LW = C_DESC + C_PCS + C_TOT           # 122mm

        # Row heights
        RH = 8     # data row
        HH = 7     # header row
        CH = 7     # general cell height

        pdf = FPDF(orientation='P', unit='mm', format='A4')
        pdf.add_page()
        pdf.set_margins(M, M, M)
        pdf.set_auto_page_break(False)

        # ── 1. TOP STRIP ─────────────────────────────
        pdf.set_xy(M, M)
        pdf.set_font("Arial", 'B', 8)
        pdf.cell(IW/3, 5, "TAX INVOICE", border=0, ln=0, align='L')
        pdf.set_font("Arial", 'I', 8)
        pdf.cell(IW/3, 5, "|| Shree Ganeshay Namah ||", border=0, ln=0, align='C')
        pdf.set_font("Arial", '', 8)
        pdf.cell(IW/3, 5, "M. 98257 71671", border=0, ln=1, align='R')

        # ── 3. LOGO + COMPANY NAME ───────────────────
        logo_y = pdf.get_y()
        pdf.set_fill_color(220, 220, 220)
        pdf.ellipse(M + 1, logo_y + 1, 20, 20, style='F')

        pdf.set_xy(M, logo_y)
        pdf.set_font("Arial", 'B', 26)
        pdf.set_text_color(180, 0, 0)
        pdf.cell(IW, 13, "RAJAN TWISTERS", border=0, ln=1, align='C')
        pdf.set_text_color(0, 0, 0)

        pdf.set_x(M)
        pdf.set_font("Arial", 'B', 8)
        pdf.cell(IW, 4, "Manufacturers of : Twisted Yarn & Art Silk Cloth", border=0, ln=1, align='C')
        pdf.set_font("Arial", '', 7)
        pdf.set_x(M)
        pdf.cell(IW, 4, "Plot No. 192, Hariom Small Scale Ind. Society-1,", border=0, ln=1, align='C')
        pdf.set_x(M)
        pdf.cell(IW, 4, "Bamroli Main Road, Bamroli, SURAT.", border=0, ln=1, align='C')
        pdf.ln(2)

        # ── 4. M/s BLOCK + RIGHT GRID ────────────────
        # Left side  (LW mm wide): outer rectangle border, M/s name top + address below
        # Right side (TW mm wide): 4 equal rows — BILL NO / DATE / CH NO / BROKER
        #                           each row split into label (RC_L) | value (RC_V)
        RC_L      = 36
        RC_V      = TW - RC_L          # 36mm
        BLOCK_H   = CH * 4             # total height = 4 rows tall

        BT = pdf.get_y()               # block top Y

        # ── Draw left outer rectangle (spans full 4-row height) ──
        pdf.rect(M, BT, LW, BLOCK_H)

        # ── M/s name text (top of left box) — auto-shrink font if name too wide ──
        ms_text = f"M/s.  {buyer}"
        for fsize in [9, 8, 7, 6]:
            pdf.set_font("Arial", '', fsize)
            if pdf.get_string_width(ms_text) <= LW - 6:
                break
        pdf.set_xy(M + 2, BT + 1)
        pdf.cell(LW - 4, CH, ms_text, border=0, ln=0, align='L')

        # ── Address: word-wrap into 2 lines capped at LW-6mm wide ──
        pdf.set_font("Arial", '', 7)
        addr_max_w = LW - 6
        words = address.split()
        line1_addr, line2_addr = "", ""
        for w in words:
            test = (line1_addr + " " + w).strip()
            if pdf.get_string_width(test) <= addr_max_w:
                line1_addr = test
            else:
                line2_addr = (line2_addr + " " + w).strip()
        pdf.set_xy(M + 2, BT + CH + 1)
        pdf.cell(LW - 4, CH - 1, line1_addr, border=0, ln=0, align='L')
        if line2_addr:
            pdf.set_font("Arial", '', 6.5)
            pdf.set_xy(M + 2, BT + CH * 2 + 1)
            pdf.cell(LW - 4, CH - 1, line2_addr, border=0, ln=0, align='L')

        # ── Right grid: 4 rows, each with label | value ──
        pdf.set_font("Arial", '', 8)
        right_rows = [
            ("  BILL NO.", f"  {bill_no}"),
            ("  DATE",     f"  {date}"),
            ("  CH. NO.",  f"  {ch_no}"),
            ("  BROKER",   f"  {broker}"),
        ]
        for i, (lbl, val) in enumerate(right_rows):
            ry = BT + i * CH
            # Top border only on first row, bottom on all
            top_b    = 'T' if i == 0 else ''
            pdf.set_xy(M + LW, ry)
            pdf.cell(RC_L, CH, lbl, border=f"{top_b}LB",  ln=0, align='L')
            pdf.cell(RC_V, CH, val, border=f"{top_b}RB",  ln=1, align='L')

        pdf.set_y(BT + BLOCK_H)
        pdf.ln(1)

        # ── 5. GSTIN ROW ─────────────────────────────
        GY = pdf.get_y()
        pdf.set_x(M)
        pdf.set_font("Arial", '', 8)

        GL_W  = 16   # "GSTIN :" label
        BOX_W = 6    # each char box
        gstin_str = gstin_buyer.strip().upper().ljust(15)[:15]

        pdf.cell(GL_W, CH, "GSTIN :", border=1, ln=0, align='L')
        for ch in gstin_str:
            pdf.cell(BOX_W, CH, ch, border=1, ln=0, align='C')

        used_x = M + GL_W + 15 * BOX_W
        hsn_w  = PAGE_W - M - used_x
        pdf.set_x(used_x)
        pdf.cell(hsn_w, CH, "  HSN Code :: 5407", border=1, ln=1, align='L')
        pdf.ln(1)

        # ── 6. TABLE HEADER ──────────────────────────
        pdf.set_x(M)
        pdf.set_font("Arial", 'B', 8)
        pdf.cell(C_DESC, HH, "DESCRIPTION",        border=1, ln=0, align='C')
        pdf.cell(C_PCS,  HH, "PIECES",             border=1, ln=0, align='C')
        pdf.cell(C_TOT,  HH, "TOTAL MTS./KGS.",    border=1, ln=0, align='C')
        pdf.cell(C_RATE, HH, "RATE PER MTR./KG.",  border=1, ln=0, align='C')
        pdf.cell(C_AMT,  HH, "AMOUNT Rs.",         border=1, ln=0, align='C')
        pdf.cell(C_PS,   HH, "Ps.",                border=1, ln=1, align='C')

        # ── 7. DATA ROW + empty rows below ──────────────────────────────
        pdf.set_font("Arial", '', 9)
        pdf.set_x(M)
        pdf.cell(C_DESC, RH, "  ART SILK CLOTH",      border='LRB', ln=0, align='L')
        pdf.cell(C_PCS,  RH, str(len(final_weights)),  border='LRB', ln=0, align='C')
        pdf.cell(C_TOT,  RH, f"{total_mtrs:.2f}",      border='LRB', ln=0, align='C')
        pdf.cell(C_RATE, RH, f"{rate:.2f}",             border='LRB', ln=0, align='C')
        pdf.cell(C_AMT,  RH, f"{amt_rs}",               border='LRB', ln=0, align='R')
        pdf.cell(C_PS,   RH, f"{amt_ps:02d}",           border='LRB', ln=1, align='C')

        # 5 empty rows with full borders
        for _ in range(5):
            pdf.set_x(M)
            pdf.cell(C_DESC, RH, "", border='LRB', ln=0)
            pdf.cell(C_PCS,  RH, "", border='LRB', ln=0)
            pdf.cell(C_TOT,  RH, "", border='LRB', ln=0)
            pdf.cell(C_RATE, RH, "", border='LRB', ln=0)
            pdf.cell(C_AMT,  RH, "", border='LRB', ln=0)
            pdf.cell(C_PS,   RH, "", border='LRB', ln=1)

        table_bot = pdf.get_y()

        # ── 8. TOTALS (right side, below table) ──────
        def tot_row(lbl, val, bold=False):
            pdf.set_x(TX)
            pdf.set_font("Arial", 'B' if bold else '', 8)
            pdf.cell(T_LBL, CH, lbl, border=1, ln=0, align='R')
            pdf.cell(T_VAL, CH, val, border=1, ln=1, align='R')

        tot_row("Total",           f"{taxable:.2f}")
        tot_row("CGST @ 2.5 %",    f"{cgst_val:.2f}")
        tot_row("SGST @ 2.5 %",    f"{sgst_val:.2f}")
        tot_row("IGST @       %",  f"{igst_val:.2f}")
        tot_row("Round up",        f"{round_up:.2f}")
        tot_row("GRAND TOTAL",     f"{float(grand_total):.2f}", bold=True)

        totals_bot = pdf.get_y()

        # ── 9. LEFT INFO (Due Date / No Dyeing / GSTIN / PAN) ──
        pdf.set_xy(M, table_bot)
        pdf.set_font("Arial", '', 9)
        pdf.cell(LW, CH, "  Due Date :", border=0, ln=1, align='L')

        pdf.set_x(M)
        pdf.set_font("Arial", 'B', 10)
        pdf.cell(LW, CH, "  No Dyeing Guarantee", border=0, ln=1, align='L')

        pdf.set_x(M)
        pdf.set_font("Arial", '', 8)
        pdf.cell(LW, 5, "  GSTIN : 24AAPPM5382C1ZN", border=0, ln=1, align='L')

        pdf.set_x(M)
        pdf.cell(LW, 5, "  PAN : AAPPM5382C", border=0, ln=1, align='L')

        # ── 10. RUPEES IN WORDS ──────────────────────
        words_y = max(totals_bot, pdf.get_y()) + 1
        pdf.set_xy(M, words_y)
        pdf.set_font("Arial", 'B', 8)
        pdf.cell(IW, CH, f"  Rupees in Words : {int(grand_total)} Rupees Only",
                 border=1, ln=1, align='L')
        pdf.ln(2)

        # ── 11. TERMS + SIGNATURE ────────────────────
        TERMS_W = round(IW * 0.68)
        SIG_W   = IW - TERMS_W
        TS_Y    = pdf.get_y()
        LINE_H  = 4.5

        terms_lines = [
            "TERMS OF SALE : (1) Goods once sold will not be taken back or exchanged.",
            "(2) We reserve the right of recovery at any time before due date.",
            "(3) We can demand for payment whenever we want. (4) No complaint will be",
            "entertained about the quality and width of goods sold. (5) Contract of sale",
            "will be taken as at Surat. (6) Profit at the rate of 2.5% per month will be",
            "charged on the amount of the bill if not paid as per the terms of the bill.",
        ]
        BLOCK_H = (len(terms_lines) + 1) * LINE_H + 4

        # Draw borders
        pdf.rect(M,           TS_Y, TERMS_W, BLOCK_H)
        pdf.rect(M + TERMS_W, TS_Y, SIG_W,   BLOCK_H)

        # Terms text
        pdf.set_font("Arial", '', 6.5)
        for i, line in enumerate(terms_lines):
            pdf.set_xy(M + 1, TS_Y + 1 + i * LINE_H)
            pdf.cell(TERMS_W - 2, LINE_H, line, border=0, align='L')

        pdf.set_xy(M + 1, TS_Y + 1 + len(terms_lines) * LINE_H)
        pdf.cell(TERMS_W - 2, LINE_H, "                                      E. & O. E.",
                 border=0, align='L')

        # Signature block
        pdf.set_xy(M + TERMS_W, TS_Y + 2)
        pdf.set_font("Arial", 'B', 9)
        pdf.cell(SIG_W, 7, "For, RAJAN TWISTERS", border=0, ln=0, align='C')

        sig_line_y = TS_Y + BLOCK_H - 7
        pdf.line(M + TERMS_W + 3, sig_line_y,
                 M + TERMS_W + SIG_W - 3, sig_line_y)
        pdf.set_xy(M + TERMS_W, sig_line_y)
        pdf.set_font("Arial", '', 8)
        pdf.cell(SIG_W, 5, "Authorised Signatory", border=0, ln=1, align='C')

        # ══════════════════════════════════════════════
        # PAGE 2 — TWO DELIVERY CHALLANS (top half + bottom half)
        # Each challan is identical — same data, same design
        # Page height 297mm split: top challan 0-145mm, bottom 150-297mm
        # ══════════════════════════════════════════════
        pdf.add_page()
        pdf.set_margins(M, M, M)
        pdf.set_auto_page_break(False)

        P2_M  = M
        P2_IW = IW       # 194mm

        # ── Challan dimensions ──
        # Each challan gets ~143mm height, with a 4mm divider line between them
        CHALLAN_H  = 143   # height of each challan block
        DIVIDER_Y  = M + CHALLAN_H + 2   # thin line between the two challans

        # ── Draw divider line ──
        pdf.set_draw_color(150, 150, 150)
        pdf.set_line_width(0.5)
        pdf.line(P2_M, DIVIDER_Y, P2_M + P2_IW, DIVIDER_Y)
        pdf.set_draw_color(0, 0, 0)
        pdf.set_line_width(0.2)

        # ══════════════════════════════════════════════
        # HELPER FUNCTION — draws one complete challan
        # Y_OFF = vertical offset (0 for top, ~148 for bottom)
        # ══════════════════════════════════════════════
        def draw_challan(Y_OFF):
            # All Y values are relative to Y_OFF
            # Layout constants
            CW       = P2_IW          # challan inner width = 194mm
            LEFT_W   = round(CW * 0.58)
            RIGHT_W  = CW - LEFT_W
            RIGHT_X  = P2_M + LEFT_W

            # Fixed Y anchors (relative)
            Y0  = Y_OFF + M          # top of challan content
            Y_TOP_ROW = Y0
            Y_TITLE   = Y0 + 5
            Y_ADDRESS = Y0 + 15
            Y_MANUF   = Y0 + 20
            Y_INFO    = Y0 + 27
            INFO_ROW_H = 6
            Y_BLANK   = Y_INFO + 4 * INFO_ROW_H + 1
            Y_DATA    = Y_BLANK + 4
            ROW_H     = 5.5
            GRID_COLS = 8
            GRID_ROWS = 12
            GC_W      = LEFT_W / GRID_COLS

            Y_DATA_END   = Y_DATA + (GRID_ROWS + 1) * ROW_H
            Y_TOTAL_PCS  = Y_DATA
            Y_TOTAL_MTRS = Y_DATA + INFO_ROW_H * 2
            Y_NODYE      = Y_DATA + INFO_ROW_H * 5
            Y_SIG        = Y_DATA_END + 2

            # ── ROW 1: Delivery challan (L) | blessing (C) | Mobile (R) ──
            # Equal 3-way split so blessing is truly centered
            THIRD = CW / 3
            pdf.set_xy(P2_M, Y_TOP_ROW)
            pdf.set_font("Arial", '', 7)
            pdf.cell(THIRD, 5, "Delivery challan",            border=1, ln=0, align='L')
            pdf.set_font("Arial", 'B', 7)
            pdf.cell(THIRD, 5, "!! shree Ganeshay Namah !!",  border=1, ln=0, align='C')
            pdf.set_font("Arial", '', 7)
            pdf.cell(THIRD, 5, "Mobile No.:  9898130771",     border=1, ln=0, align='R')

            # ── ROW 2: Rajan Twisters title ──
            pdf.set_xy(P2_M, Y_TITLE)
            pdf.set_font("Arial", 'B', 16)
            pdf.cell(CW, 9, "Rajan Twisters", border=1, ln=0, align='C')

            # ── ROW 3: Address ──
            pdf.set_xy(P2_M, Y_ADDRESS)
            pdf.set_font("Arial", '', 7)
            pdf.cell(CW, 4,
                     "192, hariom small scale Ind Society-1, bamroli main road, bamroli, surat",
                     border=1, ln=0, align='C')

            # ── ROW 4: MANUFACTURES | GSTIN ──
            pdf.set_xy(P2_M, Y_MANUF)
            pdf.set_font("Arial", 'B', 7)
            pdf.cell(LEFT_W, 6, "MANUFACTURES AND DEALER IN ART SILK CLOTH", border=1, ln=0, align='L')
            pdf.cell(RIGHT_W, 6, "GSTIN :  24AAPPM5382C1ZN  HSN: 5407", border=1, ln=0, align='L')

            # ── Word-wrap address for info block ──
            INFO_LBL   = 20
            INFO_VAL_L = LEFT_W - INFO_LBL
            INFO_VAL_R = RIGHT_W - INFO_LBL
            pdf.set_font("Arial", '', 7)
            addr_max = INFO_VAL_L - 4
            words_a  = address.split()
            al1, al2 = "", ""
            for w in words_a:
                test = (al1 + " " + w).strip()
                if pdf.get_string_width(test) <= addr_max:
                    al1 = test
                else:
                    al2 = (al2 + " " + w).strip()
            if al2 and pdf.get_string_width(al2) > addr_max:
                al2 = al2[:int(len(al2) * addr_max / pdf.get_string_width(al2))]

            # ── Left info block ──
            left_info = [
                ("M/s. :",  buyer,       7),
                ("Add. :",  al1,         7),
                ("",        al2,         6.5),
                ("GSTIN :", gstin_buyer, 7),
            ]
            for i, (lbl, val, fsz) in enumerate(left_info):
                iy = Y_INFO + i * INFO_ROW_H
                pdf.set_xy(P2_M, iy)
                pdf.set_font("Arial", 'B', 7)
                pdf.cell(INFO_LBL, INFO_ROW_H, lbl, border=1, ln=0, align='L')
                pdf.set_font("Arial", '', fsz)
                pdf.cell(INFO_VAL_L, INFO_ROW_H, f"  {val}", border=1, ln=0, align='L')

            # ── Right info block ──
            right_info = [
                ("Challan No. :", bill_no),
                ("Date :",        date),
                ("Broker :",      broker),
                ("Quality :",     ""),
            ]
            for i, (lbl, val) in enumerate(right_info):
                iy = Y_INFO + i * INFO_ROW_H
                pdf.set_xy(RIGHT_X, iy)
                pdf.set_font("Arial", 'B', 7)
                pdf.cell(INFO_LBL, INFO_ROW_H, lbl, border=1, ln=0, align='L')
                pdf.set_font("Arial", '', 7)
                pdf.cell(INFO_VAL_R, INFO_ROW_H, f"  {val}", border=1, ln=0, align='L')

            # ── Blank separator ──
            pdf.set_xy(P2_M, Y_BLANK)
            pdf.cell(LEFT_W, 3, "", border=1, ln=0)
            pdf.cell(RIGHT_W, 3, "", border=1, ln=0)

            # ── Meter grid: 8 cols x 12 rows, column-first ──
            vals = list(final_weights[:GRID_COLS * GRID_ROWS])
            pdf.set_font("Arial", '', 6.5)
            for ri in range(GRID_ROWS):
                ry = Y_DATA + ri * ROW_H
                for ci in range(GRID_COLS):
                    idx = ci * GRID_ROWS + ri
                    v   = vals[idx] if idx < len(vals) else None
                    txt = f"{v:.2f}" if v is not None else ""
                    pdf.set_xy(P2_M + ci * GC_W, ry)
                    pdf.cell(GC_W, ROW_H, txt, border=1, ln=0, align='R')

            # ── Total row ──
            total_row_y = Y_DATA + GRID_ROWS * ROW_H
            pdf.set_font("Arial", 'B', 6.5)
            for ci in range(GRID_COLS):
                col_idxs = range(ci * GRID_ROWS, min((ci + 1) * GRID_ROWS, len(vals)))
                col_sum  = sum(vals[i] for i in col_idxs) if col_idxs else 0
                txt = f"{col_sum:.2f}" if any(True for _ in col_idxs) else ""
                pdf.set_xy(P2_M + ci * GC_W, total_row_y)
                pdf.cell(GC_W, ROW_H, txt, border=1, ln=0, align='R')

            # ── Right side: Total Pieces / Meters / NO DYEING ──
            R_LBL = 36
            R_VAL = RIGHT_W - R_LBL

            pdf.set_xy(RIGHT_X, Y_TOTAL_PCS)
            pdf.set_font("Arial", 'B', 7)
            pdf.cell(R_LBL, INFO_ROW_H, "Total Pieces :", border=1, ln=0, align='R')
            pdf.set_font("Arial", '', 8)
            pdf.cell(R_VAL, INFO_ROW_H, f"  {len(final_weights)}", border=1, ln=0, align='C')

            pdf.set_xy(RIGHT_X, Y_TOTAL_PCS + INFO_ROW_H)
            pdf.cell(RIGHT_W, INFO_ROW_H, "", border=1, ln=0)

            pdf.set_xy(RIGHT_X, Y_TOTAL_MTRS)
            pdf.set_font("Arial", 'B', 7)
            pdf.cell(R_LBL, INFO_ROW_H, "Total Meters :", border=1, ln=0, align='R')
            pdf.set_font("Arial", '', 8)
            pdf.cell(R_VAL, INFO_ROW_H, f"  {total_mtrs:.2f}", border=1, ln=0, align='C')

            for bi in range(2):
                pdf.set_xy(RIGHT_X, Y_TOTAL_MTRS + INFO_ROW_H * (bi + 1))
                pdf.cell(RIGHT_W, INFO_ROW_H, "", border=1, ln=0)

            # NO DYEING GUARANTEE
            pdf.set_xy(RIGHT_X, Y_NODYE)
            pdf.set_font("Arial", 'B', 9)
            pdf.set_text_color(180, 0, 0)
            pdf.cell(RIGHT_W, 7, "NO DYEING GUARANTEE", border=1, ln=0, align='C')
            pdf.set_text_color(0, 0, 0)

            # Disclaimer
            disclaimer = ("Out despatching goods will not be any type of marking on "
                          "it's otherwise,we will not accepted return the same.")
            pdf.set_xy(RIGHT_X, Y_NODYE + 7)
            pdf.set_font("Arial", '', 6.5)
            pdf.multi_cell(RIGHT_W, 4, disclaimer, border=1, align='C')

            # ── Bottom: Prepared by | Receiver stamp ──
            pdf.set_xy(P2_M, Y_SIG)
            pdf.set_font("Arial", '', 7)
            HALF = CW / 2
            pdf.cell(HALF, 6, "Prepared by :-  ____________________",
                     border=1, ln=0, align='L')
            pdf.cell(HALF, 6, "Receiver's stamp & Signature:-  ________________",
                     border=1, ln=0, align='L')

        # ── Draw top challan (Y offset = 0, starts at margin) ──
        draw_challan(0)

        # ── Draw bottom challan (Y offset = half page) ──
        draw_challan(148)

        pdf_bytes = pdf.output()
        st.download_button("📥 Download Official Rajan PDF",
                           data=bytes(pdf_bytes),
                           file_name="Rajan_Bill_Final.pdf")
