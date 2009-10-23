#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" Put all application function. """

## http://www.python.org/dev/peps/pep-0238/
## 2/3 = 0
from __future__ import division

from google.appengine.api import memcache
import random,re,urllib2
import datamodel,plurkapi,robot

class PlurkError(Exception): pass

def randuser(mod = None):
    """ random to show user. """
    ru = datamodel.userplurkdata.all()
    count = memcache.get('randusercount')
    if count is None:
        count = ru.count()
        memcache.add('randusercount',count,60*60*6)
    result = ru.fetch(5,random.randrange(1,count - 5))
    a = ''
    if mod :
        for i in result:
            a = a + "<a href='/?u=%s'><img width='48' alt='%s' src='http://avatars.plurk.com/%s-big%s.jpg'></a>" % (i.uname,i.uname,i.key().id_or_name(),i.avatar)
    else:
        for i in result:
            a = a + "<a href='/?u=%s'>%s</a> " % (i.uname,i.uname)
    return a

def getwall(gender = 0,pernum = 126):
    """ The Wall! """
    if gender:
        cache = memcache.get('boywalls')
    else:
        cache = memcache.get('girlwalls')
    if cache is not None:
        return cache
    else:
        wall = datamodel.userplurkdata.gql("where gender = :1" ,gender)
        if gender:
            count = memcache.get('wallcountboy')
        else:
            count = memcache.get('wallcountgirl')
        if count is None:
            count = wall.count()
            if gender:
                memcache.add('wallcountboy',count,60*60)
            else:
                memcache.add('wallcountgirl',count,60*60)
        wall = wall.fetch(pernum,random.randrange(1,count - pernum))
        a =''
        for i in wall:
            if i.avatar:
                avatar = 'http://avatars.plurk.com/%s-big%s.jpg' % (i.key().id_or_name(),i.avatar)
            else:
                avatar = '/images/face-angel.png'
            a = a + "<a href='/?u=%s'><img alt='%s' src='%s'></a>" % (i.uname,i.uname,avatar)
        if gender:
            memcache.add('boywalls',a,60*6)
        else:
            memcache.add('girlwalls',a,60*6)
        return a

def karmawall(karma = 99):
    """ Show karma Wall
    """
    kw = memcache.get('karmawall')
    if kw is None:
        kw = datamodel.userplurkdata.gql("where karma >= :1" ,karma)
        a = ''
        for i in kw:
            if i.avatar:
                avatar = 'http://avatars.plurk.com/%s-big%s.jpg' % (i.key().id_or_name(),i.avatar)
            else:
                avatar = '/images/face-angel.png'
            a = a + "<a href='/?u=%s'><img alt='%s' src='%s'></a>" % (i.uname,i.uname,avatar)
        memcache.add('karmawall',a,60*60*4)
    else:
        a = kw
    return a

def morepicwall(limit = 50):
    """ Show karma Wall
    """
    kw = memcache.get('morepicwall')
    if kw is None:
        kw = datamodel.userplurkdata.gql("order by avatar desc limit :1" ,limit)
        a = ''
        for i in kw:
            if i.avatar:
                avatar = 'http://avatars.plurk.com/%s-big%s.jpg' % (i.key().id_or_name(),i.avatar)
            else:
                avatar = '/images/face-angel.png'
            a = a + "<a href='/?u=%s'><img alt='%s' src='%s'></a>" % (i.uname,i.uname,avatar)
        memcache.add('morepicwall',a,60*60*4)
    else:
        a = kw
    return a

def getnameid(name):
    """ Get Plurk user id by nickname. """
    q = name.replace('/','')
    q = q.replace(' ','')
    try:
        ## The first way to cache.
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
        ## The second way to cache if the first way fault.
        response = urllib2.urlopen('http://www.plurk.com/%s' % q)
        page = response.read()
        uid_pat = re.compile('var SETTINGS = \{.*"user_id": ([\d]+),.*\}')
        matches = uid_pat.findall(page)
        if len(matches):
            rr = matches[0]
        else:
            raise PlurkError, "Could not find user_id."
        return rr

def chartcofri(a,b,c,ta,tb):
    """ Print out co-friends chart. """
    total = 100/max(a,b)
    pa = int(a * total)
    pb = int(b * total)
    pc = int(c * total)
    re = """http://chart.apis.google.com/chart?cht=v&chs=500x400&chd=t:%s,%s,0,%s&chdl=%s (%s)|%s (%s)|Co-friends(%s)&chtt=%s and %s's Plurk co-friends""" % (pa,pb,pc,ta,a,tb,b,c,ta,tb)
    return re

def printpic(x):
    """ Print out pic list. """
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
