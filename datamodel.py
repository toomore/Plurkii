from google.appengine.ext import db

class datacofriend(db.Model):
    uaname = db.StringProperty()
    uaid = db.IntegerProperty()
    ubname = db.StringProperty()
    ubid = db.IntegerProperty()
    uindate = db.DateTimeProperty(auto_now_add = True)

class userplurkdata(db.Model):
    uname = db.StringProperty()
    fullname = db.StringProperty()
    karma = db.IntegerProperty()
    avatar = db.IntegerProperty()
    gender  = db.IntegerProperty()
    birthday = db.DateProperty()
    location = db.StringProperty()
    uindate = db.DateTimeProperty(auto_now_add = True)
