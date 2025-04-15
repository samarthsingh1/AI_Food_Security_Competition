# Pages/Priority_and_Escalation.py

import streamlit as st
import pandas as pd
from Modules.db import fetch_clickhouse_data
from Modules.agent_insights import agentic_summary_pipeline
from Modules.forecasting import escalated_tickets_per_agent_trend
from Modules.preprocessing import preprocessing, preparing_adf

st.set_page_config(page_title="Priority & Escalation", layout="wide")
st.title("🚨 Priority & Escalation Dashboard")

# --- Load and cache data ---
@st.cache_data
def load_agentic_df():
    raw = pd.read_csv("/Users/samarthsingh/Downloads/data_case2.xlsx - PSUP_Jira_Data_Email_Scrambled.csv")
    from Modules.preprocessing import preprocessing, preparing_adf
    from Modules.sentiment_analysis import generate_comment_sentiments

    adf = preparing_adf(preprocessing(raw))
    comment_df = generate_comment_sentiments(adf)
    comment_df = comment_df.head(200)  # Limit to first 200 for speed
    comment_df[['bullet_points', 'urgency', 'seriousness', 'priority']] = comment_df.apply(agentic_summary_pipeline, axis=1)
    return comment_df

df = load_agentic_df()

with st.sidebar:
    st.markdown("### 🔎 Global Filters")

    # Ensure Created is datetime and extract .date() for Streamlit input
    df['Created'] = pd.to_datetime(df['Created'], errors='coerce')
    min_date = df['Created'].min().date()
    max_date = df['Created'].max().date()

    start = st.date_input("Start Date", value=min_date, min_value=min_date, max_value=max_date, key="start_date")
    end = st.date_input("End Date", value=max_date, min_value=min_date, max_value=max_date, key="end_date")

    department_options = ["All"] + sorted(df['Relevant_Departments'].dropna().unique())
    department = st.selectbox("Department", options=department_options, key="department_filter")



df['Created'] = pd.to_datetime(df['Created'], errors='coerce')
filtered_df = df[
    (df['Created'] >= pd.to_datetime(start)) &
    (df['Created'] <= pd.to_datetime(end))
]

if department != "All":
    filtered_df = filtered_df[filtered_df["Relevant_Departments"] == department]


# --- Priority Distribution ---
st.subheader("🧭 Priority Classification (Agentic AI)")
priority_counts = filtered_df['priority'].value_counts().reset_index()
priority_counts.columns = ['Priority Level', 'Count']
st.dataframe(priority_counts, use_container_width=True)

# --- Escalation Trend ---
st.subheader("📆 Escalated Tickets per Agent (Weekly)")

adf = preparing_adf(preprocessing(pd.read_csv("/Users/samarthsingh/Downloads/data_case2.xlsx - PSUP_Jira_Data_Email_Scrambled.csv")))
escalated_df = escalated_tickets_per_agent_trend(adf)

st.dataframe(escalated_df, use_container_width=True)
