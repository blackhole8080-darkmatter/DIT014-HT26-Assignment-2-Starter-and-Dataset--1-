import json
from pathlib import Path
import csv
from text_tools import normalize_words
"""File loading and path-handling functions for HarborFlow.

Create reusable JSON and CSV loaders here. Do not hard-code sample records.
"""
def load_json(path):
    with open(path, "r", encoding="utf-8") as file:
        loaded_json = json.load(file)
        return loaded_json

def load_vessels(directory):
    registered_vessels = []
    skipped_vessels = 0
    
    for path in Path(directory).iterdir():
        if path.suffix == ".json":
            vessel = load_json(path)
            if isinstance(vessel, dict) and "vessel_id" in vessel and "name" in vessel and "imo" in vessel and "capacity_teu" in vessel:
                registered_vessels.append(vessel)
            else:
                skipped_vessels += 1
    return registered_vessels, skipped_vessels

def load_port_calls(path):
    port_calls = []
    with open(path, "r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)
        for row in reader:
            port_calls.append(row)
    return port_calls

def load_manifests(directory):
    manifests = []
    for path in Path(directory).iterdir():
        if path.suffix == ".json":
            manifest = load_json(path)
            manifests.append(manifest)
    return manifests

def load_shipments(directory):
    shipments = []
    for path in Path(directory).iterdir():
        if path.suffix == ".json":
            shipment = load_json(path)
            
            if isinstance(shipment, dict) and "shipment_id" in shipment:
                shipments.append(shipment)
    return shipments

def load_incidents(directory):
    incidents = []
    for path in Path(directory).iterdir():
        if path.suffix == ".json":
            incident = load_json(path)
            
            if isinstance(incident, dict) and "incident_id" in incident:
                incidents.append(incident)
    return incidents

def load_weather(path):
    weather_rows = []
    with open(path, "r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)
        for row in reader:
            weather_rows.append(row)
    return weather_rows
              
if __name__ == "__main__":
    registered_vessels, skipped_vessels = load_vessels(Path("dataset/vessels"))
    print(registered_vessels, skipped_vessels)
    port_calls = load_port_calls(Path("dataset/port_calls.csv"))
    print(port_calls)

