#!/bin/bash
sudo -u postgres psql -d modsec_ui -c "SELECT * FROM modsec_users;"
