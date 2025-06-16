#!/bin/bash

DB_HOST="10.4.3.159"
DB_USER="postgres"
DB_PASSWORD="123456"
DB_PORT="15432"
DB_NAME="drugcentral"

SQL_FILE="src/kg4rd/data/drugcentral/drugcentral.dump.11012023.sql"

sudo apt-get install postgresql-client

export PGPASSWORD="${DB_PASSWORD}"
    
docker run --name "${DB_NAME}" \
    -e "POSTGRES_PASSWORD=${DB_PASSWORD}" \
    -e "POSTGRES_DB=${DB_NAME}" \
    -p "${DB_PORT}:5432" \
    -d postgres:17.5

psql -h "${DB_HOST}" \
    -p "${DB_PORT}" \
    -U "${DB_USER}" \
    -d "${DB_NAME}" \
    -f "${SQL_FILE}"

psql -d "${DB_NAME}" \
    -h "${DB_HOST}" \
    -p "${DB_PORT}" \
    -U "${DB_USER}" \
    -c "SELECT DISTINCT * FROM structures RIGHT JOIN (SELECT * FROM omop_relationship WHERE relationship_name IN ('indication', 'contraindication', 'off-label use')) AS drug_disease ON structures.id = drug_disease.struct_id;" \
    -P format=csv \
    -o drug_disease.csv
