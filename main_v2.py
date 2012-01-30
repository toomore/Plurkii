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
from google.appengine.api.images import Image
from datamodel import userplurkdata
import urllib2
import plurklib
import logging
import random

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

    op = u'<div class="listq">序號 ID 暱稱 生日 地區 頭像數</div>'
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
          <div class="listq"><a href="/byid?u=%(key)s"><span id="uid">%(key)s</span></a> %(uname)s %(fullname)s %(birthday)s %(location)s <span id="no">%(avatar)s</span></div>
          <button type="button" onclick="addpics()">增加顯示照片</button><br>
          <span id="demo"></span><br>
          <span id="loadpics"></span><br>
          <img alt="" src="http://avatars.plurk.com/%(key)s-big.jpg">
          ''' % i
        tv['onload'] = " onLoad='loadpics()'"
        tv['key'] = i['key']

    tv['op'] = op
    tv['nick_name'] = get_u
    tv['moreavatar'] = ['看更多<a href="/avatar/girl">正妹的頭像</a>','看更多<a href="/avatar/boy">猛男的頭像</a>','']
    self.response.out.write(template.render('./template/h_index.htm',{'tv':tv}))

class byid(webapp.RequestHandler):
  def get(self):
    uno = self.request.get('u').replace(' ','')
    if len(uno) == 0:
      self.response.out.write(template.render('./template/h_byid.htm',{}))
    else:
      if self.request.get('m'):
        startno = -1
      else:
        startno = 0
      other_url = self.request.path_qs + '&m=1'
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
          self.response.out.write(template.render('./template/h_byid.htm',{'tv':uinfo,'uid':uno,'startno':startno,'other_url':other_url}))
        except:
          self.response.out.write(template.render('./template/h_byid.htm',{'uid':uno,'startno':startno,'other_url':other_url}))
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

class ooimg(webapp.RequestHandler):
  def get(self):
    imgdata = urllib2.urlopen(self.request.get('img')).read()
    op = Image(imgdata).histogram()
    avg = []
    for i in range(256):
      avg.append(sum([op[0][i],op[1][i],op[2][i]])/3)
    alavg = [sum(avg[:84])/85,sum(avg[85:169])/85,sum(avg[170:255])/85]
    if max(alavg) == alavg[0]: #OXX
      tip = u"暗黑"
    elif max(alavg) == alavg[1]: #XOX
      tip = u"正常"
    elif max(alavg) == alavg[2]: #XXO
      if min(alavg) == alavg[1]: #OXO
        tip = u"光明又很暗黑"
      else:
        tip = u"光亮"
    else:
      tip = '??'

    def rgbs(inirgb):
      alphabet = "0123456789abcdef"
      inirgb, i = divmod(inirgb, 16)
      shorten = alphabet[inirgb] + alphabet[i]
      return shorten

    rr = rgbs(op[0].index(max(op[0])))
    gg = rgbs(op[1].index(max(op[1])))
    bb = rgbs(op[2].index(max(op[2])))
    oprgb = {}
    oprgb['rr'] = rr
    oprgb['gg'] = gg
    oprgb['bb'] = bb

    self.response.out.write('histogram value<br>%s<br><br>' % op)
    self.response.out.write('Average histogram value<br><b>%s</b><br><br>' % avg)
    self.response.out.write('All Average histogram value<br><b>%s<br>%s</b><br><br>' % (alavg,tip))
    self.response.out.write('RGB<br><b><font color="#%(rr)s%(gg)s%(bb)s">#%(rr)s%(gg)s%(bb)s</font></b><br><br>' % oprgb)
    self.response.out.write('Orgin images<br><img src="%s"><br><br>' % self.request.get('img'))

class listk(webapp.RequestHandler):
  def get(self,gender):
    randpage = random.randrange(1,7) ## in memcache parameter
    if gender == 'girl':
      gq = 0 ## in memcache parameter
      title = 'Girls'
    else:
      gq = 1 ## in memcache parameter
      title = 'Boys'
    rno = random.randrange(1,4) ## in memcache parameter
    if rno == 1:
      rq = 'avatar > 500'
    elif rno == 2:
      rq = 'avatar <= 500 and avatar > 250'
    elif rno == 3:
      rq = 'avatar <= 250 and avatar > 100'
    else:
      rq = 'avatar <= 100'

    '''
    memcache namespace [1:5]avatar[1:2][1:4]
    [randpage][gender][rno] namespace: avatarpage
    '''
    memname = str(randpage) + str(gender) + str(rno)
    op = memcache.get(memname,'avatarpage')
    if op:
      logging.info('Useing memcache avatar page. #%s' % memname)
      self.response.out.write(template.render('./template/h_listk.htm',{'op':op,'title':title}))
    else:
      op = ''
      d = userplurkdata.gql("WHERE gender = %s and %s ORDER BY avatar desc limit %s,%s" % (gq,rq,random.randrange(1,1000 - 60),60))
      for i in d:
        if i.avatar > 500:
          url = "/byid?u=%s" % i.key().id_or_name()
        else:
          url = "/?u=%s" % i.uname
        op += '<a href="%s"><img alt="" src="http://avatars.plurk.com/%s-big%s.jpg"></a>' % (url,i.key().id_or_name(),i.avatar)
      if op:
        if memcache.set(memname,op,60*60*24,namespace='avatarpage'):
          logging.info('Set memcache avatar page. #%s' % memname)
        else:
          pass
      else:
        pass
      self.response.out.write(template.render('./template/h_listk.htm',{'op':op,'title':title}))
    '''
    for k in dir(i):
      self.response.out.write("<b>%s</b><br>%s<br><br>" % (k,getattr(i,k)))
    self.response.out.write("<hr>")
    '''

def main():
  """ Start up. """
  application = webapp.WSGIApplication([('/', MainHandler),
                                        ('/byid', byid),
                                        ('/howtofindid', howtofindid),
                                        ('/ooo', ooo),
                                        ('/oooo', oooo),
                                        ('/ooimg', ooimg),
                                        ('/avatar/(.*)', listk),
                                        ('/.*', otherpage)
                                       ],debug=True)
  run_wsgi_app(application)

if __name__ == '__main__':
  main()
