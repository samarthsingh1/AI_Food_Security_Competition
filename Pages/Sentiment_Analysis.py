import streamlit as st
import plotly.express as px
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from clickhouse_driver import Client
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


st.markdown("<h1 style='text-align: center;'>Sentiment Analysis</h1>", unsafe_allow_html=True)

import pandas as pd

@st.cache_data
def load_data():
    # df = pd.read_csv("/Users/samarthsingh/Downloads/data_case2.xlsx - PSUP_Jira_Data_Email_Scrambled.csv")
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
    return adf

adf = load_data()
filter_flag=False
with st.sidebar:
    st.markdown("### Global Filters")

    # Ensure Created is datetime and extract .date() for Streamlit input
    adf['Created'] = pd.to_datetime(adf['Created'], errors='coerce')
    min_date = adf['Created'].min().date()
    max_date = adf['Created'].max().date()

    start = st.date_input("Start Date", value=min_date, min_value=min_date, max_value=max_date, key="start_date_sent")
    end = st.date_input("End Date", value=max_date, min_value=min_date, max_value=max_date, key="end_date_sent")

    department_options = ["All"] + sorted(adf['Relevant_Departments'].dropna().unique())
    department = st.selectbox("Department", options=department_options, key="department_filter_sent")
    filter_flag=True
# Apply date and department filters
filtered_adf = adf[

    (adf['Created'].dt.date >= start) &
    (adf['Created'].dt.date <= end)
]

if department != "All":
    filtered_adf = filtered_adf[filtered_adf['Relevant_Departments'] == department]


# Sentiment Pipeline
if filter_flag:
    comment_df = generate_comment_sentiments(filtered_adf)
else:
    comment_df = generate_comment_sentiments(adf)


sentiment_df = generate_polarity_subjectivity_for_comments(comment_df)
sentiment_counts, avg_polarity, avg_subjectivity = breakdown_of_sentiments(sentiment_df)
weekly_df = weekly_sentiments(sentiment_df)
polarity_by_dept, dept_count = sentiment_by_dept(sentiment_df)
top_negatives = top_k_negative_comments(sentiment_df)
wordcloud = word_cloud_generation(comment_df)

# Dashboard Title
#st.title("Sentiment Analysis Dashboard")

# --- Sentiment Breakdown ---
st.markdown("###  Sentiment Distribution")
st.write(f"**Average Polarity:** {avg_polarity:.2f}")
st.write(f"**Average Subjectivity:** {avg_subjectivity:.2f}")
fig1 = px.pie(
    names=list(sentiment_counts.keys()),
    values=list(sentiment_counts.values()),
    hole=0.4
)
st.plotly_chart(fig1, use_container_width=True)

# # --- Weekly Sentiment Trend ---
# st.markdown("## Weekly Sentiment Trend")
# weekly_melt = weekly_df.explode('Sentiment_Label')
# weekly_chart = px.line(
#     weekly_df,
#     x="Created",
#     y="Polarity",
#     title="Average Weekly Polarity"
# )
# st.plotly_chart(weekly_chart, use_container_width=True)

# --- Prep Data ---
sentiment_df['Created'] = pd.to_datetime(sentiment_df['Created'])
sentiment_df['Week'] = sentiment_df['Created'].dt.to_period('W').dt.start_time

# Filter to Positive + Negative only
filtered_sent = sentiment_df[sentiment_df['Sentiment_Label'].isin(['Positive', 'Negative'])]

# Group by Week + Label for average polarity
weekly_sentiment = filtered_sent.groupby(['Week', 'Sentiment_Label'])['Polarity'].mean().reset_index()

# Group by Week for total comment volume
weekly_volume = sentiment_df.groupby('Week')['Polarity'].count().reset_index(name='Comment_Count')

# Separate data for lines
positive = weekly_sentiment[weekly_sentiment['Sentiment_Label'] == 'Positive']
negative = weekly_sentiment[weekly_sentiment['Sentiment_Label'] == 'Negative']

# --- Plot ---
fig = go.Figure()

# Bar chart for volume
fig.add_trace(go.Bar(
    x=weekly_volume['Week'],
    y=weekly_volume['Comment_Count'],
    name='Comment Volume',
    marker_color='lightgray',
    opacity=0.3,
    yaxis='y2'
))

# Positive sentiment line
fig.add_trace(go.Scatter(
    x=positive['Week'],
    y=positive['Polarity'],
    mode='lines+markers',
    name='Positive',
    line=dict(color='green', width=2)
))

# Negative sentiment line
fig.add_trace(go.Scatter(
    x=negative['Week'],
    y=negative['Polarity'],
    mode='lines+markers',
    name='Negative',
    line=dict(color='red', width=2)
))
st.markdown("### Weekly Sentiment Trend with Comment Volume")
# --- Layout ---
fig.update_layout(
    # title=" ",
    xaxis_title="Week",
    yaxis=dict(
        title="Polarity",
        range=[-1, 1],
        showgrid=True,
        zeroline=True
    ),
    yaxis2=dict(
        title="Comment Count",
        overlaying='y',
        side='right',
        showgrid=False
    ),
    legend=dict(
        orientation="h",  # horizontal layout
        yanchor="bottom",
        y=1.02,  # move above the plot
        xanchor="center",
        x=0.5,
        font=dict(size=12)
    ),
    # title_x=0.5,
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
)

# --- Streamlit Render ---
st.plotly_chart(fig, use_container_width=True)

# --- Department Polarity ---
st.markdown("### Department-wise Sentiment")
fig2 = px.bar(polarity_by_dept, x="Relevant_Departments", y="Polarity", color="Polarity")
st.plotly_chart(fig2, use_container_width=True)


import re

def clean_leading_ids(text):
    if isinstance(text, str):
        # Remove leading alphanumeric string followed by a semicolon (common ID pattern)
        text = re.sub(r'^[;:]?[a-fA-F0-9]{10,32}[;:]\s*', '', text)
        # Clean general hexadecimal or log-style fragments too
        text = re.sub(r'<[^>]*0x[a-fA-F0-9]+[^>]*>', '', text)
        text = text.replace("None", "").strip()
    return text

top_negatives['Consumer_Comments'] = top_negatives['Consumer_Comments'].apply(clean_leading_ids)
# --- Word Cloud ---
st.markdown("### Word Cloud of All Comments")
fig_wc, ax = plt.subplots(figsize=(10, 5))
ax.imshow(wordcloud, interpolation="bilinear")
ax.axis("off")
st.pyplot(fig_wc)

# --- Most Negative Comments ---
st.markdown("### Most Negative Comments")
# top_negatives.reset_index(inplace=True)
# st.dataframe(top_negatives[['Created', 'Consumer_Comments', 'Polarity']])
with st.expander(" View Full Table"):
     st.dataframe(top_negatives[['Created', 'Consumer_Comments', 'Polarity']].reset_index(), use_container_width=True)


# Download button
csv = filtered_adf.to_csv(index=False).encode('utf-8')
st.download_button(
    label="Download CSV",
    data=csv,
    file_name='filtered_data.csv',
    mime='text/csv'
)