import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from textblob import TextBlob
from datetime import datetime

st.set_page_config(page_title="Ticket Analytics", layout="wide")

def load_data():
    USERNAME = "samarthsingh"
    USER_PATH = f"/Users/{USERNAME}/Downloads/"
    df = pd.read_csv(USER_PATH + "data_case2.xlsx - PSUP_Jira_Data_Email_Scrambled.csv")
    return df

df = load_data()
#################


# %%
# %pip install wordcloud

# %%
from textblob import TextBlob
import pandas as pd
import math
import re
from wordcloud import WordCloud
import streamlit as st
from datetime import datetime, timedelta

# %% md
# ticket status
# %%
##Pre processing
df['Custom field (Relevant Departments).1'] = df['Custom field (Relevant Departments)'].fillna(
    df['Custom field (Relevant Departments).1'])

total_tickets = df['Status'].count()
breakdown_of_tickets = df['Status'].value_counts()
breakdown_of_tickets
# %%

df['Resolved_Timestamp'] = pd.to_datetime(df['Resolved'])
df['Created_Timestamp'] = pd.to_datetime(df['Created'])
df['Resolution_Time'] = df['Resolved_Timestamp'] - df['Created_Timestamp']
# total_tickets_resolved

# %%
##AVERAGE RESPONSE TIME
df_average_response_time = df[df['Created'].notna() & df['Updated'].notna()]
df_average_response_time['Updated_Timestamp'] = pd.to_datetime(df_average_response_time['Updated'])
df_average_response_time['Created_Timestamp'] = pd.to_datetime(df_average_response_time['Created'])
df_average_response_time['Resolution_Time'] = df_average_response_time['Updated_Timestamp'] - df_average_response_time[
    'Created_Timestamp']
average_response_time = math.ceil(df_average_response_time['Resolution_Time'].mean().total_seconds() / (24 * 3600))

# %%
##Region wise tickets

df_region = df[~(df['Custom field (Region)'].isnull() & df['Custom field (Relevant Departments)'].isnull())]
df_region['Custom field (Region)'] = df_region['Custom field (Region)'].str.strip()
df_region['Custom field (Relevant Departments)'] = df_region['Custom field (Relevant Departments)'].str.strip()
region_count = df_region['Custom field (Region)'].value_counts()
# region_count.to_dict()
department_count = df_region['Custom field (Relevant Departments)'].value_counts()
# department_count.to_dict()
region_dept_count = (df_region
                     .groupby(['Custom field (Relevant Departments)', 'Custom field (Region)'])
                     .size()
                     )
# region_dept_count.to_dict()
# %%
# Tickets by request type and request category

##Region wise tickets

df_request_type = df[~(df['Custom field (Request Type)'].isnull() & df['Custom field (Request Category)'].isnull())]
df_region['Custom field (Request Type)'] = df_region['Custom field (Request Type)'].str.strip()
df_region['Custom field (Request Category)'] = df_region['Custom field (Request Category)'].str.strip()
request_type_count = df_region['Custom field (Request Type)'].value_counts()
# region_count.to_dict()
request_category_count = df_region['Custom field (Request Category)'].value_counts()
# department_count.to_dict()
request_type_category_type = (df_region
                              .groupby(['Custom field (Request Type)', 'Custom field (Request Category)'])
                              .size()
                              )
# region_dept_count.to_dict()
# %%
##workload division

workload_df = df[df['Assignee'].notnull()]
workload = workload_df['Assignee'].value_counts()
workload.to_dict()
# %%
# top performers
performer_df = df[df['Assignee'].notnull()]
performer_df = (performer_df[performer_df['Status'].isin(['Completed', 'Closed'])]
                .groupby(['Assignee'])
                .agg({'Resolution_Time': "mean", 'Issue key': "count"})
                .reset_index()
                )
# Convert timedelta to total days
performer_df['Avg_Resolution_Days'] = performer_df['Resolution_Time'].dt.total_seconds() / (24 * 3600)

# Compute custom performance score
performer_df['Performance_Score'] = performer_df['Issue key'] / performer_df['Avg_Resolution_Days']

# Sort by performance score (higher = better)
performer_df = performer_df.sort_values(by='Performance_Score', ascending=False)



# %%
# Define the sentiment function
def analyze_sentiment(text):
    blob = TextBlob(text)
    return blob.sentiment.polarity, blob.sentiment.subjectivity


def classify_sentiment(p):
    if p > 0.1:
        return 'Positive'
    elif p < -0.1:
        return 'Negative'
    else:
        return 'Neutral'


