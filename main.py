from flask import Flask, jsonify
from flask_pymongo import PyMongo
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flasgger import Swagger
import os
from dotenv import load_dotenv
from pymongo import MongoClient
import certifi
from routes.recipeRoute import recipe_routes

from routes.registerRoute import register_routes

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['MONGO_URI'] = os.getenv('MONGO_URI')
app.config['MONGO_SSL'] = True
app.config['MONGO_SSL_CERT_REQS'] = False

# Initialize extensions using certifi for SSL verification
mongo = PyMongo(app)  # Create an instance of PyMongo with default settings

# Test MongoDB connection with custom client using certifi
client = MongoClient(app.config['MONGO_URI'], tls=True, tlsCAFile=certifi.where())
mongo.init_app(app, uri=app.config['MONGO_URI'], tls=True, tlsCAFile=certifi.where())

bcrypt = Bcrypt(app)  # Initialize Bcrypt
jwt = JWTManager(app)  # Initialize JWT Manager
swagger = Swagger(app)

# Test MongoDB connection route
@app.route('/test_db_connection', methods=['GET'])
def test_db_connection():
    try:
        collections = mongo.db.list_collection_names()
        return jsonify({"message": "MongoDB connection successful!", "collections": collections}), 200
    except Exception as e:
        return jsonify({"message": "MongoDB connection failed!", "error": str(e)}), 500

# Register routes (assuming these are defined in your routes)
register_routes(app, mongo)
recipe_routes(app)

if __name__ == "__main__":
    app.run(debug=True)