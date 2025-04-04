import json
import requests

DRUID_STREAM_URL = "http://localhost:8888/druid/indexer/v1/firehose"  # 🔁 Update if different

def stream_to_druid(data: dict):
    """
    Send a ticket record to Apache Druid via HTTP Firehose.
    """
    headers = {"Content-Type": "application/json"}
    try:
        response = requests.post(DRUID_STREAM_URL, data=json.dumps(data), headers=headers)
        if response.status_code == 200:
            print("✅ Successfully streamed to Druid")
        else:
            print(f"⚠️ Failed to stream to Druid: {response.status_code} | {response.text}")
    except Exception as e:
        print(f"❌ Error streaming to Druid: {e}")
