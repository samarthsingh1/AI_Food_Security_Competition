# app/services/kafka_producer.py

from confluent_kafka import Producer
import avro.schema
import avro.io
import io
import os
import json

SCHEMA_PATH = os.path.join(os.path.dirname(__file__), "../schemas/ticket.avsc")

with open(SCHEMA_PATH, "r") as f:
    schema = avro.schema.parse(f.read())

producer_config = {
    "bootstrap.servers": "localhost:9092"
}

producer = Producer(producer_config)

def produce_ticket_event(payload: dict):
    writer = avro.io.DatumWriter(schema)
    bytes_writer = io.BytesIO()
    encoder = avro.io.BinaryEncoder(bytes_writer)
    writer.write(payload, encoder)
    raw_bytes = bytes_writer.getvalue()

    producer.produce("ticket-ingest", value=raw_bytes)
    producer.flush()
