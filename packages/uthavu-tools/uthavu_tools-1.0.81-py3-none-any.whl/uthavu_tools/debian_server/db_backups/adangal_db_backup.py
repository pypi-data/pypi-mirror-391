# # Define variables for clarity (Execute these lines first on your VPS)
# CONTAINER_NAME="adangal-app-adangal_db-1"
# DB_NAME="Adangal"
# DB_PASS="YourStrong!Pass123" # <-- CRITICAL: Use your actual SA password
# BACKUP_FILE="/var/opt/mssql/backup/Adangal_$(date +%Y%m%d_%H%M%S).bak"

# # Execute the backup command inside the SQL Server container
# sudo docker exec -it $CONTAINER_NAME /opt/mssql-tools/bin/sqlcmd \
#   -U SA \
#   -P "$DB_PASS" \
#   -Q "BACKUP DATABASE $DB_NAME TO DISK = N'$BACKUP_FILE' WITH NOFORMAT, NOINIT, NAME = N'Adangal-Full', SKIP, NOREWIND, NOUNLOAD, STATS = 10"