"""
    Copyright (c) 2010 Kurt Karakurt <kurt.karakurt@gmail.com>

    Permission is hereby granted, free of charge, to any person obtaining a copy
    of this software and associated documentation files (the "Software"), to deal
    in the Software without restriction, including without limitation the rights
    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
    copies of the Software, and to permit persons to whom the Software is
    furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in
    all copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
    THE SOFTWARE.
"""
import sys
import urllib
import simplejson as json
if sys.version[:1] == '3':
    import http.cookiejar
elif sys.version[:1] == '2':
    import urllib2
    import cookielib
else:
    raise PlurklibError("Your python interpreter is too old. Please consider upgrading.")

class PlurklibError(Exception):
    
    def __init__(self, value):
        self.value = value
        
    def __str__(self):
        return repr(self.value)

class PlurkAPI:

    def __init__(self, key):
        """ Required parameters:
                key: Your Plurk API key.
        """
        self._api_key = key
        self._username = None
        self._password = None
        self._logged_in = False
        self._uid = -1
        self._friends = {}

    def _call_api(self, apirequest, parameters, https=False):
        """ Send a request to Plurk API and decode response.
            Required parameters:
                apirequest: The path to API's function, like: 'API/Users/logout'
                parameters: The parameters of the request, that sends like POST
            Optional parameters:
                https: If it's set to True, then HTTPS and SSL are used for the API call.
            Successful return:
                The parsed dict object is returned for further processing.
        """
        if sys.version[:1] == '3':
            return self._python3_call_api(apirequest, parameters, https)
        elif sys.version[:1] == '2': 
            return self._python2_call_api(apirequest, parameters, https)
        else:
            raise PlurklibError("Your python interpreter is too old. Please consider upgrading.")
        
    def _python2_call_api(self, apirequest, parameters, https=False):
        parameters['api_key'] = self._api_key
        post = urllib.urlencode(parameters)
        if https:
            request = urllib2.Request(url = 'https://www.plurk.com' + apirequest, data = post)
        else:
            request = urllib2.Request(url = 'http://www.plurk.com' + apirequest, data = post)
        try:
            response = urllib2.urlopen(request)
        except:
            message = urllib2.HTTPError
            if message.code == 400:
                response = json.loads(message.fp.read().decode("utf-8"))
            else:
                response = 'HTTP Error ' + message.code
            return response
        if apirequest == '/API/Users/login':
            cookies = cookielib.CookieJar()
            opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookies))
            urllib2.install_opener(opener)
            cookies.extract_cookies(response, request)
        result = json.loads(response.read().decode("utf-8"))
        return result
        
    def _python3_call_api(self, apirequest, parameters, https=False):
        parameters['api_key'] = self._api_key
        post = urllib.parse.urlencode(parameters)
        if https:
            request = urllib.request.Request(url = 'https://www.plurk.com' + apirequest, data = post)
        else:
            request = urllib.request.Request(url = 'http://www.plurk.com' + apirequest, data = post)
        try:
            response = urllib.request.urlopen(request)
        except:
            message = urllib.error.HTTPError
            if message.code == 400:
                response = json.loads(message.fp.read().decode("utf-8"))
            else:
                response = 'HTTP Error ' + message.code
            return response
        if apirequest == '/API/Users/login':
            cookies = http.cookiejar.CookieJar()
            opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookies))
            urllib.request.install_opener(opener)
            cookies.extract_cookies(response, request)
        result = json.loads(response.read().decode("utf-8"))
        return result

