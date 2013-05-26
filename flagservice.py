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

class MainHandler(tornado.web.StaticFileHandler):
  def __init__(self, application, request, **kwargs):
    tornado.web.StaticFileHandler.__init__(self, application, request, **kwargs)
    self.flag_database = {}
    self.flags = glob.glob("/home/joneil/code/flagservice/image/*.gif")
  def get(self):
    #pull the nick out of our request
    nick = self.get_argument('nick','random', True)
    print "nick is :" + nick
    
    #fetch the flag assigned to this nick
    #if one isn't assigned a random one will be assigned
    flag = self.get_flag(nick)
    print 'assigned flag is :' + flag
    return super(MainHandler, self).get(flag, True)   

  def get_flag(self, nick):
    #really, this should be a lookup via sql database, but
    #I'm not doing that tonight
    if not nick in self.flag_database:
      self.set_flag(nick)
    return self.flag_database[nick]

  def set_flag(self, nick, flag = None):
    if flag is None:
      self.flag_database[nick] = random.choice(self.flags)
    #todo: see if it's a valid flag
    return self.flag_database[nick]
 
class TestPage(tornado.web.RequestHandler):
	def get(self):
		self.render("test.html")   

def main():
  application = tornado.web.Application([
      (r"/", MainHandler, {'path': '/home/joneil/code/flagservice/image'}),
      (r"/test",TestPage),
      #(r"/image/(.*)", tornado.web.StaticFileHandler, {'path': '/home/joneil/code/flagservice/image'}),
  ])
  application.listen(8880)
  tornado.ioloop.IOLoop.instance().start() 
 
if __name__ == "__main__":
  main()
