import streamlit as st
import psycopg2
import pandas as pd
from datetime import datetime
import os

# ==========================================
# ⚙️ PAGE CONFIGURATION & DATABASE
# ==========================================
st.set_page_config(page_title="Premium Electricals - Business Management System", layout="wide", page_icon="⚡")

DB_URL = "postgresql://postgres.nerrocywloccycvdqcqn:Manjitred4505@aws-0-ap-northeast-1.pooler.supabase.com:6543/postgres"

@st.cache_resource
def init_connection():
    return psycopg2.connect(DB_URL)

try:
    conn = init_connection()
    conn.autocommit = True
except Exception as e:
    st.error(f"Database Connection Failed: {e}")
    st.stop()

def create_tables():
    with conn.cursor() as cur:
        # 1. Purchase Table
        cur.execute('''CREATE TABLE IF NOT EXISTS web_purchase_bills (
            id SERIAL PRIMARY KEY, bill_no VARCHAR(50) NOT NULL UNIQUE, bill_date DATE NOT NULL,
            company VARCHAR(100), party VARCHAR(100) NOT NULL, gstin VARCHAR(20), qty INTEGER, 
            taxable DECIMAL(15,2), cgst DECIMAL(15,2), sgst DECIMAL(15,2), igst DECIMAL(15,2), 
            total DECIMAL(15,2) NOT NULL, remarks TEXT, file_name TEXT, file_data BYTEA)''')
        
        # 2. Sales Table
        cur.execute('''CREATE TABLE IF NOT EXISTS web_sales_bills (
            id SERIAL PRIMARY KEY, inv_no VARCHAR(50) NOT NULL UNIQUE, inv_date DATE NOT NULL,
            customer_name VARCHAR(100) NOT NULL, gstin VARCHAR(20), items TEXT, qty INTEGER, 
            taxable DECIMAL(15,2), cgst DECIMAL(15,2), sgst DECIMAL(15,2), igst DECIMAL(15,2), 
            total DECIMAL(15,2) NOT NULL, remarks TEXT, file_name TEXT, file_data BYTEA)''')
        
        # 3. Proforma Tables
        cur.execute('''CREATE TABLE IF NOT EXISTS web_business_profile (
            id INTEGER PRIMARY KEY, firm_name VARCHAR(255), address TEXT, contact VARCHAR(50), gstin VARCHAR(50))''')
        cur.execute('''CREATE TABLE IF NOT EXISTS web_proforma_invoices (
            id SERIAL PRIMARY KEY, inv_no VARCHAR(50), date DATE, time TIME, party_name VARCHAR(255),
            address TEXT, mobile VARCHAR(50), gstin VARCHAR(50), subtotal DECIMAL(15,2), discount_total DECIMAL(15,2), 
            tax_total DECIMAL(15,2), grand_total DECIMAL(15,2), notes TEXT)''')
        cur.execute('''CREATE TABLE IF NOT EXISTS web_proforma_items (
            id SERIAL PRIMARY KEY, invoice_id INTEGER REFERENCES web_proforma_invoices(id) ON DELETE CASCADE,
            item_name TEXT, qty DECIMAL(10,2), price_incl DECIMAL(15,2), disc_perc DECIMAL(5,2),
            tax_perc DECIMAL(5,2), line_total DECIMAL(15,2))''')
        
        cur.execute("SELECT id FROM web_business_profile WHERE id=1")
        if not cur.fetchone():
            cur.execute("INSERT INTO web_business_profile (id, firm_name) VALUES (1, 'PREMIUM ELECTRICALS & WHOLESALERS')")
create_tables()

# ==========================================
# 🎨 CUSTOM CSS THEME
# ==========================================
st.markdown("""
    <style>
    .stApp { background-color: #121212; color: #FFFFFF; }
    .main-headline { color: #00E5FF; font-size: 42px; font-weight: 900; text-align: center; }
    .module-title { color: #00E5FF; font-size: 28px; font-weight: bold; text-align: center; margin-bottom: 20px;}
    
    /* 100% INVISIBLE BUTTONS UNTIL HOVERED */
    .stButton > button, .stFormSubmitButton > button, .stDownloadButton > button { 
        opacity: 0.0 !important; 
        transition: opacity 0.3s ease-in-out !important; 
    }
    .stButton > button:hover, .stFormSubmitButton > button:hover, .stDownloadButton > button:hover { 
        opacity: 1.0 !important; 
    }
    
    .stTextInput > div > div > input, .stNumberInput > div > div > input, .stDateInput > div > div > input, .stTimeInput > div > div > input {
        background-color: #1A1A24 !important; color: #00E5FF !important; border: 1px solid #333 !important;
    }
    label { color: #FFFFFF !important; font-weight: bold !important; font-size: 14px !important;}
    .summary-box { background-color: #1A1A24; padding: 15px; border-radius: 10px; border: 1px solid #333; margin-bottom:15px;}
    .grand-total { font-size: 24px; color: #DC2626; font-weight: bold; }
    .tagline { color: #B000FF; font-size: 16px; font-weight: bold; text-align: center; margin-top: 50px; border-top: 2px solid #00E5FF; padding-top: 10px;}
    </style>
""", unsafe_allow_html=True)

