# Tourism Arrivals & Hotel Occupancy Visualization Platform

## Run on Windows
1. Install Python 3.10+.
2. Open Command Prompt in this folder.
3. Run `python -m venv .venv`
4. Activate: `.venv\\Scripts\\activate`
5. Install: `pip install -r requirements.txt`
6. Start: `streamlit run app.py`

## Features
Interactive overview, CSV/XLSX uploads, data validation, cleaned CSV exports, tourism analysis, hotel occupancy analysis, matched destination-month comparison, destination explorer and reports.

## Data formats
Tourism requires Date, Destination, Tourist Arrivals. Optional: Domestic Arrivals, International Arrivals.
Hotel requires Date, Destination and Occupancy Rate OR Total Rooms + Occupied Rooms.
The app recognizes common alternative column names. It calculates occupancy as Occupied Rooms / Total Rooms * 100 when possible.

## Demo data
The app starts with synthetic demo data for immediate testing. It is not official tourism or hotel data. Upload real datasets to replace it.

## Notes
No paid APIs, subscription, cloud database or API keys are required. Comparative analysis joins only matching destination and calendar month. Correlation is descriptive, not causal.
