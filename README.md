[![pylint](https://github.com/zerwes/powerdns-pipe-ptr/actions/workflows/pylint.yml/badge.svg)](https://github.com/zerwes/powerdns-pipe-ptr/actions/workflows/pylint.yml)

# powerdns-pipe-ptr

a simple script to be used via [powerdns](https://github.com/PowerDNS/pdns) pipe backend

it is intended to resolve reverse lookups based on the existing `A` records via the gmysql backend,
as the `set-ptr` option has been removed (see https://github.com/PowerDNS/pdns/pull/7797)

## requirements

### python3 pymysql

the script requires `python3-pymysql` aka. `PyMySQL`

### SOA

the reverse zones in question should be created in pdns

### gmysql

the script will just work for records registered in the `gmysql` backend and uses the database connection registered for `gmysql` in the `pdns.conf` file

### pdns.conf

add the following lines to your `pdns.conf` **after** the `launch+=gmysql` line and the other gmysql settings:

```
zone-cache-refresh-interval=0
launch+=pipe
pipe-regex=^.*\.in-addr\.arpa$
pipe-command=/etc/powerdns/ptr.py
```

inserting the pipe settings **after** the gmysql settings ensures that real PTR records will be resolved via the gmysql (or other) backend,
and only if none is fpund, the pipe backend will be used.

## ptr.py

copy the script to `/etc/powerdns/ptr.py`

and

```shell
chmod 750 /etc/powerdns/ptr.py
chown root:pdns /etc/powerdns/ptr.py
```

in some cases you might need to add
```
unix_socket="/var/run/mysqld/mysqld.sock"
```
as arg to `pymysql.connect`

## restart pdns service

the script will log to syslog
