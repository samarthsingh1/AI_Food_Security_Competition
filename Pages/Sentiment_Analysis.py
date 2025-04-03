import streamlit as st
import plotly.express as px
import matplotlib.pyplot as plt

from Modules.preprocessing import preprocessing, preparing_adf
from Modules.sentiment_analysis import (
    generate_comment_sentiments,
    generate_polarity_subjectivity_for_comments,
    breakdown_of_sentiments,
    weekly_sentiments,
    sentiment_by_dept,
    top_k_negative_comments,
    word_cloud_generation
)

import pandas as pd

@st.cache_data
def load_data():
    df = pd.read_csv("/Users/samarthsingh/Downloads/data_case2.xlsx - PSUP_Jira_Data_Email_Scrambled.csv")
    df = preprocessing(df)
    adf = preparing_adf(df)
    return adf

adf = load_data()

# Sentiment Pipeline
comment_df = generate_comment_sentiments(adf)
sentiment_df = generate_polarity_subjectivity_for_comments(comment_df)
sentiment_counts, avg_polarity, avg_subjectivity = breakdown_of_sentiments(sentiment_df)
weekly_df = weekly_sentiments(sentiment_df)
polarity_by_dept, dept_count = sentiment_by_dept(sentiment_df)
top_negatives = top_k_negative_comments(sentiment_df)
wordcloud = word_cloud_generation(comment_df)

# Dashboard Title
st.title("💬 Sentiment Analysis Dashboard")

# --- Sentiment Breakdown ---
st.markdown("### 😄 Sentiment Distribution")
st.write(f"**Average Polarity:** {avg_polarity:.2f}")
st.write(f"**Average Subjectivity:** {avg_subjectivity:.2f}")
fig1 = px.pie(
    names=list(sentiment_counts.keys()),
    values=list(sentiment_counts.values()),
    hole=0.4
)
st.plotly_chart(fig1, use_container_width=True)

# --- Weekly Sentiment Trend ---
st.markdown("### 📆 Weekly Sentiment Trend")
weekly_melt = weekly_df.explode('Sentiment_Label')
weekly_chart = px.line(
    weekly_df,
    x="Created",
    y="Polarity",
    title="Average Weekly Polarity"
)
st.plotly_chart(weekly_chart, use_container_width=True)

# --- Department Polarity ---
st.markdown("### 🏢 Department-wise Sentiment")
fig2 = px.bar(polarity_by_dept, x="Relevant_Departments", y="Polarity", color="Polarity", title="Avg Polarity per Department")
st.plotly_chart(fig2, use_container_width=True)

# --- Word Cloud ---
st.markdown("### ☁️ Word Cloud of All Comments")
fig_wc, ax = plt.subplots(figsize=(10, 5))
ax.imshow(wordcloud, interpolation="bilinear")
ax.axis("off")
st.pyplot(fig_wc)

# --- Most Negative Comments ---
st.markdown("### 🚨 Most Negative Comments")
st.dataframe(top_negatives[['Created', 'Consumer_Comments', 'Polarity']])
