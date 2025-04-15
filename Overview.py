# Pages/Overview.py

import streamlit as st
st.set_page_config(
    page_title="AI Food Security Dashboard",
    page_icon="🌍",
    layout="wide"
)
st.markdown("""
    <style>
        /* Sidebar navigation text */
        section[data-testid="stSidebar"] .css-1v3fvcr, /* streamlit >= 1.18 */
        section[data-testid="stSidebar"] .css-1d391kg {  /* fallback */
            font-size: 1.1rem !important; /* You can adjust this: 1.1rem = ~17px */
        }
    </style>
""", unsafe_allow_html=True)

st.title("Welcome to the AI Food Security Dashboard")
st.markdown("Use the sidebar to navigate through different analytics modules.")

import pandas as pd
import plotly.express as px
from Modules.preprocessing import preprocessing, preparing_adf
from Modules.kpi_functions import (
    ticket_breakdown, total_tickets, average_response_time,
    col1_col2_breakdown, assignnee_workload, top_performers
)


st.title("Overview Dashboard")

# --- Load and preprocess data once ---
@st.cache_data
def load_data():
    raw = pd.read_csv("/Users/samarthsingh/Downloads/data_case2.xlsx - PSUP_Jira_Data_Email_Scrambled.csv")
    df = preprocessing(raw)
    adf = preparing_adf(df)
    return adf

adf = load_data()

with st.sidebar:
    st.markdown("###  Global Filters")

    # Ensure Created is datetime and extract .date() for Streamlit input
    adf['Created'] = pd.to_datetime(adf['Created'], errors='coerce')
    min_date = adf['Created'].min().date()
    max_date = adf['Created'].max().date()

    start = st.date_input("Start Date", value=min_date, min_value=min_date, max_value=max_date, key="start_date")
    end = st.date_input("End Date", value=max_date, min_value=min_date, max_value=max_date, key="end_date")

    department_options = ["All"] + sorted(adf['Relevant_Departments'].dropna().unique())
    department = st.selectbox("Department", options=department_options, key="department_filter")


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
# st.subheader("Ticket Status Breakdown")
# st.dataframe(ticket_breakdown(adf), use_container_width=True)

# --- Breakdown by Status ---
st.subheader("Ticket Status Breakdown")

# Get the breakdown dataframe
status_df = ticket_breakdown(adf)

# Create pie chart
fig = px.pie(
    status_df,
    names='Status',
    values='Count',
    title="Ticket Status Distribution",
    hole=0.3  # optional: donut style
)

# Optional: improve readability
fig.update_traces(textinfo='percent+label', textfont_size=14)
fig.update_layout(title_x=0.5)

st.plotly_chart(fig, use_container_width=True)

# --- Request Category/Type ---
st.subheader("Request Category vs Type")
# st.dataframe(col1_col2_breakdown(adf, 'Request_Type', 'Request_Category'), use_container_width=True)
df = col1_col2_breakdown(adf, 'Request_Type', 'Request_Category')
fig = px.treemap(
    df,
    path=['Request_Type', 'Request_Category'],
    values='Count',
    title="Request Breakdown by Type and Category (Treemap)"
)
fig.update_layout(title_x=0.5)
st.plotly_chart(fig, use_container_width=True)

# --- Region vs Department ---
st.subheader("Region vs Department")
#st.dataframe(col1_col2_breakdown(adf, 'Region', 'Relevant_Departments'), use_container_width=True)

region_dept_df = col1_col2_breakdown(adf, 'Region', 'Relevant_Departments')
region_dept_df = region_dept_df[
    (~region_dept_df['Region'].isnull()) &
    (~region_dept_df['Relevant_Departments'].isnull()) &
(~region_dept_df['Relevant_Departments'].isin(['nan'])) &
(~region_dept_df['Region'].isin(['nan']))
]
#st.dataframe(region_dept_df, use_container_width=True)

fig = px.bar(
    region_dept_df,
    x="Region",
    y="Count",
    color="Relevant_Departments",
    barmode="group",
    title="Grouped Breakdown of Departments by Region"
)
fig.update_layout(title_x=0.5)
st.plotly_chart(fig, use_container_width=True)

# --- Workload Distribution ---
st.subheader("Assignee Workload")
#st.dataframe(assignnee_workload(adf))#.rename(columns={"index": "Assignee", "Assignee": "Ticket Count"}), use_container_width=True)

# Get the data
df_workload = assignnee_workload(adf)

# Create bar chart
fig = px.bar(
    df_workload.sort_values("Tickets_Assigned", ascending=False),
    x="Assignee",
    y="Tickets_Assigned",
    title="Ticket Count by Assignee",
    text="Tickets_Assigned"
)

fig.update_traces(textposition="outside")
fig.update_layout(
    title_x=0.5,
    xaxis_title="Assignee",
    yaxis_title="Tickets Assigned",
    yaxis=dict(tickformat=","),
    uniformtext_minsize=8,
    uniformtext_mode='hide'
)

# Show chart
st.plotly_chart(fig, use_container_width=True)

# --- Top Performers ---
st.subheader("Top Performers")
st.dataframe(top_performers(adf).reset_index(), use_container_width=True)






# Download button
csv = adf.to_csv(index=False).encode('utf-8')
st.download_button(
    label="Download CSV",
    data=csv,
    file_name='filtered_data.csv',
    mime='text/csv'
)
