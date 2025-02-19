# Simple-ModSecurity-nginx-UI

## TODO

+ [x] User & Authen
  - [x] Login page
  - [x] maintain session
  - [ ]  Nếu status file là editing thì user khác lock edit
  - [ ]  Xử lý push realtime status to existing user (user editing)

+ [x] Sync config
  - [x] Sửa config file và push lên git
  - [x] Quản lý CD qua runner
  - [x] Runner xử lý config (Sync config cho nginx)
  - [ ] Runner xử lý config (Sync config cho haproxy)

+ [x] Rules/config page
  - [ ] button pull rule default from source
  - [x] commit file .disabled/enabled
  - [x] Get rules from db
  - [x] Lấy thông tin info, status từ db parse ra fe
  - [x] Bắt sự kiện change file/rename push to db
  - [x] Nếu rule disable rename to .disable
  - [x] Sort by rulecode

+ [ ]  Logs page
  - [x] limit max log query by time
  - [x] check lại hàm search logs elastic
  - [x] xử lý limit log/lazy load
  - [x] log time range picker
  - [ ] Rules exclusion tools
  - [ ] Integrate exclusion tools to logs tab
  - [x] Sửa lại log query tránh bị xss
  - [x] quick search function
  - [x] sort by columns
  - [x] page pagination
  - [x] dynamic render logs table
  - [x] sửa time range picker dynamic

+ [ ] Report summary (dashboard tab)
  - [x] Change waf mode
  - [ ] Report button
  - [x] Report chart
  - [ ] Report pdf 

+ [x]  Logs nav (access,error,audit,..)
  - [x] Audit logs
  - [x] Access logs
  - [ ] Error logs 

+ [ ] Bugs
  - [x] check lại css ghi dè
  - [x] sửa lại track config change giống rules
  - [ ] Check các bộ rules bắt buộc !!!!!!! ko được disable
  - [ ] Sửa lỗi absolute config path

+ [x] Features
  - [x] setup guide
  - [ ] setting config
    - [ ] manage multi-nodes (IP)
    - [ ] telebot tokens + test msg
    - [x] env variables (ELK ip, index, ...)
  - [ ] telegram alerts
  - [ ] build docker
  - [ ] hint (search bar)
  - [x] Quick script viewdb
  - [x] Quick script backupdb, restoredb

## Setup

```sh
apt install -y python3-pip postgresql
pip install -r requirements.txt
git clone https://git.bravo.com.vn/security/bravo.security.waf.manager.git modsec-ui
systemctl start postgresql
systemctl enable postgresql
```

### Usage

```sh
cd modsec-ui
cp $(pwd)/modsec_ui.service /etc/systemd/system/modsec_ui.service
systemctl daemon-reload
systemctl start modsec_ui.service
systemctl enable modsec_ui.service
systemctl status modsec_ui.service
```

go to http://localhost:5000 to access app

### setup DataBase

```sh
sudo -u postgres psql

modsec_users=# CREATE DATABASE modsec_ui;
CREATE DATABASE

modsec_users=# CREATE USER modsec_admin WITH PASSWORD 'bravo123';
CREATE ROLE

modsec_users=# GRANT ALL PRIVILEGES ON DATABASE modsec_ui TO modsec_admin;
GRANT

modsec_users=# \c modsec_ui
You are now connected to database "modsec_ui" as user "postgres".

modsec_ui=# CREATE TABLE modsec_users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE

modsec_ui=# CREATE TABLE modsec_rules (
    id SERIAL PRIMARY KEY,
    rule_code TEXT NOT NULL,
    rule_name TEXT NOT NULL,
    rule_path TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    content_hash TEXT NOT NULL,
    is_content_change BOOLEAN NOT NULL DEFAULT FALSE,
    is_modified BOOLEAN NOT NULL DEFAULT FALSE,
    last_modified TIMESTAMPTZ NOT NULL,
    is_enabled BOOLEAN NOT NULL DEFAULT TRUE
);
CREATE TABLE

modsec_ui=# GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO modsec_admin;
GRANT

modsec_ui=# GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO modsec_admin;
GRANT
```

### create app user

```sh
root@mosecurity:~/modsec-ui# sudo -u postgres psql
psql (14.13 (Ubuntu 14.13-0ubuntu0.22.04.1))
Type "help" for help.

postgres=# \l
                                     List of databases
     Name     |  Owner   | Encoding |   Collate   |    Ctype    |    Access privileges
--------------+----------+----------+-------------+-------------+--------------------------
 modsec_users | postgres | UTF8     | en_US.UTF-8 | en_US.UTF-8 | =Tc/postgres            +
              |          |          |             |             | postgres=CTc/postgres   +
              |          |          |             |             | modsec_user=CTc/postgres
 postgres     | postgres | UTF8     | en_US.UTF-8 | en_US.UTF-8 |

postgres=# \c modsec_ui
You are now connected to database "modsec_ui" as user "postgres".

modsec_ui=# \d
                 List of relations
 Schema |        Name         |   Type   |  Owner
--------+---------------------+----------+----------
 public | modsec_rules        | table    | postgres
 public | modsec_rules_id_seq | sequence | postgres
 public | modsec_users        | table    | postgres
 public | modsec_users_id_seq | sequence | postgres
(4 rows)

modsec_ui=# SELECT * FROM "modsec_users";
 id | username | password | created_at
----+----------+----------+------------
(0 rows)

modsec_ui=# INSERT INTO "modsec_users" (username, password) VALUES ('admin', '123');
INSERT 0 1
modsec_ui=# SELECT * FROM "modsec_users";
 id | username | password |         created_at
----+----------+----------+----------------------------
  1 | admin    | 123      | 2024-11-06 14:08:08.576257
(1 row)
```

### Backup and Restore DB

Backup

```
# connect to psql and connect to db
\! pg_dump -d modsec_ui -t modsec_rules -F p -f /tmp/modsec_rules.sql
```

Restore

```
# connect to psql and create db
\! psql -d modsec_ui_new -f /tmp/modsec_rules.sql
```

### check rule info

view rule in db

```
SELECT * FROM modsec_rules;
SELECT * FROM modsec_rules WHERE rule_code = '900';
```
