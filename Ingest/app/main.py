from fastapi import FastAPI
from app.routes import trigger, ticket

app = FastAPI(
    title="AI Food Security Competition - Ingestion API",
    description="FastAPI backend for producing Kafka events and routing to ClickHouse",
    version="1.0.0"
)

# Include the routes
app.include_router(trigger.router, prefix="/api", tags=["Trigger"])
app.include_router(ticket.router, prefix="/api", tags=["Ticket Ingestion"])

@app.get("/")
def root():
    return {"message": "Welcome to the AI Food Security Kafka Ingestion Service"}
