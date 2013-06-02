#!/usr/bin/python
 # vim: set ts=2 expandtab:
"""
Module: set_nick
Desc:
Author: John O'Neil
Email:

  Test script for simple RESTful irc flag server

  meant to implement the following HTTP PUT 

  6)Create or update a new user with a nick, country ISOV2 abbreviation and password
  PUT http://www.demo.com/flagservice/nicks <payload contains json for nick, country and possibly password>

"""
#!/usr/bin/python
 
import json
import os
import sys
import requests


def main():

  if len(sys.argv) < 3 :
    print 'USAGE: set_nick <nick> <country> [<password>]'
    sys.exit()
  nick = sys.argv[1]
  country = sys.argv[2]
  password = ''
  if (len(sys.argv) > 3):
    password = sys.argv[3]    
  
  payload = {'nick': nick, 'country': country, 'password': password}
  r = requests.put("http://192.168.1.6:8880/nicks", data=payload)
  
  print 'returned status code : ' + r.status_code
  print 'returned content: ' + r.content

if __name__ == "__main__":
  main()