#=================================== Users ===================================

    def register(self, nick_name, full_name, password, gender, date_of_birth, email = None):
        """ Register a new Plurk account. Using HTTPS.
            Required parameters:
                nick_name: The user's nick name. Should be longer than 3 characters. Should be ASCII.
                           Nick name can only contain letters, numbers and _.
                full_name: Can't be empty.
                password: Should be longer than 3 characters.
                gender: Should be 'male', 'female' or 'other'.
                date_of_birth: Should be 'YYYY-MM-DD', example '1985-05-13'.
            Optional parameters:
                email: Must be a valid email.
            Successful return:
                {'id': 3852645, 'nick_name': 'Karakurt', ...}
            Error returns:
                {'error_text': 'Email invalid'}
                {'error_text': 'User already found'}
                {'error_text': 'Email already found'}
                {'error_text': 'Password too small'}
                {'error_text': 'Nick name must be at least 3 characters long'}
                {'error_text': 'Nick name can only contain letters, numbers and _'}
                {'error_text': 'Internal service error. Please, try later'}
        """
        parameters = {'nick_name': nick_name, 
                      'full_name': full_name,
                      'password': password,
                      'gender': gender,
                      'date_of_birth': date_of_birth} 
        if email != None:
            parameters['email'] = email
        request = '/API/Users/register'
        response = self._call_api(request, parameters, True)
        return response

    def login(self, username, password, no_data=None):
        """ Log in to Plurk. Login an already created user. Using HTTPS.
            Login creates a session cookie, which can be used to access the other methods.
            Required parameters:
                username: The user's nick name or email.
                password: The user's password.
            Optional parameters:
                no_data: If it's set to "1" then the common data is not returned.
            Successful return:
                The data of /API/Profile/getOwnProfile if no_data isn't set. 
                If no_data is set to "1" then {'success_text': 'ok'} is returned.
            Error returns:
                {'error_text': 'Invalid login'}
                {'error_text': 'Too many logins'}
        """
        self._username = username
        self._password = password
        parameters = {'username': username, 
                      'password': password} 
        if no_data != None:
            parameters['no_data'] = no_data
        request = '/API/Users/login'
        response = self._call_api(request, parameters, True)
        return response

    def logout(self):
        """ Logout from Plurk.
            Successful return:
                {'success_text': 'ok'} if the user is logged out.
        """
        parameters = {}
        request = '/API/Users/logout'
        response = self._call_api(request, parameters)
        return response

    def update(self, current_password, full_name = None, new_password = None, email = None, 
               display_name = None, privacy = None, date_of_birth = None):
        """ Update a user's information (such as email, password or privacy). Using HTTPS.
            Required parameters:
                current_password: User's current password.
            Optional parameters:
                full_name: Change full name.
                new_password: Change password.
                email: Change email.
                display_name: User's display name, can be empty and full unicode. Must be shorter than 15 characters.
                privacy: User's privacy settings. The option can be world (whole world can view the profile),
                         only_friends (only friends can view the profile) or only_me (only the user can view own plurks).
                date_of_birth: Should be 'YYYY-MM-DD', example '1985-05-13'.
            Successful return:
                Dictionary object with updated user info {'id': 3852645, 'nick_name': 'Karakurt', ...}
            Error returns:
                {'error_text': 'Invalid current password'}
                {'error_text': 'Email invalid'}
                {'error_text': 'Email already found'}
                {'error_text': 'Password too small'}
                {'error_text': 'Display name too long, should be less than 15 characters long'}
                {'error_text': 'Internal service error. Please, try later'}
        """
        parameters = {'current_password': current_password} 
        if full_name != None:
            parameters['full_name'] = full_name
        if new_password != None:
            parameters['new_password'] = new_password
        if email != None:
            parameters['email'] = email
        if display_name != None:
            parameters['display_name'] = display_name
        if privacy != None:
            parameters['privacy'] = privacy
        if date_of_birth != None:
            parameters['date_of_birth'] = date_of_birth
        request = '/API/Users/update'
        response = self._call_api(request, parameters, True)
        return response

    def updatePicture(self, profile_image):
        """
        """
        image = open(profile_image, 'rb')
        parameters = {'profile_image': image}
        request = '/API/Users/updatePicture'
        response = self._call_api(request, parameters)
        return response

    def getKarmaStats(self):
        """ Returns info about a user's karma, including current karma, karma growth, 
            karma graph and the latest reason why the karma has dropped.
            Successful return:
                Dictionary object with karma stats, for details, see: 
                http://www.plurk.com/API#/API/Users/getKarmaStats
        """
        parameters = {}
        request = '/API/Users/getKarmaStats'
        response = self._call_api(request, parameters)
        return response

#=================================== Real time notifications ===================================

    def getUserChannel(self):
        """ Successful return:
                Return's a dict object with an URL that you should listen to, e.g. 
                    {"comet_server": "http://comet03.plurk.com/comet/1235515351741/?channel=generic-4-f733d8522327edf87b4d1651e6395a6cca0807a0", 
                     "channel_name": "generic-4-f733d8522327edf87b4d1651e6395a6cca0807a0"}
        """
        parameters = {}
        request = '/API/Realtime/getUserChannel'
        response = self._call_api(request, parameters)
        return response

