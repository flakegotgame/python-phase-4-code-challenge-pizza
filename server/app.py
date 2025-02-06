from flask import Flask, request, jsonify
from flask_migrate import Migrate
from flask_cors import CORS
from models import db, Restaurant, Pizza, RestaurantPizza

app = Flask(__name__)
CORS(app)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)
migrate = Migrate(app, db)

# GET /restaurants
@app.route('/restaurants', methods=['GET'])
def get_restaurants():
    restaurants = Restaurant.query.all()
    return jsonify([restaurant.to_dict() for restaurant in restaurants]), 200

# GET /restaurants/:id
@app.route('/restaurants/<int:id>', methods=['GET'])
def get_restaurant(id):
    restaurant = Restaurant.query.get(id)
    if restaurant:
        return jsonify({
            "id": restaurant.id,
            "name": restaurant.name,
            "address": restaurant.address,
            "restaurant_pizzas": [rp.to_dict() for rp in restaurant.restaurant_pizzas]
        }), 200
    return jsonify({"error": "Restaurant not found"}), 404

# DELETE /restaurants/:id
@app.route('/restaurants/<int:id>', methods=['DELETE'])
def delete_restaurant(id):
    restaurant = Restaurant.query.get(id)
    if restaurant:
        db.session.delete(restaurant)
        db.session.commit()
        return '', 204
    return jsonify({"error": "Restaurant not found"}), 404

# GET /pizzas
@app.route('/pizzas', methods=['GET'])
def get_pizzas():
    pizzas = Pizza.query.all()
    return jsonify([pizza.to_dict() for pizza in pizzas]), 200

# POST /restaurant_pizzas
@app.route('/restaurant_pizzas', methods=['POST'])
def create_restaurant_pizza():
    data = request.get_json()

    # Validate price range
    if 'price' not in data or not (1 <= data['price'] <= 30):
        return jsonify({"errors": ["Price must be between 1 and 30"]}), 400

    restaurant = Restaurant.query.get(data['restaurant_id'])
    pizza = Pizza.query.get(data['pizza_id'])

    if not restaurant or not pizza:
        return jsonify({"errors": ["Invalid restaurant or pizza ID"]}), 400

    new_restaurant_pizza = RestaurantPizza(
        price=data['price'],
        restaurant_id=data['restaurant_id'],
        pizza_id=data['pizza_id']
    )

    db.session.add(new_restaurant_pizza)
    db.session.commit()

    return jsonify(new_restaurant_pizza.to_dict()), 201

if __name__ == '__main__':
    app.run(port=5555, debug=True)
