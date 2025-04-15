from confluent_kafka import Consumer, KafkaException
from fastavro import parse_schema, schemaless_reader
import io
from app.schemas.ticket_schema import schema_dict
from clickhouse_driver import Client
import logging
from datetime import datetime


datetime_fields = [
    "Created", "Updated", "Last Viewed", "Resolved", "Due date",
    "Custom field (Satisfaction date)", "Status Category Changed",
    "Custom field ([CHART] Date of First Response)"
]


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Parse the Avro schema
parsed_schema = parse_schema(schema_dict)

# Initialize ClickHouse client
client = Client(host="localhost")




# Helper function to safely parse datetime

def safe_parse_datetime(dt_str):
    try:
        if dt_str:
            return pd.to_datetime(dt_str).to_pydatetime()
    except Exception:
        pass
    return datetime(1970, 1, 1)


def safe_str(val):
    return "" if val is None else val

def safe_float(val):
    return float(val) if val is not None else 0.0

def safe_datetime(val):
    try:
        return datetime.strptime(val, "%m/%d/%y %H:%M") if val else datetime(1970, 1, 1)
    except:
        return datetime(1970, 1, 1)

def insert_ticket():
    consumer_conf = {
        'bootstrap.servers': 'localhost:9092',
        'group.id': 'clickhouse-consumer-group',
        'auto.offset.reset': 'earliest',
        'enable.auto.commit': True,
        'session.timeout.ms': 10000,
        'heartbeat.interval.ms': 3000,
        'max.poll.interval.ms': 60000,
    }

    consumer = Consumer(consumer_conf)
    consumer.subscribe(['jira-issues-ingest'])

    logger.info("🚀 Kafka consumer started. Waiting for messages...")

    try:
        while True:
            msg = consumer.poll(1.0)
            if msg is None:
                continue
            if msg.error():
                raise KafkaException(msg.error())

            message_bytes = io.BytesIO(msg.value())
            decoded = schemaless_reader(message_bytes, parsed_schema)

            # #date time
            # decoded["Created"] = parse_datetime(decoded.get("Created"))
            # decoded["Updated"] = parse_datetime(decoded.get("Updated"))
            # decoded["Resolved"] = parse_datetime(decoded.get("Resolved"))
            # decoded["Due date"] = parse_datetime(decoded.get("Due date"))
            # decoded["Custom field (Satisfaction date)"] = parse_datetime(
            #     decoded.get("Custom field (Satisfaction date)"))
            # decoded["Status Category Changed"] = parse_datetime(decoded.get("Status Category Changed"))
            # decoded["Custom field ([CHART] Date of First Response)"] = parse_datetime(
            #     decoded.get("Custom field ([CHART] Date of First Response)"))

            print("🔍 Decoded message:", decoded)

            # Inside your loop
            client.execute(
                '''
                INSERT INTO jira_issues_raw (
                    Summary, `Issue key`, `Issue id`, `Issue Type`, Status,
                    `Project key`, `Project name`, Priority, Resolution, Assignee,
                    `Reporter (Email)`, `Creator (Email)`, Created, Updated,
                    `Last Viewed`, Resolved, `Due date`, Description, `Partner Names`,
                    `Custom field (Cause of issue)`, `Custom field (Record/Transaction ID)`,
                    `Custom field (Region)`, `Custom field (Relevant Departments)`,
                    `Custom field (Relevant Departments).1`, `Custom field (Request Category)`,
                    `Custom field (Request Type)`, `Custom field (Request language)`,
                    `Custom field (Resolution Action)`, `Satisfaction rating`,
                    `Custom field (Satisfaction date)`, `Custom field (Source)`,
                    `Custom field (Time to first response)`, `Custom field (Time to resolution)`,
                    `Custom field (Work category)`, `Status Category`, `Status Category Changed`,
                    `Custom field ([CHART] Date of First Response)`, Comment, `Comment.1`, `Comment.2`,
                    `Comment.3`, `Comment.4`, `Comment.5`, `Comment.6`, `Comment.7`, `Comment.8`,
                    `Comment.9`, `Comment.10`, `Comment.11`, `Comment.12`, `Comment.13`, `Comment.14`,
                    `Comment.15`, `Comment.16`, `Comment.17`, `Comment.18`, `Comment.19`, `Comment.20`
                )
                VALUES
                ''',
                [(
                    safe_str(decoded.get("Summary")),
                    safe_str(decoded.get("Issue key")),
                    decoded.get("Issue id", 0),  # int field
                    safe_str(decoded.get("Issue Type")),
                    safe_str(decoded.get("Status")),
                    safe_str(decoded.get("Project key")),
                    safe_str(decoded.get("Project name")),
                    safe_str(decoded.get("Priority")),
                    safe_str(decoded.get("Resolution")),
                    safe_str(decoded.get("Assignee")),
                    safe_str(decoded.get("Reporter (Email)")),
                    safe_str(decoded.get("Creator (Email)")),
                    safe_datetime(decoded.get("Created")),
                    safe_datetime(decoded.get("Updated")),
                    safe_datetime(decoded.get("Last Viewed")),
                    safe_datetime(decoded.get("Resolved")),
                    safe_datetime(decoded.get("Due date")),
                    safe_str(decoded.get("Description")),
                    safe_str(decoded.get("Partner Names")),
                    safe_str(decoded.get("Custom field (Cause of issue)")),
                    safe_str(decoded.get("Custom field (Record/Transaction ID)")),
                    safe_str(decoded.get("Custom field (Region)")),
                    safe_str(decoded.get("Custom field (Relevant Departments)")),
                    safe_str(decoded.get("Custom field (Relevant Departments).1")),
                    safe_str(decoded.get("Custom field (Request Category)")),
                    safe_str(decoded.get("Custom field (Request Type)")),
                    safe_str(decoded.get("Custom field (Request language)")),
                    safe_str(decoded.get("Custom field (Resolution Action)")),
                    safe_str(decoded.get("Satisfaction rating") or 0.0),
                    safe_parse_datetime(decoded.get("Custom field (Satisfaction date)")),
                    safe_str(decoded.get("Custom field (Source)")),
                    safe_str(decoded.get("Custom field (Time to first response)")),
                    safe_str(decoded.get("Custom field (Time to resolution)")),
                    safe_str(decoded.get("Custom field (Work category)")),
                    safe_str(decoded.get("Status Category")),
                    safe_parse_datetime(decoded.get("Status Category Changed")),
                    safe_parse_datetime(decoded.get("Custom field ([CHART] Date of First Response)")),
                    safe_str(decoded.get("Comment")),
                    safe_str(decoded.get("Comment.1")),
                    safe_str(decoded.get("Comment.2")),
                    safe_str(decoded.get("Comment.3")),
                    safe_str(decoded.get("Comment.4")),
                    safe_str(decoded.get("Comment.5")),
                    safe_str(decoded.get("Comment.6")),
                    safe_str(decoded.get("Comment.7")),
                    safe_str(decoded.get("Comment.8")),
                    safe_str(decoded.get("Comment.9")),
                    safe_str(decoded.get("Comment.10")),
                    safe_str(decoded.get("Comment.11")),
                    safe_str(decoded.get("Comment.12")),
                    safe_str(decoded.get("Comment.13")),
                    safe_str(decoded.get("Comment.14")),
                    safe_str(decoded.get("Comment.15")),
                    safe_str(decoded.get("Comment.16")),
                    safe_str(decoded.get("Comment.17")),
                    safe_str(decoded.get("Comment.18")),
                    safe_str(decoded.get("Comment.19")),
                    safe_str(decoded.get("Comment.20"))
                )]
            )

            logger.info("✅ Inserted row with Issue key: %s", decoded.get("Issue key"))
            logger.info("✅ Inserted message into ClickHouse")

    except KeyboardInterrupt:
        logger.info("🛑 Kafka consumer stopped by user.")
    finally:
        consumer.close()


if __name__ == "__main__":

    insert_ticket()