#=================================== Polling ===================================

    def getPlurks(self, offset, limit=50):
        """ You should use this call to find out if there any new plurks posted to the user's timeline. 
            Required parameters:
                offset: Return plurks newer than offset, formatted as 2009-6-20T21:55:34.
            Optional parameters:
                limit: The max number of plurks to be returned (default 50).
            Successful return:
                Returns a dictionary object of plurks and their users, e.g. 
                {'plurks': [{'plurk_id': 3, 'content': 'Test', 
                            'qualifier_translated': 'says', 'qualifier': 'says', 'lang': 'en' ...}, ...], 
                            'plurk_users': {'3': {'id': 3852645, 'nick_name': 'Karakurt', ...}}
            Error returns:
                {'error_text': "Requires login'}
        """
        parameters = {'offset': offset,
                      'limit': limit}
        request = '/API/Polling/getPlurks'
        response = self._call_api(request, parameters)
        return response

    def getUnreadCount(self):
        """ Use this call to find out if there are unread plurks on a user's timeline.
            Successful return:
                Returns a dictionary object of counts, e.g. {'all': 2, 'my': 1, 'private': 1, 'responded': 0}
            Error returns:
                {'error_text': 'Requires login'}
        """
        parameters = {}
        request = '/API/Polling/getUnreadCount'
        response = self._call_api(request, parameters)
        return response

