#
# import streamlit as st
# import pandas as pd
# import plotly.express as px
# import math
# from clickhouse_driver import Client
# from Modules.preprocessing import preprocessing, preparing_adf
# from Modules.kpi_functions import assignnee_workload, top_performers
# from Modules.forecasting import escalated_tickets_per_agent_trend
# from Modules.sentiment_analysis import generate_comment_sentiments, generate_polarity_subjectivity_for_comments
# from Modules.agent_insights import agentic_summary_pipeline
# # from Pages.Priority_and_Escalation import filtered_df
#
#
# @st.cache_data
# def load_data():
#     # raw = pd.read_csv("/Users/samarthsingh/Downloads/data_case2.xlsx - PSUP_Jira_Data_Email_Scrambled.csv")
#     client = Client(host="localhost")  # or use 'clickhouse' if running from inside Docker
#
#     # Run the query
#     query = "SELECT * FROM jira_issues_raw"
#     result = client.execute(query)
#
#     # Fetch column names from DESCRIBE TABLE
#     columns = [row[0] for row in client.execute("DESCRIBE TABLE jira_issues_raw")]
#
#     # Create pandas DataFrame
#     raw = pd.DataFrame(result, columns=columns)
#     df = preprocessing(raw)
#     adf = preparing_adf(df)
#     return adf
#
# adf = load_data()
#
# with st.sidebar:
#     st.markdown("### Global Filters")
#
#     # Ensure Created is datetime and extract .date() for Streamlit input
#     adf['Created'] = pd.to_datetime(adf['Created'], errors='coerce')
#     min_date = adf['Created'].min().date()
#     max_date = adf['Created'].max().date()
#
#     start = st.date_input("Start Date", value=min_date, min_value=min_date, max_value=max_date, key="start_date_agent")
#     end = st.date_input("End Date", value=max_date, min_value=min_date, max_value=max_date, key="end_date_agent")
#
#     department_options = ["All"] + sorted(adf['Relevant_Departments'].dropna().unique())
#     department = st.selectbox("Department", options=department_options, key="department_filter_agent")
#
# # Apply date and department filters
# filtered_adf = adf[
#
#     (adf['Created'].dt.date >= start) &
#     (adf['Created'].dt.date <= end)
# ]
#
# if department != "All":
#     filtered_adf = filtered_adf[filtered_adf['Relevant_Departments'] == department]
#
#
#
# # Agentic enrichment
# comment_df = generate_comment_sentiments(filtered_adf)
# sentiment_df = generate_polarity_subjectivity_for_comments(comment_df)
# agentic_df = sentiment_df.copy()
#
# agentic_df[['bullet_points', 'urgency', 'seriousness', 'priority']] = agentic_df.apply(agentic_summary_pipeline, axis=1)
#
# # Title
# st.title("Agent Insights")
# top_agents = top_performers(filtered_adf)
# # st.dataframe(top_agents[['Assignee', 'Issue_key', 'Avg_Resolution_Days', 'Performance_Score']])
#
# # Add derived columns
# top_agents['Performance_Score_Rounded'] = top_agents['Performance_Score'].apply(math.floor)
# top_agents['Avg_Resolution_Days_Rounded'] = top_agents['Avg_Resolution_Days'].apply(lambda x: round(x, 2))
#
# top_3 = top_agents.sort_values("Performance_Score", ascending=False).head(3)
# cols = st.columns(3)
#
# for i, (_, row) in enumerate(top_3.iterrows()):
#     score = math.floor(row['Performance_Score'])
#     issues = int(row['Issue_key'])
#     days = round(row['Avg_Resolution_Days'], 2)
#
#     with cols[i]:
#         st.markdown(f"""
#         <div style='text-align: center; line-height: 1.2;'>
#             <div style='font-size: 20px; font-weight: 600; margin-bottom: 2px;'>{row['Assignee']}</div>
#             <div style='font-size: 36px; font-weight: bold; margin-bottom: 4px;'>{score}</div>
#             <div style='color: #2ecc71; font-size: 14px;'>{issues} issues / {days} days</div>
#         </div>
#         """, unsafe_allow_html=True)
#
#
# # --- Workload Breakdown ---
# st.markdown("## Assignee Workload")
# workload = assignnee_workload(filtered_adf).reset_index()
# workload.columns = ['index','Assignee', 'Tickets_Assigned']
# fig1 = px.bar(workload, x="Assignee", y="Tickets_Assigned", title="Ticket Count by Assignee")
# st.plotly_chart(fig1, use_container_width=True)
#
# # --- Top Performers ---
#
# st.markdown("## Top Performing Agents")
#
# top_agents = top_performers(filtered_adf)
# # st.dataframe(top_agents[['Assignee', 'Issue_key', 'Avg_Resolution_Days', 'Performance_Score']])
#
# # Add derived columns
# top_agents['Performance_Score_Rounded'] = top_agents['Performance_Score'].apply(math.floor)
# top_agents['Avg_Resolution_Days_Rounded'] = top_agents['Avg_Resolution_Days'].apply(lambda x: round(x, 2))
#
#
# top_agents['Hover_Info'] = top_agents.apply(
#         lambda row: f"Performance Score: {row['Performance_Score_Rounded']}<br>"
#                     f"({row['Issue_key']} issues ÷ {row['Avg_Resolution_Days_Rounded']} days)", axis=1
#     )
#
# fig_score = px.bar(
#         top_agents.sort_values("Performance_Score_Rounded", ascending=False),
#         x="Assignee",
#         y="Performance_Score_Rounded",
#         title="Top Agents by Performance Score"
#     )
#
# fig_score.update_traces(
#         text=None,
#         hovertemplate='%{customdata[0]}<extra></extra>',
#         customdata=top_agents[['Hover_Info']].to_numpy()
#     )
#
# fig_score.update_layout(
#         title_x=0.5,
#         xaxis_title="Assignee",
#         yaxis_title="Performance Score"
#     )
#
# st.plotly_chart(fig_score, use_container_width=True)
#
# # top_3 = top_agents.sort_values("Performance_Score", ascending=False).head(3)
# # cols = st.columns(3)
# # for i, (_, row) in enumerate(top_3.iterrows()):
# #         cols[i].metric(
# #             label=f"{row['Assignee']}",
# #             value=f"{math.floor(row['Performance_Score'])}",
# #             delta=f"{int(row['Issue_key'])} issues / {round(row['Avg_Resolution_Days'], 2)} days"
# #         )
#
#
# # --- Escalated Ticket Trend by Agent ---
# st.markdown("## Weekly Escalated Ticket Trend (High Priority)")
# escalation_df = escalated_tickets_per_agent_trend(filtered_adf)
# fig2 = px.line(
#     escalation_df,
#     x="Week",
#     y="Escalated_Ticket_Count",
#     color="Assignee",
#     markers=True,
#     title="Weekly High Priority Tickets per Agent"
# )
# st.plotly_chart(fig2, use_container_width=True)
#
# # --- Agent Priority Insights ---
# st.markdown("## Agent Ticket Prioritization from Comments")
# priority_counts = agentic_df.groupby(["Assignee", "priority"]).size().reset_index(name="Ticket Count")
# fig3 = px.bar(priority_counts, x="Assignee", y="Ticket Count", color="priority", barmode="group")
# st.plotly_chart(fig3, use_container_width=True)
#
#
# # Download button
# csv = filtered_adf.to_csv(index=False).encode('utf-8')
# st.download_button(
#     label="Download CSV",
#     data=csv,
#     file_name='filtered_data.csv',
#     mime='text/csv'
# )


