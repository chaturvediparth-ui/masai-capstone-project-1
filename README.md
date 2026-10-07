Mamaearth Data Pipeline

This repository contains the complete workflow to clean, analyze, and narrate 
Mamaearth’s order dataset. The process begins with SQL: load sql/schema.sql to 
create the database tables, then sql/seed_data.sql to insert sample orders, customers, 
and products, and finally run sql/reports.sql to generate the raw Part 1 report totals. 
After the database is prepared, the analysis scripts are executed. Running analysis/clean_and_eda.py 
performs data cleaning, deduplication, imputations, reconciliation, and hypothesis testing, 
while analysis/visualize.py produces supporting charts such as return rates and monthly revenue 
trends. Task 5 of Part 2 writes the verified metrics into narrator/findings.json, which serves as 
the single source of truth for downstream steps. The final stage is narrative generation. Executing 
narrator/generate_narrative.py produces the Situation–Complication–Resolution brief. If a Gemini API 
key is set as an environment variable (export GEMINI_API_KEY="your_api_key_here"), the script calls 
Gemini to generate the narrative online. If no key is provided, the script automatically falls back 
to the offline deterministic template, ensuring reproducibility by pulling all numbers directly from 
findings.json. By following this pipeline from top to bottom, any reader can reproduce every figure 
in the brief, starting from raw SQL totals through cleaned reconciled values to the final SCR narrative.
