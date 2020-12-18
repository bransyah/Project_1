import base64
from datetime import datetime
from google.cloud import datastore
import jwt
import ssl
import time
import paho.mqtt.client as mqtt
# Project ID
PROJECT_ID = "hsc2020-04"


def save_temperature(event, context):
    # Process is there is a data field
    # Extract data from event object (a dictionary)
        # To accommodate binary types, Data is encoded in a base 64 format, need to convert it
        temp = base64.b64decode(event['data']).decode('utf-8')
        humi = base64.b64decode(event['data']).decode('utf-8')

        # Create a client to access the datastore
        client = datastore.Client(project=PROJECT_ID)

        # Create a new key to store a new entity
        newKey = client.key("bacaan")

        # Create a new entity
        newEntity = datastore.Entity(newKey)

        # Fill in its data
        newEntity.update({
            "created": datetime.now(),
            "0": temp,
            "1": humi,
        })

        # Store it
        client.put(newEntity)

        print("Writing completed...")
    else:
        # Ignore if there is no data
        print("No data")


