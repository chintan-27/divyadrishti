---
name: duckdb
description: Query and analyze data using DuckDB. Use for running SQL queries against local files (CSV, Parquet, JSON, DuckDB), in-memory databases, or MotherDuck cloud.
argument-hint: [query or file path]
user-invocable: true
allowed-tools: Bash, Read, Write, Glob
---

# DuckDB Data Skill

Use DuckDB to query and analyze data based on: $ARGUMENTS

## Capabilities

- Run SQL queries against local files (.csv, .parquet, .json, .duckdb)
- Create in-memory tables for ad-hoc analysis
- Connect to MotherDuck when MOTHERDUCK_TOKEN is set
- Summarize datasets, compute statistics, and identify patterns

## Instructions

1. If given a file path, inspect the file and determine its format
2. Use `duckdb` CLI to run SQL queries (install via `brew install duckdb` if needed)
3. For local files, query directly: `SELECT * FROM 'data.csv' LIMIT 10;`
4. For MotherDuck, connect with: `duckdb md:`
5. Present results clearly with context about what the data shows
6. When analyzing, provide summary statistics, distributions, and notable patterns

## Example Commands

```bash
# Query a CSV file
duckdb -c "SELECT * FROM 'data.csv' LIMIT 10;"

# Query a Parquet file
duckdb -c "DESCRIBE SELECT * FROM 'data.parquet';"

# Aggregate query
duckdb -c "SELECT column, COUNT(*) FROM 'data.csv' GROUP BY column ORDER BY COUNT(*) DESC;"

# MotherDuck (when token is set)
duckdb md: -c "SHOW DATABASES;"
```
