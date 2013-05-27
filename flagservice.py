#!/usr/bin/python
 # vim: set ts=2 expandtab:
"""
Module: flagservice
Desc:
Author: John O'Neil
Email:

"""
#!/usr/bin/python
 
import tornado.web
import tornado.websocket
import tornado.ioloop
import tornado.iostream
import MySQLdb as sql
import socket
import string
import json
import time
import datetime
import calendar
import os
import re
import glob
import random
import sys

#Set up and parse command line options using Tornado wrappers
#this is quick, but probably not advisable in the long term
from tornado.options import define, options
define("mysql_host", default="127.0.0.1", help="database host")
define("mysql_database", default="irc", help="database name")
define("mysql_user", default="ircuser", help="database user")
define("mysql_password", default="", help="database password")

class TestPage(tornado.web.RequestHandler):
	def get(self):
		self.render("test.html")

class FlagRequestHandler(tornado.web.StaticFileHandler):
  def get(self):
    #pull the nick out of our request
    nick = self.get_argument('nick','random', True)
    print "nick is :" + nick
    
    #fetch the flag assigned to this nick
    #if one isn't assigned a random one will be assigned
    flag = self.application.get_flag(nick)
    print 'assigned flag is :' + flag
    return super(FlagRequestHandler, self).get(flag, True)   

class FlagWebService(tornado.web.Application):
  def __init__(self, image_path):

    handlers = [
      (r"/", FlagRequestHandler, {'path': image_path}),
      (r"/test",TestPage),
    ]
    settings = dict(
      image_path=image_path,
      debug=True,
    )
    super(FlagWebService,self).__init__(handlers,**settings)
    
    self.flags = glob.glob(settings['image_path'] +'/*.gif')
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
        flag VARCHAR(4096)\
        );')
      result = cursor.fetchall()
      cursor.close()

  def ReadFlag(self, nick):
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
    
  def WriteFlag(self, nick, flag):
    cursor = self.database.cursor()
    if( cursor is not None):
      sqlcommand = 'INSERT INTO flags(nick, flag)\
        VALUES (\'{0}\', \'{1}\');'.format(nick, flag)
      print sqlcommand
      cursor.execute( sqlcommand )
      #result = cursor.fetchall()
      cursor.close()

  def get_flag(self, nick):
    flag = self.ReadFlag(nick)
    if flag is None:
      return self.set_flag(nick)
    else:
      return flag

  def set_flag(self, nick, flag = None):
    if flag is None:
      flag = random.choice(self.flags)
      self.WriteFlag(nick, flag)
    #todo: see if it's a valid flag
    return flag

def main():

  application = None
  try:
    tornado.options.parse_command_line()

    application = FlagWebService('/home/joneil/code/FlagImageService/image')
    application.listen(8880)
    tornado.ioloop.IOLoop.instance().start()
  except sql.Error, e:
    print "Error %d: %s" % (e.args[0], e.args[1])
    sys.exit(1)

  finally:
    if application:
      database.close()
 
if __name__ == "__main__":
  main()