#=================================== Timeline ===================================

    def getPlurk(self, plurk_id):
        """ Get plurk by id
            Required parameters:
                plurk_id: The unique id of the plurk. Should be passed as a number, and not base 36 encoded.
            Successful return:
                Returns a dictionary object of the plurk and the owner, e.g. 
                {'plurks': 
                        [{'plurk_id': 3, 
                        'content': "Test", 
                        'qualifier_translated': "says",
                        'qualifier': "says", 
                        'lang': 'en' ...}, ...], 
                'user': 
                        {'id': 3852645, 
                         'nick_name': 'Karakurt', ...}}
            Error returns:
                {'error_text': 'Plurk owner not found'}
                {'error_text': 'Plurk not found'}
                {'error_text': 'No permissions'}
        """
        parameters = {'plurk_id': plurk_id}
        request = '/API/Timeline/getPlurk'
        response = self._call_api(request, parameters)
        return response

    def filterPlurks(self, filter, offset=None, limit=20):
        """ Filter plurks.
            Required parameters:
                filter: Can be only_user, only_responded, only_private or only_favorite.
            Optional parameters:
                offset: Return plurks older than offset, formatted as 2009-6-20T21:55:34.
                limit: How many plurks should be returned? Default is 20.
            Successful return:
                Returns a dictionary object of plurks and their users, e.g. 
                {'plurks': 
                        [{'plurk_id': 3, 
                        'content': 'Test', 
                        'qualifier_translated': 'says', 
                        'qualifier': 'says', 
                        'lang': 'en' ...}, ...], 
                'plurk_users': {'3': {'id': 3852645, 'nick_name': 'Karakurt', ...}}
            Error returns:
                {'error_text': 'Requires login'}
        """
        parameters = {'offset': offset,
                      'limit': limit,
                      'filter': filter}
        request = '/API/Timeline/getPlurks'
        response = self._call_api(request, parameters)
        return response

    def getUnreadPlurks(self, offset=None, limit=20):
        """ Get unread plurks.
            Optional parameters:
                offset: Return plurks older than offset, formatted as 2009-6-20T21:55:34.
                limit: Limit the number of plurks that is retunred.
            Successful return:
                Returns a dictionary object of unread plurks and their users, e.g. 
                    {'plurks': 
                            [{'plurk_id': 3, 
                            'content': 'Test', 
                            'qualifier_translated': 'says', 
                            'qualifier': 'says', 
                            'lang': 'en' ...}, ...], 
                    'plurk_users': {'3': {'id': 3852645, 'nick_name': 'Karakurt', ...}}
            Error returns:
                {'error_text': 'Requires login'}
        """
        parameters = {'offset': offset,
                      'limit': limit}
        request = '/API/Timeline/getUnreadPlurks'
        response = self._call_api(request, parameters)
        return response

    def plurkAdd(self, content, qualifier=':', limited_to = None, no_comments = None, lang = None):
        """ Add new plurk.
            Required parameters:
                content: The Plurk's text.
                qualifier: The Plurk's qualifier, must be in English. See QUALIFIERS
            Optional parameters:
                limited_to: Limit the plurk only to some users (also known as private plurking). 
                            limited_to should be a list of friend ids, e.g. 
                            limited_to of [3,4,66,34] will only be plurked to these user ids. 
                            If limited_to is [0] then the Plurk is privatley posted to the poster's friends.
                no_comments: If set to 1, then responses are disabled for this plurk.
                             If set to 2, then only friends can respond to this plurk.
                lang: The plurk's language. See LANGS
            Successful return:
                Returns a dictionary object of the new plurk, e.g. 
                {'plurk_id': 3, 
                 'content': 'Test',
                 'qualifier_translated': 'says',
                 'qualifier': 'says',
                 'lang': 'en' ...}
            Error returns:
                {'error_text': 'Requires login'}
                {'error_text': 'Invalid data'}
                {'error_text': 'Must be friends'}
                {'error_text': 'Content is empty'}
                {'error_text': 'anti-flood-same-content'}
                {'error_text': 'anti-flood-too-many-new'}
        """
        parameters = {'content': content, 
                      'qualifier': qualifier}
        if limited_to != None:
            parameters['limited_to'] = limited_to
        if no_comments != None:
            parameters['no_comments'] = no_comments
        if lang != None:
            parameters['lang'] = lang
        request = '/API/Timeline/plurkAdd'
        response = self._call_api(request, parameters)
        return response

    def plurkDelete(self, plurk_id):
        """ Delete plurk.
            Required parameters:
                plurk_id: The id of the plurk.
            Successful return:
                {'success_text': 'ok'} if the plurk is deleted
            Error returns:
                {'error_text': 'Requires login'}
                {'error_text': 'Plurk not found'}
                {'error_text': 'No permissions'}
        """
        parameters = {'plurk_id': plurk_id}
        request = '/API/Timeline/plurkDelete'
        response = self._call_api(request, parameters)
        return response

    def plurkEdit(self, plurk_id, content):
        """ Edit plurk.
            Required parameters:
                plurk_id: The id of the plurk.
                content: The content of plurk.
            Successful return:
                Returns a dictionary object of the updated plurk, e.g. 
                {'plurk_id': 3, 'content': 'Test', 'qualifier_translated': 'says', 'qualifier': 'says', 'lang': 'en' ...}
            Error returns:
                {'error_text': 'Requires login'}
                {'error_text': 'Plurk not found'}
                {'error_text': 'No permissions'}
        """
        parameters = {'plurk_id': plurk_id,
                      'content': content}
        request = '/API/Timeline/plurkEdit'
        response = self._call_api(request, parameters)
        return response

    def mutePlurks(self, ids):
        """ Mute plurks by id's
            Required parameters:
                ids: The plurk ids, formated as list, e.g. [342,23242,2323]
            Successful return:
                {'success_text': 'ok'} if the plurks are muted
            Error returns:
                {'error_text': 'Requires login'}
        """
        parameters = {'ids': ids}
        request = '/API/Timeline/mutePlurks'
        response = self._call_api(request, parameters)
        return response

    def unmutePlurks(self, ids):
        """ Unmute plurks by id's
            Required parameters:
                ids: The plurk ids, formated as list, e.g. [342,23242,2323]
            Successful return:
                {'success_text': 'ok'} if the plurks are unmuted
            Error returns:
                {'error_text': 'Requires login'}
        """
        parameters = {'ids': ids}
        request = '/API/Timeline/unmutePlurks'
        response = self._call_api(request, parameters)
        return response

    def favoritePlurks(self, ids):
        """ Favorite plurks by id's
            Required parameters:
                ids: The plurk ids, formated as list, e.g. [342,23242,2323]
            Successful return:
                {'success_text': 'ok'} if the plurks are favorited
            Error returns:
                {'error_text': 'Requires login'}
        """
        parameters = {'ids': ids}
        request = '/API/Timeline/favoritePlurks'
        response = self._call_api(request, parameters)
        return response

    def unfavoritePlurks(self, ids):
        """ Unfavorite plurks by id's
            Required parameters:
                ids: The plurk ids, formated as list, e.g. [342,23242,2323]
            Successful return:
                {'success_text': 'ok'} if the plurks are unfavorited
            Error returns:
                {'error_text': 'Requires login'}
        """
        parameters = {'ids': ids}
        request = '/API/Timeline/unfavoritePlurks'
        response = self._call_api(request, parameters)
        return response

    def markAsRead(self, ids, note_position=False):
        """ Required parameters:
                ids: The plurk ids, formated as list, e.g. [342,23242,2323]
            Optional parameters:
                note_position: If true responses_seen of the plurks will be updated as well (to match response_count).
            Successful return:
                {'success_text': 'ok'} if the plurks are marked as read
            Error returns:
                {'error_text': 'Requires login'}
                {'error_text': "'int' object is not iterable"} if type(ids) is int, not list
        """
        parameters = {'ids': ids}
        if note_position == True:
            parameters['note_position'] = note_position
        request = '/API/Timeline/markAsRead'
        response = self._call_api(request, parameters)
        return response

