from ollama import Client
import pandas as pd
import math
import re
from wordcloud import WordCloud
import streamlit as st
from textblob import TextBlob
from datetime import datetime, timedelta
import re
import pandas as pd
# import openai
# import nltk
# from nltk.tokenize import sent_tokenize
# import ssl
# import certifi
# ssl._create_default_https_context = ssl._create_unverified_context
from statsmodels.tsa.arima.model import ARIMA
import matplotlib.pyplot as plt
# Ensure the Punkt tokenizer is available for sentence splitting
# nltk.download('punkt_tab')

###CONSTANTS


USERNAME="samarthsingh"
USER_PATH = '/Users/{}/Downloads/'.format(USERNAME)

cols_for_df = {
    'Summary':'Summary',
    'Issue key':'Issue_key',
    'Issue id':'Issue_id',
    'Issue Type':'Issue_Type',
    'Status':'Status',
    'Project key':'Project_key',
    'Project name':'Project_name',
    'Priority':'Priority',
    'Resolution':'Resolution',
    'Assignee':'Assignee',
    'Reporter (Email)':'Reporter_Email',
    'Creator (Email)':'Creator_Email',
    'Created':'Created',
    'Updated':'Updated',
    'Last Viewed':'Last_Viewed',
    'Resolved':'Resolved',
    'Due date':'Due_date',
    'Description':'Description',
    'Partner Names':'Partner_Names',
    'Custom field (Cause of issue)':'Cause_of_issue',
    'Custom field (Record/Transaction ID)':'Record/Transaction_ID',
    'Custom field (Region)':'Region',
    'Custom field (Relevant Departments)':'Relevant_Departments',
    'Custom field (Relevant Departments).1':'Relevant_Departments.1',
    'Custom field (Request Category)':'Request_Category',
    'Custom field (Request Type)':'Request_Type',
    'Custom field (Request language)':'Request_language',
    'Custom field (Resolution Action)':'Resolution_Action',
    'Satisfaction rating':'Satisfaction_rating',
    'Custom field (Satisfaction date)':'Satisfaction_date',
    'Custom field (Source)':'Source',
    'Custom field (Time to first response)':'Time_to_first_response',
    'Custom field (Time to resolution)':'Time_to_resolution',
    'Custom field (Work category)':'Work_category',
    'Status Category':'Status_Category',
    'Status Category Changed':'Status_Category_Changed',
    'Custom field ([CHART] Date of First Response)':'Date_of_First_Response',
    'Comment':'Comment',
    'Comment.1':'Comment1',
    'Comment.2':'Comment2',
    'Comment.3':'Commen3',
    'Comment.4':'Comment4',
    'Comment.5':'Comment5',
    'Comment.6':'Comment6',
    'Comment.7':'Comment7',
    'Comment.8':'Comment8',
    'Comment.9':'Comment9',
    'Comment.10':'Comment10',
    'Comment.11':'Comment11',
    'Comment.12':'Comment12',
    'Comment.13':'Comment13',
    'Comment.14':'Comment14',
    'Comment.15':'Comment15',
    'Comment.16':'Comment16',
    'Comment.17':'Comment17',
    'Comment.18':'Comment18',
    'Comment.19':'Comment19',
    'Comment.20':'Comment20'
}
###GENERAL FUNCTIONS

def clean_comment(text):
    if pd.isna(text) or not isinstance(text, str):
        return ""

    # Normalize base noise
    text = text.replace("nan", " ")

    # Remove email addresses and URLs
    text = re.sub(r'\S+@\S+', '', text)
    text = re.sub(r'https?://\S+', '', text)

    # Remove HTML tags
    text = re.sub(r'<.*?>', '', text)

    # Remove dates, timestamps, and IDs
    text = re.sub(r'\d{2}/\d{2}/\d{4}', '', text)
    text = re.sub(r'\d{2}/[A-Za-z]{3}/\d{4}', '', text)
    text = re.sub(r'\b\d{1,2}:\d{2}\s*(AM|PM|am|pm)?', '', text)
    text = re.sub(r'\b[a-f0-9]{24}\b', '', text)

    # Remove tracking codes or Jira references
    text = re.sub(r'\[[A-Z]+-\d+\]', '', text)
    text = re.sub(r'\[IT-\d+\|?.*?\]', '', text)

    # Remove salutations and signatures
    text = re.sub(r'^(hi|hello|dear)\b.*?(?=\n)', '', text, flags=re.IGNORECASE | re.MULTILINE)
    text = re.sub(r'thanks.*|regards.*|sincerely.*|best.*|cheers.*', '', text, flags=re.IGNORECASE)

    # Remove system-generated templates
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

    # Remove markdown, unicode, and special formatting
    text = re.sub(r'{[^}]+}', '', text)
    text = re.sub(r'\[.*?\|.*?\]', '', text)
    text = re.sub(r'[^\x00-\x7F]+', ' ', text)
    text = re.sub(r'[*_“”"–—]', '', text)

    # Collapse excess newlines, spaces, dashes
    text = re.sub(r'[-_]{2,}', ' ', text)
    text = re.sub(r'\s+', ' ', text)

    return text.strip()

##Pre processing


def preprocessing(df):
    """

    :param df: This is the raw dataset
    :return: This is the analytical dataset ready for analytics
    """

    # Handling duplicate department columns
    df['Custom field (Relevant Departments).1'] = df['Custom field (Relevant Departments)'].fillna(
        df['Custom field (Relevant Departments).1'])

    # Renaming columns
    df.rename(columns=cols_for_df, inplace=True)

    return df


def preparing_adf(df):
    """

    :param df: This contains the santized dataset
    :return: We shall add the calculated columns for our analytics to the df
    """

    # adding resolution time
    df['Resolved_Timestamp'] = pd.to_datetime(df['Resolved'])
    df['Created_Timestamp'] = pd.to_datetime(df['Created'])
    df['Resolution_Time'] = df['Resolved_Timestamp'] - df['Created_Timestamp']

    return df

def generate_comment_sentiments(df):
    comment_cols = [col for col in df.columns if col.startswith("Comment")]
    null_comment_df=(df.dropna(subset=comment_cols,how='all'))
    null_comment_df['Consumer_Comments']=null_comment_df[comment_cols].astype(str).agg(' '.join, axis=1).apply(clean_comment)
    return null_comment_df
### AGENTIC AI FUNCTIONS
def generate_bullet_summary(comment: str) -> str:
    """
    Generate a bullet-point summary from a given Jira-style comment using LLaMA 3 via Ollama.

    Args:
        comment (str): Raw input text containing a consumer food bank complaint or Jira-style thread.

    Returns:
        str: Human-readable summary in bullet-point format.
    """
    client = Client()
    response = client.chat(
        model='llama3',
        messages=[
            {
                'role': 'user',
                'content': f'Summarize this and create bullet points for the pertinent details: ;;{comment}'
            }
        ]
    )
    return response['message']['content']

###





df=pd.read_csv(USER_PATH+'data_case2.xlsx - PSUP_Jira_Data_Email_Scrambled.csv')
df=(preprocessing(df))
adf=preparing_adf(df)
comment_df=generate_comment_sentiments(adf)
workload=comment_df.head(1)['Consumer_Comments'].apply(generate_bullet_summary)
(workload)


