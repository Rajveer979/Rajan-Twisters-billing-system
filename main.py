import streamlit as st
from google import genai
from google.genai import types
from fpdf import FPDF
from PIL import Image
import re
import io
import base64
import tempfile
import os

# --- LOGO (embedded as base64 so it works on Streamlit Cloud) ---
LOGO_B64 = "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"

# --- CONFIGURATION ---
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
except:
    st.error("⚠️ API Key not found. Please add GEMINI_API_KEY to your .streamlit/secrets.toml file.")
    st.stop()
client = genai.Client(api_key=API_KEY)
MODEL_ID = "gemini-1.5-flash"

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
            except Exception as e:
                st.error(f"Error: {str(e)}")

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

    # ── Load parties from parties.json (same folder as app) ──
    import json, os
    parties = {}
    parties_file = os.path.join(os.path.dirname(__file__), "parties.json")
    try:
        with open(parties_file, "r") as f:
            parties = json.load(f)
    except:
        parties = {"-- Select Party --": {"address": "", "gstin": ""}}

    # ── Party selector ──
    st.subheader("Select Party")
    party_names = list(parties.keys())
    selected = st.selectbox("Choose existing party or select manually below:", party_names)

    # Auto-fill values from selected party
    if selected and selected != "-- Select Party --":
        default_buyer   = selected
        default_address = parties[selected]["address"]
        default_gstin   = parties[selected]["gstin"]
        default_broker  = parties[selected].get("broker", "")
    else:
        default_buyer   = ""
        default_address = ""
        default_gstin   = ""
        default_broker  = ""

    c1, c2 = st.columns(2)
    with c1:
        buyer       = st.text_input("M/s.",               value=default_buyer)
        address     = st.text_area("Address",             value=default_address)
        gstin_buyer = st.text_input("GSTIN (Receiver)",   value=default_gstin)
    with c2:
        bill_no = st.text_input("BILL NO.", "2")
        ch_no   = st.text_input("CH. NO.", "2")
        date    = st.text_input("DATE", "07-03-2026")
        broker  = st.text_input("BROKER", value=default_broker)
        rate    = st.number_input("RATE", value=15.0)

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

        # Decode logo and save to temp file for fpdf
        logo_bytes = base64.b64decode(LOGO_B64)
        tmp_logo = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
        tmp_logo.write(logo_bytes)
        tmp_logo.close()
        # Draw logo at same position/size as the old grey circle (20x20mm)
        pdf.image(tmp_logo.name, x=M + 1, y=logo_y + 1, w=20, h=20)
        os.unlink(tmp_logo.name)

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

        # ── Separator line between M/s name row and address rows ──
        pdf.set_draw_color(0, 0, 0)
        pdf.set_line_width(0.2)
        pdf.line(M, BT + CH, M + LW, BT + CH)

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

        pdf.set_x(M)
        pdf.set_font("Arial", '', 8)
        pdf.cell(LW, 5, "  Bank Name : Kotak Mahindra Bank", border=0, ln=1, align='L')

        pdf.set_x(M)
        pdf.cell(LW, 5, "  Account Number : 9825771671", border=0, ln=1, align='L')

        pdf.set_x(M)
        pdf.cell(LW, 5, "  IFCI Code : kkbk0002864", border=0, ln=1, align='L')

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
            pdf.cell(THIRD, 5, "Mobile No.:  9825771671",     border=1, ln=0, align='R')

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
                ("Quality :",     "Renyal"),
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
        from datetime import datetime
        today = datetime.now().strftime("%d-%m-%Y")
        st.download_button("📥 Download Official Rajan PDF",
                           data=bytes(pdf_bytes),
                           file_name=f"bill_{bill_no}_{today}.pdf")
