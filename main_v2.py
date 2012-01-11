#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" Main WSGI. """
'''
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
from google.appengine.dist import use_library
use_library('django', '1.2')
'''
from google.appengine.ext import webapp
from google.appengine.api import memcache
from google.appengine.ext.db import GqlQuery
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template
from datamodel import userplurkdata

class MainHandler(webapp.RequestHandler):
  def get(self):
    q = userplurkdata.gql("WHERE uname = '%s'" % self.request.get('u'))
    p2uinmem = []
    p2u = {}
    for i in q:
      p2u['key'] = i.key().id_or_name()
      p2u['uname'] = i.uname
      p2u['fullname'] = i.fullname
      p2u['birthday'] = i.birthday
      p2u['location'] = i.location
      p2u['avatar'] = i.avatar
      p2uinmem.append(p2u.copy())
    op = u'序號 ID 暱稱 生日 地區 頭像數<br>'
    for i in p2uinmem:
      if i['avatar'] > 0:
        i['pics'] = ''
        for no in range(2,i['avatar']*10,2):
          i['pics'] += "<img src='http://avatars.plurk.com/%s-big%s.jpg'>" % (i['key'],no)
      else:
        i['pics'] = None
      op += '%(key)s %(uname)s %(fullname)s %(birthday)s %(location)s %(avatar)s<br>%(pics)s<br>' % i
    self.response.out.write(op)

def main():
  """ Start up. """
  application = webapp.WSGIApplication([('/', MainHandler),
                                        ('/.*',MainHandler)],debug=True)
  run_wsgi_app(application)

if __name__ == '__main__':
  main()
