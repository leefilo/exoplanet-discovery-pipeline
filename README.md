# Exoplanet Discovery Pipeline

**What can NASA's exoplanet data tell us about planets beyond our solar system?**

NASA's Exoplanet Archive contains data on over 5,000 confirmed planets discovered through various detection methods. I built an ELT pipeline to analyze discovery trends, identify potentially habitable worlds, and explore which telescopes and techniques have been most productive. The pipeline ingests data from NASA's TAP API, transforms it using a star schema, and stores it in S3 for analysis.

![Python](https://img.shields.io/badge/Python-3.9+-blue?logo=python&logoColor=white)
![Airflow](https://img.shields.io/badge/Airflow-2.7-017CEE?logo=apacheairflow&logoColor=white)
![DuckDB](https://img.shields.io/badge/DuckDB-yellow?logo=duckdb&logoColor=black)
![AWS S3](https://img.shields.io/badge/AWS_S3-569A31?logo=amazons3&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?logo=docker&logoColor=white)

---

## Architecture

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  NASA TAP    │────▶│    S3/Raw    │────▶│  S3/Staged   │────▶│   S3/Mart    │
│     API      │     │  (Parquet)   │     │  (Parquet)   │     │  (Parquet)   │
└──────────────┘     └──────────────┘     └──────────────┘     └──────────────┘
```

**Orchestrated by Apache Airflow:**

![Airflow DAG](assets/dag_screenshot.png)

---

## Key Questions

The notebook explores patterns in exoplanet discoveries:
- Which nearby stars have potentially habitable planets?
- How has planet discovery evolved over time?
- What detection methods find what kinds of planets?
- Which telescopes/missions have been most productive?

---

## Quick Start

**Prerequisites:** Docker Desktop, AWS account with S3 bucket

```bash
git clone https://github.com/leefilo/exoplanet-discovery-pipeline.git
cd exoplanet-discovery-pipeline
```

Create a `.env` file with your AWS credentials:
```
AWS_ACCESS_KEY_ID=your-key
AWS_SECRET_ACCESS_KEY=your-secret
AWS_DEFAULT_REGION=us-east-2
S3_BUCKET=your-bucket-name
```

Start the pipeline:
```bash
docker compose build
docker compose up -d
```

Access Airflow at http://localhost:8080 (admin/admin). Trigger the `exoplanet_pipeline` DAG.

---

## Data Source

| Dataset | Source | Description |
|---------|--------|-------------|
| Planetary Systems | NASA Exoplanet Archive TAP API | Planet properties, host star data, discovery info |

---

## Project Structure

```
exoplanet-discovery-pipeline/
├── dags/
│   └── exoplanet_dag.py          # Airflow DAG definition
├── src/
│   ├── ingestion/
│   │   └── ingest.py             # NASA API ingestion
│   ├── staging/
│   │   └── stage_planets.py      # Remove unwanted columns
│   └── mart/
│       └── build_mart.py         # Create marts from data
├── notebooks/
│   └── analysis.ipynb            # Query marts
├── docker-compose.yaml
├── Dockerfile
└── requirements.txt
```

---

## Pipeline DAG

```
ingest ──▶ stage ──▶ build_mart
```

---

## Dimensional Model

**fact_planets:** One row per planet with measurements and foreign keys

**dim_star:** Host star properties (temperature, luminosity, distance)

**dim_discovery:** Discovery method and facility

**dim_date:** Discovery year

---

## Tech Decisions

**DuckDB over Postgres:** Same reasoning as the hospital pipeline project I have built. I had no need for a running database server. DuckDB reads and writes Parquet directly through its httpfs extension.

**Dimensional model over flat table:** Wanted to practice star schema design. The raw data has 355 columns; the model focuses on the ~12 most analytically useful.

**S3 storage:** Getting more practice in with data and using S3 as main storage.

---

## What I Learned

- Working with NASA's TAP API and ADQL syntax
- Modeling data using the star schema
