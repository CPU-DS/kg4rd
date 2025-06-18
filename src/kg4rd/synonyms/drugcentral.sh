#!/bin/bash

DB_HOST="10.4.3.159"
DB_USER="postgres"
DB_PASSWORD="123456"
DB_PORT="15432"
DB_NAME="drugcentral"

psql -d "${DB_NAME}" \
    -h "${DB_HOST}" \
    -p "${DB_PORT}" \
    -U "${DB_USER}" \
    -c "SELECT DISTINCT st.id, st.cas_reg_no, sy.name, sy.preferred_name FROM structures st JOIN synonyms sy ON st.id = sy.id;" \
    -P format=csv \
    -o data_synonyms/drugcentral_synonyms.csv