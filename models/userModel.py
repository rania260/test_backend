from flask import Flask
from flask_pymongo import PyMongo
from flask_bcrypt import Bcrypt

# Initialize Bcrypt globally
bcrypt = Bcrypt()

mongo = PyMongo()  # This will be initialized in main.py

class User:
    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = self.hash_password(password)

    @staticmethod
    def hash_password(password):
        """Hash the password using Bcrypt."""
        return bcrypt.generate_password_hash(password).decode('utf-8')

    @staticmethod
    def create_user(mongo, username, email, password):
        """Create a new user in the database."""
        # Validate required fields
        if not username or not email or not password:
            return {'error': 'All fields (username, email, password) are required'}, 400

        # Check if the username or email already exists
        if mongo.db.users.find_one({'username': username}):
            return {'error': 'Username already exists'}, 400

        if mongo.db.users.find_one({'email': email}):
            return {'error': 'Email already exists'}, 400

        # Create a new user
        hashed_password = User.hash_password(password)
        mongo.db.users.insert_one({
            'username': username,
            'email': email,
            'password': hashed_password
        })
        
        return {'message': 'User created successfully', 'username': username}, 201
    
    @staticmethod
    def find_user(mongo, username):
        """Find a user by their username."""
        return mongo.db.users.find_one({'username': username})