#=================================== Responses ===================================

    def getResponses(self, plurk_id, from_response):
        """ Fetches responses for plurk with plurk_id and some basic info about the users.
            Required parameters:
                plurk_id: The plurk that the responses belong to.
                from_response: Only fetch responses from an offset - could be 5, 10 or 15.
            Successful return:
                Returns a dict object of responses, friends (users that has posted responses) 
                and responses_seen (the last response that the logged in user has seen) e.g. 
                {'friends': {'3': ...}, 
                 'responses_seen': 2, 
                 'responses': [{'lang': 'en', 'content_raw': 'Reforms...}}
            Error returns:
                {'error_text': 'Requires login'}
                {'error_text': 'Invalid data'}
                {'error_text': 'Plurk not found'}
                {'error_text': 'No permissions'}
        """
        parameters = {'plurk_id': plurk_id,
                      'from_response': from_response}
        request = '/API/Responses/get'
        response = self._call_api(request, parameters)
        return response

    def responseAdd(self, plurk_id, content, qualifier):
        """ Adds a responses to plurk_id. Language is inherited from the plurk.
            Required parameters:
                plurk_id: The plurk that the responses should be added to.
                content: The response's text.
                qualifier: The Plurk's qualifier, must be in English. Can be following: Show example data
            Successful return:
                Returns a dict object of the new responses, e.g. 
                {'id': 3, 'content': 'Test', 'qualifier_translated': 'says', 'qualifier': 'says', ...}
            Error returns:
                {"error_text": "Requires login"}
                {"error_text": "Invalid data"}
                {"error_text": "Content is empty"}
                {"error_text": "Plurk not found"}
                {"error_text": "No permissions"}
                {"error_text": "anti-flood-same-content"}
                {"error_text": "anti-flood-too-many-new"}
        """
        parameters = {'plurk_id': plurk_id,
                      'content': content,
                      'qualifier': qualifier}
        request = '/API/Responses/responseAdd'
        response = self._call_api(request, parameters)
        return response

    def responseDelete(self, response_id, plurk_id):
        """ Deletes a response. A user can delete own responses or responses that are posted to own plurks.
            Required parameters:
                response_id: The id of the response to delete.
                plurk_id: The plurk that the response belongs to.
            Successful return:
                {'success_text': 'ok'} if the response has been deleted.
            Error returns:
                {'error_text': 'Requires login'}
                {'error_text': 'Invalid data'}
                {'error_text': 'No permissions'}
        """
        parameters = {'response_id': response_id,
                      'plurk_id': plurk_id}
        request = '/API/Responses/responseDelete'
        response = self._call_api(request, parameters)
        return response

#=================================== Profile ===================================

    def getOwnProfile(self):
        """ Returns data that's private for the currently logged in user. 
            This can be used to construct a profile and render a timeline of the latest plurks.
            Successful return:
                Returns a dict object with a lot of information that can be used to construct a user's own profile and timeline
                For details, see: http://www.plurk.com/API#/API/Users/getOwnProfile
        """
        parameters = {}
        request = '/API/Profile/getOwnProfile'
        response = self._call_api(request, parameters)
        return response

    def getPublicProfile(self, user_id):
        """ Fetches public information such as a user's public plurks and basic information. 
            Fetches also if the current logged in user is following the user, are friends with or is a fan.
            Required parameters:
                user_id: The user_id of the public profile. Can be integer (like 3852645) or nick name (like "Karakurt").
            Successful return:
                Returns a dict object with a lot of information that can be used to construct 
                a user's public profile and timeline.
                For details, see: http://www.plurk.com/API#/API/Users/getPublicProfile
            Error returns:
                {'error_text': 'Invalid user_id'}
                {'error_text': 'User not found'}
        """
        parameters = {'user_id': user_id}
        request = '/API/Profile/getPublicProfile'
        response = self._call_api(request, parameters)
        return response

