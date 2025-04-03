# Pages/Home.py

import streamlit as st
from datetime import datetime

# Title and intro
st.title("📊 AI Food Security Support Dashboard")
st.markdown("""
Welcome to the Partner Support Analytics Dashboard.  
Use the filters below to customize your view across all pages.
""")

# --- GLOBAL FILTERS using st.session_state ---
st.subheader("🔍 Global Filters")

# Initialize session state
if "start_date" not in st.session_state:
    st.session_state["start_date"] = datetime(2023, 1, 1)
if "end_date" not in st.session_state:
    st.session_state["end_date"] = datetime.today()
if "department_filter" not in st.session_state:
    st.session_state["department_filter"] = "All"

# Date range picker
start, end = st.date_input(
    "Select date range",
    (st.session_state["start_date"], st.session_state["end_date"]),
    format="YYYY-MM-DD"
)

st.session_state["start_date"] = start
st.session_state["end_date"] = end

# Department filter (can be dynamically populated later)
department = st.selectbox(
    "Select a department (applies to all pages)",
    options=["All", "Operations", "Pantry", "Finance", "Tech Support"],
    index=0
)
st.session_state["department_filter"] = department

st.success("✅ Filters set — use sidebar to explore more pages.")
