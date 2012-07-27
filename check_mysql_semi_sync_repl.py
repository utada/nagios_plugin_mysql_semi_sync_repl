#!/usr/bin/env python26

import sys
import socket
import argparse
import MySQLdb
from MySQLdb import cursors

class Nagios_semi_repl_check:
  nagios_codes = dict(OK=0, WARNING=1, CRITICAL=2, UNKNOWN=3, DEPENDENT=4)

  def nagios_return(self, code, response):
    print (code+': '+response)

  def opt_parse(self):
    parser = argparse.ArgumentParser(description="redis check nagios plugin")
    parser.add_argument('-H', dest='hostname', default='127.0.0.1', help='hostname (default: %(default)s)')
    parser.add_argument('-P', dest='port', default='3306', help='port (default: %(default)s)')
    parser.add_argument('-u', dest='username', default='root', help='username (default: %(default)s)')
    parser.add_argument('-p', dest='password', default='', help='password (default: %(default)s)')
    parser.add_argument('repl', choices=['master','slave'], help='master or slave')

    return parser.parse_args()

  def mysql_conn(self, args):
    try:
      conn = MySQLdb.connect(host=args.hostname,
                     user=args.username,
                     passwd=args.password,
                     port=int(args.port),
                     charset="utf8",
                     cursorclass = cursors.SSCursor)
    except MySQLdb.Error, e:
      self.nagios_return('CRITICAL', str(repr(e)))
      sys.exit(self.nagios_codes['CRITICAL'])
    return conn

  def check_version(self, conn):
    cur = conn.cursor()
    cur.execute('select version()')
    return cur.fetchall()

  def check_status(self, conn):
    cur = conn.cursor()
    cur.execute('show status')
    return cur.fetchall()

  def main(self):
    args = self.opt_parse()
    con = self.mysql_conn(args)
    semi_sync_master_status = 'OFF'
    semi_sync_slave_status  = 'OFF'
    for row in self.check_status(con):
      if row[0] == 'Rpl_semi_sync_master_status':
        semi_sync_master_status = row[1]
      if row[0] == 'Rpl_semi_sync_slave_status':
        semi_sync_slave_status = row[1]
    if args.repl == 'master':
      if semi_sync_master_status == 'ON':
        self.nagios_return('OK', args.hostname+':'+args.port+' Rpl_semi_sync_master_status = '+semi_sync_master_status)
      else:
        self.nagios_return('CRITICAL', args.hostname+':'+args.port+' Rpl_semi_sync_master_status = '+semi_sync_master_status)
    if args.repl == 'slave':
      if semi_sync_slave_status == 'ON':
        self.nagios_return('OK', args.hostname+':'+args.port+' Rpl_semi_sync_slave_status = '+semi_sync_slave_status)
      else:
        self.nagios_return('CRITICAL', args.hostname+':'+args.port+' Rpl_semi_sync_slave_status = '+semi_sync_slave_status)

if __name__ == "__main__":
  Nagios_semi_repl_check().main()



