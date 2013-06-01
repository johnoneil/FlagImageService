#!/usr/bin/python
 # vim: set ts=2 expandtab:
"""
Module: flagservice
Desc:
Author: John O'Neil
Email:

  This is an attempt at a simple RESTful api
  to provide little flags for IRC users (just associate
  countries and flag images with irc nicks). I'm not
  building in security (no passwords) so anyone should
  be able to reassign someone's flag (i don't care really,
  it's just an experiment).
  it should work as follows:
  1)Request a list of countries (returned as json):
  http://www.demo.com/flagservice/countries
  2)Request the country associated with a nick (as json)
  http://www.demo.com/flagservice/NICK/country
  3)Request an image of the flag associated with a given nick
  http://www.demo.com/flagservice/NICK/country/image
  4)Requst an image of any country's flag
  http://www.demo.com/flagservice/countries/XX/image (where XX is the ISOv2 country abbreviation)
  5)Create a nick entry associated with a country, or update a nick's associated country:
  http://www.demo.com/flagservice/NICK/?country=xx

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
import FlagServiceDatabase
import pycountry


class TestPage(tornado.web.RequestHandler):
  def post(self):
    # nick = self.get_argument('nick','random', True)
    # print "nick is :" + nick

    #Pull an optional 'country' argument out of request
    #if the country argument exists, this is an attempt to set
    #a nick/country association
    #country = self.get_argument('country',None)
    #if(country):
    #  print 'country is ' + country
    #  iso_country = pycountry.countries.get(name=country)
    #  if(iso_country):
    #    print 'country iso name = ' + iso_country.alpha2
    self.render("test.html")

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
  

  def post(self):
    nick = self.get_argument('nick','random', True)
    print "nick is :" + nick

    #Pull an optional 'country' argument out of request
    #if the country argument exists, this is an attempt to set
    #a nick/country association
    country = self.get_argument('country',None)
    if(country):
      print 'country is ' + country
      iso_country = pycountry.countries.get(name=country)
      if(iso_country):
        print 'country iso name = ' + iso_country.alpha2

class ListCountries(tornado.web.RequestHandler):
  def get(self, **params):
    countries = {'countries':self.application.flags}
    self.write(json.dumps((countries),sort_keys=True, indent=4))

class GetFlagForCountry(tornado.web.StaticFileHandler):
  def get(self, **params):
    country = params['country']
    print 'requesting flag for country :' + country
    return super(GetFlagForCountry, self).get('/home/joneil/code/FlagImageService/image/' + country + '.gif', True)

class GetCountryForNick(tornado.web.RequestHandler):
  def get(self, **params):
    nick = params['nick']
    country = self.application.get_flag(nick)
    print nick + ' has assigned country ' + country
    assigned_country = {nick:country}
    self.write(json.dumps(assigned_country,sort_keys=True, indent=4))
    #self.write(country)

class GetFlagForNick(tornado.web.StaticFileHandler):
  def get(self, **params):
    nick = params['nick']
    country = self.application.get_flag(nick)
    print nick + ' has assigned country ' + country
    return super(GetFlagForNick, self).get('/home/joneil/code/FlagImageService/image/' + country + '.gif', True)

class SetFlagForNick(tornado.web.RequestHandler):
  def set(self, **params):
    nick = params['nick']
    country = params['country']
    self.application.set_flag(nick,country)
      

class FlagWebService(tornado.web.Application):
  def __init__(self, image_path):

    handlers = [
      (r'/countries', ListCountries),
      (r'/countries/?(?P<country>[A-Za-z]{2})?/image',GetFlagForCountry, {'path': image_path}),
      (r'/nick/?(?P<nick>[A-Za-z0-9-_]+)?/country',GetCountryForNick),
      (r'/nick/?(?P<nick>[A-Za-z0-9-_]+)?/country/image',GetFlagForNick,{'path': image_path}),
      (r'/nick/?(?P<nick>[A-Za-z0-9-_]+)?/country/?(?P<country>[A-Za-z]{2})?',SetFlagForNick),
      (r"/", FlagRequestHandler, {'path': image_path}),
      (r"/test",TestPage),
    ]
    settings = dict(
      image_path=image_path,
      debug=True,
    )
    super(FlagWebService,self).__init__(handlers,**settings)
    self.flags = filter(lambda x: x.endswith('.gif'), os.listdir(settings['image_path']))
    self.flags = [ os.path.splitext(e)[0] for e in self.flags ]
    #self.flags = [ os.path.splitext(e)[0] for e in glob.glob(settings['image_path'] +'/*.gif')]
    self.database = FlagServiceDatabase.FlagServiceDatabase()
    self.database.CreateTableIfNoneExists()

  def get_flag(self, nick):
    if nick == 'random':
      return random.choice(self.flags)
    flag = self.database.ReadFlag(nick)
    if flag is None:
      return self.set_flag(nick)
    else:
      return flag

  def set_flag(self, nick, flag = None):
    if flag is None:
      flag = random.choice(self.flags)
      self.database.WriteFlag(nick, flag)
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
      application.database.close()
 
if __name__ == "__main__":
  main()