def clean_comment(text):
    if pd.isna(text) or not isinstance(text, str):
        return ""

    # Normalize base noise
    text = text.replace("nan", " ")

    # Remove links and email addresses
    text = re.sub(r'https?://\S+', '', text)
    text = re.sub(r'\S+@\S+', '', text)

    # Remove dates and timestamps
    text = re.sub(r'\d{2}/\d{2}/\d{4}', '', text)
    text = re.sub(r'\d{2}/[A-Za-z]{3}/\d{4}', '', text)
    text = re.sub(r'\d{2}/\d{2}/\d{4} \d{2}:\d{2};[A-Za-z0-9\-]+;', '', text)

    # Remove IDs and tracking codes
    text = re.sub(r'\b[a-f0-9]{24};?', '', text)
    text = re.sub(r'[A-Za-z0-9\-]+:[A-Za-z0-9\-]+;', '', text)
    text = re.sub(r'\bSO\d+\b', '', text)
    text = re.sub(r'\[[A-Z]+-\d+\]', '', text)
    text = re.sub(r'\[IT-\d+\|?.*?\]', '', text)

    # Remove system messages and repeated phrasing
    system_patterns = [
        r'This is an automated reminder.*',
        r'Ticket migrated.*',
        r'Customer has replied.*',
        r'DH changed the status.*',
        r'You are receiving this email.*',
        r'Powered by Jira.*',
        r'Sent from my iPhone.*',
        r'nan nan nan.*',
        r'}]},.*',
        r"Thank you for contacting.*?Food Bank",
        r"We just received your request.*?",
        r"Our hours of operation.*?",
        r"Customer Relations Capital Area Food Bank",
        r"Charity",
        r"Thank you,\s*CH",
        r"Begin forwarded message.*",
        r'Hello, We recently sent an update.*?',
        r'Ticket From - Partner Support.*?status of \*.*?\*'
    ]
    for pattern in system_patterns:
        text = re.sub(pattern, '', text, flags=re.IGNORECASE)

    # Remove formatting tags and markdown
    text = re.sub(r'{[^}]+}', '', text)
    text = re.sub(r'\[.*?\|.*?\]', '', text)
    text = re.sub(r'\[~accountid:[^\]]+\]', '', text)
    text = re.sub(r'\[\^.*?\]', '', text)
    text = re.sub(r'\[.*?\]', '', text)
    text = re.sub(r'!\S+\.\w+\|thumbnail!', '', text)
    text = re.sub(r'[^\x00-\x7F]+', ' ', text)
    text = re.sub(r'[*_`“”"]', '', text)

    # Remove leftover HTML/JSON structures
    text = re.sub(r'\{"type":"text","text":".*?"\}', '', text)
    text = re.sub(r'"\s*attrs\s*":\s*}', '', text)

    # Special Jira headers
    text = re.sub(r'h6\. Message originally posted.*?(?=[A-Z]|$)', '', text)
    text = re.sub(r'"Ticket From - Partner Support.*?status of.*?--+', '', text)

    # Final cleanup
    text = re.sub(r'\s+', ' ', text).strip()

    return text


# %%
##Sentiment analysis on comments

comment_cols = [col for col in df.columns if col.startswith("Comment")]
null_comment_df = (df.dropna(subset=comment_cols, how='all'))
null_comment_df['Consumer_Comments'] = null_comment_df[comment_cols].astype(str).agg(' '.join, axis=1).apply(
    clean_comment)
null_comment_df
# %%
null_comment_df[['Polarity', 'Subjectivity']] = null_comment_df['Consumer_Comments'].apply(
    lambda x: pd.Series(analyze_sentiment(x))
)
null_comment_df['Sentiment_Label'] = null_comment_df['Polarity'].apply(classify_sentiment)
null_comment_df

# %%
##Sentiment comment breakdown

# Total comments
total_comments = null_comment_df.shape[0]

# Sentiment label distribution
sentiment_counts = null_comment_df['Sentiment_Label'].value_counts().to_dict()

# Polarity/subjectivity averages
avg_polarity = null_comment_df['Polarity'].mean()
avg_subjectivity = null_comment_df['Subjectivity'].mean()
print(total_comments, sentiment_counts, avg_polarity, avg_subjectivity)


# %%
null_comment_df['Created'] = pd.to_datetime(df['Created'], errors='coerce')
null_comment_df = null_comment_df.dropna(subset=['Created'])

