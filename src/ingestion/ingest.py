import requests
import duckdb
import json



query = "SELECT+*+FROM+ps"
url = f"https://exoplanetarchive.ipac.caltech.edu/TAP/sync?query={query}&format=json"

response = requests.get(url)

if response.status_code == 200:
    print("Success!")
else:
    print(f"Request failed with status code: {response.status_code}")

data = response.json()

json_path = "data/raw/planetary_systems_raw.json"
with open(json_path, "w") as f:
    json.dump(data, f)

output_path = "data/raw/planetary_systems_raw.parquet"

con = duckdb.connect()

con.execute(f"""

    COPY (SELECT * FROM read_json_auto('{json_path}'))
    TO '{output_path}' (FORMAT PARQUET)

""")