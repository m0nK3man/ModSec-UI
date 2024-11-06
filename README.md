# Simple-ModSecurity-nginx-UI

## TODO
+ LOGIN (Authen)
+ Sửa config file và push lên git
  - Quản lý CD qua runner
  - Runner xử lý config (Sync config cho nginx)

+ Lấy log từ ELK


+ Rules exclusion tools
+ Integrate exclusion tools to logs tab

+ Report summary (home tab)

+ Logs nav (access,error,audit,..)
+ Reload button (Rule tab)

+ search log

+ setup guide
+ running service

## Usage

```sh
pip install requirements.txt
git clone https://git.bravo.com.vn/security/bravo.security.waf.manager.git modsec-ui
cd modsec-ui
python3 app.py
```

go to http://localhost:5000 to access app

### create DB

```sh
sudo -u postgres psql
CREATE DATABASE modsec_users;
CREATE USER modsec_user WITH PASSWORD 'yourpassword';
GRANT ALL PRIVILEGES ON DATABASE modsec_users TO modsec_user;
```

### create app user

```sh
root@test-docker:~/modsec-ui# sudo -u postgres psql
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

postgres=# \c modsec_users
You are now connected to database "modsec_users" as user "postgres".

modsec_users=# \d
               List of relations
 Schema |    Name     |   Type   |    Owner
--------+-------------+----------+-------------
 public | user        | table    | modsec_user
 public | user_id_seq | sequence | modsec_user
(2 rows)

modsec_users=# SELECT * FROM "user";
 id | username |                                                                      password
----+----------+-----------------------------------------------------------------------------------------------------------------------------------------------------
  1 | test     | 123
  2 | anhnht   | 123
(2 rows)

modsec_users=# INSERT INTO "user" (username, password) VALUES ('newuser', '123');
INSERT 0 1
modsec_users=# SELECT * FROM "user";
 id | username |                                                                      password
----+----------+-----------------------------------------------------------------------------------------------------------------------------------------------------
  1 | test     | 123
  2 | anhnht   | 123
  3 | newuser  | 123
(3 rows)
```


