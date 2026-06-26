import duckdb
import os
from dotenv import load_dotenv

load_dotenv()

USE_S3 = True
BUCKET = os.getenv("S3_BUCKET", "exoplanet-discovery-pipeline-leefilo")

if USE_S3:
    staged_planets_path = f"s3://{BUCKET}/staged/stg_planets.parquet"
    dim_star_path = f"s3://{BUCKET}/mart/dim_star.parquet"
    dim_discovery_path = f"s3://{BUCKET}/mart/dim_discovery.parquet"
    dim_date_path = f"s3://{BUCKET}/mart/dim_date.parquet"
    fact_planets_path = f"s3://{BUCKET}/mart/fact_planets.parquet"
else:
    staged_planets_path = "data/staged/stg_planets.parquet"
    dim_star_path = "data/mart/dim_star.parquet"
    dim_discovery_path = "data/mart/dim_discovery.parquet"
    dim_date_path = "data/mart/dim_date.parquet"
    fact_planets_path = "data/mart/fact_planets.parquet"

con = duckdb.connect()

if USE_S3:
    con.execute("INSTALL httpfs; LOAD httpfs;")
    con.execute(f"SET s3_region='{os.getenv('AWS_DEFAULT_REGION', 'us-east-2')}';")
    con.execute(f"SET s3_access_key_id='{os.getenv('AWS_ACCESS_KEY_ID')}';")
    con.execute(f"SET s3_secret_access_key='{os.getenv('AWS_SECRET_ACCESS_KEY')}';")


# dim_star
con.execute(f"""
    COPY (SELECT ROW_NUMBER() OVER () as star_key, hostname, MAX(st_teff) as st_teff, MAX(st_lum) as st_lum, MAX(sy_dist) as sy_dist
          FROM read_parquet('{staged_planets_path}')
          GROUP BY hostname)
    TO '{dim_star_path}' (FORMAT PARQUET)
""")


# dim_discovery
con.execute(f"""
    COPY (SELECT ROW_NUMBER() OVER () as discovery_key,
            discoverymethod, disc_facility
          FROM  (SELECT DISTINCT discoverymethod, disc_facility
                 FROM read_parquet('{staged_planets_path}')))
    TO '{dim_discovery_path}' (FORMAT PARQUET)
            
""")

# dim_date
con.execute(f"""
    COPY (SELECT ROW_NUMBER() OVER () as date_key,
            disc_year
          FROM  (SELECT DISTINCT disc_year
                 FROM read_parquet('{staged_planets_path}')))
    TO '{dim_date_path}' (FORMAT PARQUET)
            
""")

# fact_planets
con.execute(f"""
    COPY (SELECT ROW_NUMBER() OVER () as planet_key, p.pl_name, p.pl_rade, p.pl_masse, p.pl_orbper, p.pl_eqt, s.star_key, d.discovery_key, dt.date_key
          FROM read_parquet('{staged_planets_path}') as p
          JOIN read_parquet('{dim_star_path}') as s ON p.hostname = s.hostname
          JOIN read_parquet('{dim_discovery_path}') as d ON p.discoverymethod = d.discoverymethod AND p.disc_facility = d.disc_facility
          JOIN read_parquet('{dim_date_path}') as dt ON p.disc_year = dt.disc_year)
    TO '{fact_planets_path}' (FORMAT PARQUET)
""")