source ../../.env
export PGPASSWORD=$DB_PASSWORD
psql -h $DB_HOST -d $DB_NAME -U $DB_USER -p $DB_PORT 