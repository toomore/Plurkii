#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Choice a robot by random from datastore.
"""

from google.appengine.ext import db
import random

class iirobot(db.Model):
    """ Robot data property. """
    botno = db.IntegerProperty()
    botname = db.StringProperty()
    botpwd = db.StringProperty()

def robot():
    """ Robot for cache user info. auto. """
    b = random.randrange(1,8)
    a = iirobot().all().filter('botno =',b)

    for c in a:
        return c.botname,c.botpwd
