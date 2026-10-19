HARBORFLOW PORT INTELLIGENCE CONSOLE - TEAM README

Run instructions
----------------
Command:python main.py (run from the project root, the folder that contains main.py)
Python version tested: Python 3.11+

Team members and concrete contributions
---------------------------------------
Name: Sheraz
Contribution: Developed Task 0 (main menu loop, option routing, menu input validation and option 10 exit), Task 1 (loading vessel JSON files, validating required fields, skipping and counting invalid files, and sorting by name), and Task 2 (finding the earliest upcoming call for a vessel, loading its manifest, resolving shipments, handling missing records, and calculating totals).

Name: Aryan
Contribution: Developed Task 3 (classifying shipments as CONTROLLED, COLD CHAIN, EXPEDITE or STANDARD using the first matching rule, including reasons and category totals) and Task 4 (building customer profiles and writing or updating exports/customer-profiles.csv with a header and no duplicate rows).

Name: Abubakr
Contribution: Developed Task 5 (finding port calls by month, skipping rows with invalid dates or unknown vessels, and sorting by date and vessel name), Task 6 (sanitizing incident reports using regular expressions for container IDs, seal numbers and email addresses, and saving sanitized reports to exports/sanitized/), and Task 7 (finding the longest stable event sequence using a sliding window).

Name: Sameer
Contribution: Developed Task 8 (joining upcoming port calls with weather.csv and printing weather recommendations, including handling unavailable forecasts and malformed rows) and Task 9 (building an inverted index, saving and reloading dataset/incident-index.json, rebuilding a missing, broken or outdated cache, and scoring search results). Also created test-ledger.csv.

Architecture
------------
main.py responsibilities: Runs the main menu, validates user input, routes the selected option to the relevant service function, and displays results.
data_access.py responsibilities: Loads and validates data from JSON and CSV files, handles file-reading errors, and returns validated records or reports skipped records as appropriate.
operations.py responsibilities: Implements reusable business rules, including classify_shipment, find_manifest, find_shipment, parse_date and build_weather_recommendations.
text_tools.py responsibilities: Defines regular expressions for sensitive identifiers, normalizes text, finds the longest stable event sequence, sanitizes incident reports, and builds and searches the incident index.

File and error-handling design: 
------------------------------
How paths are resolved: File paths are specified relative to the project root. Run python main.py from the directory containing main.py so the dataset and exports paths resolve as expected.
How malformed or missing input is handled: Input validation loops re-prompt users when menu choices, month values, dates or incident selections are invalid. File-loading code handles expected errors, such as FileNotFoundError, json.JSONDecodeError, csv.Error and ValueError, where applicable. Invalid records are skipped or reported rather than causing the entire program to terminate.
How generated files are updated safely: Generated files are written to their designated locations, including exports/customer-profiles.csv, exports/sanitized/ and dataset/incident-index.json. Existing customer-profile rows are checked to prevent duplicates. Cache data can be rebuilt when it is missing, broken or outdated.

Known limitations
-----------------
None known.
