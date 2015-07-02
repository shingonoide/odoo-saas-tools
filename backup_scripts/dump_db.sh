#!/bin/sh
hostname=`hostname`

##########################################
## Odoo Backup
## Backup databases
##########################################

# Stop Odoo Server
service odoo stop

# Dump DBs
for db in `sudo -u postgres psql -l | grep "| openerp" | cut -d "|" -f1`
do
  date=`date +"%Y%m%d_%H%M%N"`
  filename="/var/pgdump/${hostname}_${db}_${date}.sql"
  pg_dump -E UTF-8 -p 5433 -F p -b -f $filename $db
  gzip $filename
done

# Start Odoo Server
service odoo start

exit 0
