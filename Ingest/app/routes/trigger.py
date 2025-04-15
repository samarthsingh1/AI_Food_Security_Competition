from fastapi import APIRouter
from app.services.clickhouse_sink import insert_ticket

router = APIRouter()

@router.get("/test-insert")
async def test_insert():
    sample_data = {
        "Issue_key": "FOO-123",
        "Summary": "Example summary",
        "Issue_id": "1001",
        "Issue_Type": "Bug",
        "Status": "Open",
        "Priority": "High",
        "Resolution": None,
        "Assignee": "john.doe@example.com",
        "Reporter_Email": "alice@example.com",
        "Created": "2024-04-01T12:00:00Z",
        "Updated": "2024-04-02T12:00:00Z",
        "Resolved": None,
        "Region": "NA",
        "Relevant_Departments": "Support",
        "Request_Category": "Software",
        "Request_Type": "Bug",
        "Resolution_Action": "Pending",
        "Satisfaction_rating": 4,
        "Source": "Jira",
        "Time_to_resolution": None,
        "Work_category": "Engineering"
    }

    insert_ticket(sample_data)
    return {"status": "inserted"}
