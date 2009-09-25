#!/usr/bin/env python
# -*- coding: utf-8 -*-
import google.appengine.ext.db
import robotlist,random

def robot():
    b = random.randrange(1,8)
    a = robotlist.iirobot().all().filter('botno =',b)

    for c in a:
        return c.botname,c.botpwd
