import pandas as pd
import re
from textblob import TextBlob
from wordcloud import WordCloud

def clean_comment(text):
    if pd.isna(text) or not isinstance(text, str):
        return ""

    text = text.replace("nan", " ")
    text = re.sub(r'\S+@\S+', '', text)
    text = re.sub(r'https?://\S+', '', text)
    text = re.sub(r'<.*?>', '', text)
    text = re.sub(r'\d{2}/\d{2}/\d{4}', '', text)
    text = re.sub(r'\b\d{1,2}:\d{2}\s*(AM|PM|am|pm)?', '', text)
    text = re.sub(r'\[[A-Z]+-\d+\]', '', text)
    text = re.sub(r'thanks.*|regards.*|sincerely.*|best.*|cheers.*', '', text, flags=re.IGNORECASE)

    system_patterns = [
        r'This is an automated reminder.*',
        r'You are receiving this email.*',
        r'Ticket migrated.*',
        r'Powered by Jira.*',
        r'Begin forwarded message.*',
        r'DH changed the status.*',
        r'Ticket From - Partner Support.*?status of \*.*?\*'
    ]
    for pattern in system_patterns:
        text = re.sub(pattern, '', text, flags=re.IGNORECASE)

    text = re.sub(r'{[^}]+}', '', text)
    text = re.sub(r'\[.*?\|.*?\]', '', text)
    text = re.sub(r'[^\x00-\x7F]+', ' ', text)
    text = re.sub(r'[*_“”"–—]', '', text)
    text = re.sub(r'[-_]{2,}', ' ', text)
    text = re.sub(r'\s+', ' ', text)

    return text.strip()


def analyze_sentiment(text):
    blob = TextBlob(text)
    return blob.sentiment.polarity, blob.sentiment.subjectivity


def classify_sentiment(polarity):
    if polarity > 0.1:
        return 'Positive'
    elif polarity < -0.1:
        return 'Negative'
    else:
        return 'Neutral'


def generate_comment_sentiments(df):
    comment_cols = [col for col in df.columns if col.startswith("Comment")]
    filtered_df = df.dropna(subset=comment_cols, how='all').copy()
    filtered_df['Consumer_Comments'] = filtered_df[comment_cols].astype(str).agg(' '.join, axis=1).apply(clean_comment)
    return filtered_df


def generate_polarity_subjectivity_for_comments(df):
    df[['Polarity', 'Subjectivity']] = df['Consumer_Comments'].apply(lambda x: pd.Series(analyze_sentiment(x)))
    df['Sentiment_Label'] = df['Polarity'].apply(classify_sentiment)
    return df


def breakdown_of_sentiments(df):
    sentiment_counts = df['Sentiment_Label'].value_counts().to_dict()
    avg_polarity = df['Polarity'].mean()
    avg_subjectivity = df['Subjectivity'].mean()
    return sentiment_counts, avg_polarity, avg_subjectivity


def weekly_sentiments(df):
    df['Created'] = pd.to_datetime(df['Created'], errors='coerce')
    df = df.dropna(subset=['Created'])
    weekly_sentiment = df.set_index('Created').resample('W').agg({
        'Polarity': 'mean',
        'Sentiment_Label': lambda x: x.value_counts().to_dict()
    }).reset_index()
    return weekly_sentiment


def sentiment_by_dept(df):
    polarity_by_dept = df.groupby('Relevant_Departments')['Polarity'].mean().sort_values().reset_index()
    count_by_dept = df['Relevant_Departments'].value_counts().reset_index()
    return polarity_by_dept, count_by_dept


def top_k_negative_comments(df, k=10):
    negative_comments = df[df['Sentiment_Label'] == 'Negative']
    top_negatives = negative_comments.sort_values(by='Polarity').head(k)
    return top_negatives[['Created', 'Consumer_Comments', 'Polarity']]


def word_cloud_generation(df):
    neg_text = ' '.join(df['Consumer_Comments'].dropna().astype(str))
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate(neg_text)
    return wordcloud
