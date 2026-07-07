import streamlit as st
import pandas as pd
import os
import datetime
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
if 'redo_history' not in st.session_state:
    st.session_state.redo_history = [] 
if 'budget' not in st.session_state: 
    st.session_state.budget = 5000.0
if 'income' not in st.session_state: 
    st.session_state.income = 0.0
if 'use_income' not in st.session_state:
    st.session_state.use_income = False

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
REQUIRED_COLUMNS = ['Timestamp', 'Type', 'Item', 'Amount', 'Category']
CATEGORY_OPTIONS = ["Food", "Travel", "Fees", "Incentive", "Entertainment", "Health", "Investment", "Shopping", "Utilities", "Misc"]

def save_data(df):
    df.to_csv(DATA_FILE, index=False)

if 'expenses' not in st.session_state:
    if os.path.exists(DATA_FILE):
        df = pd.read_csv(DATA_FILE)
        if 'Type' in df.columns:
            if 'Timestamp' not in df.columns:
                df.insert(0, 'Timestamp', 'Prior Entry')
            st.session_state.expenses = df
        else:
            st.session_state.expenses = pd.DataFrame(columns=REQUIRED_COLUMNS)
    else:
        st.session_state.expenses = pd.DataFrame(columns=REQUIRED_COLUMNS)

# --- 6. HEADER & METRICS ---
st.markdown(f"<h2 style='text-align: center;'>👋 Hello, {st.session_state.user.capitalize()}</h2>", unsafe_allow_html=True)

with st.expander("⚙️ Configuration"):
    c1, c2, c3 = st.columns([2, 1, 2])
    new_budget = c1.number_input("Monthly Budget", value=float(st.session_state.budget), step=1.0)
    
    st.session_state.use_income = c2.checkbox("Enable Daily Income", value=st.session_state.use_income)
    
    if st.session_state.use_income:
        new_income = c3.number_input("Base Daily Income", value=float(st.session_state.income), step=1.0)
        st.session_state.income = new_income
    else:
        st.session_state.income = 0.0
        
    st.session_state.budget = new_budget

# Calculations
total_exp = st.session_state.expenses[st.session_state.expenses['Type'] == 'Expense']['Amount'].sum()
total_gain = st.session_state.expenses[st.session_state.expenses['Type'] == 'Gain']['Amount'].sum()
current_bal = (st.session_state.budget + st.session_state.income + total_gain) - total_exp

m1, m2, m3 = st.columns(3)
m1.metric("Wallet", f"₹{current_bal:,.2f}")
m2.metric("Spent", f"₹{total_exp:,.2f}")
m3.metric("Earnings", f"₹{total_gain:,.2f}")

st.divider()

# --- 7. MODERN ENTRY FORM ---
_, mid, _ = st.columns([1, 4, 1]) 
with mid:
    with st.container():
        st.markdown("### 📝 New Entry")
        with st.form("modern_form", clear_on_submit=True):
            e_type = st.radio("Type", ["Expense", "Gain"], horizontal=True)
            item = st.text_input("What is this for?")
            amt = st.number_input("Amount (₹)", min_value=0.01, step=1.00, format="%.2f")
            cat = st.selectbox("Category", CATEGORY_OPTIONS)
            
            if st.form_submit_button("Confirm Entry"):
                if item and amt >= 0.01:
                    st.session_state.history.append(st.session_state.expenses.copy())
                    st.session_state.redo_history.clear() # Clear redo stack on new action
                    now_ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    new_row = pd.DataFrame([[now_ts, e_type, item, amt, cat]], columns=REQUIRED_COLUMNS)
                    st.session_state.expenses = pd.concat([st.session_state.expenses, new_row], ignore_index=True)
                    save_data(st.session_state.expenses)
                    st.rerun()

# --- 8. TABLE & ACTIONS ---
st.markdown("### 📜 Recent Activity")
st.caption("💡 Double-click any text cell to edit its value directly. To delete rows, select them using the checkboxes on the left and hit the 🗑️ icon or press Delete on your keyboard.")

# Interactive Data Editor mapping
edited_df = st.data_editor(
    st.session_state.expenses,
    use_container_width=True,
    num_rows="dynamic",
    hide_index=True,
    column_config={
        "Timestamp": st.column_config.TextColumn("Timestamp", disabled=True),
        "Type": st.column_config.SelectboxColumn("Type", options=["Expense", "Gain"], required=True),
        "Category": st.column_config.SelectboxColumn("Category", options=CATEGORY_OPTIONS, required=True),
        "Amount": st.column_config.NumberColumn("Amount (₹)", min_value=0.01, format="%.2f", required=True)
    }
)

# Track inline table modifications seamlessly
if not edited_df.equals(st.session_state.expenses):
    st.session_state.history.append(st.session_state.expenses.copy())
    st.session_state.redo_history.clear() # Clear redo stack on cell edit
    st.session_state.expenses = edited_df.reset_index(drop=True)
    save_data(st.session_state.expenses)
    st.rerun()

# Operations Bar (Undo, Redo, Clear Last)
col_undo, col_redo, col_del = st.columns(3)

if col_undo.button("↩️ Undo"):
    if st.session_state.history:
        st.session_state.redo_history.append(st.session_state.expenses.copy())
        st.session_state.expenses = st.session_state.history.pop()
        save_data(st.session_state.expenses)
        st.rerun()

if col_redo.button("↪️ Redo"):
    if st.session_state.redo_history:
        st.session_state.history.append(st.session_state.expenses.copy())
        st.session_state.expenses = st.session_state.redo_history.pop()
        save_data(st.session_state.expenses)
        st.rerun()

if col_del.button("🗑️ Clear Last"):
    if not st.session_state.expenses.empty:
        st.session_state.history.append(st.session_state.expenses.copy())
        st.session_state.redo_history.clear()
        st.session_state.expenses = st.session_state.expenses.iloc[:-1]
        save_data(st.session_state.expenses)
        st.rerun()

st.divider()

if st.button("Logout"):
    st.session_state.logged_in = False
    st.rerun()
