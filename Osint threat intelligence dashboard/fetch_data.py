import requests
import pandas as pd
import os
from dotenv import load_dotenv
load_dotenv()

API_URL = "https://threatfox-api.abuse.ch/api/v1/"
OUTPUT_FILE = "data/iocs.csv"

AUTH_KEY = os.getenv("api_key")

if not AUTH_KEY:
    print("ERROR: API key not found in .env file.")
    exit()


def get_bad_indicators():
    payload = {
        "query": "get_iocs",
        "days": 3
    }

    headers = {
        "Auth-Key": AUTH_KEY
    }

    print("Asking ThreatFox for recent threat data...")
    response = requests.post(API_URL, json=payload, headers=headers, timeout=30)
    result = response.json()

    if result.get("query_status") != "ok":
        print("Something went wrong:", result.get("query_status"))
        return []

    print(f"Got {len(result['data'])} entries.")
    return result["data"]


def save_to_csv(records):
    if not records:
        print("No data to save.")
        return

    df = pd.DataFrame(records)

    useful_columns = {
        "ioc": "indicator",
        "ioc_type": "type",
        "threat_type": "threat_type",
        "malware_printable": "malware",
        "confidence_level": "confidence",
        "first_seen_utc": "first_seen"
    }

    available = [c for c in useful_columns if c in df.columns]
    df = df[available]
    df = df.rename(columns=useful_columns)

    os.makedirs("data", exist_ok=True)
    df.to_csv(OUTPUT_FILE, index=False)
    print(f"Saved {len(df)} rows to {OUTPUT_FILE}")


if __name__ == "__main__":
    records = get_bad_indicators()
    save_to_csv(records)
