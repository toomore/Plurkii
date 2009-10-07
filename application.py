#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Put all application function.
"""

from google.appengine.ext import db
from google.appengine.api import memcache
import random
import datamodel

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
