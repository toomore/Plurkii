#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
A Cron for robot to cache user info.
About cron frequency please view cron.yaml
"""

from google.appengine.ext import db
import urllib2,re,random,datetime
import application,datamodel,plurkapi,robot

class PlurkError(Exception): pass

def crondata(u = None,uid = None):
    """ Use by uid or nickname.
    """
    try:
        pp = plurkapi.PlurkAPI()
        botid,botpwd = robot.robot()
        pp.login(botid,botpwd)
    except:
        raise PlurkError, 'login fault.'
    tv = {}
    try:
        ## To know uid or nickname.
        if uid is None:
            ## by nick_name
            u = u.replace('/','')
            u = u.replace(' ','')
            dd = pp.uidToUserinfo(application.getnameid(u))
        else:
            ## by uid
            uid = uid.replace('/','')
            uid = uid.replace(' ','')
            dd = pp.uidToUserinfo(uid)
    except:
        raise PlurkError, 'uid fault.'
    if dd['karma']:
        if dd['avatar'] is None : dd['avatar'] = ''
        if dd['date_of_birth'] is None:
            databirthday = None
        else:
            dd['date_of_birth'] = dd['date_of_birth'][5:-13]
            day,mon,year = dd['date_of_birth'].split(' ')
            mons = {'Jan':1,'Feb':2,'Mar':3,'Apr':4,'May':5,'Jun':6,'Jul':7,'Aug':8,'Sep':9,'Oct':10,'Nov':11,'Dec':12}
            databirthday = datetime.date(int(year),int(mons[mon]),int(day))
            
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
            avatar = int(tv['avatar'])
        except:
            avatar = 0
        try:
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
    else:
        pass

## function working.
try:
    ## Random to cache per 1,000,000 users id.
    ## Most of Taiwan's users are in 3,000,000 ~ 4,000,000 uid.
    def rockcron(cycle = 6,per = 1000000,times = 3):
        for a in range(cycle):
	    start = 1 + per * a
	    end = per * (a+1)
	    for b in range(times):
                crondata(uid = str(random.randrange(start,end)))
    rockcron()
except:
    pass