# Weekly sentiment trend
weekly_sentiment = null_comment_df.set_index('Created').resample('W').agg({
    'Polarity': 'mean',
    'Sentiment_Label': lambda x: x.value_counts().to_dict()
}).reset_index()
weekly_sentiment
# %%
###Sentiment Anlaysis by department

# Avg polarity per department
polarity_by_dept = null_comment_df.groupby('Custom field (Relevant Departments)')['Polarity'].mean().sort_values()

# Count of comments per department
count_by_dept = null_comment_df['Custom field (Relevant Departments)'].value_counts()


# %%
##most negative comments

negative_comments = null_comment_df[null_comment_df['Sentiment_Label'] == 'Negative']

# Sort by polarity (most negative first)
top_negatives = negative_comments.sort_values(by='Polarity').head(10)

top_negatives[['Created', 'Consumer_Comments', 'Polarity']]

# %%
##wordcloud
# Generate from negative comments
neg_text = ' '.join(negative_comments['Consumer_Comments'].dropna().astype(str))

wordcloud = WordCloud(width=800, height=400, background_color='white').generate(neg_text)



#####################
pages = ["📊 Ticket KPIs", "💬 Sentiment Analysis", "☁️ Word Cloud"]
selection = st.sidebar.radio("Navigation", pages)


if selection == "📊 Ticket KPIs":
    st.title("📊 Ticket Dashboard")

    col1, col2 = st.columns(2)

    # --- Breakdown of Tickets ---
    with col1:
        st.subheader("Ticket Status Breakdown")
        status_counts = df['Status'].value_counts()
        fig1, ax1 = plt.subplots()
        ax1.pie(status_counts, labels=status_counts.index, autopct='%1.1f%%')
        ax1.axis("equal")
        st.pyplot(fig1)

    # --- Average Response Time ---
    with col2:
        st.metric("Average Response Time", f"{average_response_time} days")

    st.markdown("---")

    # --- Region & Department Breakdown with Drilldown ---
    st.subheader("🎯 Region & Department Ticket Breakdown")
    drill_option = st.selectbox("View by", ["Both", "Region Only", "Department Only"])

    if drill_option == "Both":
        st.dataframe(region_dept_count.reset_index(name="Ticket Count"))
    elif drill_option == "Region Only":
        st.bar_chart(region_count)
    else:
        st.bar_chart(department_count)

    # --- Request Type & Category with Drilldown ---
    st.subheader("🧾 Request Type & Category Breakdown")
    req_option = st.selectbox("Request View", ["Both", "Type Only", "Category Only"])

    if req_option == "Both":
        st.dataframe(request_type_category_type.reset_index(name="Ticket Count"))
    elif req_option == "Type Only":
        st.bar_chart(request_type_count)
    else:
        st.bar_chart(request_category_count)

    # --- Workload by Assignee ---
    st.subheader("👤 Workload by Assignee")
    st.bar_chart(workload)

    # --- Top Performers ---
    st.subheader("🏆 Top 20 Performers")
    st.dataframe(performer_df.head(20))

elif selection == "💬 Sentiment Analysis":
    st.title("💬 Sentiment Dashboard")

    # --- Sentiment Pie ---
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Sentiment Distribution")
        fig2, ax2 = plt.subplots()
        ax2.pie(sentiment_counts.values(), labels=sentiment_counts.keys(), autopct='%1.1f%%')
        ax2.axis("equal")
        st.pyplot(fig2)

    with col2:
        st.metric("Total Comments Analyzed", total_comments)

    st.markdown("---")

    # --- Weekly Sentiment Trend ---
    st.subheader("📅 Weekly Sentiment Trend")
    st.line_chart(weekly_sentiment.set_index('Created')['Polarity'])

    # --- Polarity by Department ---
    st.subheader("🏢 Average Polarity by Department")
    st.bar_chart(polarity_by_dept)

    # --- Most Negative Comments ---
    st.subheader("❗ Top 20 Most Negative Comments")
    st.dataframe(top_negatives[['Created', 'Consumer_Comments', 'Polarity']])

elif selection == "☁️ Word Cloud":
    st.title("☁️ Word Cloud - Negative Comments")
    neg_text = ' '.join(negative_comments['Consumer_Comments'].dropna())

    wordcloud = WordCloud(width=800, height=400, background_color='white').generate(neg_text)

    fig3, ax3 = plt.subplots(figsize=(10, 5))
    ax3.imshow(wordcloud, interpolation='bilinear')
    ax3.axis("off")
    st.pyplot(fig3)



