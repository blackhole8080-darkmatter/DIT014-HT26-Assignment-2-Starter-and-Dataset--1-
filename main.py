"""HarborFlow Assignment 2 starter entry point."""

from datetime import datetime
import os, csv, calendar, re
import data_access as da
import operations as op
import text_tools as ttools

# connecting the vessels data to the main with the handle list function
def handle_list_vessels():
    vessels, skipped = da.load_vessels("dataset/vessels")
    print(f"Registered HarborFlow vessels:")
    
    sorted_vessels = sorted(vessels, key=lambda vessel: vessel["name"].lower() )
    for vessel in sorted_vessels:
        print(f"- {vessel['name']} | IMO {vessel['imo']} | {vessel['capacity_teu']:,} TEU")
    print(f"Skipped vessel files: {skipped}")

def inspect_vessel():
    vessels, skipped = da.load_vessels("dataset/vessels")
    vessel_name = input("Vessel name: ").strip()
    selected_vessel = None
    
    for vessel in vessels:
        if vessel_name.lower() == vessel["name"].lower():
            selected_vessel = vessel
            break
    if selected_vessel is None:
        print("Vessel not found.")
        return
    while True:
        date_text = input("Reference date (YYYY-MM-DD): ")
        try:
            reference_date = datetime.strptime(date_text, "%Y-%m-%d").date()
            break
        except ValueError:
            print("Error - Date must use YYYY-MM-DD.") 
    
    port_calls = da.load_port_calls("dataset/port_calls.csv")
    upcoming_calls = []

    for call in port_calls:
        if call["vessel_id"] != selected_vessel["vessel_id"]:
            continue

        call_date = op.parse_date(call["arrival_date"])

        if call_date is None:
            print(f"Invalid date for port call {call['call_id']}. Skipping.")
            continue

        if call_date >= reference_date:
            upcoming_calls.append((call_date, call["call_id"], call))

    if not upcoming_calls:
        print("No upcoming port calls found.")
        return

    upcoming_calls.sort(key=lambda item: (item[0], item[1]))

    selected_call_date = upcoming_calls[0][0]
    selected_call = upcoming_calls[0][2]

    manifests = da.load_manifests("dataset/manifests")
    manifest = op.find_manifest(manifests, selected_call["call_id"])

    if manifest is None:
        print("Manifest unavailable.")
        return

    print(
        f"Manifest for {selected_vessel['name']} | "
        f"Call {selected_call['call_id']} | "
        f"{selected_call_date.strftime('%d %B %Y')}"
    )
    
    shipments = da.load_shipments("dataset/shipments")
    declared_count = 0
    missing_count = 0
    resolved_weight = 0.0
    for number, shipment_id in enumerate(manifest["shipment_ids"], start=1):
        shipment = op.find_shipment(shipments, shipment_id)
        if shipment is None:
            print(f"{number}. {shipment_id} | MISSING RECORD")
            missing_count += 1
        else:
            cargo_type = shipment.get("cargo_type", "NOT PROVIDED")
            weight = shipment["weight_kg"]
            print(f"{number}. {shipment_id} | {shipment['customer']} | {weight} kg | {cargo_type} ")
            
            resolved_weight += weight
        declared_count += 1
    print(f"Declared shipments: {declared_count}")
    print(f"Resolved weight: {resolved_weight:.2f} kg")
    print(f"Missing shipment records: {missing_count}")

def identify_priority_cargo():
    call_id = input("Port call ID: ").strip() 
    port_calls = da.load_port_calls("dataset/port_calls.csv")
    selected_call = None
    
    for call in port_calls:
        if call["call_id"].lower() == call_id.lower():
            selected_call = call
            break
    if selected_call is None: print("Port call not found."); return

    manifests = da.load_manifests("dataset/manifests")
    manifest = op.find_manifest(manifests, selected_call["call_id"])
    if manifest is None: print("Manifest unavailable."); return
    
    shipments = da.load_shipments("dataset/shipments")
    category_totals = { "CONTROLLED": 0, "COLD CHAIN": 0, "EXPEDITE": 0, "STANDARD": 0}
    
    for shipment_id in manifest["shipment_ids"]:
        shipment = op.find_shipment(shipments, shipment_id)
        
        if shipment is None: continue
        
        category, reason = op.classify_shipment(shipment)
        category_totals[category] += 1
        
        print(f"{shipment_id} | {category} | {reason}")
    
    print(f"Category totals: CONTROLLED={category_totals['CONTROLLED']}, COLD CHAIN={category_totals['COLD CHAIN']}, EXPEDITE={category_totals['EXPEDITE']}, STANDARD={category_totals['STANDARD']}")

