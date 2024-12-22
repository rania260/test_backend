import pytest
from flask import Flask
from flask_pymongo import PyMongo
from dotenv import load_dotenv
import os

# Charger les variables d'environnement depuis le fichier .env
load_dotenv()

@pytest.fixture
def app():
    app = Flask(__name__)
    
    # Configuration de l'application pour les tests
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    app.config['MONGO_URI'] = os.getenv('MONGO_URI')
    app.config['MONGO_SSL'] = True
    app.config['MONGO_SSL_CERT_REQS'] = False
    
    # Initialisation de MongoDB
    mongo = PyMongo(app)
    
    # Enregistrement des routes
    from routes.registerRoute import register_routes
    register_routes(app, mongo)
    
    return app

@pytest.fixture
def mongo(app):
    return PyMongo(app)
