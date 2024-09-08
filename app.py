from models import db, Hero, Power, HeroPower
from flask_migrate import Migrate
from flask import Flask, request, jsonify, make_response
from flask_restful import Api, Resource
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)
db.init_app(app)
api = Api(app)

class Home(Resource):
    def get(self):
        response = {"message": "Welcome to the Heroes API"}
        return make_response(jsonify(response), 200)

api.add_resource(Home, "/")

class Heroes(Resource):
    def get(self):
        heroes = Hero.query.all()
        hero_list = [hero.to_dict(only=("id", "name", "super_name")) for hero in heroes]
        return make_response(jsonify(hero_list), 200)

api.add_resource(Heroes, "/heroes")

class HeroById(Resource):
    def get(self, id):
        hero = db.session.get(Hero, id)
        if hero:
            return make_response(jsonify(hero.to_dict(only=("id", "name", "super_name", "hero_powers.power", "hero_powers.strength"))), 200)
        else:
            return make_response(jsonify({"error": "Hero not found"}), 404)

api.add_resource(HeroById, "/heroes/<int:id>")

class Powers(Resource):
    def get(self):
        powers = Power.query.all()
        power_list = [power.to_dict(only=("id", "name", "description")) for power in powers]
        return make_response(jsonify(power_list), 200)

api.add_resource(Powers, "/powers")

class PowerById(Resource):
    def get(self, id):
        power = db.session.get(Power, id)
        if power:
            return make_response(jsonify(power.to_dict(only=("id", "name", "description"))), 200)
        else:
            return make_response(jsonify({"error": "Power not found"}), 404)

    # PATCH /powers/:id: Update power description
    def patch(self, id):
        power = db.session.get(Power, id)
        if not power:
            return make_response(jsonify({"error": "Power not found"}), 404)
        
        data = request.get_json()
        description = data.get("description", "")

        if len(description) < 20:
            # Return the standardized error message
            return make_response(jsonify({"errors": ["validation errors"]}), 400)

        try:
            power.description = description
            db.session.commit()
            return make_response(jsonify(power.to_dict(only=("id", "name", "description"))), 200)
        except Exception as e:
            return make_response(jsonify({"errors": ["validation errors"]}), 400)

api.add_resource(PowerById, "/powers/<int:id>")

class HeroPowers(Resource):
    def post(self):
        data = request.get_json()
        try:
            hero_id = data["hero_id"]
            power_id = data["power_id"]
            strength = data["strength"]

            # Ensure hero and power exist
            hero = db.session.get(Hero, hero_id)
            power = db.session.get(Power, power_id)
            if not hero or not power:
                raise ValueError("Hero or Power not found.")

            # Validate strength value
            allowed_strengths = ['Strong', 'Weak', 'Average']
            if strength not in allowed_strengths:
                return make_response(jsonify({"errors": ["validation errors"]}), 400)

            # Validation and creation of HeroPower
            new_hero_power = HeroPower(hero_id=hero_id, power_id=power_id, strength=strength)
            db.session.add(new_hero_power)
            db.session.commit()

            response_dict = new_hero_power.to_dict()
            return make_response(jsonify(response_dict), 200)
        except ValueError as e:
            return make_response(jsonify({"errors": ["validation errors"]}), 400)

api.add_resource(HeroPowers, "/hero_powers")

if __name__ == '__main__':
    app.run(port=5555, debug=True)