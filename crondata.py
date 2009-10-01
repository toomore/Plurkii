#!/usr/bin/env python
# -*- coding: utf-8 -*-

from google.appengine.ext import db
import urllib2,re,random,datetime
import plurkapi,robot,datamodel

class PlurkError(Exception): pass

def crondata(u = None,uid = None):
    try:
        pp = plurkapi.PlurkAPI()
        botid,botpwd = robot.robot()
        pp.login(botid,botpwd)
    except:
        raise PlurkError, 'login fault.'
    tv = {}
    try:
        if uid is None:
            u = u.replace('/','')
            u = u.replace(' ','')
            dd = pp.uidToUserinfo(getnameid(u))
        else:
            uid = uid.replace('/','')
            uid = uid.replace(' ','')
            dd = pp.uidToUserinfo(uid)
        #print '1231231'
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
            #print databirthday
            
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
            indataplurk = datamodel.userplurkdata(
                                                    key_name = str(tv['uid']),
                                                    uname = str(tv['nick_name']),
                                                    fullname = unicode(tv['full_name']),
                                                    karma = int(tv['karma']),
                                                    avatar = int(tv['avatar']),
                                                    gender = int(tv['gender']),
                                                    location = unicode(tv['location']),
                                                    birthday = databirthday
                                                    )
            indataplurk.put()
        except:
            raise PlurkError, 'indata fault.'
    else:
        pass
    #return tv

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
        #print '22'
        return rr
'''
calldata = datamodel.userplurkdata.gql('limit %s,4' % random.randrange(0,64))

for result in calldata:
    crondata(result.uname)
    print result.uname
'''
try:
    crondata(uid = str(random.randrange(4000000,5000000)))
    crondata(uid = str(random.randrange(3000000,4000000)))
    crondata(uid = str(random.randrange(2000000,3000000)))
    crondata(uid = str(random.randrange(1000000,2000000)))
    crondata(uid = str(random.randrange(1,1000000)))
except:
    pass
