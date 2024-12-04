#!/bin/bash
DB=modsec_ui
TB=modsec_users
BACKUP_DIR=$(pwd)/database
BACKUP_FILE=$BACKUP_DIR/$TB.sql

if [ -e $BACKUP_FILE ]; then
    echo "Backup file $BACKUP_FILE found."
    read -p "Are you sure you want to restore table $TB to database $DB? This will overwrite the existing data. (yes/no): " CONFIRM
    if [ "$CONFIRM" = "yes" ]; then
        echo "Restoring table $TB to database $DB..."
        sudo -u postgres psql -d $DB -c "\! psql -d $DB -f $BACKUP_FILE"
        if [ $? -eq 0 ]; then
            echo "Table $TB successfully restored to database $DB."
        else
            echo "An error occurred while restoring the table."
        fi
    else
        echo "Restore operation cancelled."
    fi
else
    echo "Backup file $BACKUP_FILE does not exist. Restore operation aborted."
fi
