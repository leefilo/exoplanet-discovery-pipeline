import duckdb
import os
from dotenv import load_dotenv

load_dotenv()

USE_S3 = True
BUCKET = os.getenv("S3_BUCKET", "exoplanet-discovery-pipeline-leefilo")

if USE_S3:
    input_path = f"s3://{BUCKET}/raw/planetary_systems_raw.parquet"
    output_path = f"s3://{BUCKET}/staged/stg_planets.parquet"
else:
    input_path = "data/raw/planetary_systems_raw.parquet"
    output_path = "data/staged/stg_planets.parquet"


con = duckdb.connect()

if USE_S3:
    con.execute("INSTALL httpfs; LOAD httpfs;")
    con.execute(f"SET s3_region='{os.getenv('AWS_DEFAULT_REGION', 'us-east-2')}';")
    con.execute(f"SET s3_access_key_id='{os.getenv('AWS_ACCESS_KEY_ID')}';")
    con.execute(f"SET s3_secret_access_key='{os.getenv('AWS_SECRET_ACCESS_KEY')}';")

con.execute(f"""
        COPY (SELECT pl_name, pl_rade, pl_masse, pl_orbper, pl_eqt, hostname, st_teff, st_lum, sy_dist, discoverymethod, disc_facility, disc_year
        FROM read_parquet('{input_path}')
        WHERE default_flag = 1)            
        TO '{output_path}' (FORMAT PARQUET)
""")