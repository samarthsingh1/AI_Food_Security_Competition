import os
from dotenv import load_dotenv

load_dotenv()

KAFKA_BROKER_URL = os.getenv("KAFKA_BROKER_URL", "localhost:9092")
KAFKA_TOPIC = os.getenv("KAFKA_TOPIC", "ticket-events")
SCHEMA_PATH = os.path.join(os.path.dirname(__file__), '..', 'schemas', 'ticket.avsc')
