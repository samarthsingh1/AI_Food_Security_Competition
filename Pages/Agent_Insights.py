
import streamlit as st
import pandas as pd
import plotly.express as px

from Modules.preprocessing import preprocessing, preparing_adf
from Modules.kpi_functions import assignnee_workload, top_performers
from Modules.forecasting import escalated_tickets_per_agent_trend
from Modules.sentiment_analysis import generate_comment_sentiments, generate_polarity_subjectivity_for_comments
from Modules.agent_insights import agentic_summary_pipeline

@st.cache_data
def load_data():
    raw = pd.read_csv("/Users/samarthsingh/Downloads/data_case2.xlsx - PSUP_Jira_Data_Email_Scrambled.csv")
    df = preprocessing(raw)
    adf = preparing_adf(df)
    return adf

adf = load_data()

# Agentic enrichment
comment_df = generate_comment_sentiments(adf)
sentiment_df = generate_polarity_subjectivity_for_comments(comment_df)
agentic_df = sentiment_df.copy()
agentic_df[['bullet_points', 'urgency', 'seriousness', 'priority']] = agentic_df.apply(agentic_summary_pipeline, axis=1)

# Title
st.title("🧑‍💻 Agent Insights")

# --- Workload Breakdown ---
st.markdown("### 📊 Assignee Workload")
workload = assignnee_workload(adf).reset_index()
workload.columns = ['index','Assignee', 'Tickets_Assigned']
fig1 = px.bar(workload, x="Assignee", y="Tickets_Assigned", title="Ticket Count by Assignee")
st.plotly_chart(fig1, use_container_width=True)

# --- Top Performers ---
st.markdown("### 🥇 Top Performing Agents")
top_agents = top_performers(adf)
st.dataframe(top_agents[['Assignee', 'Issue_key', 'Avg_Resolution_Days', 'Performance_Score']])

# --- Escalated Ticket Trend by Agent ---
st.markdown("### 🚨 Weekly Escalated Ticket Trend (High Priority)")
escalation_df = escalated_tickets_per_agent_trend(adf)
fig2 = px.line(
    escalation_df,
    x="Week",
    y="Escalated_Ticket_Count",
    color="Assignee",
    markers=True,
    title="Weekly High Priority Tickets per Agent"
)
st.plotly_chart(fig2, use_container_width=True)

# --- Agent Priority Insights ---
st.markdown("### 🔥 Agent Ticket Prioritization from Comments")
priority_counts = agentic_df.groupby(["Assignee", "priority"]).size().reset_index(name="Ticket Count")
fig3 = px.bar(priority_counts, x="Assignee", y="Ticket Count", color="priority", barmode="group")
st.plotly_chart(fig3, use_container_width=True)
