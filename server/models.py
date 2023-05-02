from flask_sqlalchemy import SQLAlchemy
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy.orm import validates
from sqlalchemy.ext.associationproxy import association_proxy

db = SQLAlchemy()


class Camper(db.Model, SerializerMixin):
    __tablename__ = 'campers'
    serialize_rules = ('-created_at','-updated_at', '-signups',  '-activities.created_at','-activities.updated_at', '-activities.campers')

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    age = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, server_default = db.func.now())
    updated_at = db.Column(db.DateTime, onupdate = db.func.now())
    signups = db.relationship('Signup', backref = 'camper', cascade ='all,delete,delete-orphan')
    activities = association_proxy('signups', 'activity')

@validates('name')
def validate_name(self, key, value):
    if not value:
        raise ValueError('name required')
    return value

@validates('age')
def validate_age(self, key, value):
    if not value:
        raise ValueError('age required')
    elif not (8>= value <=18):
        raise ValueError('age must be between 8 and 18')
    return value
    

class Activity(db.Model, SerializerMixin):
    __tablename__ = 'activities'
    serialize_rules = ('-created_at','-updated_at', '-signups',  '-campers.activities')
    

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    difficulty = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())
    signups =db.relationship('Signup', backref = 'activity', cascade = 'all,delete,delete-orphan')
    campers = association_proxy('signups', 'camper')


class Signup(db.Model, SerializerMixin):
    __tablename__ = 'signups'
    serialize_rules = ('-camper.signups', '-activity.signups','-camper.activities', '-activity.campers', '-created_at', '-updated_at')

    id = db.Column(db.Integer, primary_key=True)
    camper_id = db.Column(db.Integer, db.ForeignKey("campers.id"))
    activity_id = db.Column(db.Integer, db.ForeignKey('activities.id'))
    time = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())

@validates('time')
def validate_time(self, key, value):
    if not value:
        raise ValueError('Time is Required')
    elif value < 0 or value > 23:
                raise ValueError('Time must be between 0 and 23.')
    return value