def export_customer_profile():
    customer_name = input("Customer name: ").strip()
    shipments = da.load_shipments("dataset/shipments")
    customer_shipments = []
    
    for shipment in shipments:
        if shipment["customer"].lower() == customer_name.lower():
            customer_shipments.append(shipment)
    if len(customer_shipments) == 0:
        print("Customer not found.")
        return
    
    shipment_count = len(customer_shipments)
    
    total_weight = 0.0
    express_count = 0
    destinations = []
    
    for shipment in customer_shipments:
        total_weight += shipment["weight_kg"]
        
        if shipment["priority"] == "EXPRESS":
            express_count += 1
         
        if shipment["destination"] not in destinations:
            destinations.append(shipment["destination"])
    
    destinations.sort()
    new_row = [customer_name, str(shipment_count), f"{total_weight:.2f}", str(express_count), "|".join(destinations)]
    
    os.makedirs("exports", exist_ok=True)
    export_path = "exports/customer-profiles.csv"
    existing_rows = []
    
    if os.path.exists(export_path):
        with open(export_path, "r", encoding="utf-8") as file:
            existing_rows = list(csv.reader(file))
    output_rows = []
    
    if len(existing_rows) == 0:
        output_rows.append([
            "customer",
            "shipment_count",
            "total_weight_kg",
            "express_count",
            "destinations"
        ])
    else:
        output_rows.append(existing_rows[0])
        
        for row in existing_rows[1:]:
            if row and row[0].lower() == customer_name.lower():
                output_rows.append(new_row)
            else:
                output_rows.append(row)
    
    if not any(row and row[0].lower() == customer_name.lower() for row in output_rows[1:]):
        output_rows.append(new_row)

    with open(export_path, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerows(output_rows)

    print("Customer profile updated: exports/customer-profiles.csv")

def find_port_calls_by_month():
    while True:
        month_input = input("Month (1-12): ").strip()
        if not month_input.isdigit():
            print("Error - Enter a month from 1 to 12.")
            continue
        
        month = int(month_input)
        if month < 1 or month > 12:
            print("Error - Enter a month from 1 to 12.")
            continue
        break
    
    port_calls = da.load_port_calls("dataset/port_calls.csv")
    vessels, _ = da.load_vessels("dataset/vessels")
    
    matching_calls = []
    
    for call in port_calls:
        arrival_date = op.parse_date(call["arrival_date"])
        
        if arrival_date is None:
            print(f"Invalid date for port call {call['call_id']}. Skipping.")
            continue
        
        vessel_name = op.find_vessel_name(vessels, call["vessel_id"])
        if vessel_name is None:
            print(f"Unknown vessel ID for port call {call['call_id']}. Skipping.")
            continue
        if arrival_date.month == month:
            matching_calls.append({
                "arrival_date": arrival_date,
                "vessel_name": vessel_name,
                "port_code": call["port_code"],
                "call_id": call["call_id"]
                })
    matching_calls.sort(key=lambda call: (call["arrival_date"], call["vessel_name"]))
    if len(matching_calls) == 0:
        print("No port calls found.")
        return
    month_name = calendar.month_name[month]
    print(f"Port calls in {month_name}:")
    for call in matching_calls:
        date_text = call["arrival_date"].strftime("%d %B %Y")
        print(f"- {date_text} | {call['vessel_name']} | {call['port_code']} | {call['call_id']}")

def sanitize_incident_report():
    incidents = da.load_incidents("dataset/incidents")
    sorted_incidents = sorted(
        incidents, key=lambda incident: incident["title"].lower()
    )

    print("Incidents:")

    for index, incident in enumerate(sorted_incidents, start=1):
        print(f"{index}. {incident['title']}")

    while True:
        selection_input = input("Select incident number: ").strip()

        if not selection_input.isdigit():
            print("Error - Select a listed incident.")
            continue

        selection = int(selection_input)

        if selection < 1 or selection > len(sorted_incidents):
            print("Error - Select a listed incident.")
            continue

        break

    selected_incident = sorted_incidents[selection - 1]
    report_value = selected_incident["report"]

    # Use report text directly if "report" is not a valid file path.
    if os.path.isfile(report_value):
        with open(report_value, "r", encoding="utf-8") as file:
            report_text = file.read()
    else:
        report_text = report_value

    sanitized_text = re.sub(ttools.CONTAINER_PATTERN, "[CONTAINER]", report_text)
    sanitized_text = re.sub(ttools.SEAL_PATTERN, "[SEAL]", sanitized_text)
    sanitized_text = re.sub(ttools.EMAIL_PATTERN, "[EMAIL]", sanitized_text)

    os.makedirs("exports/sanitized", exist_ok=True)
    output_path = (
        f"exports/sanitized/"
        f"{selected_incident['incident_id']}-sanitized.txt"
    )

    with open(output_path, "w", encoding="utf-8") as file:
        file.write(sanitized_text)

    print("Incident sanitized:")
    print(sanitized_text)
    print(f"Sanitized report saved: {output_path}")

def analyze_stable_event_sequence(): 
    call_id = input("Port call ID: ").strip()
    port_calls = da.load_port_calls("dataset/port_calls.csv")
    
    selected_call = None
    for call in port_calls:
        if call["call_id"].lower() == call_id.lower():
            selected_call = call
            break
    if selected_call is None: print("Port call not found."); return
    
    manifests = da.load_manifests("dataset/manifests")
    manifest = op.find_manifest(manifests, selected_call["call_id"])
    if manifest is None: print("Manifest unavailable."); return
    
    event_codes = manifest["event_codes"]
    stable_sequence = ttools.find_longest_stable_sequence(event_codes)
    
    print(f"Longest stable sequence length: {len(stable_sequence)}")
    print(f"Sequence: {' -> '.join(stable_sequence)}")

def assess_weather_risk():
    vessel_name = input("Vessel name: ").strip()
    vessels, _ = da.load_vessels("dataset/vessels")
    selected_vessel = None
    
    for vessel in vessels:
        if vessel["name"].lower() == vessel_name.lower():
            selected_vessel = vessel
            break
    if selected_vessel is None: print("Vessel not found."); return
    while True:
        date_text = input("Reference date (YYYY-MM-DD): ")
        try:
            reference_date = datetime.strptime(date_text, "%Y-%m-%d").date()
            break
        except ValueError:
            print("Error - Date must use YYYY-MM-DD.")
    port_calls = da.load_port_calls("dataset/port_calls.csv")
    upcoming_calls = []
    
    for call in port_calls:
        if call["vessel_id"] != selected_vessel["vessel_id"]:
            continue
        arrival_date = op.parse_date(call["arrival_date"])
        if arrival_date is None:
            print(f"Invalid date for port call {call['call_id']}. Skipping.")
            continue
        if arrival_date >= reference_date:
            upcoming_calls.append({
                "call_id": call["call_id"],
                "port_code": call["port_code"],
                "arrival_date": arrival_date
            })
    upcoming_calls.sort(
            key=lambda call: (call["arrival_date"], call["call_id"])
        )
    if len(upcoming_calls) == 0: print("No upcoming port calls found."); return
    
    weather_rows = da.load_weather("dataset/weather.csv")
    forecast_lookup = {}
    for weather in weather_rows:
        forecast_date = op.parse_date(weather["date"])
        if forecast_date is None:
            print(f"Invalid date in weather data. Skipping.")
            continue
        key = (weather["port_code"], forecast_date)
        forecast_lookup[key] = weather
    
    for call in upcoming_calls:
        print(f"{selected_vessel['name']} | {call['port_code']} | {call['arrival_date'].strftime('%d %B %Y')}")

        forecast = forecast_lookup.get((call["port_code"], call["arrival_date"]))        
        if forecast is None: print("Forecast unavailable"); continue
        
        weather_values = op.parse_weather_numbers(forecast)
        if weather_values is None: print("Malformed weather forecast. Skipping."); continue 
        
        wind, waves, rain = weather_values
        print(f"Wind: {wind:.1f} km/h | Rain: {rain:.1f} mm | Waves: {waves:.1f} m")
        print(f"Recommendation: {op.build_weather_recommendations(wind, waves, rain)}")

def search_incident_reports():
    incidents = da.load_incidents("dataset/incidents")
    
    index, titles = ttools.load_or_build_incident_index(incidents)
    query = input("Search incident reports: ").strip()
    matches = ttools.search_incident_index(index, titles, query) or []
    print(f"Matches for '{query}':")
    
    for match in matches:
        print(f"- {match['incident_id']} | score {match['score']} | {match['title']}")

def main():
    """Run the HarborFlow Port Intelligence Console."""
    # TODO: implement the persistent menu and orchestrate the services.
    console_running = True
    while console_running:
        print("HARBORFLOW PORT INTELLIGENCE")
        print("1. List registered vessels")
        print("2. Inspect a vessel manifest")
        print("3. Identify priority cargo")
        print("4. Export a customer operations profile")
        print("5. Find port calls by month")
        print("6. Sanitize an incident report")
        print("7. Analyze the longest stable event sequence")
        print("8. Assess weather risk for upcoming calls")
        print("9. Search incident reports")
        print("10. Close console")
        service = input("Select service: ")
        try: 
            service = int(service)
        except ValueError:
            print("Error - Select a service from 1 to 10.")
            continue
        if service < 1 or service > 10:
            print("Error - Select a service from 1 to 10.")
            continue
        if service == 1:
            handle_list_vessels()
        elif service == 2:
            inspect_vessel()
        elif service == 3:
            identify_priority_cargo()
        elif service == 4:
            export_customer_profile()
        elif service == 5:
            find_port_calls_by_month()
        elif service == 6:
            sanitize_incident_report()
        elif service == 7:
            analyze_stable_event_sequence()
        elif service == 8:
            assess_weather_risk()
        elif service == 9:
            search_incident_reports()
        elif service == 10:
            print("Console closed. HarborFlow operational data remains safe.")
            console_running = False   

if __name__ == "__main__":
    main()