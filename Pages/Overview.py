# Pages/Overview.py

import streamlit as st
import pandas as pd
from Modules.preprocessing import preprocessing, preparing_adf
from Modules.kpi_functions import (
    ticket_breakdown, total_tickets, average_response_time,
    col1_col2_breakdown, assignnee_workload, top_performers
)

st.set_page_config(page_title="Overview", layout="wide")
st.title("📊 Overview Dashboard")

# --- Load and preprocess data once ---
@st.cache_data
def load_data():
    raw = pd.read_csv("/Users/samarthsingh/Downloads/data_case2.xlsx - PSUP_Jira_Data_Email_Scrambled.csv")
    df = preprocessing(raw)
    adf = preparing_adf(df)
    return adf

adf = load_data()

# --- Apply global filters ---
if "start_date" not in st.session_state:
    st.session_state["start_date"] = pd.to_datetime("2022-01-01")  # or earliest date in dataset

if "end_date" not in st.session_state:
    st.session_state["end_date"] = pd.to_datetime("2022-12-31")  # or latest date

if "department_filter" not in st.session_state:
    st.session_state["department_filter"] = "All"

start = st.session_state["start_date"]
end = st.session_state["end_date"]
department = st.session_state["department_filter"]

adf = adf[
    (adf["Created_Timestamp"] >= pd.to_datetime(start)) &
    (adf["Created_Timestamp"] <= pd.to_datetime(end))
]

if department != "All":
    adf = adf[adf["Relevant_Departments"] == department]

# --- KPIs ---
col1, col2, col3 = st.columns(3)
col1.metric("Total Tickets", total_tickets(adf))
col2.metric("Avg Response Time (days)", average_response_time(adf))
col3.metric("Unique Assignees", adf['Assignee'].nunique())

# --- Breakdown by Status ---
st.subheader("📌 Ticket Status Breakdown")
st.dataframe(ticket_breakdown(adf), use_container_width=True)

# --- Request Category/Type ---
st.subheader("🗂 Request Category vs Type")
st.dataframe(col1_col2_breakdown(adf, 'Request_Type', 'Request_Category'), use_container_width=True)

# --- Region vs Department ---
st.subheader("🌍 Region vs Department")
st.dataframe(col1_col2_breakdown(adf, 'Region', 'Relevant_Departments'), use_container_width=True)

# --- Workload Distribution ---
st.subheader("👷 Assignee Workload")
st.dataframe(assignnee_workload(adf).reset_index().rename(columns={"index": "Assignee", "Assignee": "Ticket Count"}), use_container_width=True)

# --- Top Performers ---
st.subheader("🏆 Top Performers")
st.dataframe(top_performers(adf), use_container_width=True)
