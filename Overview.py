# Pages/Overview.py

import streamlit as st
st.set_page_config(
    page_title="Overview Dashboard",
    page_icon="",
    layout="wide"
)
st.markdown("""
    <style>
    /* Headings */
    h1 {
        font-size: 2.5rem !important;
        font-weight: 800 !important;
    }
    h2 {
        font-size: 1.8rem !important;
        font-weight: 700 !important;
    }

    /* Metric labels */
    div[data-testid="metric-container"] > label {
        font-size: 1rem !important;
        color: #6c757d;
    }

    /* Metric values */
    div[data-testid="metric-container"] > div {
        font-size: 2rem !important;
        font-weight: 600;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("""
    <style>
    /* Section spacing */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }

    /* Reduce padding around charts */
    .element-container:has(div[data-testid="stPlotlyChart"]) {
        margin-top: 1rem;
        margin-bottom: 2rem;
    }

    /* Subheader spacing */
    h3 {
        margin-top: 1.5rem;
        margin-bottom: 1rem;
    }

    /* Expander spacing */
    .streamlit-expanderHeader {
        font-size: 1.1rem;
        font-weight: 600;
    }

    .streamlit-expanderContent {
        padding: 0.5rem 1rem;
    }
    </style>
""", unsafe_allow_html=True)


st.markdown("<h1 style='text-align: center;'>Overview</h1>", unsafe_allow_html=True)
# st.markdown("Use the sidebar ?to navigate through different analytics modules.")

import pandas as pd
import plotly.express as px
from Modules.preprocessing import preprocessing, preparing_adf
from Modules.kpi_functions import (
    ticket_breakdown, total_tickets, average_response_time,
    col1_col2_breakdown, assignnee_workload, top_performers
)
from clickhouse_driver import Client

# st.title()

# --- Load and preprocess data once ---
@st.cache_data
def load_data():
    client = Client(host="localhost")
    query = "SELECT * FROM jira_issues_raw"
    result = client.execute(query)
    columns = [row[0] for row in client.execute("DESCRIBE TABLE jira_issues_raw")]
    raw = pd.DataFrame(result, columns=columns)

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
# --- KPI Card Layout ---
st.markdown("### Key Metrics")

kpi1, kpi2, kpi3 = st.columns(3)

with kpi1:
    st.markdown("""
        <div style="background-color: #f9f9f9; padding: 20px 15px; border-radius: 12px; box-shadow: 0 2px 6px rgba(0,0,0,0.05); text-align: center;">
            <div style="color: #6c757d; font-size: 1rem;">Total Tickets</div>
            <div style="font-size: 2rem; font-weight: 600;">{}</div>
        </div>
    """.format(total_tickets(adf)), unsafe_allow_html=True)

with kpi2:
    st.markdown("""
        <div style="background-color: #f9f9f9; padding: 20px 15px; border-radius: 12px; box-shadow: 0 2px 6px rgba(0,0,0,0.05); text-align: center;">
            <div style="color: #6c757d; font-size: 1rem;">Avg Response Time (days)</div>
            <div style="font-size: 2rem; font-weight: 600;">{}</div>
        </div>
    """.format(average_response_time(adf)), unsafe_allow_html=True)

with kpi3:
    st.markdown("""
        <div style="background-color: #f9f9f9; padding: 20px 15px; border-radius: 12px; box-shadow: 0 2px 6px rgba(0,0,0,0.05); text-align: center;">
            <div style="color: #6c757d; font-size: 1rem;">Unique Assignees</div>
            <div style="font-size: 2rem; font-weight: 600;">{}</div>
        </div>
    """.format(adf['Assignee'].nunique()), unsafe_allow_html=True)

# --- Breakdown by Status ---
# st.subheader("Ticket Status Breakdown")
# st.dataframe(ticket_breakdown(adf), use_container_width=True)

st.markdown("---")
#st.subheader("Overview Insights")

# --- Ticket Status Breakdown ---
st.markdown("### Ticket Status Breakdown")
status_df = ticket_breakdown(adf)
fig_status = px.pie(
    status_df,
    names='Status',
    values='Count',
    hole=0.2
)
fig_status.update_traces(textinfo='percent+label', textfont_size=12)
#fig_status.update_layout(title_x=0.2, margin=dict(t=6, b=6))
st.plotly_chart(fig_status, use_container_width=True)

# --- Request Category vs Type ---
st.markdown("### Request Category vs Type")
req_cat_df = col1_col2_breakdown(adf, 'Request_Type', 'Request_Category')
fig_req = px.treemap(
    req_cat_df,
    path=['Request_Type', 'Request_Category'],
    values='Count'
)
#fig_req.update_layout(title_x=0.5, margin=dict(t=10, b=10))
st.plotly_chart(fig_req, use_container_width=True)

# --- Region vs Department ---
st.markdown("---")
st.markdown("### Region vs Department")

region_dept_df = col1_col2_breakdown(adf, 'Region', 'Relevant_Departments')
region_dept_df = region_dept_df[
    (~region_dept_df['Region'].isnull()) &
    (~region_dept_df['Relevant_Departments'].isnull()) &
    (~region_dept_df['Relevant_Departments'].isin(['nan'])) &
    (~region_dept_df['Region'].isin(['nan']))
]

fig_region = px.bar(
    region_dept_df,
    x="Region",
    y="Count",
    color="Relevant_Departments",
    barmode="group"
)
#fig_region.update_layout(title="Grouped Breakdown of Departments by Region", title_x=0.5)
st.plotly_chart(fig_region, use_container_width=True)

# --- Assignee Workload ---
st.markdown("---")
st.markdown("### Assignee Workload")

df_workload = assignnee_workload(adf)
fig_workload = px.bar(
    df_workload.sort_values("Tickets_Assigned", ascending=False),
    x="Assignee",
    y="Tickets_Assigned",
    # title="",
    # text="Tickets_Assigned"
)
fig_workload.update_traces(textposition="outside")
fig_workload.update_layout(
    #title_x=0.5,
    xaxis_title="Assignee",
    yaxis_title="Tickets Assigned",
    yaxis=dict(tickformat=","),
    uniformtext_minsize=8,
    uniformtext_mode='hide'
)
st.plotly_chart(fig_workload, use_container_width=True)

# --- Top Performers (Expandable Table) ---
st.markdown("---")
st.markdown("### Top Performers")

with st.expander(" View Full Performer Table"):
    st.dataframe(top_performers(adf).reset_index(), use_container_width=True)




# Download button
csv = adf.to_csv(index=False).encode('utf-8')
st.download_button(
    label="Download CSV",
    data=csv,
    file_name='filtered_data.csv',
    mime='text/csv'
)
