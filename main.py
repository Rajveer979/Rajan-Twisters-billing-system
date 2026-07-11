import streamlit as st
from fpdf import FPDF
from PIL import Image
import re
import io
import base64
import os
import pandas as pd
from datetime import datetime

# --- LOGO (embedded as base64 so it works on Streamlit Cloud) ---
LOGO_B64 = "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"

def get_logo_bytes():
    return base64.b64decode(LOGO_B64)


# --- 1. METER ENTRY ---
st.header("1. Meter Entry")

entry_count = st.selectbox(
    "Select Meter Entry Count",
    [48, 96],
    index=0
)

st.subheader("Manual / Verified Entry")

# Initialize dataframe
if (
    "meter_df" not in st.session_state
    or len(st.session_state.meter_df) != entry_count
):
    st.session_state.meter_df = pd.DataFrame({
        "Sr No": range(1, entry_count + 1),
        "Meter": [""] * entry_count
    })

if "extracted_meters" in st.session_state:
    extracted = st.session_state.pop("extracted_meters")
    if len(extracted) <= entry_count:
        st.session_state.meter_df = pd.DataFrame({
            "Sr No": range(1, len(extracted) + 1),
            "Meter": extracted
        })

edited_df = st.data_editor(
    st.session_state.meter_df,
    key="meter_editor",
    use_container_width=True,
    hide_index=True,
    num_rows="fixed",
    height=700,
    column_config={
        "Sr No": st.column_config.NumberColumn(
            "Sr No",
            disabled=True,
            width="small"
        ),
        "Meter": st.column_config.TextColumn(
            "Meter",
            width="medium"
        )
    }
)



# -----------------------------
# PROCESS VALUES
# -----------------------------
final_weights = []

for val in edited_df["Meter"]:

    try:

        if str(val).strip():

            final_weights.append(
                float(str(val).strip())
            )

    except:
        pass

final_weights.sort()
# -----------------------------
# SUMMARY CARDS
# -----------------------------
c1, c2, c3, c4 = st.columns(4)

with c1:
    st.metric("Required", entry_count)

with c2:
    st.metric("Entered", len(final_weights))

with c3:
    st.metric(
        "Total Meters",
        f"{sum(final_weights):.2f}"
        if final_weights else "0.00"
    )

with c4:
    st.metric(
        "Remaining",
        entry_count - len(final_weights)
    )



