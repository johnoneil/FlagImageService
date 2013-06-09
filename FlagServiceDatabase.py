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
import hashlib
import uuid

#Set up and parse command line options using Tornado wrappers
#this is quick, but probably not advisable in the long term
from tornado.options import define, options
define("mysql_host", default="127.0.0.1", help="database host")
define("mysql_database", default="irc", help="database name")
define("mysql_user", default="ircuser", help="database user")
define("mysql_password", default="", help="database password")

IRCUserDataTableName = 'UserData'


class FlagServiceDatabase:
  def __init__(self):
    self.database = sql.connect(options.mysql_host, options.mysql_user, 
      options.mysql_password, options.mysql_database,use_unicode=1,charset="utf8")
    self.CreateTableIfNoneExists()

  def CreateTableIfNoneExists(self):
    cursor =  self.database.cursor()
    if cursor is not None:
      cursor.execute( 'CREATE TABLE IF NOT EXISTS UserData \
      (\
        id INT NOT NULL AUTO_INCREMENT PRIMARY KEY UNIQUE,\
        timestamp TIMESTAMP DEFAULT NOW(),\
        created TIMESTAMP,\
        nick VARCHAR(255) UNIQUE NOT NULL,\
        country VARCHAR(255) NOT NULL,\
        password VARCHAR(4096),\
        salt VARCHAR(4096)\
        );')
      result = cursor.fetchall()
      cursor.close()

  def ReadCountry(self, nick):
    cursor = self.database.cursor()
    if(cursor is not None):
      query = 'SELECT * FROM UserData WHERE nick = \'{0}\''.format(nick)
      print query
      rows = cursor.execute(query)
      result = cursor.fetchone()
      if result:
        print result
        return result[4]
      cursor.close()
    return None

  def ReadHash(self, nick):
    cursor = self.database.cursor()
    if(cursor is not None):
      query = 'SELECT * FROM UserData WHERE nick = \'{0}\''.format(nick)
      print query
      rows = cursor.execute(query)
      result = cursor.fetchone()
      if result:
        print result
        server_hash = result[5]
        server_salt = result[6]
        return (server_hash, server_salt)
      cursor.close()
    return (None,None)

  def CheckPassword(self,nick, password):
    (server_hash, server_salt) = self.ReadHash(nick)
    if(server_hash is not None and server_hash != ''):
      client_hash = hashlib.sha512(password + server_salt).hexdigest()
      if server_hash != client_hash:
        print "PASSWORD FAILURE: " + password + ' != ' + server_hash
        return False
      else:
        print "PASSWORD SUCCESS: " + password + ' == ' + server_hash
        return True
    else:
      print 'PASSWORD SUCCESS by empty server_hash'
      return True #no hash in server DB, so all passwords pass

  def GenerateHash(self, password):
    client_hash = ''
    client_salt = ''
    if(password):
      client_salt = salt = uuid.uuid4().hex
      client_hash = hashlib.sha512(password + salt).hexdigest()
    return (client_hash, client_salt)
    
  def WriteCountry(self, nick, country, password=''):
    if self.CheckPassword(nick, password) == False:
      #TODO: throw or return failure
      return False
    cursor = self.database.cursor()
    if( cursor is not None):
      sqlcommand = 'UPDATE UserData SET country=\'{0}\' WHERE nick=\'{1}\';'.format(country, nick)
      print sqlcommand
      r = cursor.execute( sqlcommand )
      if(r == 0):#no value updated above, insert a new entry
        (client_hash, client_salt) = self.GenerateHash(password)
        sqlcommand = 'INSERT INTO UserData(nick, country, password,salt)\
        VALUES (\'{0}\', \'{1}\',\'{2}\',\'{3}\');'.format(nick, country, client_hash, client_salt)
        print sqlcommand
        cursor.execute( sqlcommand )
        #result = cursor.fetchall()
      cursor.close()
    return True

  def DeleteNickEntry(self, nick, password=''):
    if self.CheckPassword(nick, password) == False:
      #TODO: throw failure or return failure?
      return False
    cursor = self.database.cursor()
    if cursor is not None:
      query = "delete from UserData where nick = '%s' " % nick
      cursor.execute(query)
      #TODO: return success
      return True
    return False

  def close(self):
    if(self.database):
      self.database.close()



