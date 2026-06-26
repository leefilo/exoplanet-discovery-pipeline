import requests
import duckdb
import json
import os
from dotenv import load_dotenv

load_dotenv()

# S3 bucket or local
USE_S3 = True
BUCKET = os.getenv("S3_BUCKET", "exoplanet-discovery-pipeline-leefilo")

query = "SELECT+*+FROM+ps"
url = f"https://exoplanetarchive.ipac.caltech.edu/TAP/sync?query={query}&format=json"

response = requests.get(url)

if response.status_code == 200:
    print("Success!")
else:
    print(f"Request failed with status code: {response.status_code}")

data = response.json()

base_dir = os.getenv('BASE_DIR', '')
json_path = os.path.join(base_dir, "data/raw/planetary_systems_raw.json")
with open(json_path, "w") as f:
    json.dump(data, f)
    
if USE_S3:
    output_path = f"s3://{BUCKET}/raw/planetary_systems_raw.parquet"
else:
    output_path = "data/raw/planetary_systems_raw.parquet"


con = duckdb.connect()

if USE_S3:
    con.execute("INSTALL httpfs; LOAD httpfs;")
    con.execute(f"SET s3_region='{os.getenv('AWS_DEFAULT_REGION', 'us-east-2')}';")
    con.execute(f"SET s3_access_key_id='{os.getenv('AWS_ACCESS_KEY_ID')}';")
    con.execute(f"SET s3_secret_access_key='{os.getenv('AWS_SECRET_ACCESS_KEY')}';")

con.execute(f"""

    COPY (SELECT * FROM read_json_auto('{json_path}'))
    TO '{output_path}' (FORMAT PARQUET)

""")