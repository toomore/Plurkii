#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" Main WSGI. """

from google.appengine.ext import webapp
from google.appengine.api import memcache
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template
import datamodel,datetime,random
import application,plurkapi,robot

class PlurkError(Exception): pass

class MainHandler(webapp.RequestHandler):
    """
    Index page, If u is None,show the search input page.
    Else show the user information page.    
    """
    def get(self):
        #d = pp.getPlurks()
        #self.response.out.write(d)

        if self.request.get('u') == '' or self.request.get('u') == None:
            ## Show Index.
            try:
                tv = {'tip' : application.randuser()}
                self.response.out.write(template.render('./template/h_index.htm',{'tv':tv}))
            except:
                self.redirect('/')
        else:
            ## Show user information page.
            try:
                pp = plurkapi.PlurkAPI()
                botid,botpwd = robot.robot()
                pp.login(botid,botpwd)
            except:
                #raise PlurkError, 'login fault.'
		self.redirect('/?u=%s' % self.request.get('u'))
            tv = {}
            u = self.request.get('u').replace('/','')
            u = u.replace(' ','')
            value = memcache.get(u.upper())
            try:
                ## Check the user wherether cached.
                if value is None:
                    ## No cache and create the new one.
                    dd = pp.uidToUserinfo(application.getnameid(u))
                    try:
                        ## Solute avatar,date_of_birthday format problems.
                        if dd['avatar'] is None : dd['avatar'] = ''
                        if dd['date_of_birth'] is None:
                            databirthday = None
                        else:
                            dd['date_of_birth'] = dd['date_of_birth'][5:-13]
                            day,mon,year = dd['date_of_birth'].split(' ')                        
                            mons = {'Jan':1,'Feb':2,'Mar':3,'Apr':4,'May':5,'Jun':6,'Jul':7,'Aug':8,'Sep':9,'Oct':10,'Nov':11,'Dec':12}
                            databirthday = datetime.date(int(year),int(mons[mon]),int(day))
                    except:
                        raise PlurkError, 'cal date fault.'
                    '''
                    for v in dd:
                        self.response.out.write("- %s:%s<br>" % (v,dd[v]))
                    self.response.out.write("+---------------------------+")
                    '''
                    ## Base data formate.
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
                    try:
                        try:
                            ## convert avatar to int or 0.
                            avatar = int(tv['avatar'])
                        except:
                            avatar = 0
                        ## store into data.
                        indataplurk = datamodel.userplurkdata(
                                                key_name = str(tv['uid']),
                                                uname = str(tv['nick_name']),
                                                fullname = unicode(tv['full_name']),
                                                karma = int(tv['karma']),
                                                avatar = avatar,
                                                gender = int(tv['gender']),
                                                location = unicode(tv['location']),
                                                birthday = databirthday
                                                )
                        indataplurk.put()
                    except:
                        raise PlurkError, 'indata fault.'
                    memcache.add(u.upper(), tv,604800)
                else:
                    ## user informations has cached. Direct use memcache value.
                    tv = value
                self.response.out.write(template.render('./template/hh_firstpage.htm',{'tv':tv}))
            except:
                ## All fault go to '/oops' page.
                self.redirect('/oops')

class showavatar(webapp.RequestHandler):
    """ Show user all avatars.
    """
    def get(self):
        u = self.request.get('u').replace('/','')
        u = u.replace(' ','')
        try:
            p = {}
            tv = memcache.get(u.upper())
            if tv is None:
                self.redirect('/?u=%s' % u)
            else:
                p['piclist'] = application.printpic(tv['avatar'])
                self.response.out.write(template.render('./template/hh_avatar.htm',{'tv':tv,'p':p}))
        except:
            self.redirect('/?u=%s' % u)


class seeallfriend(webapp.RequestHandler):
    """ Show user all friends.
        If get too many friends, loading will be fault and then will show refresh page to try again.
    """
    def get(self):
        u = self.request.get('u').replace('/','')
        u = u.replace(' ','')
        try:
            tv = memcache.get(u.upper())
            if tv is None:
                ## If no cache data, return to user info. page to start up.
                self.redirect('/?u=%s' % u)
            else:
                p = plurkapi.PlurkAPI()
                try:
                    ## Login
                    botid,botpwd = robot.robot()
                    p.login(botid,botpwd)
                except:
                    ## If login fault, go to refresh to try again.
                    url = '/friends?u=%s' % u
                    re = {'url':url}
                    self.response.out.write(template.render('./template/hh_refresh.htm',{'re':re}))
                ## Friends cache
                getcache = memcache.get("f_%s" % u.upper())
                if getcache is None:
                    ff = p.getcpfriend(application.getnameid(u))
                    f = []
                    ## Chech all friends if cached.
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
                self.response.out.write(template.render('./template/hh_friend.htm',{'f':f,'tv':tv}))
        except:
            ## If loading fault, go to refresh to try again.
            url = '/friends?u=%s' % u
            re = {'url':url}
            self.response.out.write(template.render('./template/hh_refresh.htm',{'re':re}))

class friccindex(webapp.RequestHandler):
    """ Co-friends Index page.
        parma. 'u' for default a user for one.
    """
    def get(self):
        u = self.request.get('u').replace('/','')
        tv = {'nick_name': u}
        self.response.out.write(template.render('./template/h_friccindex.htm',{'tv':tv}))

