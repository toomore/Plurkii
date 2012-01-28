#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" Main WSGI. """

import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
from google.appengine.dist import use_library
use_library('django', '1.2')

from google.appengine.ext import webapp
from google.appengine.api import memcache
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template
from datamodel import userplurkdata
import plurklib
import logging

class MainHandler(webapp.RequestHandler):
  def get(self):
    p2uinmem = []
    p2u = {}
    tv = {}
    get_u = str(self.request.get('u').replace(' ',''))
    if len(get_u) == 0:
      pass
    else:
      if get_u.isdigit() == False:
        q = userplurkdata.gql("WHERE uname = '%s'" % get_u)
        if q.count() == 0:
          try:
            uname = get_u.lower()
            uno = memcache.get(uname)
            if uno:
              logging.info('Useing memcache: %s %s' % (uname,uno))
              self.redirect('/byid?u=%s' % uno)
            else:
              p = plurklib.PlurkAPI('mCDwgcld4WKj1GFzZPB7mJlgm9lSHwks')
              uno = p.usernameToUid(uname)
              memcache.set(uname,uno)
              logging.info('Add memcache: %s %s' % (uname,uno))
              self.redirect('/byid?u=%s' % uno)
          except:
            logging.info('plurklib connect error.(by user nickname)')
            self.redirect('/')
        else:
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
          q = userplurkdata.get_by_key_name(get_u)
          p2u['key'] = q.key().id_or_name()
          p2u['uname'] = q.uname
          p2u['fullname'] = q.fullname
          p2u['birthday'] = q.birthday
          p2u['location'] = q.location
          p2u['avatar'] = q.avatar
          p2uinmem.append(p2u.copy())
        except:
          try:
            p = plurklib.PlurkAPI('mCDwgcld4WKj1GFzZPB7mJlgm9lSHwks')
            uno = p.usernameToUid(get_u)
            self.redirect('/byid?u=%s' % uno)
          except:
            logging.info('plurklib connect error.(by search uid)')
            self.redirect('/')

    op = u'序號 ID 暱稱 生日 地區 頭像數<br>'
    for i in p2uinmem:
      if i['avatar'] > 0:
        tv['avatar'] = i['avatar']
      else:
        i['avatar'] = None
        tv['avatar'] = 0
      if len(p2uinmem) > 1:
        op += u'''
          <a href="/byid?u=%(key)s"><div class="listq"><span id="uid">%(key)s</span> %(uname)s %(fullname)s %(birthday)s %(location)s <span id="no">%(avatar)s</span></div></a><br>
          ''' % i
        tv['key'] = i['key']
      else:
        op += u'''
          <a href="/byid?u=%(key)s"><span id="uid">%(key)s</span></a> %(uname)s %(fullname)s %(birthday)s %(location)s <span id="no">%(avatar)s</span><br>
          <button type="button" onclick="addpics()">增加顯示照片</button><br>
          <span id="demo"></span><br>
          <span id="loadpics"></span><br>
          <img alt="" src="http://avatars.plurk.com/%(key)s-big.jpg">
          ''' % i
        tv['onload'] = " onLoad='loadpics()'"
        tv['key'] = i['key']

    tv['op'] = op
    tv['nick_name'] = get_u
    self.response.out.write(template.render('./template/h_index.htm',{'tv':tv}))

class byid(webapp.RequestHandler):
  def get(self):
    uno = self.request.get('u').replace(' ','')
    if len(uno) == 0:
      self.response.out.write(template.render('./template/h_byid.htm',{}))
    else:
      try:
        uno = int(uno)
        try:
          uinfo = memcache.get(str(uno),'userinfo')
          if uinfo:
            logging.info('Use userinfo memcache')
          else:
            try:
              p = plurklib.PlurkAPI('mCDwgcld4WKj1GFzZPB7mJlgm9lSHwks')
              uinfo = p.get_user_info(uno)
              memcache.set(str(uno),uinfo,namespace='userinfo')
            except:
              memcache.set(str(uno),' ',namespace='userinfo')
            logging.info('Set userinfo memcache')
          self.response.out.write(template.render('./template/h_byid.htm',{'tv':uinfo,'uid':uno}))
        except:
          self.response.out.write(template.render('./template/h_byid.htm',{'uid':uno}))        
      except:
        self.redirect('/?u=%s' % uno)

class howtofindid(webapp.RequestHandler):
  def get(self):
    self.response.out.write(template.render('./template/h_howtofindid.htm',{}))

class otherpage(webapp.RequestHandler):
  def get(self):
    self.response.out.write('<a href="http://plurkii.appspot.com/">Plurkii!</a>')

class ooo(webapp.RequestHandler):
  def get(self):
    for i in dir(self.request):
      self.response.out.write("<b>%s</b><br>%s<br><br>" % (i,getattr(self.request,i)))

class oooo(webapp.RequestHandler):
  def get(self):
    p = plurklib.PlurkAPI('mCDwgcld4WKj1GFzZPB7mJlgm9lSHwks')
    uno = p.get_user_info(703365)
    self.response.out.write(uno)

def main():
  """ Start up. """
  application = webapp.WSGIApplication([('/', MainHandler),
                                        ('/byid', byid),
                                        ('/howtofindid', howtofindid),
                                        ('/ooo', ooo),
                                        ('/oooo', oooo),
                                        ('/.*', otherpage)
                                       ],debug=True)
  run_wsgi_app(application)

if __name__ == '__main__':
  main()