#=================================== Friends and fans ===================================

    def getFriendsByOffset(self, user_id, offset=None):
        """ Returns user_id's friend list in chucks of 10 friends at a time.
            Required parameters:
                user_id: The user_id of the public profile. Can be integer (like 3852645)
            Optional parameters:
                offset: The offset, can be 10, 20, 30 etc.
            Successful return:
                Returns a list of dict objects users, e.g. [{'id': 3852645, 'nick_name': 'Karakurt', ...}, ...]
        """
        parameters = {'user_id': user_id}
        if offset != None:
            parameters['offset'] = offset
        request = '/API/FriendsFans/getFriendsByOffset'
        response = self._call_api(request, parameters)
        return response

    def getFansByOffset(self, user_id, offset=None):
        """ Returns user_id's fans list in chucks of 10 fans at a time.
            Required parameters:
                user_id: The user_id of the public profile. Can be integer (like 3852645)
            Optional parameters:
                offset: The offset, can be 10, 20, 30 etc.
            Successful return:
                Returns a list of dict objects users, e.g. [{'id': 3852645, 'nick_name': 'Karakurt', ...}, ...]
        """
        parameters = {'user_id': user_id}
        if offset != None:
            parameters['offset'] = offset
        request = '/API/FriendsFans/getFansByOffset'
        response = self._call_api(request, parameters)
        return response

    def getFollowingByOffset(self, user_id, offset=None):
        """ Returns users that the current logged in user follows as fan - in chucks of 10 fans at a time.
            Required parameters:
                user_id: The user_id of the public profile. Can be integer (like 3852645)
            Optional parameters:
                offset: The offset, can be 10, 20, 30 etc.
            Successful return:
                Returns a list of dict objects users, e.g. [{'id': 3852645, 'nick_name': 'Karakurt', ...}, ...]
        """
        parameters = {'user_id': user_id}
        if offset != None:
            parameters['offset'] = offset
        request = '/API/FriendsFans/getFollowingByOffset'
        response = self._call_api(request, parameters)
        return response

    def becomeFriend(self, friend_id):
        """ Create a friend request to friend_id. User with friend_id has to accept a friendship.
            Required parameters:
                friend_id: The ID of the user you want to befriend.
            Successful return:
                {'success_text': 'ok'} if a friend request has been made.
            Error returns:
                {'error_text': "User can't be befriended"}
                {'error_text': 'User already befriended'}
        """
        parameters = {'friend_id': friend_id}
        request = '/API/FriendsFans/becomeFriend'
        response = self._call_api(request, parameters)
        return response

    def removeAsFriend(self, friend_id):
        """ Remove friend with ID friend_id. friend_id won't be notified.
            Required parameters:
                friend_id: The ID of the user you want to remove
            Successful return:
                {'success_text': 'ok'} if friend_id has been removed as friend.
        """
        parameters = {'friend_id': friend_id}
        request = '/API/FriendsFans/removeAsFriend'
        response = self._call_api(request, parameters)
        return response

    def becomeFan(self, fan_id):
        """ Become fan of fan_id. To stop being a fan of someone, use setFollowing with parameter follow=false.
            Required parameters:
                fan_id: The ID of the user you want to become fan of
            Successful return:
                {'success_text': 'ok'} if the current logged in user is a fan of fan_id.
            Error returns:
                {'error_text': "You can't fan yourself!"}
        """
        parameters = {'fan_id': fan_id}
        request = '/API/FriendsFans/becomeFan'
        response = self._call_api(request, parameters)
        return response

    def setFollowing(self, user_id, follow):
        """ Update following of user_id. A user can befriend someone, but can unfollow them.
            This request is also used to stop following someone as a fan.
            Required parameters:
                user_id: The ID of the user you want to follow/unfollow
                follow: true if the user should be followed, and false if the user should be unfollowed.
            Successful return:
                {'success_text': 'ok'} if following information is updated.
            Error returns:
                {'error_text': 'User must be befriended before you can follow them'}
        """
        if follow:
            follow = 'true'
        else:
            follow = 'false'
        parameters = {'user_id': user_id,
                      'follow': follow}
        request = '/API/FriendsFans/setFollowing'
        response = self._call_api(request, parameters)
        return response

    def getCompletion(self):
        """ Returns a dict object of the logged in users friends (nick name and full name).
            This information can be used to construct auto-completion for private plurking.
            Notice that a friend list can be big, depending on how many friends a user has,
            so this list should be lazy-loaded in your application.
            Successful return:
                Returns a list of dict objects users, e.g. 
                {'3852645': {'nick_name': 'Karakurt', 'full_name': 'Kurt Karakurt'}, 
                 '4': {'nick_name': 'mitsuhiko', ...}, ...}
        """
        parameters = {}
        request = '/API/FriendsFans/getCompletion'
        response = self._call_api(request, parameters)
        return response

