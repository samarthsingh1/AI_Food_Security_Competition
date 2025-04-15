import os
from pydantic import BaseSettings

class Settings(BaseSettings):
    # Kafka settings
    kafka_bootstrap_servers: str = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
    kafka_topic: str = os.getenv("KAFKA_TOPIC", "ticket-events")
    schema_registry_url: str = os.getenv("SCHEMA_REGISTRY_URL", "http://localhost:8081")

    # Avro schema path
    schema_path: str = os.getenv(
        "SCHEMA_PATH",
        os.path.join(os.path.dirname(__file__), "../schemas/ticket.avsc")
    )

    # ClickHouse settings
    clickhouse_host: str = os.getenv("CLICKHOUSE_HOST", "localhost")
    clickhouse_port: int = int(os.getenv("CLICKHOUSE_PORT", "9000"))
    clickhouse_database: str = os.getenv("CLICKHOUSE_DATABASE", "ai_food")
    clickhouse_table: str = os.getenv("CLICKHOUSE_TABLE", "ticket_data")

settings = Settings()
