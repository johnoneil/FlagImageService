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
  1)Request a list of countries (returned as ):
  GET http://www.demo.com/flagservice/countries <lists names and isoalpha2 codes in json dict>
  GET http://www.demo.com/flagservice/countries/names
  GET http://www.demo.com/flagservice/countries/isoalpha2
  
  2)Request a flag image for a country given its isov2 abbreviation
  GET http://www.demo.com/flagservice/countries/us/image

  3)Request a random iosv2 country name, isov2 abbreviation
  GET http://www.demo.com/flagservice/countries/random

  4)Request the country associated with a nick (as json)
  GET http://www.demo.com/flagservice/nicks/NICK/country/name
  GET http://www.demo.com/flagservice/nicks/NICK/country/isoalpha2

  5)Request an image of the flag associated with a given nick
  GET http://www.demo.com/flagservice/nicks/NICK/country/image

  6)Create or update a new user with a nick, country ISOV2 abbreviation and password
  PUT http://www.demo.com/flagservice/nicks <payload contains json for nick, country and possibly password>

  8)Delete a nick entry from database
  DELETE http://www.demo.com/flagservice/nicks <payload contains json for nick, country and possibly password>

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
  def get(self):
    self.render("test.html")

class ListCountries(tornado.web.RequestHandler):
  def get(self, **params):
    self.write(json.dumps(self.application.countries,sort_keys=True, indent=4))

class ListCountryNames(tornado.web.RequestHandler):
  def get(self, **params):
    countries = {'countries':self.application.countries.keys() }
    self.write(json.dumps((countries),sort_keys=True, indent=4))

class ListCountriesisoalpha2(tornado.web.RequestHandler):
  def get(self, **params):
    countries = {'isoalpha2':self.application.countries.values() }
    self.write(json.dumps((countries),sort_keys=True, indent=4))

class GetFlagForCountry(tornado.web.StaticFileHandler):
  def get(self, **params):
    country = params['country']
    print 'requesting flag for country :' + country
    return super(GetFlagForCountry, self).get('/home/joneil/code/FlagImageService/image/' + country + '.gif', True)

class RandomCountry(tornado.web.RequestHandler):
  def get(self, **params):
    country = random.choice(self.application.countries.keys())
    random_choice = {country:self.application.countries[country]}
    self.write(json.dumps(random_choice,sort_keys=True, indent=4))

class GetCountryForNick(tornado.web.RequestHandler):
  def get(self, **params):
    nick = params['nick']
    country = self.application.get_country(nick)
    print nick + ' has assigned country ' + country
    assigned_country = {nick:country}
    self.write(json.dumps(assigned_country,sort_keys=True, indent=4))

class GetFlagForNick(tornado.web.StaticFileHandler):
  def get(self, **params):
    nick = params['nick']
    country = self.application.get_country(nick)
    if country:
      flag = self.application.countries[country]
    else:
      flag = 'fag'
    print nick + ' has assigned flag ' + flag
    return super(GetFlagForNick, self).get('/home/joneil/code/FlagImageService/image/' + flag + '.gif', True)

class CreateOrUpdateNick(tornado.web.RequestHandler):
  def put(self):
    (nick, country, password) = self.GetPayload()
    self.application.set_country(nick, country, password)
  def delete(self):
    payload = self.request.body
    j = json.loads(payload)
    nick = j['nick']
    password = j['password']
    self.application.RemoveNickEntry(nick,password)
  def GetPayload(self):
    payload = self.request.body
    j = json.loads(payload)
    nick = j['nick']
    country = j['country']
    password = j['password']
    return (nick, country, password)
      

class FlagWebService(tornado.web.Application):
  def __init__(self, image_path):

    handlers = [
      (r'/countries', ListCountries),
      (r'/countries/names', ListCountryNames),
      (r'/countries/isoalpha2', ListCountriesisoalpha2),
      (r'/countries/random', RandomCountry),
      (r'/countries/?(?P<country>[A-Za-z]+)?/image',GetFlagForCountry, {'path': image_path}),
      (r'/nicks/?(?P<nick>[A-Za-z0-9-_]+)?/country/name',GetCountryForNick),
      (r'/nicks/?(?P<nick>[A-Za-z0-9-_]+)?/country/image',GetFlagForNick,{'path': image_path}),
      (r'/nicks',CreateOrUpdateNick),
      (r"/test",TestPage),
    ]
    settings = dict(
      image_path=image_path,
      debug=True,
    )
    super(FlagWebService,self).__init__(handlers,**settings)
    self.flags = filter(lambda x: x.endswith('.gif'), os.listdir(settings['image_path']))
    self.flags = [ os.path.splitext(e)[0] for e in self.flags ]
    self.countries = {}
    for entry in self.flags:
      #pycountry appears to be weak in the area of key errors
      try:
        iso_country = pycountry.countries.get(alpha2=entry.upper())
      except KeyError, e:
        self.countries[entry] = entry
      if(iso_country):
        self.countries[iso_country.name] = entry
      else:
        self.countries[entry] = entry

    self.database = FlagServiceDatabase.FlagServiceDatabase()
    self.database.CreateTableIfNoneExists()

  def get_country(self, nick):
    country = self.database.ReadCountry(nick)
    if country == None:
      return 'fag'
    else:
      return country

  def set_country(self, nick, country, password=''):
    self.database.WriteCountry(nick, country, password)
    #todo: see if it's a valid flag
    return country

  def RemoveNickEntry(self,nick,password=''):
    self.database.DeleteNickEntry(nick, password)

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
