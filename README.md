[![pylint](https://github.com/zerwes/powerdns-pipe-ptr/actions/workflows/pylint.yml/badge.svg)](https://github.com/zerwes/powerdns-pipe-ptr/actions/workflows/pylint.yml)

# powerdns-pipe-ptr

a simple script to be used via [powerdns](https://github.com/PowerDNS/pdns) pipe backend

it is intended to resolve reverse lookups based on the existing `A` records via the gmysql backend,
as the `set-ptr` option has been removed (see https://github.com/PowerDNS/pdns/pull/7797)

## requirements

### SOA

the reverse zones in question should be created in pdns

### gmysql

the script will just work for records registered in the `gmysql` backend and uses the database connection registered for `gmysql` in the `pdns.conf` file

### pdns.conf

add the following lines to your `pdns.conf`

```
zone-cache-refresh-interval=0
launch+=pipe
pipe-regex=^.*\.in-addr\.arpa$
pipe-command=/etc/powerdns/ptr.py
```

# ptr.py

copy the script to `/etc/powerdns/ptr.py`

and

```shell
chmod 750 /etc/powerdns/ptr.py
chown root:pdns /etc/powerdns/ptr.py
```

# restart pdns service

the script will log to syslog
