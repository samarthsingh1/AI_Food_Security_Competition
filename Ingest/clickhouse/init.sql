CREATE DATABASE IF NOT EXISTS ai_competition;

CREATE TABLE IF NOT EXISTS ai_competition.ticket_events (
    Issue_key String,
    Summary Nullable(String),
    Issue_id Nullable(String),
    Issue_Type Nullable(String),
    Status Nullable(String),
    Priority Nullable(String),
    Resolution Nullable(String),
    Assignee Nullable(String),
    Reporter_Email Nullable(String),
    Created Nullable(DateTime),
    Updated Nullable(DateTime),
    Resolved Nullable(DateTime),
    Region Nullable(String),
    Relevant_Departments Nullable(String),
    Request_Category Nullable(String),
    Request_Type Nullable(String),
    Resolution_Action Nullable(String),
    Satisfaction_rating Nullable(Int32),
    Source Nullable(String),
    Time_to_resolution Nullable(String),
    Work_category Nullable(String)
) ENGINE = MergeTree()
ORDER BY Issue_key;
