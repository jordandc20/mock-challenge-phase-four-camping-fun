from flask_sqlalchemy import SQLAlchemy
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy.orm import validates
from sqlalchemy.ext.associationproxy import association_proxy

db = SQLAlchemy()


class Camper(db.Model, SerializerMixin):
    __tablename__ = 'campers'
    serialize_rules = ('-created_at', '-updated_at',
                       '-signups', '-activities.campers')

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    age = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())

    signups = db.relationship(
        'Signup', backref='camper', cascade="all, delete, delete-orphan")
    activities = association_proxy('signups', 'activity')

    @validates('name')
    def validate_camper_name(self, key, value):
        if not value:
            raise ValueError('must provide camper name')
        return value

    @validates('age')
    def validate_camper_age(self, key, value):
        if value < 8:
            raise ValueError('camper mut be at least 8 years old')
        elif value > 18:
            raise ValueError('camper mut be at most 18 years old')
        return value


class Activity(db.Model, SerializerMixin):
    __tablename__ = 'activities'
    serialize_rules = ('-created_at', '-updated_at',
                       '-signups', '-campers.activities')

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    difficulty = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())
    signups = db.relationship(
        'Signup', backref='activity', cascade="all, delete, delete-orphan")
    campers = association_proxy('signups', 'camper')


class Signup(db.Model, SerializerMixin):
    __tablename__ = 'signups'

    id = db.Column(db.Integer, primary_key=True)
    camper_id = db.Column(db.Integer, db.ForeignKey(
        'campers.id'), nullable=False)
    activity_id = db.Column(db.Integer, db.ForeignKey(
        'activities.id'), nullable=False)
    time = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())

    @validates('time')
    def validate_time(self, key, value):
        if value < 0:
            raise ValueError('time mut be at least 0')
        elif value > 23:
            raise ValueError('time mut be at most 23')
        return value

    @validates('camper_id')
    def validate_camper_id(self, key, value):
        campers = Camper.query.all()
        campers_dict = [camper.id for camper in campers]
        if value not in campers_dict:
            raise ValueError('invalid camper')
        return value

    @validates('activity_id')
    def validate_activity_id(self, key, value):
        activities = Activity.query.all()
        activities_dict = [activity.id for activity in activities]
        if value not in activities_dict:
            raise ValueError('invalid activity')
        return value
