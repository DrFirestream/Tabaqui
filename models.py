from app import db
from datetime import datetime

class Journal(db.Model):
    __tablename__ = 'journal'

    id = db.Column(db.Integer, primary_key=True)
    request = db.Column(db.DateTime, nullable = False, default = datetime.utcnow)


    #def __init__(self, name, author, published):
    #    self.name = name
    #    self.author = author
    #    self.published = published

    def __repr__(self):
        return '<id {}>'.format(self.id)
    
    def serialize(self):
        return {
            'id': self.id, 
            'request': self.request
        }