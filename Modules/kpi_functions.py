import pandas as pd
import math


def ticket_breakdown(df):
    """Returns ticket count by status."""
    return df['Status'].value_counts().reset_index(name='Count').rename(columns={'index': 'Status'})


def total_tickets(df):
    """Returns total number of tickets."""
    return df['Status'].count()


def average_response_time(df):
    """Returns average response time in days (based on Created and Updated)."""
    valid_df = df[df['Created'].notna() & df['Updated'].notna()].copy()
    valid_df['Updated_Timestamp'] = pd.to_datetime(valid_df['Updated'])
    valid_df['Created_Timestamp'] = pd.to_datetime(valid_df['Created'])
    valid_df['Response_Time'] = valid_df['Updated_Timestamp'] - valid_df['Created_Timestamp']

    if not valid_df.empty:
        avg_seconds = valid_df['Response_Time'].mean().total_seconds()
        return math.ceil(avg_seconds / (24 * 3600))  # days
    return None


def col1_col2_breakdown(df, col1, col2):
    """Grouped count of values for two categorical columns."""
    df_valid = df[~(df[col1].isnull() & df[col2].isnull())].copy()
    df_valid[col1] = df_valid[col1].astype(str).str.strip()
    df_valid[col2] = df_valid[col2].astype(str).str.strip()

    return df_valid.groupby([col1, col2]).size().reset_index(name='Count')


def assignnee_workload(df):
    """Number of tickets assigned per user."""
    return df[df['Assignee'].notnull()]['Assignee'].value_counts().reset_index(name='Tickets_Assigned')


def top_performers(df):
    """
    Compute resolution efficiency per agent:
    - total completed tickets
    - avg resolution time
    - performance score (tickets / resolution days)
    """
    completed_df = df[df['Status'].isin(['Completed', 'Closed']) & df['Assignee'].notnull()].copy()
    grouped = (
        completed_df.groupby('Assignee')
        .agg({'Resolution_Time': 'mean', 'Issue_key': 'count'})
        .reset_index()
    )

    grouped['Avg_Resolution_Days'] = grouped['Resolution_Time'].dt.total_seconds() / (24 * 3600)
    grouped['Performance_Score'] = grouped['Issue_key'] / grouped['Avg_Resolution_Days']
    grouped.sort_values(by='Performance_Score', ascending=False, inplace=True)

    return grouped
