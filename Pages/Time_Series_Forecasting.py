import streamlit as st
import plotly.express as px
import pandas as pd

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

# Load & prepare data (adjust path if needed)
@st.cache_data
def load_data():
    df = pd.read_csv("/Users/samarthsingh/Downloads/data_case2.xlsx - PSUP_Jira_Data_Email_Scrambled.csv")
    df = preprocessing(df)
    adf = preparing_adf(df)
    sentiment_df = generate_comment_sentiments(adf)
    sentiment_df = generate_polarity_subjectivity_for_comments(sentiment_df)
    return adf, sentiment_df

adf, sentiment_df = load_data()

st.title("📊 Time-Based Trends & Forecasts")

st.markdown("---")
st.subheader("📈 Weekly Ticket Inflow vs. Outflow")
inflow_outflow_df = weekly_inflow_outflow(adf)
fig1 = px.line(inflow_outflow_df, x="Week", y=["Inflow", "Outflow"], markers=True)
st.plotly_chart(fig1, use_container_width=True)

st.markdown("---")
st.subheader("📉 Backlog Growth/Decay Over Time")
backlog_df = backlog_trend(adf)
fig2 = px.line(backlog_df, x="Week", y="Backlog", markers=True)
st.plotly_chart(fig2, use_container_width=True)

st.markdown("---")
st.subheader("🚨 % of Negative Comments Over Time")
neg_pct_df = percent_negative_comments_over_time(sentiment_df)
fig3 = px.line(neg_pct_df, x="Week", y="% Negative", markers=True)
st.plotly_chart(fig3, use_container_width=True)

st.markdown("---")
st.subheader("🕒 Avg Resolution Time of Negative Tickets")
neg_res_df = negative_ticket_resolution_time_trend(adf, sentiment_df)
fig4 = px.line(neg_res_df, x="Week", y="Avg_Resolution_Negative_Tickets", markers=True)
st.plotly_chart(fig4, use_container_width=True)

st.markdown("---")
st.subheader("📍 Escalated Tickets per Agent (High Priority)")
escalation_df = escalated_tickets_per_agent_trend(adf)
fig5 = px.bar(escalation_df, x="Week", y="Escalated_Ticket_Count", color="Assignee", barmode="group")
st.plotly_chart(fig5, use_container_width=True)

st.markdown("---")
st.subheader("📅 Forecast: Ticket Volume")
forecast_tickets = forecast_weekly_ticket_volume(adf)
fig6 = px.line(forecast_tickets, x="Week", y=["observed", "forecast"], markers=True)
st.plotly_chart(fig6, use_container_width=True)

st.markdown("---")
st.subheader("⏳ Forecast: Avg Resolution Time")
forecast_resolution = forecast_weekly_resolution_time(adf)
fig7 = px.line(forecast_resolution, x="Week", y=["observed", "forecast"], markers=True)
st.plotly_chart(fig7, use_container_width=True)
