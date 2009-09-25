#!/usr/bin/env python
# -*- coding: utf-8 -*-

from google.appengine.ext import webapp
from google.appengine.api import memcache
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template
import plurkapi,time,random,urllib2,re,robot


class MainHandler(webapp.RequestHandler):
    def get(self):
        #d = pp.getPlurks()
        #self.response.out.write(d)
        if self.request.get('u') == '' or self.request.get('u') == None:
            self.response.out.write(template.render('h_index.htm',{}))
        else:
            try:
                pp = plurkapi.PlurkAPI()
                botid,botpwd = robot.robot()
                pp.login(botid,botpwd)
            except:
                pass
            try:
                tv = {}
                u = self.request.get('u').replace('/','')
                u = u.replace(' ','')
                value = memcache.get(u.upper())
                if value is None:
                    dd = pp.uidToUserinfo(getnameid(u))
                    if dd['avatar'] is None : dd['avatar'] = ''
                    if dd['date_of_birth'] is None:
                        pass
                    else:
                        dd['date_of_birth'] = dd['date_of_birth'][5:-13]
                    '''
                    for v in dd:
                        self.response.out.write("- %s:%s<br>" % (v,dd[v]))
                    self.response.out.write("+---------------------------+")
                    '''
                    tv['display_name'] = dd.get('display_name','(no)')
                    tv['uid'] = dd.get('uid','(no)')
                    tv['relationship'] = dd.get('relationship','(no)')
                    tv['nick_name'] = dd.get('nick_name','(no)')
                    tv['karma'] = dd.get('karma','(no)')
                    tv['date_of_birth'] = dd.get('date_of_birth','(no)')
                    tv['location'] = dd.get('location','(no)')
                    tv['relationship'] = dd.get('relationship','(no)')
                    tv['full_name'] = dd.get('full_name','(no)')
                    tv['gender'] = dd.get('gender','(no)')
                    tv['timezone'] = dd.get('timezone','(no)')
                    tv['avatar'] = dd.get('avatar','(no)')
                    memcache.add(u.upper(), tv,604800)
                else:
                    tv = value
                self.response.out.write(template.render('hh_firstpage.htm',{'tv':tv}))
            except:
                self.redirect('/oops')

class showavatar(webapp.RequestHandler):
    def get(self):
        u = self.request.get('u').replace('/','')
        u = u.replace(' ','')
        try:
            p = {}
            tv = memcache.get(u.upper())
            if tv is None:
                self.redirect('/?u=%s' % u)
            else:
                p['piclist'] = printpic(tv['avatar'])
                self.response.out.write(template.render('hh_avatar.htm',{'tv':tv,'p':p}))
        except:
            self.redirect('/?u=%s' % u)


class seeallfriend(webapp.RequestHandler):
    def get(self):
        u = self.request.get('u').replace('/','')
        u = u.replace(' ','')
        try:
            tv = memcache.get(u.upper())
            if tv is None:
                self.redirect('/?u=%s' % u)
            else:
                p = plurkapi.PlurkAPI()
                try:
                    botid,botpwd = robot.robot()
                    p.login(botid,botpwd)
                except:
                    url = '/friends?u=%s' % u
                    re = {'url':url}
                    self.response.out.write(template.render('hh_refresh.htm',{'re':re}))
                #friends cache
                getcache = memcache.get("f_%s" % u.upper())
                if getcache is None:
                    ff = p.getcpfriend(getnameid(u))
                    f = []
                    for i in ff:
                        fff = {}
                        pcache = memcache.get(ff[i]['nick_name'].upper())
                        fff = ff[i]
                        if pcache is None:
                            pass
                        else:
                            fff['uid'] = pcache['uid']
                            fff['avatar'] = pcache['avatar']
                        f.append(fff)
                    memcache.add("f_%s" % u.upper(), f, 180)
                else:
                    f = getcache
                self.response.out.write(template.render('hh_friend.htm',{'f':f,'tv':tv}))
        except:
            #self.redirect('/oops')
            url = '/friends?u=%s' % u
            re = {'url':url}
            self.response.out.write(template.render('hh_refresh.htm',{'re':re}))

class vote(webapp.RequestHandler):
    def get(self):
        u = self.request.get('u').replace('/','')
        u = u.replace(' ','')
        try:
            tv = memcache.get(u.upper())
            if tv is None:
                self.redirect('/?u=%s' % u)
            else:
                self.response.out.write(template.render('hh_vote.htm',{'tv':tv}))
        except:
            self.redirect('/?u=%s' % u)

class push(webapp.RequestHandler):
    def get(self):
        self.response.out.write(template.render('hh_push.htm',{}))

class searchuser(webapp.RequestHandler):
    def get(self):
        self.response.out.write(template.render('hh_aboutuser.htm',{}))

class about(webapp.RequestHandler):
    def get(self):
        self.response.out.write(template.render('hh_about.htm',{}))

class contact(webapp.RequestHandler):
    def get(self):
        self.response.out.write(template.render('hh_contact.htm',{}))

class promote(webapp.RequestHandler):
    def get(self):
        self.response.out.write(template.render('hh_promote.htm',{}))

class oops(webapp.RequestHandler):
    def get(self):
        self.response.out.write(template.render('hh_oops.htm',{}))

class oopspage(webapp.RequestHandler):
    def get(self):
        self.redirect('/oops')

class getmemstats(webapp.RequestHandler):
    def get(self):
        g = memcache.get_stats()
        for i in g:
            self.response.out.write(' - %s:%s<br>' % (i,g[i]))

class fls(webapp.RequestHandler):
    def get(self):
        if memcache.flush_all():
            self.response.out.write("flush_all OK!")
        else:
            self.response.out.write("ERROR!!")

def main():
    application = webapp.WSGIApplication([('/', MainHandler),
                                                        ('/friends',seeallfriend),
                                                        ('/avatar',showavatar),
                                                        ('/talk',vote),
                                                        ('/push',push),
                                                        ('/searchuser',searchuser),
                                                        ('/about',about),
                                                        ('/promote',promote),
                                                        ('/contact',contact),
                                                        ('/getmemstats',getmemstats),
                                                        ('/fls',fls),
                                                        ('/oops',oops),
                                                        ('/.*',oopspage)],debug=True)
    run_wsgi_app(application)

def getnameid(name):
    q = name.replace('/','')
    q = q.replace(' ','')
    try:
        pp = plurkapi.PlurkAPI()
        botid,botpwd = robot.robot()
        pp.login(botid,botpwd)
        qqq = pp.search(q)
        
        for i in qqq['users']:
            for k in qqq['users'][i]:
                if qqq['users'][i]['nick_name'].upper() == q.upper() :
                    rr = qqq['users'][i]['uid']
        return rr
    except:
        response = urllib2.urlopen('http://www.plurk.com/%s' % q)
        page = response.read()
        uid_pat = re.compile('var SETTINGS = \{.*"user_id": ([\d]+),.*\}')
        matches = uid_pat.findall(page)
        if len(matches):
            rr = matches[0]
        else:
            raise PlurkError, "Could not find user_id."
        return rr

def printpic(x):
    try:                
        x = int(x)
    except:
        x = 0
    y = []
    y.append(x)
    while x > 0:
        x = x -2
        if x > 1:
            y.append(x)
    #else:
        #y.append('')
    return y

if __name__ == '__main__':
    main()