#=================================== Alerts ===================================

    def getActive(self):
        """ Return a dict with list of current active alerts.
            Successful return:
                Dict object of all the active alerts, e.g.
                [{'id': 3852645, 'nick_name': 'Karakurt', ...}, ...] 
            Error returns:
                {'error_text': 'Requires login'}
        """
        parameters = {}
        request = '/API/Alerts/getActive'
        response = self._call_api(request, parameters)
        return response

    def getHistory(self):
        """ Return a dict with list of past 30 alerts.
            Successful return:
                Dict object of all the history alerts
                [{'nick_name': 'Karakurt', ...}, ...] 
            Error returns:
                {'error_text': 'Requires login'}
        """
        parameters = {}
        request = '/API/Alerts/getHistory'
        response = self._call_api(request, parameters)
        return response

    def addAsFan(self, user_id):
        """ Accept user_id as fan.
            Required parameters:
                user_id: The user_id that has asked for friendship.
            Successful return:
                {'success_text': 'ok'}
            Error returns:
                {'error_text': 'Requires login'}
        """
        parameters = {'user_id': user_id}
        request = '/API/Alerts/addAsFan'
        response = self._call_api(request, parameters)
        return response

    def addAllAsFan(self):
        """ Accept all friendship requests as fans.
            Successful return:
                {'success_text': 'ok'}
            Error returns:
                {'error_text': 'Requires login'}
        """
        parameters = {}
        request = '/API/Alerts/addAllAsFan'
        response = self._call_api(request, parameters)
        return response

    def addAllAsFriends(self):
        """ Accept all friendship requests as friends.
            Successful return:
                {'success_text': 'ok'}
            Error returns:
                {'error_text': 'Requires login'}
        """
        parameters = {}
        request = '/API/Alerts/addAllAsFriends'
        response = self._call_api(request, parameters)
        return response

    def addAsFriend(self, user_id):
        """ Accept user_id as friend.
            Required parameters:
                user_id: The user_id that has asked for friendship.
            Successful return:
                {'success_text': 'ok'}
            Error returns:
                {'error_text': 'Requires login'}
        """
        parameters = {'user_id': user_id}
        request = '/API/Alerts/addAsFriend'
        response = self._call_api(request, parameters)
        return response

    def denyFriendship(self, user_id):
        """ Deny friendship to user_id.
            Required parameters:
                user_id: The user_id that has asked for friendship.
            Successful return:
                {'success_text': 'ok'}
            Error returns:
                {'error_text': 'Requires login'}
        """
        parameters = {'user_id': user_id}
        request = '/API/Alerts/denyFriendship'
        response = self._call_api(request, parameters)
        return response

    def removeNotification(self, user_id):
        """ Remove notification to user with id user_id.
            Required parameters:
                user_id: The user_id that the current user has requested friendship for.
            Successful return:
                {'success_text': 'ok'}
            Error returns:
                {'error_text': 'Requires login'}
        """
        parameters = {'user_id': user_id}
        request = '/API/Alerts/removeNotification'
        response = self._call_api(request, parameters)
        return response

#=================================== Search ===================================

    def plurkSearch(self, query, offset = None):
        """ Returns the latest 20 plurks on a search term.
            Required parameters:
                query: The query after Plurks.
            Optional parameters:
                offset: A plurk_id of the oldest Plurk in the last search result.
            Successful return:
                A dict of list of plurks that the user have permissions to see:
                [{'id': 3, 'content': 'Test', 'qualifier_translated': 'says', 'qualifier': 'says', ...}, ...]
        """
        parameters = {'query': query}
        if offset != None:
            parameters['offset'] = offset
        request = '/API/PlurkSearch/search'
        response = self._call_api(request, parameters)
        return response

    def userSearch(self, query, offset = None):
        """ Returns 10 users that match query, users are sorted by karma.
            Required parameters:
                query: The query after users.
            Optional parameters:
                offset: Page offset, like 10, 20, 30 etc.
            Successful return:
                A dict of list of plurks that the user have permissions to see:
                [{'id': 3, 'content': 'Test', 'qualifier_translated': 'says', 'qualifier': 'says', ...}, ...]
        """
        parameters = {'query': query}
        if offset != None:
            parameters['offset'] = offset
        request = '/API/UserSearch/search'
        response = self._call_api(request, parameters)
        return response

#=================================== Emoticons ===================================

    def emoticonsGet(self):
        """ Emoticons are a big part of Plurk since they make it easy to express feelings. 
            Check out current Plurk emoticons: http://www.plurk.com/Help/extraSmilies
            This call returns a dict object that looks like:
                {"karma": {"0": [[":-))", "http:\/\/statics.plurk.com\/XXX.gif"], ...], ...},
                 "recuited": {"10": [["(bigeyes)", "http:\/\/statics.plurk.com\/XXX.gif"], ...], ...} }
            emoticons["karma"][25] denotes that the user has to have karma over 25 to use these emoticons.
            emoticons["recuited"][10] means that the user has to have user.recuited >= 10 to use these emoticons.
            It's important to check for these things on the client as well,
            since the emoticon levels are checked in the models.
        """
        parameters = {}
        request = '/API/Emoticons/get'
        response = self._call_api(request, parameters)
        return response

#=================================== Blocks ===================================

    def getBlocks(self, offset = None):
        """ A list of users that are blocked by the current user.
            Optional parameters:
                offset: What page should be shown, e.g. 0, 10, 20.
            Successful return:
                A dict with list of users that are blocked by the current user, e.g. 
                {"total": 12, "users": {"display_name": "amix3", "gender": 0, "nick_name": "amix", 
                 "has_profile_image": 1, "id": 3476548, "avatar": null}, ...]}
        """
        parameters = {}
        if offset != None:
            parameters['offset'] = offset
        request = '/API/Blocks/get'
        response = self._call_api(request, parameters)
        return response

    def block(self, user_id):
        """ Block user by user_id.
        Required parameters:
            user_id: The id of the user that should be blocked.
        Successful return:
            {'success_text': 'ok'}
        """
        parameters = {'user_id': user_id}
        request = '/API/Blocks/block'
        response = self._call_api(request, parameters)
        return response

    def unblock(self, user_id):
        """ Unblock user by user_id.
            Required parameters:
                user_id: The id of the user that should be unblocked.
            Successful return:
                {'success_text': 'ok'}
        """
        parameters = {'user_id': user_id}
        request = '/API/Blocks/unblock'
        response = self._call_api(request, parameters)
        return response

