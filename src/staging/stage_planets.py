import duckdb
from datetime import datetime

output_path = "data/staged/stg_planets.parquet"

planetary_systems_raw_path = "data/raw/planetary_systems_raw.parquet"

con = duckdb.connect()

con.execute(f"""
        COPY (SELECT pl_name, pl_rade, pl_masse, pl_orbper, pl_eqt, hostname, st_teff, st_lum, sy_dist, discoverymethod, disc_facility, disc_year
        FROM read_parquet('{planetary_systems_raw_path}')
        WHERE default_flag = 1)            
        TO '{output_path}' (FORMAT PARQUET)
""")