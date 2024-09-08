from flask import Flask, request, jsonify, abort
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///example.db'

# Initialize SQLAlchemy and Migrate
db = SQLAlchemy(app)
migrate = Migrate(app, db)

class Hero(db.Model):
    __tablename__ = 'heroes'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    super_name = db.Column(db.String, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "super_name": self.super_name
        }

class Power(db.Model):
    __tablename__ = 'powers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description
        }

class HeroPower(db.Model):
    __tablename__ = 'hero_powers'
    id = db.Column(db.Integer, primary_key=True)
    hero_id = db.Column(db.Integer, db.ForeignKey('heroes.id'), nullable=False)
    power_id = db.Column(db.Integer, db.ForeignKey('powers.id'), nullable=False)
    strength = db.Column(db.String, nullable=False)

    hero = db.relationship('Hero', backref='hero_powers')
    power = db.relationship('Power', backref='hero_powers')

    def to_dict(self):
        return {
            "id": self.id,
            "hero_id": self.hero_id,
            "power_id": self.power_id,
            "strength": self.strength,
            "hero": self.hero.to_dict(),
            "power": self.power.to_dict()
        }

@app.route('/heroes', methods=['GET'])
def get_heroes():
    heroes = Hero.query.all()
    return jsonify([hero.to_dict() for hero in heroes])

@app.route('/heroes/<int:id>', methods=['GET'])
def get_hero(id):
    hero = Hero.query.get(id)
    if not hero:
        return jsonify({"error": "Hero not found"}), 404
    return jsonify(hero.to_dict())

@app.route('/powers', methods=['GET'])
def get_powers():
    powers = Power.query.all()
    return jsonify([power.to_dict() for power in powers])

@app.route('/powers/<int:id>', methods=['GET'])
def get_power(id):
    power = Power.query.get(id)
    if not power:
        return jsonify({"error": "Power not found"}), 404
    return jsonify(power.to_dict())

@app.route('/powers/<int:id>', methods=['PATCH'])
def update_power(id):
    power = Power.query.get(id)
    if not power:
        return jsonify({"error": "Power not found"}), 404
    
    data = request.json
    description = data.get('description')
    
    if description:
        if len(description) < 20:
            return jsonify({"errors": ["description must be at least 20 characters long"]}), 400
        power.description = description
        db.session.commit()
    
    return jsonify(power.to_dict())

@app.route('/hero_powers', methods=['POST'])
def create_hero_power():
    data = request.json
    strength = data.get('strength')
    hero_id = data.get('hero_id')
    power_id = data.get('power_id')
    
    if strength not in ["Strong", "Weak", "Average"]:
        return jsonify({"errors": ["Invalid strength value"]}), 400
    
    try:
        hero_power = HeroPower(hero_id=hero_id, power_id=power_id, strength=strength)
        db.session.add(hero_power)
        db.session.commit()
    except ValueError as e:
        return jsonify({"errors": [str(e)]}), 400
    except IntegrityError:
        db.session.rollback()
        return jsonify({"errors": ["Invalid hero_id or power_id"]}), 400

    return jsonify(hero_power.to_dict())

if __name__ == '__main__':
    app.run(port=5555, debug=True)