#=================================== Cliques ===================================

    def getCliques(self):
        """ Get list of users current cliques
        Successful return:
            Returns a dict with list of users current cliques, e.g. ['Homies', 'Coders', ...]
        """
        parameters = {}
        request = '/API/Cliques/getCliques'
        response = self._call_api(request, parameters)
        return response

    def getClique(self, clique_name):
        """ Get the users in the clique.
            Required parameters:
                clique_name: The name of the clique
            Successful return:
                Returns the users in the clique, e.g. 
                [{'display_name': 'Kurt', 'gender': 0, 'nick_name': 'Karakurt',
                  'has_profile_image': 1, 'id': 3852645, 'avatar': null}, ...]
        """
        parameters = {'clique_name': clique_name}
        request = '/API/Cliques/getClique'
        response = self._call_api(request, parameters)
        return response

    def createClique(self, clique_name):
        """ Create new clique.
            Required parameters:
                clique_name: The name of the new clique
            Successful return:
                {'success_text': 'ok'}
        """
        parameters = {'clique_name': clique_name}
        request = '/API/Cliques/createClique'
        response = self._call_api(request, parameters)
        return response

    def renameClique(self, clique_name, new_name):
        """ Rename clique clique_name to new_name.
            Required parameters:
                clique_name: The name of the clique to rename
                new_name: The name of the new clique
            Successful return:
                {'success_text': 'ok'}
        """
        parameters = {'clique_name': clique_name,
                      'new_name': new_name}
        request = '/API/Cliques/renameClique'
        response = self._call_api(request, parameters)
        return response

    def addToClique(self, clique_name, user_id):
        """ Add user to the clique.
            Required parameters:
                clique_name: The name of the clique
                user_id: The user to add to the clique
            Successful return:
                {'success_text': 'ok'}
            Error returns:
                {'error_text': 'Clique not created'}
        """
        parameters = {'clique_name': clique_name,
                      'user_id': user_id}
        request = '/API/Cliques/add'
        response = self._call_api(request, parameters)
        return response

    def removeFromClique(self, clique_name, user_id):
        """ Add user to the clique.
            Required parameters:
                clique_name: The name of the clique
                user_id: The user to remove from the clique
            Successful return:
                {'success_text': 'ok'}
            Error returns:
                {'error_text': 'Clique not created'}
        """
        parameters = {'clique_name': clique_name,
                      'user_id': user_id}
        request = '/API/Cliques/remove'
        response = self._call_api(request, parameters)
        return response

    def deleteClique(self, clique_name):
        """ Delete clique.
            Required parameters:
                clique_name: The name of the delete clique
            Successful return:
                {'success_text': 'ok'}
        """
        parameters = {'clique_name': clique_name}
        request = '/API/Cliques/delete_clique'
        response = self._call_api(request, parameters)
        return response

#=================================== Utils ===================================

    def usernameToUid(self, username):
        """ Convert username to user_id.
            Required parameters:
                username: The user's nick name
            Successful return:
                The user_id of the public profile. Can be integer (like 3852645).
        """
        return self.getPublicProfile(username)['user_info']['id']

    def linkToPlurkID(self, link):
        """ Convert link to plurk_id. 
            Required parameters:
                link: The link to plurk
            Successful return:
                The unique id of the plurk. Can be integer (like 3852645).
        """
        shorten = link[len('http://www.plurk.com/p/'):]
        plurk_id = int(shorten, 36)
        return plurk_id

    def plurkIDToLink(self, plurk_id):
        """ Convert plurk_id to link. 
            Required parameters:
                plurk_id: The unique id of the plurk. Should be passed as a number, and not base 36 encoded.
            Successful return:
                The link to the plurk, e.g. "http://www.plurk.com/p/7ym3mf"
        """
        alphabet = "0123456789abcdefghijklmnopqrstuvwxyz"
        if plurk_id == 0:
            return '0'
        shorten = ''
        while plurk_id != 0:
            plurk_id, i = divmod(plurk_id, 36)
            shorten = alphabet[i] + shorten
        link = 'http://www.plurk.com/p/' + shorten
        return link
