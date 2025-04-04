import os
import json
import avro.schema
import avro.io
import io
from confluent_kafka import Consumer
from app.services.druid_sink import stream_to_druid

# Load Avro schema
SCHEMA_PATH = os.path.join(os.path.dirname(__file__), "../schemas/ticket.avsc")
with open(SCHEMA_PATH, "r") as f:
    schema = avro.schema.parse(f.read())

# Kafka Consumer configuration
consumer_config = {
    'bootstrap.servers': 'localhost:9092',
    'group.id': 'ticket-consumer-group',
    'auto.offset.reset': 'earliest'
}

# Create Kafka Consumer
consumer = Consumer(consumer_config)
consumer.subscribe(['ticket-ingest'])

print("✅ Kafka consumer started. Listening on topic: ticket-ingest")

try:
    while True:
        msg = consumer.poll(1.0)  # Poll every 1 second
        if msg is None:
            continue
        if msg.error():
            print(f"⚠️ Consumer error: {msg.error()}")
            continue

        # Deserialize Avro message
        bytes_reader = io.BytesIO(msg.value())
        decoder = avro.io.BinaryDecoder(bytes_reader)
        reader = avro.io.DatumReader(schema)
        decoded_msg = reader.read(decoder)
        stream_to_druid(decoded_msg)
        print(f"📥 Received ticket event:\n{json.dumps(decoded_msg, indent=2)}")

except KeyboardInterrupt:
    print("🛑 Consumer stopped manually")

finally:
    consumer.close()
