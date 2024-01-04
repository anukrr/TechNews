source .env
export PGPASSWORD=$DB_PASSWORD
psql -h $DB_HOST -U $DB_USER -d postgres -p $DB_PORT -f schema.sql 