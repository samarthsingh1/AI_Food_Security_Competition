import pandas as pd

# Column renaming map
cols_for_df = {
    'Summary': 'Summary',
    'Issue key': 'Issue_key',
    'Issue id': 'Issue_id',
    'Issue Type': 'Issue_Type',
    'Status': 'Status',
    'Project key': 'Project_key',
    'Project name': 'Project_name',
    'Priority': 'Priority',
    'Resolution': 'Resolution',
    'Assignee': 'Assignee',
    'Reporter (Email)': 'Reporter_Email',
    'Creator (Email)': 'Creator_Email',
    'Created': 'Created',
    'Updated': 'Updated',
    'Last Viewed': 'Last_Viewed',
    'Resolved': 'Resolved',
    'Due date': 'Due_date',
    'Description': 'Description',
    'Partner Names': 'Partner_Names',
    'Custom field (Cause of issue)': 'Cause_of_issue',
    'Custom field (Record/Transaction ID)': 'Record/Transaction_ID',
    'Custom field (Region)': 'Region',
    'Custom field (Relevant Departments)': 'Relevant_Departments',
    'Custom field (Relevant Departments).1': 'Relevant_Departments.1',
    'Custom field (Request Category)': 'Request_Category',
    'Custom field (Request Type)': 'Request_Type',
    'Custom field (Request language)': 'Request_language',
    'Custom field (Resolution Action)': 'Resolution_Action',
    'Satisfaction rating': 'Satisfaction_rating',
    'Custom field (Satisfaction date)': 'Satisfaction_date',
    'Custom field (Source)': 'Source',
    'Custom field (Time to first response)': 'Time_to_first_response',
    'Custom field (Time to resolution)': 'Time_to_resolution',
    'Custom field (Work category)': 'Work_category',
    'Status Category': 'Status_Category',
    'Status Category Changed': 'Status_Category_Changed',
    'Custom field ([CHART] Date of First Response)': 'Date_of_First_Response',
    'Comment': 'Comment',
    'Comment.1': 'Comment1',
    'Comment.2': 'Comment2',
    'Comment.3': 'Commen3',
    'Comment.4': 'Comment4',
    'Comment.5': 'Comment5',
    'Comment.6': 'Comment6',
    'Comment.7': 'Comment7',
    'Comment.8': 'Comment8',
    'Comment.9': 'Comment9',
    'Comment.10': 'Comment10',
    'Comment.11': 'Comment11',
    'Comment.12': 'Comment12',
    'Comment.13': 'Comment13',
    'Comment.14': 'Comment14',
    'Comment.15': 'Comment15',
    'Comment.16': 'Comment16',
    'Comment.17': 'Comment17',
    'Comment.18': 'Comment18',
    'Comment.19': 'Comment19',
    'Comment.20': 'Comment20'
}

def preprocessing(df):
    """
    Renames columns and fills missing department info.
    """
    df['Custom field (Relevant Departments).1'] = df['Custom field (Relevant Departments)'].fillna(
        df['Custom field (Relevant Departments).1']
    )
    df.rename(columns=cols_for_df, inplace=True)
    return df

def preparing_adf(df):
    """
    Adds Created_Timestamp, Resolved_Timestamp and Resolution_Time columns.
    """
    df['Resolved_Timestamp'] = pd.to_datetime(df['Resolved'], errors='coerce')
    df['Created_Timestamp'] = pd.to_datetime(df['Created'], errors='coerce')
    df['Resolution_Time'] = df['Resolved_Timestamp'] - df['Created_Timestamp']
    return df
