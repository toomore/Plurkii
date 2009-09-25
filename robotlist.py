from google.appengine.ext import db

class iirobot(db.Model):
    botno = db.IntegerProperty()
    botname = db.StringProperty()
    botpwd = db.StringProperty()
