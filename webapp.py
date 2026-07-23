import streamlit as st
import psycopg2

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Premium Electricals - Business Management System",
    layout="wide",
    page_icon="⚡"
)

# --- DATABASE CONNECTION ---
# Put your active Supabase URL here
DB_URL = "postgresql://postgres.nerrocywloccycvdqcqn:[YOUR-PASSWORD]@aws-0-ap-northeast-1.pooler.supabase.com:6543/postgres"

@st.cache_resource
def init_connection():
    return psycopg2.connect(DB_URL)

# --- CUSTOM CSS FOR DARK THEME (MATCHING YOUR DESKTOP UI) ---
st.markdown("""
    <style>
    /* Dark Navy/Black Background */
    .stApp {
        background-color: #0F0F17;
        color: #FFFFFF;
    }

    /* Main Title Styling */
    .main-headline {
        color: #00E5FF;
        font-size: 42px;
        font-weight: 900;
        text-align: center;
        letter-spacing: 2px;
        margin-top: 20px;
    }

    /* Subtitle Styling */
    .sub-headline {
        color: #B000FF;
        font-size: 20px;
        font-weight: bold;
        text-align: center;
        margin-bottom: 50px;
    }

    /* Footer Styling */
    .footer-text {
        color: #666666;
        font-size: 14px;
        font-weight: bold;
        text-align: center;
        margin-top: 80px;
    }

    /* Large Dashboard Action Cards/Buttons */
    div.stButton > button {
        background-color: #1A1A24 !important;
        color: #FFFFFF !important;
        border: 2px solid #8B5CF6 !important;
        border-radius: 15px !important;
        padding: 30px 15px !important;
        height: 180px !important;
        width: 100% !important;
        font-size: 20px !important;
        font-weight: bold !important;
        white-space: pre-wrap !important;
        box-shadow: 0px 4px 15px rgba(139, 92, 246, 0.2);
        transition: all 0.3s ease-in-out;
    }

    /* Hover State for Action Cards */
    div.stButton > button:hover {
        background-color: #8B5CF6 !important;
        color: #FFFFFF !important;
        border: 2px solid #00E5FF !important;
        box-shadow: 0px 6px 25px rgba(0, 229, 255, 0.4);
    }
    </style>
""", unsafe_allow_html=True)

# --- PAGE NAVIGATION STATE ---
if "page" not in st.session_state:
    st.session_state.page = "home"

# ==========================================
# 🏠 HOME DASHBOARD PAGE
# ==========================================
if st.session_state.page == "home":
    # Main Headlines
    st.markdown('<div class="main-headline">⚡ PREMIUM ELECTRICALS ⚡</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-headline">Commercial Sales & Business Operations Dashboard</div>', unsafe_allow_html=True)

    # 3 Large Action Cards Side-by-Side
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("🛒 PURCHASE REGISTER\n\n(Inward Stock)", key="nav_purchase"):
            st.session_state.page = "purchase"
            st.rerun()

    with col2:
        if st.button("📄 PROFORMA INVOICE\n\n(Quotation Builder)", key="nav_proforma"):
            st.session_state.page = "proforma"
            st.rerun()

    with col3:
        if st.button("💰 SALES REGISTER\n\n(Tax Invoice Billing)", key="nav_sales"):
            st.session_state.page = "sales"
            st.rerun()

    # Footer
    st.markdown('<div class="footer-text">Developed by Er. Manjit Balmiki | System Active</div>', unsafe_allow_html=True)

# ==========================================
# 🛒 MODULE 1: PURCHASE REGISTER
# ==========================================
elif st.session_state.page == "purchase":
    if st.button("⬅️ BACK TO MAIN DASHBOARD"):
        st.session_state.page = "home"
        st.rerun()
    st.divider()
    
    st.header("🛒 Purchase Register (Inward Stock)")
    st.info("Purchase Entry and Stock Management forms go here.")

# ==========================================
# 📄 MODULE 2: PROFORMA INVOICE
# ==========================================
elif st.session_state.page == "proforma":
    if st.button("⬅️ BACK TO MAIN DASHBOARD"):
        st.session_state.page = "home"
        st.rerun()
    st.divider()
    
    st.header("📄 Proforma Invoice (Quotation Builder)")
    st.info("Quotation creation and Proforma Invoice generator forms go here.")

# ==========================================
# 💰 MODULE 3: SALES REGISTER
# ==========================================
elif st.session_state.page == "sales":
    if st.button("⬅️ BACK TO MAIN DASHBOARD"):
        st.session_state.page = "home"
        st.rerun()
    st.divider()
    
    st.header("💰 Sales Register (Tax Invoice Billing)")
    
    # Sales Entry Form
    with st.form("sales_form", clear_on_submit=True):
        inv_no = st.text_input("Invoice No *")
        customer = st.text_input("Customer Name *")
        amount = st.number_input("Total Invoice Amount (₹)", min_value=0.0, step=1.0)
        submitted = st.form_submit_button("💾 SAVE SALES BILL")

        if submitted:
            if not inv_no or not customer:
                st.error("Invoice No and Customer Name are required!")
            else:
                try:
                    conn = init_connection()
                    with conn.cursor() as cur:
                        cur.execute(
                            "INSERT INTO web_sales_bills (inv_no, customer, amount) VALUES (%s, %s, %s)",
                            (inv_no, customer, amount)
                        )
                        conn.commit()
                    st.success(f"Invoice {inv_no} saved successfully into Supabase Cloud!")
                except Exception as e:
                    st.error(f"Database error: {e}")