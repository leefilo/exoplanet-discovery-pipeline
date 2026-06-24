import duckdb

staged_planets_path = "data/staged/stg_planets.parquet"

dim_star_path = "data/mart/dim_star.parquet"

dim_discovery_path = "data/mart/dim_discovery.parquet"

dim_date_path = "data/mart/dim_date.parquet"

fact_planets_path = "data/mart/fact_planets.parquet"

con = duckdb.connect()


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
          JOIN read_parquet('data/mart/dim_star.parquet') as s on p.hostname = s.hostname
          JOIN read_parquet('data/mart/dim_discovery.parquet') as d on p.discoverymethod = d.discoverymethod AND p.disc_facility = d.disc_facility
          JOIN read_parquet('data/mart/dim_date.parquet') as dt on p.disc_year = dt.disc_year)
          TO '{fact_planets_path}' (FORMAT PARQUET)
            
""")