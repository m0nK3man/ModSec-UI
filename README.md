# Simple-ModSecurity-nginx-UI

## TODO
+ LOGIN (Authen)
+ Sửa config file và push lên git
  - Quản lý CD qua runner
  - Runner xử lý config (Sync config cho nginx)

+ Lấy log từ ELK
+ Check các bộ rules bắt buộc !!!!!!! ko được disable
+ commit file .disabled/enabled

+ Rules exclusion tools
+ Integrate exclusion tools to logs tab

+ Report summary (home tab)

+ Logs nav (access,error,audit,..)
+ Save/Commit button (Rule tab)
+ Get rules from db
  - Lấy thông tin info,status từ db parse ra fe
  - Bắt sự kiện change file/rename push to db
  - Nếu rule disable rename to .disable
  - Sort by id
  - Nếu status file là editing thì user khác lock edit
  - Xử lý push realtime status to existing user
+ search log

+ setup guide
+ running service

## Usage

```sh
pip install requirements.txt
git clone https://git.bravo.com.vn/security/bravo.security.waf.manager.git modsec-ui
cd modsec-ui
ln -s $(pwd)/modsec_ui.service /etc/systemd/system/modsec_ui.service
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
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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

### init rule info

```sh
INSERT INTO modsec_rules (rule_code, rule_name, rule_path) VALUES ('900', 'Exclusion Rules Before Crs', 'REQUEST-900-EXCLUSION-RULES-BEFORE-CRS.conf');
INSERT INTO modsec_rules (rule_code, rule_name, rule_path) VALUES ('901', 'Initialization', 'REQUEST-901-INITIALIZATION.conf');
INSERT INTO modsec_rules (rule_code, rule_name, rule_path) VALUES ('905', 'Common Exceptions', 'REQUEST-905-COMMON-EXCEPTIONS.conf');
INSERT INTO modsec_rules (rule_code, rule_name, rule_path) VALUES ('911', 'Method Enforcement', 'REQUEST-911-METHOD-ENFORCEMENT.conf');
INSERT INTO modsec_rules (rule_code, rule_name, rule_path) VALUES ('913', 'Scanner Detection', 'REQUEST-913-SCANNER-DETECTION.conf');
INSERT INTO modsec_rules (rule_code, rule_name, rule_path) VALUES ('920', 'Protocol Enforcement', 'REQUEST-920-PROTOCOL-ENFORCEMENT.conf');
INSERT INTO modsec_rules (rule_code, rule_name, rule_path) VALUES ('921', 'Protocol Attack', 'REQUEST-921-PROTOCOL-ATTACK.conf');
INSERT INTO modsec_rules (rule_code, rule_name, rule_path) VALUES ('922', 'Multipart Attack', 'REQUEST-922-MULTIPART-ATTACK.conf');
INSERT INTO modsec_rules (rule_code, rule_name, rule_path) VALUES ('930', 'Application Attack Lfi', 'REQUEST-930-APPLICATION-ATTACK-LFI.conf');
INSERT INTO modsec_rules (rule_code, rule_name, rule_path) VALUES ('931', 'Application Attack Rfi', 'REQUEST-931-APPLICATION-ATTACK-RFI.conf');
INSERT INTO modsec_rules (rule_code, rule_name, rule_path) VALUES ('932', 'Application Attack Rce', 'REQUEST-932-APPLICATION-ATTACK-RCE.conf');
INSERT INTO modsec_rules (rule_code, rule_name, rule_path) VALUES ('933', 'Application Attack Php', 'REQUEST-933-APPLICATION-ATTACK-PHP.conf');
INSERT INTO modsec_rules (rule_code, rule_name, rule_path) VALUES ('934', 'Application Attack Generic', 'REQUEST-934-APPLICATION-ATTACK-GENERIC.conf');
INSERT INTO modsec_rules (rule_code, rule_name, rule_path) VALUES ('941', 'Application Attack Xss', 'REQUEST-941-APPLICATION-ATTACK-XSS.conf');
INSERT INTO modsec_rules (rule_code, rule_name, rule_path) VALUES ('942', 'Application Attack Sqli', 'REQUEST-942-APPLICATION-ATTACK-SQLI.conf');
INSERT INTO modsec_rules (rule_code, rule_name, rule_path) VALUES ('943', 'Application Attack Session Fixation', 'REQUEST-943-APPLICATION-ATTACK-SESSION-FIXATION.conf');
INSERT INTO modsec_rules (rule_code, rule_name, rule_path) VALUES ('944', 'Application Attack Java', 'REQUEST-944-APPLICATION-ATTACK-JAVA.conf');
INSERT INTO modsec_rules (rule_code, rule_name, rule_path) VALUES ('949', 'Blocking Evaluation', 'REQUEST-949-BLOCKING-EVALUATION.conf');
INSERT INTO modsec_rules (rule_code, rule_name, rule_path) VALUES ('950', 'Data Leakages', 'RESPONSE-950-DATA-LEAKAGES.conf');
INSERT INTO modsec_rules (rule_code, rule_name, rule_path) VALUES ('951', 'Data Leakages Sql', 'RESPONSE-951-DATA-LEAKAGES-SQL.conf');
INSERT INTO modsec_rules (rule_code, rule_name, rule_path) VALUES ('952', 'Data Leakages Java', 'RESPONSE-952-DATA-LEAKAGES-JAVA.conf');
INSERT INTO modsec_rules (rule_code, rule_name, rule_path) VALUES ('953', 'Data Leakages Php', 'RESPONSE-953-DATA-LEAKAGES-PHP.conf');
INSERT INTO modsec_rules (rule_code, rule_name, rule_path) VALUES ('954', 'Data Leakages Iis', 'RESPONSE-954-DATA-LEAKAGES-IIS.conf');
INSERT INTO modsec_rules (rule_code, rule_name, rule_path) VALUES ('955', 'Web Shells', 'RESPONSE-955-WEB-SHELLS.conf');
INSERT INTO modsec_rules (rule_code, rule_name, rule_path) VALUES ('959', 'Blocking Evaluation', 'RESPONSE-959-BLOCKING-EVALUATION.conf');
INSERT INTO modsec_rules (rule_code, rule_name, rule_path) VALUES ('980', 'Correlation', 'RESPONSE-980-CORRELATION.conf');
INSERT INTO modsec_rules (rule_code, rule_name, rule_path) VALUES ('999', 'Exclusion Rules After Crs', 'RESPONSE-999-EXCLUSION-RULES-AFTER-CRS.conf');
```

view rule in db

```
SELECT * FROM modsec_rules;
SELECT * FROM modsec_rules WHERE rule_code = '900';
```