class fricc(webapp.RequestHandler):
    """ Show co-friends page.
        parma. ua,ub for two users.
    """
    def get(self):
        ua = self.request.get('ua').replace('/','')
        ub = self.request.get('ub').replace('/','')
        ua = ua.replace(' ','')
        ub = ub.replace(' ','')
        
        if len(ua) and len(ub):
            p = plurkapi.PlurkAPI()
        else:
            self.redirect('/oops')

        #self.response.out.write(u)
        
        try:
            botid,botpwd = robot.robot()
            p.login(botid,botpwd)

            pa = p.getcpfriend(application.getnameid(ua))
            pb = p.getcpfriend(application.getnameid(ub))
            pp = set(pa.keys()) & set(pb.keys())

            f = []
            for i in pp:
                fff = {}
                pcache = memcache.get(pa[i]['nick_name'].upper())
                if pcache is None:
                    fff['nick_name'] = pa[i]['nick_name']
                else:
                    fff['uid'] = pcache['uid']
                    fff['avatar'] = pcache['avatar']
                    fff['nick_name'] = pcache['nick_name']
                f.append(fff)
            pchart = application.chartcofri(len(pa),len(pb),len(pp),ua,ub)
            p = {'pa':ua,'pb':ub,'pchart':pchart}
            indata = datamodel.datacofriend(
                                            uaname = ua,
                                            uaid = int(application.getnameid(ua)),
                                            ubname = ub,
                                            ubid = int(application.getnameid(ub))
                                            )
            indata.put()
            self.response.out.write(template.render('./template/hh_friendcc.htm',{'f':f,'p':p}))
        except:
            self.redirect('/oops')

class friccc(webapp.RequestHandler):
    """ For co-friends tinyurl.
        '/friccc?u={{ua}}|{{ub}}'
    """
    def get(self):
        u = self.request.get('u').replace('/','')
        u = u.replace(' ','')
        a = u.split('|')
        self.redirect('/fricc?ua=%s&ub=%s' % (a[0],a[1]))

class girls(webapp.RequestHandler):
    """ Girls Wall
    """
    def get(self):
        tv =    {
                'title':'Girls',
                'content':application.getwall()
                }
        self.response.out.write(template.render('./template/hh_wall.htm',{'tv':tv}))

class boys(webapp.RequestHandler):
    """ Boys Wall
    """
    def get(self):
        tv =    {
                'title':'Boys',
                'content':application.getwall(1)
                }
        self.response.out.write(template.render('./template/hh_wall.htm',{'tv':tv}))

class karma(webapp.RequestHandler):
    """ karma Wall
    """
    def get(self):
        tv =    {
                'title':'Karma 100',
                'content':application.karmawall()
                }
        self.response.out.write(template.render('./template/hh_wall.htm',{'tv':tv}))

class morepic(webapp.RequestHandler):
    """ karma Wall
    """
    def get(self):
        tv =    {
                'title':'More Avatars',
                'content':application.morepicwall()
                }
        self.response.out.write(template.render('./template/hh_wall.htm',{'tv':tv}))

class vote(webapp.RequestHandler):
    """ User talk and vote page.
    """
    def get(self):
        u = self.request.get('u').replace('/','')
        u = u.replace(' ','')
        try:
            tv = memcache.get(u.upper())
            if tv is None:
                self.redirect('/?u=%s' % u)
            else:
                self.response.out.write(template.render('./template/hh_vote.htm',{'tv':tv}))
        except:
            self.redirect('/?u=%s' % u)

class push(webapp.RequestHandler):
    """ PUSH page.
    """
    def get(self):
        self.response.out.write(template.render('./template/hh_push.htm',{}))

class searchuser(webapp.RequestHandler):
    """ Search user info. from Google page.
    """
    def get(self):
        self.response.out.write(template.render('./template/hh_aboutuser.htm',{}))

class about(webapp.RequestHandler):
    """ Plurkii about page.
    """
    def get(self):
        self.response.out.write(template.render('./template/hh_about.htm',{}))

class contact(webapp.RequestHandler):
    """ Contact page.
    """
    def get(self):
        self.response.out.write(template.render('./template/hh_contact.htm',{}))

class promote(webapp.RequestHandler):
    """ Promote Plurkii page.
    """
    def get(self):
        self.response.out.write(template.render('./template/hh_promote.htm',{}))

class oops(webapp.RequestHandler):
    """ Page fault show page.
    """
    def get(self):
        self.response.out.write(template.render('./template/hh_oops.htm',{}))

class oopspage(webapp.RequestHandler):
    """ All no default page will redirection to '/oops'
    """
    def get(self):
        self.redirect('/oops')

## system info. page.
class getmemstats(webapp.RequestHandler):
    """ Show memcache info.
    """
    def get(self):
        g = memcache.get_stats()
        for i in g:
            self.response.out.write(' - %s:%s<br>' % (i,g[i]))

class fls(webapp.RequestHandler):
    """ Clean/reset memcache
    """
    def get(self):
        if memcache.flush_all():
            self.response.out.write("flush_all OK!")
        else:
            self.response.out.write("ERROR!!")

def main():
    """ Start up. """
    application = webapp.WSGIApplication([('/', MainHandler),
                                                        ('/friends',seeallfriend),
                                                        ('/co-friends',friccindex),
                                                        ('/fricc',fricc),
                                                        ('/friccc',friccc),
                                                        ('/girls',girls),
                                                        ('/boys',boys),
                                                        ('/karma',karma),
                                                        ('/moreavatar',morepic),
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

if __name__ == '__main__':
    main()
