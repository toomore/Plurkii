#!/usr/bin/env python
# -*- coding: utf-8 -*-
from google.appengine.ext import db
import datamodel,random

def randuser(mod = None):
    """random to show user. """
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
