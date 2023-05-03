from flask import Flask, request, make_response, jsonify
from flask_cors import CORS
from flask_migrate import Migrate
from flask_restful import Api, Resource
from models import db, Camper, Activity, Signup

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

CORS(app)
migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)


class Campers(Resource):
    def get(self):
        campers = Camper.query.all()
        campers_dict = [camper.to_dict() for camper in campers]
        return make_response(campers_dict, 200)

    def post(self):
        request_json = request.get_json()
        try:
            camper = Camper(
                name=request_json['name'],
                age=request_json['age']
            )
            db.session.add(camper)
            db.session.commit()
        except Exception as ex:
            msg = {"error": [ex.__str__()]}
            print(msg)
            return (msg, 422)
        return (camper.to_dict(), 201)
api.add_resource(Campers, '/campers')

class CamperById(Resource):
    def get(self, id):
        camper = Camper.query.filter_by(id=id).first()
        if not camper:
            return make_response({'error': 'Camper not found'}, 404)
        return make_response(camper.to_dict(rules=('activities',)), 200)
api.add_resource(CamperById, '/campers/<int:id>')


class Activities(Resource):
    def get(self):
        activities = Activity.query.all()
        activities_dict = [activity.to_dict() for activity in activities]
        return make_response(activities_dict, 200)
api.add_resource(Activities, '/activities')


class ActivityById(Resource):
    def delete(self, id):
        activity = Activity.query.filter_by(id=id).first()
        if not activity:
            return make_response({'error': 'Activity not found'}, 404)
        db.session.delete(activity)
        db.session.commit()
        return make_response("", 200)
api.add_resource(ActivityById, '/activities/<int:id>')


class Signups(Resource):
    def post(self):
        request_json = request.get_json()
        try:
            signup = Signup(
                time=request_json['time'],
                camper_id=request_json['camper_id'],
                activity_id=request_json['activity_id']
            )
            db.session.add(signup)
            db.session.commit()
        except Exception as ex:
            return ({"error": [ex.__str__()]}, 422)
        return (signup.activity.to_dict(), 201)
api.add_resource(Signups, '/signups')


if __name__ == '__main__':
    app.run(port=5555, debug=True)
