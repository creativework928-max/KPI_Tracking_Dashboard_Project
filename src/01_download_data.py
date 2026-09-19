from pathlib import Path
import zipfile
import requests

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
RAW.mkdir(parents=True, exist_ok=True)

URL = "https://archive.ics.uci.edu/static/public/502/online+retail+ii.zip"
ZIP = RAW / "online_retail_ii.zip"

print("Downloading UCI Online Retail II...")
r = requests.get(URL, timeout=120)
r.raise_for_status()
ZIP.write_bytes(r.content)

with zipfile.ZipFile(ZIP) as z:
    z.extractall(RAW)

print("Downloaded and extracted:", RAW)
