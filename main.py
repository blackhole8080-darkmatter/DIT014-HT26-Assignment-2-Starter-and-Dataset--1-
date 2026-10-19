from data_access import load_vessels, load_manifests, load_port_calls, load_shipments, load_incidents, load_weather 
from datetime import datetime
from operations import classify_shipment, find_shipment, find_manifest, parse_date, find_vessel_name, parse_weather_numbers, build_weather_recommendations
from text_tools import CONTAINER_PATTERN, SEAL_PATTERN, EMAIL_PATTERN, find_longest_stable_sequence, load_or_build_incident_index, search_incident_index
import os, csv, calendar, re

# TASK 1: List all registered vessels.
def handle_list_vessels():
    # Load valid vessel records and count files that could not be used.
    vessels, skipped = load_vessels("dataset/vessels")
    print(f"Registered HarborFlow vessels:")

    # Sort vessels alphabetically by name, ignoring uppercase/lowercase.
    sorted_vessels = sorted(vessels, key=lambda vessel: vessel["name"].lower() )
    # Print the name, IMO identifier and capacity for each vessel.
    for vessel in sorted_vessels:
        print(f"- {vessel['name']} | IMO {vessel['imo']} | {vessel['capacity_teu']:,} TEU")
    # Report how many vessel files were skipped during loading.
    print(f"Skipped vessel files: {skipped}")

# TASK 2: Inspect the manifest for a vessel's next eligible port call.
def inspect_vessel():
    # Load vessels and ask which vessel the user wants to inspect.
    vessels, skipped = load_vessels("dataset/vessels")
    vessel_name = input("Vessel name: ").strip()
    selected_vessel = None

    # Search for a vessel name without caring about capitalization.
    for vessel in vessels:
        if vessel_name.lower() == vessel["name"].lower():
            selected_vessel = vessel
            break
    # Stop this service if the requested vessel does not exist.
    if selected_vessel is None:
        print("Vessel not found.")
        return
    # Keep asking until the user provides a valid calendar date.
    while True:
        date_text = input("Reference date (YYYY-MM-DD): ")
        try:
            reference_date = datetime.strptime(date_text, "%Y-%m-%d").date()
            break
        except ValueError:
            print("Error - Date must use YYYY-MM-DD.")

    # Read the port-call CSV and prepare a list of matching future calls.
    port_calls = load_port_calls("dataset/port_calls.csv")
    upcoming_calls = []

    for call in port_calls:
        # Ignore calls belonging to another vessel.
        if call["vessel_id"] != selected_vessel["vessel_id"]:
            continue

        # Convert the arrival-date text into a date object.
        call_date = parse_date(call["arrival_date"])

        # Skip records whose arrival date could not be parsed.
        if call_date is None:
            print(f"Invalid date for port call {call['call_id']}. Skipping.")
            continue

        # Keep calls arriving on or after the user's reference date.
        if call_date >= reference_date:
            upcoming_calls.append((call_date, call["call_id"], call))

    # If no calls match, return to the main menu.
    if not upcoming_calls:
        print("No upcoming port calls found.")
        return

    # Sort first by arrival date, then by call ID to break ties.
    upcoming_calls.sort(key=lambda item: (item[0], item[1]))

    # The first sorted call is the earliest eligible one.
    selected_call_date = upcoming_calls[0][0]
    selected_call = upcoming_calls[0][2]

    # Load manifests and find the one linked to this port call.
    manifests = load_manifests("dataset/manifests")
    manifest = find_manifest(manifests, selected_call["call_id"])

    # A missing manifest means we cannot show shipment details.
    if manifest is None:
        print("Manifest unavailable.")
        return

    # Show the vessel name, selected call ID and arrival date.
    print(
        f"Manifest for {selected_vessel['name']} | "
        f"Call {selected_call['call_id']} | "
        f"{selected_call_date.strftime('%d %B %Y')}"
    )

    # Load shipment records and start the summary counters.
    shipments = load_shipments("dataset/shipments")
