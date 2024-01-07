source .env
export PGPASSWORD=$DB_PASSWORD
psql -h $DB_HOST -d postgres -p $DB_PORT -U $DB_USER -f schema.sql 