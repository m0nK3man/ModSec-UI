# Simple-ModSecurity-nginx-UI

## TODO
+ LOGIN (Authen)
+ Sửa config file và push lên git
  - Quản lý CD qua runner
  - Runner xử lý config (Sync config cho nginx)

+ Lấy log từ ELK
+ Check các bộ rules bắt buộc !!!!!!! ko được disable
+ commit file .disabled/enabled
+ limit max log query by time
+ check l?i css ghi dè

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
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    content_hash TEXT NOT NULL,
    is_modified BOOLEAN NOT NULL,
    last_modified TIMESTAMPTZ NOT NULL,
    is_enabled BOOLEAN NOT NULL
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
INSERT INTO modsec_rules (rule_code, rule_name, rule_path, created_at, content_hash, is_modified, last_modified, is_enabled) 
VALUES
(933, 'Application Attack Php', 'REQUEST-933-APPLICATION-ATTACK-PHP.conf', '2024-11-07 11:22:00.509458', '8e1382c74beddad0dbec64c92b56089a', false, '2024-11-07 11:22:00.509458', true),
(950, 'Data Leakages', 'RESPONSE-950-DATA-LEAKAGES.conf', '2024-11-07 11:22:00.512398', '47b4951e471bfec01abab24d9232e7f9', false, '2024-11-07 11:22:00.512398', true),
(934, 'Application Attack Generic', 'REQUEST-934-APPLICATION-ATTACK-GENERIC.conf', '2024-11-07 11:22:00.509864', '0de43628698a32bfc4f3f08b5472672c', false, '2024-11-07 11:22:00.509864', true),
(921, 'Protocol Attack', 'REQUEST-921-PROTOCOL-ATTACK.conf', '2024-11-07 11:22:00.506932', 'c546f56121a62b38d86a0e9c24b23744', false, '2024-11-07 11:22:00.506932', true),
(941, 'Application Attack Xss', 'REQUEST-941-APPLICATION-ATTACK-XSS.conf', '2024-11-07 11:22:00.510231', '4941037e41d391c07ebec4ece87acc71', false, '2024-11-07 11:22:00.510231', true),
(942, 'Application Attack Sqli', 'REQUEST-942-APPLICATION-ATTACK-SQLI.conf', '2024-11-07 11:22:00.510618', '20864b6a9fdbfce311a8d61ef19a58d0', false, '2024-11-07 11:22:00.510618', true),
(943, 'Application Attack Session Fixation', 'REQUEST-943-APPLICATION-ATTACK-SESSION-FIXATION.conf', '2024-11-07 11:22:00.511188', '1fad307b172feae9463cc791cefc4535', false, '2024-11-07 11:22:00.511188', true),
(905, 'Common Exceptions', 'REQUEST-905-COMMON-EXCEPTIONS.conf', '2024-11-07 11:22:00.504895', '8c7d6aebe678e28f9317894cf52204be', false, '2024-11-07 11:22:00.504895', true),
(911, 'Method Enforcement', 'REQUEST-911-METHOD-ENFORCEMENT.conf', '2024-11-07 11:22:00.505408', '5ed7d30fbbe3e1a0238c04641a4f25ac', false, '2024-11-07 11:22:00.505408', true),
(913, 'Scanner Detection', 'REQUEST-913-SCANNER-DETECTION.conf', '2024-11-07 11:22:00.505912', 'dca99889523543188ac48e68c84c63d8', false, '2024-11-07 11:22:00.505912', true),
(920, 'Protocol Enforcement', 'REQUEST-920-PROTOCOL-ENFORCEMENT.conf', '2024-11-07 11:22:00.506286', '38fe7f443a5f1cb7a28d96b89631a9be', false, '2024-11-07 11:22:00.506286', true),
(944, 'Application Attack Java', 'REQUEST-944-APPLICATION-ATTACK-JAVA.conf', '2024-11-07 11:22:00.511621', '3ee57b4f9438af6a7f56f89c455e61b6', false, '2024-11-07 11:22:00.511621', true),
(922, 'Multipart Attack', 'REQUEST-922-MULTIPART-ATTACK.conf', '2024-11-07 11:22:00.50749', '60f7af8cc580cf8627932c305dcda63a', false, '2024-11-07 11:22:00.50749', true),
(930, 'Application Attack Lfi', 'REQUEST-930-APPLICATION-ATTACK-LFI.conf', '2024-11-07 11:22:00.508189', '1873d512ea0d9ac404095e6d4980fbb0', false, '2024-11-07 11:22:00.508189', true),
(931, 'Application Attack Rfi', 'REQUEST-931-APPLICATION-ATTACK-RFI.conf', '2024-11-07 11:22:00.50868', 'c1cc87fa430b42088bc0dfce661a6bcc', false, '2024-11-07 11:22:00.50868', true),
(932, 'Application Attack Rce', 'REQUEST-932-APPLICATION-ATTACK-RCE.conf', '2024-11-07 11:22:00.509079', '564b5468365c51e0b2be9c7ea72d5b18', false, '2024-11-07 11:22:00.509079', true),
(949, 'Blocking Evaluation', 'REQUEST-949-BLOCKING-EVALUATION.conf', '2024-11-07 11:22:00.511997', '11fa467f05a97d5d821d3b46e7244f08', false, '2024-11-07 11:22:00.511997', true),
(951, 'Data Leakages Sql', 'RESPONSE-951-DATA-LEAKAGES-SQL.conf', '2024-11-07 11:22:00.512765', 'cf517720778838e63c24970ab64d65fb', false, '2024-11-07 11:22:00.512765', true),
(952, 'Data Leakages Java', 'RESPONSE-952-DATA-LEAKAGES-JAVA.conf', '2024-11-07 11:22:00.513164', '44be41d89b7f581892fd0973712bafc0', false, '2024-11-07 11:22:00.513164', true),
(953, 'Data Leakages Php', 'RESPONSE-953-DATA-LEAKAGES-PHP.conf', '2024-11-07 11:22:00.513711', '415a9d89ddf3a1b3d8fed9304bf8b2c7', false, '2024-11-07 11:22:00.513711', true),
(954, 'Data Leakages Iis', 'RESPONSE-954-DATA-LEAKAGES-IIS.conf', '2024-11-07 11:22:00.514088', '51d036076ef3fadcd4c3ceeb28a7105e', false, '2024-11-07 11:22:00.514088', true),
(901, 'Initialization', 'REQUEST-901-INITIALIZATION.conf', '2024-11-07 11:22:00.504047', 'd0a50f90a3740174637b2ec0f2619b20', false, '2024-11-07 11:22:00.504047', true),
(955, 'Web Shells', 'RESPONSE-955-WEB-SHELLS.conf', '2024-11-07 11:22:00.514498', '7f6c9d0c4e7ca65ef2eb4f150e2cc3a9', false, '2024-11-07 11:22:00.514498', true),
('CONFIG_CRS', 'Crs Configuration', '../local-conf/crs/crs-setup.conf', '2024-11-07 13:18:41.305888', 'a5d80a88c84865cff8f589531e245c72', true, '2024-11-07 22:37:26.420076', true),
(900, 'Exclusion Rules Before Crs', 'REQUEST-900-EXCLUSION-RULES-BEFORE-CRS.conf', '2024-11-07 11:22:00.501399', 'a5d80a88c84865cff8f589531e245c72', true, '2024-11-07 11:22:00.501399', true),
(959, 'Blocking Evaluation', 'RESPONSE-959-BLOCKING-EVALUATION.conf', '2024-11-07 11:22:00.514882', 'f177ae40a0c7c9fba9b60a3c7ff83231', false, '2024-11-07 11:22:00.514882', true),
(980, 'Correlation', 'RESPONSE-980-CORRELATION.conf', '2024-11-07 11:22:00.515311', 'e28f9394286c8ef45a80c04aa2fb47f8', false, '2024-11-07 11:22:00.515311', true),
(999, 'Exclusion Rules After Crs', 'RESPONSE-999-EXCLUSION-RULES-AFTER-CRS.conf', '2024-11-07 11:22:00.515726', '684ce3182cb569b21e118791d0c75333', false, '2024-11-07 11:22:00.515726', true),
('CONFIG_MODSEC', 'Modsecurity Configuration', '../local-conf/modsecurity.conf', '2024-11-07 13:16:24.107794', 'a5d80a88c84865cff8f589531e245c72', true, '2024-11-07 22:56:37.064783', true);
```

view rule in db

```
SELECT * FROM modsec_rules;
SELECT * FROM modsec_rules WHERE rule_code = '900';
```
