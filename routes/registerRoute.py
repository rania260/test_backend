from flask import request, jsonify, Flask
from flask.typing import ResponseReturnValue
from pymongo.database import Database
import jwt
import datetime
import re
from flask_bcrypt import Bcrypt
from models.userModel import User

bcrypt = Bcrypt()

def register_routes(app: Flask, mongo: Database) -> None:
    """Register all authentication related routes.

    Args:
        app: Flask application instance
        mongo: MongoDB database instance
    """

    @app.route('/')
    def home() -> str:
        return "Welcome to the Flask JWT Auth API!"

    @app.route('/register', methods=['POST'])
    def register() -> ResponseReturnValue:
        """Register a new user."""
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        email = data.get('email')

        # Input validation
        if not email or not username or not password:
            return jsonify({'error': 'All fields (username, email, password) are required'}), 400

        # Validate email format
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            return jsonify({'error': 'Invalid email format'}), 400

        if mongo.db.users.find_one({'$or': [{'email': email}, {'username': username}]}):
            return jsonify({"error": "Email or Username already exists"}), 400
        
        new_user = User.create_user(mongo, username, email, password)  
        if not new_user:
            return jsonify({"error": "Error Creating User"}), 500

        return jsonify({"message": "User registered successfully!"}), 201

    @app.route('/login', methods=['POST'])
    def login() -> ResponseReturnValue:
        """Authenticate a user and return a JWT token."""
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return jsonify({"error": "Email and password are required"}), 400

        user = mongo.db.users.find_one({'email': email})
        if user and bcrypt.check_password_hash(user['password'], password):
            try:
                token = jwt.encode({
                    'sub': str(user['_id']),
                    'username': user['username'],
                    'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)
                }, app.config['SECRET_KEY'], algorithm='HS256')
                return jsonify({'token': token}), 200
            except Exception as e:
                return jsonify({"error": "Error generating token"}), 500
        
        return jsonify({"error": "Invalid credentials"}), 401