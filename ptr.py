#! /usr/bin/env python
# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4 smartindent
# pylint: disable=invalid-name

"""
(c) 2024 Klaus Zerwes zero-sys.net
This package is free software.
This software is licensed under the terms of the
GNU GENERAL PUBLIC LICENSE version 3 or later,
as published by the Free Software Foundation.
See https://www.gnu.org/licenses/gpl.html
"""

import sys
import syslog
import configparser
import pymysql.cursors

__doc__ = """
simple pdns pipe backend script generating ptr records as
reverse resolution of registered A via the gmysqlbackend
"""

def _send_resp(msg):
    sys.stdout.write(msg + '\n')
    sys.stdout.flush()
    syslog.syslog(f"send resp {msg}")

config = configparser.ConfigParser(strict=False)
with open("/etc/powerdns/pdns.conf", 'r', encoding="utf-8") as stream:
    config.read_string("[PDNS]\n" + stream.read())

try:
    dbname = config['PDNS']['gmysql-dbname']
    dbhost = config['PDNS']['gmysql-host']
    dbuser = config['PDNS']['gmysql-user']
    dbpass = config['PDNS']['gmysql-password']
except KeyError as e:
    sys.exit(f"KeyError from ini cfg : {e}")

# db connect
connection = pymysql.connect(
        host=dbhost,
        user=dbuser,
        password=dbpass,
        database=dbname,
        cursorclass=pymysql.cursors.DictCursor
    )

"""main program loop"""
syslog.syslog("startup ...")
first_loop = True
while True:
    rawline = sys.stdin.readline()
    if rawline == '':
        syslog.syslog("EOF received; exiting")
        sys.exit(0)
    line = rawline.rstrip()
    syslog.syslog(f"received request {line}")
    if first_loop:
        first_loop = False
        if line == 'HELO\t1':
            _send_resp('OK\tpython ptr pipe backend firing up')
        else:
            syslog.syslog("HELO was missing!")
            _send_resp('FAIL')
            sys.exit(1)
    else:
        query = line.split('\t')
        if len(query) != 6:
            syslog.syslog("ERROR unparseable line")
            _send_resp('LOG\tunparseable line')
            _send_resp('FAIL')
            sys.exit(2)
        # Q qname       qclass  qtype   id  remote-ip-address
        # Q 1.20.168.192.in-addr.arpa IN SOA -1 0.0.0.0
        qname = query[1]
        qtype = query[3]
        if qtype == 'SOA':
            syslog.syslog(f"qname:{qname} qtype:{qtype}")
            qarr = qname.split('.')
            i = 0
            mi = len(qarr)
            while i < mi:
                domain = '.'.join(qarr[i:])
                i += 1
                with connection.cursor() as cursor:
                    # pylint: disable=line-too-long
                    sql = f"SELECT name,ttl,content FROM records WHERE type LIKE 'SOA' AND disabled=0 AND name LIKE '{domain}'"
                    cursor.execute(sql)
                    result = cursor.fetchone()
                    if result and 'name' in result.keys():
                        _send_resp(f"DATA\t{result['name']}\tIN\t{qtype}\t{result['ttl']}\t-1\t{result['content']}")
                        i = mi
        if qtype in ['PTR', 'ANY']:
            ip = '.'.join(qname.split('.')[0:4][::-1])
            syslog.syslog(f"qname:{qname} qtype:{qtype} ip:{ip}")
            with connection.cursor() as cursor:
                # pylint: disable=line-too-long
                sql = f"SELECT name,ttl FROM records WHERE type = 'A' AND disabled = 0 AND content LIKE '{ip}' LIMIT 0,1"
                cursor.execute(sql)
                result = cursor.fetchone()
                if result and 'name' in result.keys():
                    # DATA    qname       qclass  qtype   ttl id  content
                    _send_resp(f"DATA\t{qname}\tIN\tPTR\t{result['ttl']}\t-1\t{result['name']}")
                else:
                    _send_resp(f"LOG: no ptr found for {qname} ({ip}")
        _send_resp('END')