import streamlit as st
import pandas as pd
import plotly.express as px
import math
from clickhouse_driver import Client
from Modules.preprocessing import preprocessing, preparing_adf
from Modules.kpi_functions import assignnee_workload, top_performers
from Modules.forecasting import escalated_tickets_per_agent_trend
from Modules.sentiment_analysis import generate_comment_sentiments, generate_polarity_subjectivity_for_comments
from Modules.agent_insights import agentic_summary_pipeline

# Inject CSS styling
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
st.markdown("<h1 style='text-align: center;'>Agent Insights</h1>", unsafe_allow_html=True)

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
    st.markdown("### Global Filters")
    adf['Created'] = pd.to_datetime(adf['Created'], errors='coerce')
    min_date = adf['Created'].min().date()
    max_date = adf['Created'].max().date()
    start = st.date_input("Start Date", value=min_date, min_value=min_date, max_value=max_date, key="start_date_agent")
    end = st.date_input("End Date", value=max_date, min_value=min_date, max_value=max_date, key="end_date_agent")
    department_options = ["All"] + sorted(adf['Relevant_Departments'].dropna().unique())
    department = st.selectbox("Department", options=department_options, key="department_filter_agent")

filtered_adf = adf[
    (adf['Created'].dt.date >= start) &
    (adf['Created'].dt.date <= end)
]
if department != "All":
    filtered_adf = filtered_adf[filtered_adf['Relevant_Departments'] == department]

