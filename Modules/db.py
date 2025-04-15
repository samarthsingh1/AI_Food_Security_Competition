# Modules/db.py

from clickhouse_driver import Client
import pandas as pd

def fetch_clickhouse_data(query: str) -> pd.DataFrame:
    client = Client(host="localhost")  # adjust if needed
    result = client.execute(query)
    columns = [desc[0] for desc in client.execute("DESCRIBE TABLE default.tickets")]
    return pd.DataFrame(result, columns=columns)


query = "SELECT * FROM default.tickets"
raw = fetch_clickhouse_data(query)
print(raw)