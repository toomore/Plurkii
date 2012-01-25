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
from datamodel import userplurkdata,datacofriend

def ckini(s):
  try:
    return int(s)
  except:
    return False

class MainHandler(webapp.RequestHandler):
  def get(self):
    p2uinmem = []
    p2u = {}
    tv = {}
    if ckini(self.request.get('u')) == False:
      q = userplurkdata.gql("WHERE uname = '%s'" % self.request.get('u').replace(' ',''))
      for i in q:
        p2u['key'] = i.key().id_or_name()
        p2u['uname'] = i.uname
        p2u['fullname'] = i.fullname
        p2u['birthday'] = i.birthday
        p2u['location'] = i.location
        p2u['avatar'] = i.avatar
        p2uinmem.append(p2u.copy())
    else:
      try:
        q = userplurkdata.get_by_key_name(str(int(self.request.get('u').replace(' ',''))))
        p2u['key'] = q.key().id_or_name()
        p2u['uname'] = q.uname
        p2u['fullname'] = q.fullname
        p2u['birthday'] = q.birthday
        p2u['location'] = q.location
        p2u['avatar'] = q.avatar
        p2uinmem.append(p2u.copy())
      except:
        self.redirect('/')

    op = u'序號 ID 暱稱 生日 地區 頭像數<br>'
    for i in p2uinmem:
      if i['avatar'] > 0:
        '''
        i['pics'] = ''
        for no in range(2,i['avatar']+2,2):
          i['pics'] += "<img alt='' src='http://avatars.plurk.com/%s-big%s.jpg'>" % (i['key'],no)
        '''
        tv['avatar'] = i['avatar']
      else:
        i['avatar'] = None
        tv['avatar'] = 0
      op += u'''
        <a href="/byid?u=%(key)s"><span id="uid">%(key)s</span></a> %(uname)s %(fullname)s %(birthday)s %(location)s <span id="no">%(avatar)s</span><br>
        <button type="button" onclick="addpics()">增加照片</button><br>
        <span id="demo"></span><br>
        <span id="loadpics"></span><br>
        ''' % i
      tv['onload'] = " onLoad='loadpics()'"
      tv['key'] = i['key']

    tv['op'] = op
    tv['nick_name'] = self.request.get('u')
    self.response.out.write(template.render('./template/h_index.htm',{'tv':tv}))

class byid(webapp.RequestHandler):
  def get(self):
    try:
      uid = str(self.request.get('u'))
      self.response.out.write(template.render('./template/h_byid.htm',{'uid':uid}))
    except:
      self.redirect('/byid')

class Tolist(webapp.RequestHandler):
  def get(self):
    a = userplurkdata.all()
    for i in a:
      print '123'
      print i.key().id_or_name(),i.uname

class chlow(webapp.RequestHandler):
  def get(self):
    addcklow = memcache.get('addcklow')
    print '123'
    print addcklow
    if addcklow:
      data = userplurkdata.gql("limit %s,5" % str(5 * addcklow))
      for i in data:
        i.uname = i.uname.lower()
        #i.cklowstr = True
        i.put()
        print i.uname
      memcache.incr('addcklow')
    else:
      memcache.incr('addcklow',initial_value=0)

class delooo(webapp.RequestHandler):
  def get(self):
    deldata = datacofriend.all().fetch(100)
    for i in deldata:
      i.delete()

def main():
  """ Start up. """
  application = webapp.WSGIApplication([('/', MainHandler),
                                        ('/byid', byid),
                                        ('/.*',MainHandler)],debug=True)
  run_wsgi_app(application)

if __name__ == '__main__':
  main()
