#!/usr/bin/python
 # vim: set ts=2 expandtab:
"""
Module: FlagServiceDatabase
Desc:
Author: John O'Neil
Email:

"""

import MySQLdb as sql
import string
import sys
import random

#Set up and parse command line options using Tornado wrappers
#this is quick, but probably not advisable in the long term
from tornado.options import define, options
define("mysql_host", default="127.0.0.1", help="database host")
define("mysql_database", default="irc", help="database name")
define("mysql_user", default="ircuser", help="database user")
define("mysql_password", default="", help="database password")


class FlagServiceDatabase:
  def __init__(self):
    self.database = sql.connect(options.mysql_host, options.mysql_user, 
      options.mysql_password, options.mysql_database,use_unicode=1,charset="utf8")
    self.CreateTableIfNoneExists()

  def CreateTableIfNoneExists(self):
    cursor =  self.database.cursor()
    if cursor is not None:
      cursor.execute( 'CREATE TABLE IF NOT EXISTS flags \
      (\
        id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,\
        timestamp TIMESTAMP DEFAULT NOW(),\
        created TIMESTAMP,\
        nick VARCHAR(4096),\
        country VARCHAR(4096),\
        password VARCHAR(4096)\
        );')
      result = cursor.fetchall()
      cursor.close()

  def ReadCountry(self, nick):
    cursor = self.database.cursor()
    if(cursor is not None):
      query = 'SELECT * FROM flags WHERE nick = \'{0}\''.format(nick)
      print query
      rows = cursor.execute(query)
      result = cursor.fetchone()
      if result:
        print result
        return result[4]
      cursor.close()
    return None
    
  def WriteCountry(self, nick, country, password=''):
    cursor = self.database.cursor()
    if( cursor is not None):
      sqlcommand = 'INSERT INTO flags(nick, country, password)\
        VALUES (\'{0}\', \'{1}\',\'{2}\');'.format(nick, country, password)
      print sqlcommand
      cursor.execute( sqlcommand )
      #result = cursor.fetchall()
      cursor.close()

  def close(self):
    if(self.database):
      self.database.close()



