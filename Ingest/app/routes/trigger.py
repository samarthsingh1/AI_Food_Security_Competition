# app/routes/trigger.py

from fastapi import APIRouter, Request
from app.services.kafka_producer import produce_ticket_event

router = APIRouter()

@router.post("/trigger")
async def trigger_event(request: Request):
    payload = await request.json()
    produce_ticket_event(payload)  # no need for `await` here, it's not async
    return {"status": "Event successfully pushed to Kafka"}