# STATE MANAGEMENT
if "page" not in st.session_state: st.session_state.page = "home"
if "purchase_tab" not in st.session_state: st.session_state.purchase_tab = "entry"
if "sales_tab" not in st.session_state: st.session_state.sales_tab = "entry"
if "proforma_tab" not in st.session_state: st.session_state.proforma_tab = "entry"
if "proforma_items" not in st.session_state:
    st.session_state.proforma_items = pd.DataFrame(columns=["Item Name", "Qty", "Price (Incl. GST)", "Disc %", "Tax %"], data=[["", 1, 0.0, 0, 0] for _ in range(5)])

def fetch_profile():
    with conn.cursor() as cur:
        cur.execute("SELECT firm_name, address, contact, gstin FROM web_business_profile WHERE id=1")
        return cur.fetchone()

# ==========================================
# 🏠 1. HOME DASHBOARD
# ==========================================
if st.session_state.page == "home":
    st.markdown('<div class="main-headline">⚡ PREMIUM ELECTRICALS ⚡</div>', unsafe_allow_html=True)
    st.markdown('<h3 style="color:#B000FF; text-align:center;">Commercial Sales & Business Operations Dashboard</h3><br><br>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🛒 PURCHASE REGISTER\n\n(Inward Stock)", use_container_width=True): st.session_state.page = "purchase"; st.rerun()
    with col2:
        if st.button("📄 PROFORMA INVOICE\n\n(Quotation Builder)", use_container_width=True): st.session_state.page = "proforma"; st.rerun()
    with col3:
        if st.button("💰 SALES REGISTER\n\n(Tax Invoice Billing)", use_container_width=True): st.session_state.page = "sales"; st.rerun()

# ==========================================
# 🛒 2. PURCHASE REGISTER
# ==========================================
elif st.session_state.page == "purchase":
    if st.button("⬅️ BACK TO MAIN DASHBOARD"): st.session_state.page = "home"; st.rerun()
    st.markdown('<div class="module-title">NEW PURCHASE ENTRY</div>', unsafe_allow_html=True)
    
    c1, c2, _ = st.columns([1.5, 1.5, 5])
    with c1:
        if st.button("➕ New Purchase Entry", use_container_width=True): st.session_state.purchase_tab = "entry"; st.rerun()
    with c2:
        if st.button("📋 View Purchase Register", use_container_width=True): st.session_state.purchase_tab = "register"; st.rerun()
    st.divider()

    if st.session_state.purchase_tab == "entry":
        with st.form("purchase_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                bill_no = st.text_input("Bill Number *")
                company = st.text_input("Company Name")
                gstin = st.text_input("Party GSTIN")
                taxable = st.number_input("Taxable Amount (₹)", min_value=0.0, format="%.2f")
                sgst = st.number_input("SGST Amount (₹)", min_value=0.0, format="%.2f")
                total = st.number_input("Total Bill Amount (₹) *", min_value=0.0, format="%.2f")
                uploaded_file = st.file_uploader("Bill Image/PDF", type=["png", "jpg", "jpeg", "pdf"])
            with col2:
                bill_date = st.date_input("Bill Date *", datetime.today())
                party = st.text_input("Party Name *")
                qty = st.number_input("Total Qty", min_value=0, step=1)
                cgst = st.number_input("CGST Amount (₹)", min_value=0.0, format="%.2f")
                igst = st.number_input("IGST Amount (₹)", min_value=0.0, format="%.2f")
                remarks = st.text_input("Remarks / Notes")

            if st.form_submit_button("💾 SAVE PURCHASE BILL", use_container_width=True):
                if not bill_no or not party or total <= 0: st.error("⚠️ Bill No, Party Name, and Total Amount required!")
                else:
                    file_name = uploaded_file.name if uploaded_file else None
                    file_data = psycopg2.Binary(uploaded_file.getvalue()) if uploaded_file else None
                    try:
                        with conn.cursor() as cur:
                            cur.execute("""INSERT INTO web_purchase_bills (bill_no, bill_date, company, party, gstin, qty, taxable, cgst, sgst, igst, total, remarks, file_name, file_data)
                                           VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""", 
                                        (bill_no, bill_date, company, party, gstin, qty, taxable, cgst, sgst, igst, total, remarks, file_name, file_data))
                        st.success(f"✅ Purchase Bill {bill_no} saved!")
                    except psycopg2.IntegrityError: st.error("⚠️ Bill Number already exists!")
                    except Exception as e: st.error(f"Error: {e}")

    elif st.session_state.purchase_tab == "register":
        st.subheader("📋 Saved Purchase Register")
        c_search, c_start, c_end = st.columns([2, 1, 1])
        with c_search: search_query = st.text_input("🔍 Search Party, Bill No...")
        with c_start: start_date = st.date_input("From Date", datetime(datetime.today().year, datetime.today().month, 1))
        with c_end: end_date = st.date_input("To Date", datetime.today())

        query = "SELECT id, bill_no, bill_date, party, company, gstin, qty, taxable, total, remarks, file_name FROM web_purchase_bills WHERE bill_date BETWEEN %s AND %s"
        params = [start_date, end_date]
        if search_query:
            query += " AND (party ILIKE %s OR bill_no ILIKE %s)"
            params.extend([f"%{search_query}%", f"%{search_query}%"])
        query += " ORDER BY bill_date DESC"
        
        df = pd.read_sql_query(query, conn, params=params)
        if df.empty: st.info("No records found.")
        else:
            st.markdown('<div class="summary-box">', unsafe_allow_html=True)
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Visible Bills", len(df)); m2.metric("Total Qty", int(df['qty'].sum()))
            m3.metric("Total Taxable", f"₹{df['taxable'].sum():,.2f}"); m4.metric("Grand Total", f"₹{df['total'].sum():,.2f}")
            st.markdown('</div>', unsafe_allow_html=True)
            st.dataframe(df, use_container_width=True, hide_index=True)

            st.write("**Download Attachment**")
            selected_id = st.selectbox("Select Bill ID to download attachment:", df['id'].tolist(), key="pur_dl")
            with conn.cursor() as cur:
                cur.execute("SELECT file_name, file_data FROM web_purchase_bills WHERE id=%s", (selected_id,))
                file_info = cur.fetchone()
                if file_info and file_info[1]:
                    st.download_button(label=f"📂 Download {file_info[0]}", data=file_info[1], file_name=file_info[0], mime="application/octet-stream")
                else: st.button("📂 No File Attached", disabled=True)

# ==========================================
# 📄 3. PROFORMA INVOICE
# ==========================================
elif st.session_state.page == "proforma":
    if st.button("⬅️ BACK TO MAIN DASHBOARD"): st.session_state.page = "home"; st.rerun()
    profile = fetch_profile()
    firm_name = profile[0] if profile else "Not Set"
    st.markdown(f'<h2 style="color:#1E3A8A; font-weight:bold; margin:0;">FIRM NAME: {firm_name.upper()}</h2>', unsafe_allow_html=True)
    
    c1, c2, c3, _ = st.columns([1.5, 1.5, 1.5, 4])
    with c1:
        if st.button("➕ New Invoice", use_container_width=True): st.session_state.proforma_tab = "entry"; st.rerun()
    with c2:
        if st.button("📋 View Saved Bills", use_container_width=True): st.session_state.proforma_tab = "register"; st.rerun()
    with c3:
        if st.button("⚙️ Edit Profile", use_container_width=True): st.session_state.proforma_tab = "profile"; st.rerun()
    st.divider()

    if st.session_state.proforma_tab == "entry":
        col1, col2 = st.columns(2)
        with col1:
            party_name = st.text_input("Party Name *")
            party_address = st.text_input("Address")
            c_a, c_b = st.columns(2)
            with c_a: party_mobile = st.text_input("Mobile Number")
            with c_b: party_gstin = st.text_input("GSTIN (Optional)")
        with col2:
            inv_no = st.text_input("Invoice No *")
            c_c, c_d = st.columns(2)
            with c_c: inv_date = st.date_input("Date", datetime.today())
            with c_d: inv_time = st.time_input("Time", datetime.now().time())
            notes = st.text_input("Terms & Comments")

        st.subheader("Items Table")
        edited_df = st.data_editor(st.session_state.proforma_items, num_rows="dynamic", use_container_width=True,
            column_config={"Qty": st.column_config.NumberColumn(min_value=1), "Price (Incl. GST)": st.column_config.NumberColumn(format="₹%.2f"),
                           "Disc %": st.column_config.NumberColumn(min_value=0, max_value=100), "Tax %": st.column_config.NumberColumn(min_value=0, max_value=100)})

        total_taxable, total_disc, total_tax, grand_total = 0.0, 0.0, 0.0, 0.0
        calculated_items = []
        for index, row in edited_df.iterrows():
            if row["Item Name"].strip() != "":
                qty = float(row["Qty"] or 0); price_incl = float(row["Price (Incl. GST)"] or 0); disc_perc = float(row["Disc %"] or 0); tax_rate = float(row["Tax %"] or 0)
                gross_incl = qty * price_incl; disc_amt = gross_incl * (disc_perc / 100); net_incl = gross_incl - disc_amt
                taxable_amt = net_incl / (1 + (tax_rate / 100)); tax_amt = net_incl - taxable_amt
                total_taxable += taxable_amt; total_disc += disc_amt; total_tax += tax_amt; grand_total += net_incl
                calculated_items.append((row["Item Name"], qty, price_incl, disc_perc, tax_rate, net_incl))

        s1, s2, s3, s4 = st.columns(4)
        s1.metric("Sub Total", f"₹{total_taxable:,.2f}"); s2.metric("Discount", f"₹{total_disc:,.2f}"); s3.metric("Total Tax", f"₹{total_tax:,.2f}"); s4.markdown(f'<div class="grand-total">Grand Total: ₹{grand_total:,.2f}</div>', unsafe_allow_html=True)

        if st.button("💾 SAVE INVOICE", type="primary"):
            if not inv_no or not party_name: st.error("⚠️ Invoice No and Party Name are mandatory.")
            elif not calculated_items: st.error("⚠️ Please add at least one item.")
            else:
                try:
                    with conn.cursor() as cur:
                        cur.execute("INSERT INTO web_proforma_invoices (inv_no, date, time, party_name, address, mobile, gstin, subtotal, discount_total, tax_total, grand_total, notes) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id", 
                                    (inv_no, inv_date, inv_time.strftime("%H:%M"), party_name, party_address, party_mobile, party_gstin, total_taxable, total_disc, total_tax, grand_total, notes))
                        invoice_id = cur.fetchone()[0]
                        for item in calculated_items:
                            cur.execute("INSERT INTO web_proforma_items (invoice_id, item_name, qty, price_incl, disc_perc, tax_perc, line_total) VALUES (%s, %s, %s, %s, %s, %s, %s)", 
                                        (invoice_id, item[0], item[1], item[2], item[3], item[4], item[5]))
                    st.success("✅ Invoice saved!"); st.session_state.proforma_items = pd.DataFrame(columns=["Item Name", "Qty", "Price (Incl. GST)", "Disc %", "Tax %"], data=[["", 1, 0.0, 0, 0] for _ in range(5)])
                except Exception as e: st.error(f"Error: {e}")

    elif st.session_state.proforma_tab == "register":
        st.subheader("📋 Saved Proforma Invoices")
        df = pd.read_sql_query("SELECT id, inv_no, date, party_name, grand_total FROM web_proforma_invoices ORDER BY id DESC", conn)
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        st.divider()
        if not df.empty:
            st.write("**Print / Download Invoice**")
            selected_id = st.selectbox("Select Invoice ID to Print:", df['id'].tolist(), key="prof_dl")
            if st.button("🖨️ Generate Web Invoice"):
                with conn.cursor() as cur:
                    cur.execute("SELECT * FROM web_proforma_invoices WHERE id=%s", (selected_id,))
                    inv = cur.fetchone()
                    cur.execute("SELECT item_name, qty, price_incl, line_total FROM web_proforma_items WHERE invoice_id=%s", (selected_id,))
                    items = cur.fetchall()
                    html_content = f"""<div style="background:white; color:black; padding:20px; font-family:sans-serif; border:1px solid #ddd; max-width: 800px; margin: auto;">
                        <h1 style="text-align:center; color:#0A2540;">{firm_name}</h1><h3 style="text-align:center; letter-spacing: 2px;">PROFORMA INVOICE</h3><hr>
                        <p><b>Bill To:</b> {inv[4]} <br> <b>Invoice No:</b> {inv[1]} <br> <b>Date:</b> {inv[2]}</p>
                        <table style="width:100%; border-collapse: collapse; margin-top: 20px;"><tr style="background:#0A2540; color:white;">
                        <th style="padding:10px; border:1px solid #ccc;">Item Name</th><th style="padding:10px; border:1px solid #ccc;">Qty</th><th style="padding:10px; border:1px solid #ccc;">Amount</th></tr>"""
                    for it in items: html_content += f"<tr><td style='padding:8px; border:1px solid #ccc;'>{it[0]}</td><td style='padding:8px; border:1px solid #ccc; text-align:center;'>{it[1]}</td><td style='padding:8px; border:1px solid #ccc; text-align:right;'>₹{it[3]:.2f}</td></tr>"
                    html_content += f"</table><h2 style='text-align:right; color:#DC2626;'>Grand Total: ₹{inv[11]:.2f}</h2><p><b>Terms:</b> {inv[12]}</p><br><button onclick='window.print()' style='padding: 10px 20px; background: #059669; color: white; cursor: pointer;'>Print Invoice</button></div>"
                    st.components.v1.html(html_content, height=600, scrolling=True)

    elif st.session_state.proforma_tab == "profile":
        with st.form("profile_form"):
            new_firm = st.text_input("Firm Name", profile[0] if profile else "")
            new_addr = st.text_input("Address", profile[1] if profile else "")
            new_cont = st.text_input("Contact No", profile[2] if profile else "")
            new_gst = st.text_input("GSTIN", profile[3] if profile else "")
            if st.form_submit_button("💾 Save Profile"):
                with conn.cursor() as cur: cur.execute("UPDATE web_business_profile SET firm_name=%s, address=%s, contact=%s, gstin=%s WHERE id=1", (new_firm, new_addr, new_cont, new_gst))
                st.success("Profile Updated!"); st.rerun()

# ==========================================
# 💰 4. SALES REGISTER
# ==========================================
elif st.session_state.page == "sales":
    if st.button("⬅️ BACK TO MAIN DASHBOARD"): st.session_state.page = "home"; st.rerun()
    st.markdown('<div class="module-title">NEW SALES ENTRY</div>', unsafe_allow_html=True)
    
    c1, c2, _ = st.columns([1.5, 1.5, 5])
    with c1:
        if st.button("➕ New Sales Entry", use_container_width=True): st.session_state.sales_tab = "entry"; st.rerun()
    with c2:
        if st.button("📋 View Sales Register", use_container_width=True): st.session_state.sales_tab = "register"; st.rerun()
    st.divider()

    if st.session_state.sales_tab == "entry":
        with st.form("sales_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                inv_no = st.text_input("Invoice No *")
                customer = st.text_input("Customer Name *")
                items = st.text_input("Item Details", placeholder="e.g., GM BLDC Fan, 2.5mm Wire...")
                taxable = st.number_input("Taxable Amount (₹)", min_value=0.0, format="%.2f")
                sgst = st.number_input("SGST Amount (₹)", min_value=0.0, format="%.2f")
                total = st.number_input("Total Invoice Amount (₹) *", min_value=0.0, format="%.2f")
                uploaded_file = st.file_uploader("Bill Image/PDF", type=["png", "jpg", "jpeg", "pdf"])
            with col2:
                inv_date = st.date_input("Invoice Date *", datetime.today())
                gstin = st.text_input("Customer GSTIN")
                qty = st.number_input("Total Qty", min_value=0, step=1)
                cgst = st.number_input("CGST Amount (₹)", min_value=0.0, format="%.2f")
                igst = st.number_input("IGST Amount (₹)", min_value=0.0, format="%.2f")
                remarks = st.text_input("Remarks / Notes")

            if st.form_submit_button("💾 SAVE SALES BILL", use_container_width=True):
                if not inv_no or not customer or total <= 0: st.error("⚠️ Invoice No, Customer Name, and Total Amount are required!")
                else:
                    file_name = uploaded_file.name if uploaded_file else None
                    file_data = psycopg2.Binary(uploaded_file.getvalue()) if uploaded_file else None
                    try:
                        with conn.cursor() as cur:
                            cur.execute("""INSERT INTO web_sales_bills (inv_no, inv_date, customer_name, gstin, items, qty, taxable, cgst, sgst, igst, total, remarks, file_name, file_data)
                                           VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""", 
                                        (inv_no, inv_date, customer, gstin, items, qty, taxable, cgst, sgst, igst, total, remarks, file_name, file_data))
                        st.success(f"✅ Sales Bill {inv_no} saved successfully!")
                    except psycopg2.IntegrityError: st.error("⚠️ Invoice Number already exists!")
                    except Exception as e: st.error(f"Error: {e}")

    elif st.session_state.sales_tab == "register":
        st.subheader("📋 Saved Sales Register")
        c_search, c_start, c_end = st.columns([2, 1, 1])
        with c_search: search_query = st.text_input("🔍 Search Customer, Invoice No...")
        with c_start: start_date = st.date_input("From Date", datetime(datetime.today().year, datetime.today().month, 1))
        with c_end: end_date = st.date_input("To Date", datetime.today())

        query = "SELECT id, inv_no, inv_date, customer_name, gstin, items, qty, taxable, cgst, sgst, igst, total, remarks, file_name FROM web_sales_bills WHERE inv_date BETWEEN %s AND %s"
        params = [start_date, end_date]
        if search_query:
            query += " AND (customer_name ILIKE %s OR inv_no ILIKE %s OR items ILIKE %s)"
            params.extend([f"%{search_query}%"] * 3)
        query += " ORDER BY inv_date DESC, id DESC"
        
        df = pd.read_sql_query(query, conn, params=params)
        if df.empty: st.info("No records found.")
        else:
            st.markdown('<div class="summary-box">', unsafe_allow_html=True)
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Visible Sales", len(df)); m2.metric("Total Qty", int(df['qty'].sum()))
            m3.metric("Total Taxable", f"₹{df['taxable'].sum():,.2f}"); m4.metric("Grand Total", f"₹{df['total'].sum():,.2f}")
            st.markdown('</div>', unsafe_allow_html=True)
            st.dataframe(df, use_container_width=True, hide_index=True)

            st.divider()
            st.write("**Invoice Actions**")
            selected_id = st.selectbox("Select Invoice ID to Action:", df['id'].tolist(), key="sales_dl")
            
            col_action1, col_action2, _ = st.columns([2,2,4])
            with col_action1:
                if st.button("🖨️ Generate Web Invoice"):
                    with conn.cursor() as cur:
                        cur.execute("SELECT * FROM web_sales_bills WHERE id=%s", (selected_id,))
                        inv = cur.fetchone()
                        html_content = f"""<div style="background:white; color:black; padding:30px; font-family:sans-serif; border:1px solid #ddd; max-width: 800px; margin: auto;">
                            <h1 style="text-align:center; color:#2c3e50; margin-bottom: 0;">TAX INVOICE</h1>
                            <h3 style="text-align:center; color:#444; margin-top: 5px;">PREMIUM ELECTRICALS & WHOLESALERS</h3>
                            <hr><div style="display:flex; justify-content:space-between; margin-bottom: 20px;">
                            <div><b>Invoice No:</b> {inv[1]}<br><b>Billed To:</b> {inv[3]}</div><div style="text-align:right;"><b>Date:</b> {inv[2]}</div></div>
                            <table style="width:100%; border-collapse: collapse; margin-bottom: 20px;"><tr style="background:#e6e6e6; font-weight:bold;">
                            <th style="padding:10px; border:1px solid #000;">Item Description</th><th style="padding:10px; border:1px solid #000;">Qty</th><th style="padding:10px; border:1px solid #000;">Total (Rs)</th></tr>
                            <tr><td style="padding:10px; border:1px solid #000;">{inv[5]}</td><td style="padding:10px; border:1px solid #000; text-align:center;">{inv[6]}</td><td style="padding:10px; border:1px solid #000; text-align:right;">{inv[11]:.2f}</td></tr>
                            </table><h2 style="text-align:right;">Grand Total: Rs. {inv[11]:.2f}</h2><p><b>Remarks:</b> {inv[12]}</p>
                            <br><button onclick="window.print()" style="padding: 10px 20px; background: #00E5FF; color: black; font-weight:bold; cursor: pointer;">Print / Save PDF</button></div>"""
                        st.components.v1.html(html_content, height=800, scrolling=True)

            with col_action2:
                with conn.cursor() as cur:
                    cur.execute("SELECT file_name, file_data FROM web_sales_bills WHERE id=%s", (selected_id,))
                    file_info = cur.fetchone()
                    if file_info and file_info[1]: st.download_button(label="📂 Download Attached Bill", data=file_info[1], file_name=file_info[0], mime="application/octet-stream")
                    else: st.button("📂 No File Attached", disabled=True)

st.markdown('<div class="tagline">DEVELOPED BY ER. MANJIT BALMIKI</div>', unsafe_allow_html=True)