# --- 2. BILLING DETAILS ---
if len(final_weights) > 0:
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
    col_sel, col_btn = st.columns([4, 1])
    with col_sel:
        selected = st.selectbox("Choose existing party:", party_names)
    with col_btn:
        st.markdown("<br>", unsafe_allow_html=True)
        add_clicked = st.button("➕ Add Party")

    if add_clicked:
        st.session_state["show_add_party"] = True

    if st.session_state.get("show_add_party"):
        st.markdown("#### ➕ Add New Party")
        a1, a2 = st.columns(2)
        with a1:
            np_name    = st.text_input("Party Name *", key="np_name")
            np_address = st.text_area("Address", key="np_address")
        with a2:
            np_gstin   = st.text_input("GSTIN", key="np_gstin")
            np_broker  = st.text_input("Broker", key="np_broker")

        s1, s2 = st.columns([1, 5])
        with s1:
            if st.button("💾 Save Party"):
                if np_name.strip():
                    parties[np_name.strip()] = {
                        "address": np_address.strip(),
                        "gstin":   np_gstin.strip(),
                        "broker":  np_broker.strip()
                    }
                    with open(parties_file, "w") as f:
                        json.dump(parties, f, indent=2, ensure_ascii=False)
                    st.success(f"✅ '{np_name}' saved! Select from dropdown above.")
                    st.session_state["show_add_party"] = False
                    st.rerun()
                else:
                    st.error("Please enter a party name.")
        with s2:
            if st.button("❌ Cancel"):
                st.session_state["show_add_party"] = False
                st.rerun()
        st.divider()

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
        date    = st.text_input("DATE", datetime.now().strftime("%d-%m-%Y"))
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
        RH = 9     # data row
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

        # FIX: use an in-memory BytesIO stream instead of writing/deleting a
        # temp file on disk. The previous tempfile + os.unlink approach was
        # the most likely cause of the segfault crashing the Streamlit
        # Cloud container (native fpdf2/Pillow image decode + filesystem
        # race on the ephemeral container). fpdf2 accepts file-like objects
        # directly via pdf.image(), so no temp file is needed at all.
        logo_stream = io.BytesIO(get_logo_bytes())
        pdf.image(logo_stream, x=M + 1, y=logo_y + 1, w=20, h=20)

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

        # ── 7. DATA ROW (NO horizontal line below) ─────────────────────
        pdf.set_font("Arial", '', 9)

        pdf.set_x(M)

        pdf.cell(C_DESC, RH, "  ART SILK CLOTH",       border='LR', ln=0, align='L')
        pdf.cell(C_PCS,  RH, str(len(final_weights)),  border='LR', ln=0, align='C')
        pdf.cell(C_TOT,  RH, f"{total_mtrs:.2f}",      border='LR', ln=0, align='C')
        pdf.cell(C_RATE, RH, f"{rate:.2f}",            border='LR', ln=0, align='C')
        pdf.cell(C_AMT,  RH, f"{amt_rs}",              border='LR', ln=0, align='R')
        pdf.cell(C_PS,   RH, f"{amt_ps:02d}",          border='LR', ln=1, align='C')


        # ─────────────────────────────────────────────
        # Fill remaining area WITHOUT horizontal lines
        # ─────────────────────────────────────────────

        TARGET_TABLE_BOTTOM = 195

        current_y = pdf.get_y()
        remaining_space = TARGET_TABLE_BOTTOM - current_y

        blank_height = max(80, remaining_space)

        pdf.set_x(M)

        pdf.cell(C_DESC, blank_height, "", border='LR', ln=0)
        pdf.cell(C_PCS,  blank_height, "", border='LR', ln=0)
        pdf.cell(C_TOT,  blank_height, "", border='LR', ln=0)
        pdf.cell(C_RATE, blank_height, "", border='LR', ln=0)
        pdf.cell(C_AMT,  blank_height, "", border='LR', ln=0)
        pdf.cell(C_PS,   blank_height, "", border='LR', ln=1)

        # Bottom closing border only
        pdf.set_x(M)

        pdf.cell(C_DESC, 0, "", border='T', ln=0)
        pdf.cell(C_PCS,  0, "", border='T', ln=0)
        pdf.cell(C_TOT,  0, "", border='T', ln=0)
        pdf.cell(C_RATE, 0, "", border='T', ln=0)
        pdf.cell(C_AMT,  0, "", border='T', ln=0)
        pdf.cell(C_PS,   0, "", border='T', ln=1)

        table_bot = pdf.get_y()
        pdf.ln(2)
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
        pdf.cell(LW, CH, f"  Due Date : {date}", border=0, ln=1, align='L')
        pdf.set_x(M)
        pdf.set_font("Arial", 'B', 10)
        pdf.cell(LW, CH, "  No Dyeing Guarantee", border=0, ln=1, align='L')

        pdf.set_x(M)
        pdf.set_font("Arial", '', 8)
        pdf.cell(LW, 5, "  GSTIN : 24AAPPM5382C1ZN", border=0, ln=1, align='L')

        pdf.set_x(M)
        pdf.cell(LW, 5, "  PAN : AAPPM5382C", border=0, ln=1, align='L')

        pdf.set_x(M)
        pdf.cell(LW, 5, "  Bank Name : Kotak Mahindra Bank", border=0, ln=1, align='L')

        pdf.set_x(M)
        pdf.cell(LW, 5, "  Account Number : 9825771671", border=0, ln=1, align='L')

        pdf.set_x(M)
        pdf.cell(LW, 5, "  IFSC Code : kkbk0002864", border=0, ln=1, align='L')
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
        today = datetime.now().strftime("%d-%m-%Y")
        st.download_button("📥 Download Official Rajan PDF",
                        data=bytes(pdf_bytes),
                        file_name=f"bill_{bill_no}_{today}.pdf")
