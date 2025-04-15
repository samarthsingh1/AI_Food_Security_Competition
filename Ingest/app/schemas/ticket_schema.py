import json
import os

# Get the absolute path to ticket.avsc
avsc_file = os.path.join(os.path.dirname(__file__), "ticket.avsc")

with open(avsc_file, "r") as f:
    schema_dict = json.load(f)
