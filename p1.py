import streamlit as st
import pandas as pd
import os
import streamlit.components.v1 as components

# --- 1. PAGE CONFIG ---
st.set_page_config(page_title="FinTrack Pro", layout="wide", initial_sidebar_state="collapsed")

# JavaScript: Enter as Tab
components.html(
    """
    <script>
    const doc = window.parent.document;
    doc.addEventListener('keydown', function(e) {
        if (e.key === 'Enter') {
            const inputs = Array.from(doc.querySelectorAll('input, select, button'));
            const index = inputs.indexOf(doc.activeElement);
            if (index > -1 && index < inputs.length - 1) {
                e.preventDefault();
                inputs[index + 1].focus();
            }
        }
    });
    </script>
    """,
    height=0,
)

# --- 2. MODERN MOBILE-FRIENDLY CSS ---
st.markdown("""
    <style>
    /* Google Font Import */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap');
    
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

    /* Modern Card Styling */
    div[data-testid="stExpander"], .stContainer {
        border-radius: 15px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        padding: 15px;
        background: rgba(255, 255, 255, 0.05);
    }

    /* Centering and Mobile Scaling */
    .stMetric {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 12px;
        padding: 10px;
        text-align: center;
    }

    /* Force Table Centering */
    [data-testid="stDataFrame"] div[role="gridcell"] > div { 
        justify-content: center !important; 
        text-align: center !important; 
    }
    [data-testid="stDataFrame"] div[role="columnheader"] > div { 
        justify-content: center !important; 
    }

   /* Full-width buttons for Mobile touch (excluding password toggle overlays) */
    button[data-testid="stBaseButton-secondary"] {
        width: 100% !important;
        border-radius: 10px !important;
        height: 3em !important;
    }
    /* Remove extra padding on mobile */
    .block-container { padding: 1rem 1rem !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. SESSION STATE ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user = ""
if 'history' not in st.session_state:
    st.session_state.history = [] 

USER_REGISTRY = {"sayam": "123", "judge": "win101", "tcet": "aimlb" , "test": "123"}

# --- 4. LOGIN ---
if not st.session_state.logged_in:
    _, col, _ = st.columns([1, 2, 1])
    with col:
        st.markdown("<h1 style='text-align: center;'>🔐 FinTrack</h1>", unsafe_allow_html=True)
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.button("Sign In"):
            if u in USER_REGISTRY and USER_REGISTRY[u] == p:
                st.session_state.logged_in = True
                st.session_state.user = u
                st.rerun()
            else:
                st.error("Invalid Login")
    st.stop()

# --- 5. DATA LOGIC ---
DATA_FILE = f"data_{st.session_state.user}.csv"
REQUIRED_COLUMNS = ['Type', 'Item', 'Amount', 'Category']

def save_data(df):
    df.to_csv(DATA_FILE, index=False)

if 'expenses' not in st.session_state:
    if os.path.exists(DATA_FILE):
        df = pd.read_csv(DATA_FILE)
        st.session_state.expenses = df if 'Type' in df.columns else pd.DataFrame(columns=REQUIRED_COLUMNS)
    else:
        st.session_state.expenses = pd.DataFrame(columns=REQUIRED_COLUMNS)

if 'budget' not in st.session_state: st.session_state.budget = 5000.0
if 'income' not in st.session_state: st.session_state.income = 0.0

# --- 6. HEADER & METRICS ---
st.markdown(f"<h2 style='text-align: center;'>👋 Hello, {st.session_state.user.capitalize()}</h2>", unsafe_allow_html=True)

with st.expander("⚙️ Configuration"):
    c1, c2 = st.columns(2)
    st.session_state.budget = c1.number_input("Monthly Budget", value=st.session_state.budget)
    st.session_state.income = c2.number_input("Base Daily Income", value=st.session_state.income)

# Math
total_exp = st.session_state.expenses[st.session_state.expenses['Type'] == 'Expense']['Amount'].sum()
total_gain = st.session_state.expenses[st.session_state.expenses['Type'] == 'Gain']['Amount'].sum()
current_bal = (st.session_state.budget + st.session_state.income + total_gain) - total_exp

m1, m2, m3 = st.columns(3)
m1.metric("Wallet", f"₹{current_bal:,.2f}")
m2.metric("Spent", f"₹{total_exp:,.2f}")
m3.metric("Earnings", f"₹{total_gain:,.2f}")

st.divider()

# --- 7. MODERN ENTRY FORM ---
_, mid, _ = st.columns([1, 4, 1]) # Wider for mobile but centered for desktop
with mid:
    with st.container():
        st.markdown("### 📝 New Entry")
        with st.form("modern_form", clear_on_submit=True):
            e_type = st.radio("Type", ["Expense", "Gain"], horizontal=True)
            item = st.text_input("What is this for?")
            # Updated: min_value=1.0 as requested
            amt = st.number_input("Amount (₹)", min_value=1.0, step=1.0, format="%.2f")
            cat = st.selectbox("Category", ["Food", "Travel", "Fees", "Incentive", "Misc"])
            
            if st.form_submit_button("Confirm Entry"):
                if item and amt >= 1:
                    st.session_state.history.append(st.session_state.expenses.copy())
                    new_row = pd.DataFrame([[e_type, item, amt, cat]], columns=REQUIRED_COLUMNS)
                    st.session_state.expenses = pd.concat([st.session_state.expenses, new_row], ignore_index=True)
                    save_data(st.session_state.expenses)
                    st.rerun()

# --- 8. TABLE & ACTIONS ---
st.markdown("### 📜 Recent Activity")
col_undo, col_del = st.columns(2)
if col_undo.button("↩️ Undo"):
    if st.session_state.history:
        st.session_state.expenses = st.session_state.history.pop()
        save_data(st.session_state.expenses)
        st.rerun()

if col_del.button("🗑️ Clear Last"):
    if not st.session_state.expenses.empty:
        st.session_state.history.append(st.session_state.expenses.copy())
        st.session_state.expenses = st.session_state.expenses.iloc[:-1]
        save_data(st.session_state.expenses)
        st.rerun()

st.dataframe(st.session_state.expenses, use_container_width=True, hide_index=True)

if st.button("Logout"):
    st.session_state.logged_in = False
    st.rerun()
