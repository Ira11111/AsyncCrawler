import os
import json

with open('conf.json', 'rb') as file:
    data = json.load(file)

START_URLS = data.get("START_URLS")
MAX_DEPTH = data.get("MAX_DEPTH")
OUTPUT_PATH = data.get("OUTPUT_PATH")
