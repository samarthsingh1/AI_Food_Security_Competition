# Pages/Priority_and_Escalation.py

import streamlit as st
import plotly.express as px
import pandas as pd
# from Modules.db import fetch_clickhouse_data
from Modules.agent_insights import agentic_summary_pipeline
from Modules.forecasting import escalated_tickets_per_agent_trend
from Modules.preprocessing import preprocessing, preparing_adf

st.set_page_config(page_title="Priority & Escalation", layout="wide")
#st.title("Priority & Escalation Dashboard")

# --- Load and cache data ---

from clickhouse_driver import Client
import pandas as pd

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


st.markdown("<h1 style='text-align: center;'>Priority & Escalation</h1>", unsafe_allow_html=True)

@st.cache_data
def load_clickhouse_table():
    # Connect to ClickHouse server
    client = Client(host="localhost")  # or use 'clickhouse' if running from inside Docker

    # Run the query
    query = "SELECT * FROM jira_issues_raw"
    result = client.execute(query)

    # Fetch column names from DESCRIBE TABLE
    columns = [row[0] for row in client.execute("DESCRIBE TABLE jira_issues_raw")]

    # Create pandas DataFrame
    raw = pd.DataFrame(result, columns=columns)
    from Modules.preprocessing import preprocessing, preparing_adf
    from Modules.sentiment_analysis import generate_comment_sentiments

    adf = preparing_adf(preprocessing(raw))
    comment_df = generate_comment_sentiments(adf)
    # comment_df = comment_df.head(200)  # Limit to first 200 for speed
    comment_df[['bullet_points', 'urgency', 'seriousness', 'priority']] = comment_df.apply(agentic_summary_pipeline,
                                                                                           axis=1)
    return comment_df

# Example usage
# if __name__ == "__main__":
#     df = load_clickhouse_table()
#     print(df.head())

# def load_agentic_df():
#     raw = pd.read_csv("/Users/samarthsingh/Downloads/data_case2.xlsx - PSUP_Jira_Data_Email_Scrambled.csv")
#     from Modules.preprocessing import preprocessing, preparing_adf
#     from Modules.sentiment_analysis import generate_comment_sentiments
#
#     adf = preparing_adf(preprocessing(raw))
#     comment_df = generate_comment_sentiments(adf)
#     #comment_df = comment_df.head(200)  # Limit to first 200 for speed
#     comment_df[['bullet_points', 'urgency', 'seriousness', 'priority']] = comment_df.apply(agentic_summary_pipeline, axis=1)
#     return comment_df

df = load_clickhouse_table()

with st.sidebar:
    st.markdown("### Global Filters")

    # Ensure Created is datetime and extract .date() for Streamlit input
    df['Created'] = pd.to_datetime(df['Created'], errors='coerce')
    min_date = df['Created'].min().date()
    max_date = df['Created'].max().date()

    start = st.date_input("Start Date", value=min_date, min_value=min_date, max_value=max_date, key="start_date_priority")
    end = st.date_input("End Date", value=max_date, min_value=min_date, max_value=max_date, key="end_date_priority")

    department_options = ["All"] + sorted(df['Relevant_Departments'].dropna().unique())
    department = st.selectbox("Department", options=department_options, key="department_filter_priority")


# df['Created'] = pd.to_datetime(df['Created'], errors='coerce')
filtered_df = df[
    (df['Created'] >= pd.to_datetime(start)) &
    (df['Created'] <= pd.to_datetime(end))
]

if department != "All":
    filtered_df = filtered_df[filtered_df["Relevant_Departments"] == department]


# --- Priority Distribution ---
# st.subheader("Priority Classification (Agentic AI)")
# priority_counts = filtered_df['priority'].value_counts().reset_index()
# priority_counts.columns = ['Priority Level', 'Count']
# st.dataframe(priority_counts, use_container_width=True)

# --- Priority Distribution ---
st.subheader("Priority Classification (Agentic AI)")

priority_counts = filtered_df['priority'].value_counts().reset_index()
priority_counts.columns = ['Priority Level', 'Count']

# Create and show pie chart
fig = px.pie(
    priority_counts,
    names='Priority Level',
    values='Count',
    #title='Priority Level Distribution',
    hole=0.3,  # for donut-style chart; remove for full pie
)

# Improve readability
fig.update_traces(textinfo='percent+label', textfont_size=14)
fig.update_layout(
    showlegend=True,
    legend_title_text='Priority Level',
    #title_x=0.5
)

st.plotly_chart(fig, use_container_width=True)


# --- Escalation Trend ---
st.subheader("Escalated Tickets per Agent (Weekly)")

adf = preparing_adf(preprocessing(pd.read_csv("/Users/samarthsingh/Downloads/data_case2.xlsx - PSUP_Jira_Data_Email_Scrambled.csv")))
escalated_df = escalated_tickets_per_agent_trend(adf)

#st.dataframe(escalated_df, use_container_width=True)

# Pivot to wide format for area chart
pivot_df = escalated_df.pivot_table(
    index='Week',
    columns='Assignee',
    values='Escalated_Ticket_Count',
    aggfunc='sum',
    fill_value=0
).reset_index()

# Melt back to long format for stacked area chart
melted_df = pivot_df.melt(id_vars='Week', var_name='Assignee', value_name='Escalated_Ticket_Count')

fig_area = px.area(
    melted_df,
    x="Week",
    y="Escalated_Ticket_Count",
    color="Assignee",
    #title="Stacked Area Chart: Escalated Tickets per Agent Over Time"
)

fig_area.update_layout(xaxis_title="Week", yaxis_title="Escalated Tickets")
st.plotly_chart(fig_area, use_container_width=True)



# Download button
csv = filtered_df.to_csv(index=False).encode('utf-8')
st.download_button(
    label="Download CSV",
    data=csv,
    file_name='filtered_data.csv',
    mime='text/csv'
)