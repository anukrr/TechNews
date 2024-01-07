source ../../.env
export PGPASSWORD=$DB_PASSWORD
psql -h $DB_HOST -d $DB_NAME -p $DB_PORT -U $DB_USER