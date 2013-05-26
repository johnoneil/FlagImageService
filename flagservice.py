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
  def __init__(self):#, handlers=None, default_host='', transforms=None, wsgi=False, **settings):
    image_path = '/home/joneil/code/flagservice/image'
    handlers = [
      (r"/", FlagRequestHandler, {'path': '/home/joneil/code/flagservice/image'}),
      (r"/test",TestPage),
    ]
    settings = dict(
      image_path=os.path.join(os.path.dirname(__file__), "image"),
      debug=True,
    )
    super(FlagWebService,self).__init__(handlers,**settings)
    
    self.flag_database = {}
    self.flags = glob.glob(image_path +'/*.gif')

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

def main():

  application = FlagWebService()
  application.listen(8880)
  tornado.ioloop.IOLoop.instance().start()
 
if __name__ == "__main__":
  main()