# --- KPI Scorecards (Agentic)
comment_df = generate_comment_sentiments(filtered_adf)
sentiment_df = generate_polarity_subjectivity_for_comments(comment_df)
agentic_df = sentiment_df.copy()
agentic_df[['bullet_points', 'urgency', 'seriousness', 'priority']] = agentic_df.apply(agentic_summary_pipeline, axis=1)

# st.markdown("""
#     <h1 style='text-align: center;'>Agent Insights</h1>
# """, unsafe_allow_html=True)

st.markdown("### Top Performing Agents")
top_agents = top_performers(filtered_adf)
top_agents['Performance_Score_Rounded'] = top_agents['Performance_Score'].apply(math.floor)
top_agents['Avg_Resolution_Days_Rounded'] = top_agents['Avg_Resolution_Days'].apply(lambda x: round(x, 2))
top_3 = top_agents.sort_values("Performance_Score", ascending=False).head(3)

kpi1, kpi2, kpi3 = st.columns(3)

for i, (_, row) in enumerate(top_3.iterrows()):
    score = math.floor(row['Performance_Score'])
    issues = int(row['Issue_key'])
    days = round(row['Avg_Resolution_Days'], 2)
    with [kpi1, kpi2, kpi3][i]:
        st.markdown(f"""
            <div style="background-color: #f9f9f9; padding: 20px 15px; border-radius: 12px; 
                        box-shadow: 0 2px 6px rgba(0,0,0,0.05); text-align: center;">
                <div style="color: #6c757d; font-size: 1rem;">{row['Assignee']}</div>
                <div style="font-size: 2rem; font-weight: 600;">{score}</div>
                <div style="color: #2ecc71; font-size: 14px;">{issues} issues / {days} days</div>
            </div>
        """, unsafe_allow_html=True)

# --- Assignee Workload ---
st.markdown("---")
st.markdown("### Assignee Workload")
workload = assignnee_workload(filtered_adf).reset_index()
workload.columns = ['index','Assignee', 'Tickets_Assigned']
fig1 = px.bar(workload, x="Assignee", y="Tickets_Assigned")
#fig1.update_layout(title_x=0.5)
st.plotly_chart(fig1, use_container_width=True)

# --- Top Performers Chart ---
st.markdown("---")
st.markdown("###  Top Performers Chart")
top_agents['Hover_Info'] = top_agents.apply(
        lambda row: f"Performance Score: {row['Performance_Score_Rounded']}<br>"
                    f"({row['Issue_key']} issues ÷ {row['Avg_Resolution_Days_Rounded']} days)", axis=1
    )
fig_score = px.bar(
        top_agents.sort_values("Performance_Score_Rounded", ascending=False),
        x="Assignee",
        y="Performance_Score_Rounded",
        #title="Top Agents by Performance Score"
    )
fig_score.update_traces(
        text=None,
        hovertemplate='%{customdata[0]}<extra></extra>',
        customdata=top_agents[['Hover_Info']].to_numpy()
    )
fig_score.update_layout(xaxis_title="Assignee", yaxis_title="Performance Score")
st.plotly_chart(fig_score, use_container_width=True)

# --- Weekly Escalation ---
st.markdown("---")
st.markdown("###  Weekly Escalated Ticket Trend (High Priority)")
escalation_df = escalated_tickets_per_agent_trend(filtered_adf)
fig2 = px.line(escalation_df, x="Week", y="Escalated_Ticket_Count", color="Assignee", markers=True)
#fig2.update_layout(title="Weekly High Priority Tickets per Agent", title_x=0.5)
st.plotly_chart(fig2, use_container_width=True)

# --- Priority Breakdown ---
st.markdown("---")
st.markdown("###  Agent Ticket Prioritization from Comments")
priority_counts = agentic_df.groupby(["Assignee", "priority"]).size().reset_index(name="Ticket Count")
fig3 = px.bar(priority_counts, x="Assignee", y="Ticket Count", color="priority", barmode="group")
st.plotly_chart(fig3, use_container_width=True)

# --- Download ---
csv = filtered_adf.to_csv(index=False).encode('utf-8')
st.download_button(
    label="Download CSV",
    data=csv,
    file_name='filtered_data.csv',
    mime='text/csv'
)
