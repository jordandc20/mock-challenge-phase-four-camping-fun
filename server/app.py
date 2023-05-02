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
        campers = [camper.to_dict() for camper in Camper.query.all()]
        return make_response(campers,200)
    
    def post(self):
        try:
            camper_data = request.get_json()
            new_camper = Camper(
                name = camper_data['name'],
                age = camper_data['age']
            )
            db.session.add(new_camper)
            db.session.commit()
        except Exception as ex:
            return make_response({
                'error': [ex.__str__()]
            }, 422)
            
        
        return make_response(new_camper.to_dict(), 201)
        
    
api.add_resource(Campers, '/campers')

class CamperById(Resource):
    def get(self,id):
        camper = Camper.query.filter_by(id=id).first()
        if not camper:
            return make_response({'error':'Camper not found'}, 404)
        return make_response(camper.to_dict(rules = ('activities',)),200)
    
api.add_resource(CamperById,'/campers/<int:id>')


class Activities(Resource):
    def get(self):
        activities = [activity.to_dict() for activity in Activity.query.all()]
        return make_response(activities,200)
api.add_resource(Activities,'/activities')
    
class ActivityById(Resource):
    def delete(self,id):
        activity = Activity.query.filter_by(id=id).first()
        
        if not activity:
            return make_response({'error':'Activity not found'},404)
        try:
            db.session.delete(activity)
            db.session.commit()
        except Exception as e:
            return make_response(
                {
                    "errors": [e.__str__()]
                },
                422
            )
        return make_response({}, 200)
        
api.add_resource(ActivityById,'/activities/<int:id>')
        
class Signups(Resource):
    def post(self):
        signup_data = request.get_json()
        try:
            new_signup = Signup(
                time= signup_data['time'],
                camper_id= signup_data['camper_id'],
                activity_id= signup_data['activity_id']
            )
            db.session.add(new_signup)
            db.session.commit()
        except Exception as ex:
            return make_response({
                'error': [ex.__str__()]
            }, 422) 
        
        return make_response(new_signup.activity.to_dict(), 201)
            
            
api.add_resource(Signups,'/signups')

if __name__ == '__main__':
    app.run(port=5555, debug=True)
