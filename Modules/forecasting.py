import pandas as pd
from statsmodels.tsa.arima.model import ARIMA

def forecast_weekly_ticket_volume(adf, weeks_ahead=4):
    ts = adf[['Created_Timestamp']].dropna().copy()
    ts['Created_Timestamp'] = pd.to_datetime(ts['Created_Timestamp'])
    ts.set_index('Created_Timestamp', inplace=True)
    weekly_counts = ts.resample('W').size()

    model = ARIMA(weekly_counts, order=(1, 1, 1))
    fit = model.fit()
    forecast = fit.forecast(steps=weeks_ahead)

    combined = pd.concat([
        weekly_counts.rename('observed'),
        forecast.rename('forecast')
    ], axis=1)

    combined = combined.reset_index()
    combined.rename(columns={combined.columns[0]: 'Week'}, inplace=True)

    return combined


def forecast_weekly_resolution_time(adf, weeks_ahead=4):
    ts = adf[['Created_Timestamp', 'Resolution_Time']].dropna().copy()
    ts['Created_Timestamp'] = pd.to_datetime(ts['Created_Timestamp'])
    ts['Resolution_Days'] = ts['Resolution_Time'].dt.total_seconds() / (24 * 3600)

    weekly_avg = ts.groupby(pd.Grouper(key='Created_Timestamp', freq='W'))['Resolution_Days'].mean()

    model = ARIMA(weekly_avg, order=(1, 1, 1))
    fit = model.fit()
    forecast = fit.forecast(steps=weeks_ahead)

    combined = pd.concat([
        weekly_avg.rename('observed'),
        forecast.rename('forecast')
    ], axis=1)

    combined = combined.reset_index()
    combined.rename(columns={combined.columns[0]: 'Week'}, inplace=True)

    return combined


def backlog_trend(adf):
    df = adf[['Created_Timestamp', 'Resolved_Timestamp']].dropna(how='all').copy()
    df['Created_Week'] = pd.to_datetime(df['Created_Timestamp']).dt.to_period('W').dt.start_time
    df['Resolved_Week'] = pd.to_datetime(df['Resolved_Timestamp']).dt.to_period('W').dt.start_time

    created_weekly = df['Created_Week'].value_counts().sort_index().cumsum().rename('Cumulative_Created')
    resolved_weekly = df['Resolved_Week'].value_counts().sort_index().cumsum().rename('Cumulative_Resolved')

    backlog_df = pd.concat([created_weekly, resolved_weekly], axis=1).fillna(method='ffill').fillna(0)
    backlog_df['Backlog'] = backlog_df['Cumulative_Created'] - backlog_df['Cumulative_Resolved']
    backlog_df['Backlog_Change'] = backlog_df['Backlog'].diff().fillna(0)

    return backlog_df.reset_index().rename(columns={'index': 'Week'})


def weekly_inflow_outflow(adf):
    df = adf[['Created_Timestamp', 'Resolved_Timestamp']].dropna(how='all').copy()
    df['Created_Week'] = pd.to_datetime(df['Created_Timestamp']).dt.to_period('W').dt.start_time
    df['Resolved_Week'] = pd.to_datetime(df['Resolved_Timestamp']).dt.to_period('W').dt.start_time

    inflow = df['Created_Week'].value_counts().sort_index().rename('Inflow')
    outflow = df['Resolved_Week'].value_counts().sort_index().rename('Outflow')

    return pd.concat([inflow, outflow], axis=1).fillna(0).reset_index().rename(columns={'index': 'Week'})


def percent_negative_comments_over_time(sentiment_df):
    df = sentiment_df[['Created', 'Sentiment_Label']].copy()
    # df['Created'] = pd.to_datetime(df['Created'], errors='coerce')
    df = df.dropna(subset=['Created'])

    df['Week'] = df['Created'].dt.to_period('W').dt.start_time

    weekly_counts = df.groupby('Week').size().rename("Total_Comments")
    weekly_negatives = df[df['Sentiment_Label'] == 'Negative'].groupby('Week').size().rename("Negative_Comments")

    combined = pd.concat([weekly_counts, weekly_negatives], axis=1).fillna(0)
    combined['% Negative'] = (combined['Negative_Comments'] / combined['Total_Comments']) * 100

    return combined.reset_index()


def negative_ticket_resolution_time_trend(adf, sentiment_df):
    df = sentiment_df[sentiment_df['Sentiment_Label'] == 'Negative'].copy()
    df = df[['Issue_key', 'Created']].dropna()

    merged = pd.merge(df, adf[['Issue_key', 'Created_Timestamp', 'Resolution_Time']], on='Issue_key', how='inner')
    merged = merged.dropna(subset=['Created_Timestamp', 'Resolution_Time'])

    merged['Resolution_Days'] = merged['Resolution_Time'].dt.total_seconds() / (24 * 3600)
    merged['Week'] = merged['Created_Timestamp'].dt.to_period('W').dt.start_time

    result = (
        merged.groupby('Week')['Resolution_Days']
        .mean()
        .reset_index()
        .rename(columns={'Resolution_Days': 'Avg_Resolution_Negative_Tickets'})
    )

    return result


def escalated_tickets_per_agent_trend(adf):
    df = adf[(adf['Priority'].notna()) & (adf['Assignee'].notna())].copy()
    # df = adf[(adf['Priority'].str.lower() == 'high')]
    df['Week'] = df['Created_Timestamp'].dt.to_period('W').dt.start_time

    return (
        df.groupby(['Week', 'Assignee'])
        .size()
        .reset_index(name='Escalated_Ticket_Count')
    )
