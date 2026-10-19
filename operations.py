"""HarborFlow operational business rules.

Keep calculations and record-processing logic separate from user interaction
where practical.
"""
from datetime import datetime

# Finding a shipment given a shipment_id in multiple manifests  
def find_shipment(shipments, shipment_id):
    for shipment in shipments:
        if shipment["shipment_id"] == shipment_id:
            return shipment
    return None
# Finding a manifest given a call_id in multiple manifests  
def find_manifest(manifests, call_id):
    for manifest in manifests:
        if manifest["call_id"] == call_id:
            return manifest
    return None   

def classify_shipment(shipment):
    hazardous = shipment.get("hazardous", False)
    temperature_controlled = shipment.get("temperature_controlled", False)
    
    if hazardous: 
        return "CONTROLLED", "hazardous cargo"
    if temperature_controlled: 
        return "COLD CHAIN", "temperature-controlled cargo"
    if shipment["priority"] == "EXPRESS" or shipment["weight_kg"] >= 5000:
        return "EXPEDITE", "express service"
    
    return "STANDARD", "standard handling"

def parse_date(date_text):
    try:
        return datetime.strptime(date_text, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return None

def find_vessel_name(vessels, vessel_id):
    for vessel in vessels:
        if vessel["vessel_id"] == vessel_id:
            return vessel["name"]
    return None 

def parse_weather_numbers(weather):
    try:
        wind = float(weather["wind_kmh"])
        waves = float(weather["wave_height_m"])
        rain = float(weather["precipitation_mm"])
    except (KeyError, TypeError, ValueError):
        return None
    return wind, waves, rain

def build_weather_recommendations(wind, waves, rain):
    recommendations = []
    
    if wind >= 45:
        recommendations.append("Suspend crane operations.")
    if waves >= 2.5:
        recommendations.append("Arrange tug assistance.")
    if rain >= 8 and wind < 45:
        recommendations.append("Prepare covered handling.")
    if len(recommendations) == 0:
        recommendations.append("Normal operating plan.")
    
    return " ".join(recommendations)
    
