from google.appengine.ext import db

class datacofriend(db.Model):
    uaname = db.StringProperty()
    uaid = db.IntegerProperty()
    ubname = db.StringProperty()
    ubid = db.IntegerProperty()
    uindate = db.DateTimeProperty(auto_now_add = True)
