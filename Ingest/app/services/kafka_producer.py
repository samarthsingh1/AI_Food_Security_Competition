import pandas as pd
from confluent_kafka import Producer
import avro.schema
import avro.io
import io
import os
import json

# ---------------------------------------
# Load Avro schema
# ---------------------------------------
SCHEMA_PATH = "app/schemas/ticket.avsc"  # update path if needed
with open(SCHEMA_PATH, "r") as f:
    schema = avro.schema.parse(f.read())


# ---------------------------------------
# Kafka Producer Config
# ---------------------------------------
producer = Producer({'bootstrap.servers': 'localhost:9092'})

def send_row_to_kafka(row: dict):
    writer = avro.io.DatumWriter(schema)
    bytes_writer = io.BytesIO()
    encoder = avro.io.BinaryEncoder(bytes_writer)
    writer.write(row, encoder)
    raw_bytes = bytes_writer.getvalue()
    producer.produce("jira-issues-ingest", value=raw_bytes)
    producer.flush()
    print("✅ Message sent to Kafka")


# ---------------------------------------
# Load CSV and send to Kafka
# ---------------------------------------
def produce_from_csv(csv_path: str):
    df = pd.read_csv("/Users/samarthsingh/Downloads/data_case2.xlsx - PSUP_Jira_Data_Email_Scrambled.csv")

    print(f"🚀 Sending {len(df)} rows to Kafka...")

    for i, row in df.iterrows():
        try:
            # Replace NaNs with None and convert to dict
            clean_row = row.where(pd.notnull(row), None).to_dict()
            send_row_to_kafka(clean_row)
            print(f"✅ Sent row {i + 1}")
        except Exception as e:
            print(f"❌ Failed to send row {i + 1}: {e}")

    print("🎉 All rows processed.")

# ---------------------------------------
# Run it
# ---------------------------------------
if __name__ == "__main__":
    CSV_PATH = "path/to/your_file.csv"  # UPDATE this to your actual CSV path
    produce_from_csv(CSV_PATH)
