import streamlit as st
import plotly.express as px
import pandas as pd
from clickhouse_driver import Client


from Modules.preprocessing import preprocessing, preparing_adf
from Modules.sentiment_analysis import generate_comment_sentiments, generate_polarity_subjectivity_for_comments
from Modules.forecasting import (
    backlog_trend,
    weekly_inflow_outflow,
    percent_negative_comments_over_time,
    negative_ticket_resolution_time_trend,
    escalated_tickets_per_agent_trend,
    forecast_weekly_ticket_volume,
    forecast_weekly_resolution_time
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


st.markdown("<h1 style='text-align: center;'>Time Series Forecasting</h1>", unsafe_allow_html=True)

# Load & prepare data (adjust path if needed)
@st.cache_data
def load_data():
    # df = pd.read_csv("/Users/samarthsingh/Downloads/data_case2.xlsx - PSUP_Jira_Data_Email_Scrambled.csv")
    # Connect to ClickHouse server
    client = Client(host="localhost")  # or use 'clickhouse' if running from inside Docker

    # Run the query
    query = "SELECT * FROM jira_issues_raw"
    result = client.execute(query)

    # Fetch column names from DESCRIBE TABLE
    columns = [row[0] for row in client.execute("DESCRIBE TABLE jira_issues_raw")]

    # Create pandas DataFrame
    df = pd.DataFrame(result, columns=columns)
    df = preprocessing(df)
    adf = preparing_adf(df)
    sentiment_df = generate_comment_sentiments(adf)
    sentiment_df = generate_polarity_subjectivity_for_comments(sentiment_df)

    return adf, sentiment_df

adf, sentiment_df = load_data()

filter_flag=False
with st.sidebar:
    st.markdown("### Global Filters")

    # Ensure Created is datetime and extract .date() for Streamlit input
    adf['Created'] = pd.to_datetime(adf['Created'], errors='coerce')
    min_date = adf['Created'].min().date()
    max_date = adf['Created'].max().date()

    start = st.date_input("Start Date", value=min_date, min_value=min_date, max_value=max_date, key="start_date_time")
    end = st.date_input("End Date", value=max_date, min_value=min_date, max_value=max_date, key="end_date_time")

    department_options = ["All"] + sorted(adf['Relevant_Departments'].dropna().unique())
    department = st.selectbox("Department", options=department_options, key="department_filter_time")
    filter_flag=True

# Apply date and department filters
filtered_adf = adf[

    (adf['Created'].dt.date >= start) &
    (adf['Created'].dt.date <= end)
]

if department != "All":
    filtered_adf = filtered_adf[filtered_adf['Relevant_Departments'] == department]

# Filter sentiment_df using the same Created date range and department

sentiment_df['Created'] = pd.to_datetime(sentiment_df['Created'], errors='coerce')
filtered_sentiment_df = sentiment_df[

    (sentiment_df['Created'].dt.date >= start) &
    (sentiment_df['Created'].dt.date <= end)
]

if department != "All":
    filtered_sentiment_df = filtered_sentiment_df[
        filtered_sentiment_df['Relevant_Departments'] == department
    ]

#st.title("Time-Based Trends & Forecasts")

st.markdown("---")
st.subheader("Weekly Ticket Inflow vs. Outflow")
inflow_outflow_df = weekly_inflow_outflow(filtered_adf)
fig1 = px.line(inflow_outflow_df, x="Week", y=["Inflow", "Outflow"], markers=True)
st.plotly_chart(fig1, use_container_width=True)

st.markdown("---")
st.subheader(" Backlog Growth/Decay Over Time")
backlog_df = backlog_trend(filtered_adf)
fig2 = px.line(backlog_df, x="Week", y="Backlog", markers=True)
st.plotly_chart(fig2, use_container_width=True)

st.markdown("---")
st.subheader("% of Negative Comments Over Time")

neg_pct_df = percent_negative_comments_over_time(filtered_sentiment_df)
fig3 = px.line(neg_pct_df, x="Week", y="% Negative", markers=True)
st.plotly_chart(fig3, use_container_width=True)

# st.markdown("---")
# st.subheader(" % of Negative Comments Over Time")

# neg_pct_df = percent_negative_comments_over_time(filtered_sentiment_df)  # use filtered!
# fig3 = px.line(neg_pct_df, x="Week", y="% Negative", markers=True)
#
# fig3.update_layout(
#     title_x=0.5,
#     xaxis_title="Week",
#     yaxis_title="% Negative",
#     yaxis_range=[0, 100]
# )
#
# st.plotly_chart(fig3, use_container_width=True)

st.markdown("---")
st.subheader("Avg Resolution Time of Negative Tickets")
neg_res_df = negative_ticket_resolution_time_trend(filtered_adf, sentiment_df)
fig4 = px.line(neg_res_df, x="Week", y="Avg_Resolution_Negative_Tickets", markers=True)
st.plotly_chart(fig4, use_container_width=True)

st.markdown("---")
st.subheader("Escalated Tickets per Agent (High Priority)")
escalation_df = escalated_tickets_per_agent_trend(filtered_adf)
fig5 = px.bar(escalation_df, x="Week", y="Escalated_Ticket_Count", color="Assignee", barmode="group")
st.plotly_chart(fig5, use_container_width=True)

st.markdown("---")
st.subheader("Forecast: Ticket Volume")
forecast_tickets = forecast_weekly_ticket_volume(filtered_adf)
fig6 = px.line(forecast_tickets, x="Week", y=["observed", "forecast"], markers=True)
st.plotly_chart(fig6, use_container_width=True)

st.markdown("---")
st.subheader("Forecast: Avg Resolution Time")
forecast_resolution = forecast_weekly_resolution_time(filtered_adf)
fig7 = px.line(forecast_resolution, x="Week", y=["observed", "forecast"], markers=True)
st.plotly_chart(fig7, use_container_width=True)



# Download button
csv = filtered_adf.to_csv(index=False).encode('utf-8')
st.download_button(
    label="Download CSV",
    data=csv,
    file_name='filtered_data.csv',
    mime='text/csv'
)