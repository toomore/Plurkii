#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Put all application function.
"""

from google.appengine.ext import db
import random
import datamodel

def randuser(mod = None):
    """ random to show user. """
    ru = datamodel.userplurkdata.all()
    result = ru.fetch(5,random.randrange(1,ru.count()-5))
    a = ''
    if mod :
        for i in result:
            a = a + "<a href='/?u=%s'><img width='48' alt='%s' src='http://avatars.plurk.com/%s-big%s.jpg'></a>" % (i.uname,i.uname,i.key().id_or_name(),i.avatar)
    else:
        for i in result:
            a = a + "<a href='/?u=%s'>%s</a> " % (i.uname,i.uname)
    return a

def getwall(gender = 0):
    wall = datamodel.userplurkdata.gql("where gender = :1" ,gender)
    count = wall.count()
    print '111'
    print count
    a =''
    for i in wall:
        if i.avatar:
            avatar = 'http://avatars.plurk.com/%s-big%s.jpg' % (i.key().id_or_name(),i.avatar)
        else:
            avatar = '/images/face-angel.png'
        a = a + "<a href='/?u=%s'><img border='0' width='50' src='%s'></a>" % (i.uname,avatar)
    return a
print getwall()
print getwall(1)



