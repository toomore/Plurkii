# -*- coding: utf-8 -*-
import time,urllib,urllib2,cookielib,re
from django.utils import simplejson
#import simplejson # http://www.undefined.org/python/

#class PlurkError(Exception): pass
'''
def permalinkToPlurkID(permalink):
    base36number = permalink[len('http://www.plurk.com/p/'):]
    return int(base36number, 36)

def _baseN(num,b):
    return ((num == 0) and  "0" ) or ( _baseN(num // b, b).lstrip("0") + "0123456789abcdefghijklmnopqrstuvwxyz"[num % b])

def PlurkIDToPermalink(plurk_id):
    return 'http://www.plurk.com/p/' + _baseN(int(plurk_id), 36)
'''

class PlurkAPI:
    """QQQ"""
    def __init__(self):
        self._logged_in = False
        self._uid = -1
        self._nickname = None
        self._friends = {}
        self._cookies = cookielib.CookieJar()
        self._opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self._cookies))
        urllib2.install_opener(self._opener)
        self.page = 'tt'
    
    def login(self, nickname, password):
        """ login to plurk and keep a session cookie """
        post = urllib.urlencode({'nick_name': nickname, 'password': password})
        request = urllib2.Request('http://www.plurk.com/Users/login', post)
        response = urllib2.urlopen( request )
        self._cookies.extract_cookies( response, request )
        self._nickname = nickname
        return self._cookies

    def gc(self):
        #ree = urllib2.urlopen('http://www.plurk.com/Users/getCompletion?user_id=4426157')
        ree = urllib2.urlopen('http://www.plurk.com/Users/getCompletion?user_id=703365')
        self.page = ree.read()
        return self.page

    def gid(self):
        response = urllib2.urlopen('http://www.plurk.com/user/%s' % (self._nickname) )
        page = response.read()
        uid_pat = re.compile('var SETTINGS = \{.*"user_id": ([\d]+),.*\}')
        matches = uid_pat.findall(page)
        if len(matches):
            self._uid = matches[0]
        else:
            raise PlurkError, "Could not find user_id."
        #self._nickname = nickname;

    def gcomp(self):
        post = urllib.urlencode({ 'user_id': self._uid })
        ree = urllib2.urlopen('http://www.plurk.com/Users/getCompletion?user_id=%s' % self._uid)
        self.page = ree.read()
        return self.page

    def getPlurks(self, uid = None, date_from = None, only_responded = False):
        """ If logged in, gets yours and your friends' plurks.
            If not logged in, gets only the plurks for the specified user id.
            date_from should be of the form 2008-9-5T19:07:29 """
        if uid == None:
            uid = self._uid

        params = { 'user_id': uid, }
        if date_from != None:
            params['offset'] = date_from
        if only_responded != False:
            params['only_responded'] = 1
        post = urllib.urlencode(params)
        response = urllib2.urlopen(self._plurk_paths['plurk_get'], post )
        page = response.read()
        # The following two lines are a hack around the fact that
        # simplejson doesn't create Date objects.
        date_pat = re.compile('\"posted\": new Date\((\".+?\")\)')
        data = simplejson.loads(re.sub(date_pat, '"posted": \g<1>', page))
        return data

    def addPlurk(self, lang='en', qualifier='says', content='', allow_comments=True, limited_to=[]):
        """ Add a plurk to your timeline.  (Must be logged in.) """
        '''
        if self._logged_in == False:
            return False
        '''
        if allow_comments == True:
            no_comments = '0'
        else:
            no_comments = '1'

        params = {'posted': time.strftime('%Y-%m-%dT%H:%M:%S', time.gmtime()),
                  'qualifier': qualifier,
                  'content': content,
                  'lang': lang,
                  'uid': self._uid,
                  'no_comments': no_comments }

        if len(limited_to):
            params['limited_to'] = '[%s]' % ','.join(limited_to)

        post = urllib.urlencode(params)
        response = urllib2.urlopen( self._plurk_paths['plurk_add'], post) 
        page = response.read()
        if page.find('anti-flood') != -1:
            raise PlurkError, 'Anti-flood rules prohibited the plurk.'
        matches = re.compile('"error":\s(\S+)}').findall(page)
        if len(matches) and matches[0] != 'null':
            raise PlurkError, matches[0]
        
        return True

    _plurk_paths = {
        'http_base'             : 'http://www.plurk.com',
        'login'                 : 'http://www.plurk.com/Users/login?redirect_page=main',
        'getCompletion'         : 'http://www.plurk.com/Users/getCompletion',
        'plurk_add'             : 'http://www.plurk.com/TimeLine/addPlurk',
        'plurk_respond'         : 'http://www.plurk.com/Responses/add',
        'plurk_get'             : 'http://www.plurk.com/TimeLine/getPlurks',
        'plurk_get_by_id'       : 'http://www.plurk.com/TimeLine/getPlurksById',
        'plurk_get_responses'   : 'http://www.plurk.com/Responses/get2',
        'plurk_get_unread'      : 'http://www.plurk.com/TimeLine/getUnreadPlurks',
        'plurk_mute'            : 'http://www.plurk.com/TimeLine/setMutePlurk',
        'plurk_delete'          : 'http://www.plurk.com/TimeLine/deletePlurk',
        'notification'          : 'http://www.plurk.com/Notifications',
        'notification_accept'   : 'http://www.plurk.com/Notifications/allow',
        'notification_makefan'  : 'http://www.plurk.com/Notifications/allowDontFollow',
        'notification_deny'     : 'http://www.plurk.com/Notifications/deny',
        'friends_get'           : 'http://www.plurk.com/Users/friends_get',
        'friends_block'         : 'http://www.plurk.com/Friends/blockUser',
        'friends_remove_block'  : 'http://www.plurk.com/Friends/removeBlock',
        'friends_get_blocked'   : 'http://www.plurk.com/Friends/getBlockedByOffset',
        'user_get_info'         : 'http://www.plurk.com/Users/fetchUserInfo',
        'remove_friend'         : 'http://www.plurk.com/Users/removeFriend'
    }

    _qualifiers = { 'en': (':', 'loves',  'likes', 'shares', 'gives', 'hates', 'wants', 'wishes',
                             'needs', 'will', 'hopes', 'asks', 'has', 'was', 'wonders', 'feels', 'thinks', 'says', 'is')
                  }