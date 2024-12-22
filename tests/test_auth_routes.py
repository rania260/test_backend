import pytest
from flask import json

@pytest.fixture
def test_client(app):
    # Configure un client de test Flask
    return app.test_client()

def test_register_success(test_client, mongo):
    """Test successful user registration"""
    # Efface les utilisateurs avant le test
    mongo.db.users.delete_many({})
    
    data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "password123"
    }
    
    response = test_client.post('/register',
                                data=json.dumps(data),
                                content_type='application/json')
    
    assert response.status_code == 201
    assert b"User registered successfully" in response.data

def test_register_duplicate_email(test_client, mongo):
    """Test registration with duplicate email"""
    # Efface les utilisateurs avant le test
    mongo.db.users.delete_many({})
    
    # Première inscription
    data = {
        "username": "testuser1",
        "email": "test@example.com",
        "password": "password123"
    }
    test_client.post('/register',
                     data=json.dumps(data),
                     content_type='application/json')
    
    # Deuxième inscription avec le même email
    data["username"] = "testuser2"
    response = test_client.post('/register',
                                data=json.dumps(data),
                                content_type='application/json')
    
    assert response.status_code == 400
    assert b"Email or Username already exists" in response.data

def test_register_missing_fields(test_client):
    """Test registration with missing fields"""
    data = {
        "username": "testuser",
        "email": "test@example.com"
        # Le champ password manque
    }
    
    response = test_client.post('/register',
                                data=json.dumps(data),
                                content_type='application/json')
    
    assert response.status_code == 400
    assert b"All fields (username, email, password) are required" in response.data

def test_login_success(test_client, mongo):
    """Test successful login"""
    # Efface les utilisateurs avant le test
    mongo.db.users.delete_many({})
    
    # Inscrit un utilisateur
    register_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "password123"
    }
    test_client.post('/register',
                     data=json.dumps(register_data),
                     content_type='application/json')
    
    # Tente de se connecter
    login_data = {
        "email": "test@example.com",
        "password": "password123"
    }
    response = test_client.post('/login',
                                data=json.dumps(login_data),
                                content_type='application/json')
    
    assert response.status_code == 200
    response_data = json.loads(response.data)
    assert 'token' in response_data

def test_login_invalid_credentials(test_client, mongo):
    """Test login with invalid credentials"""
    # Efface les utilisateurs avant le test
    mongo.db.users.delete_many({})
    
    # Inscrit un utilisateur
    register_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "password123"
    }
    test_client.post('/register',
                     data=json.dumps(register_data),
                     content_type='application/json')
    
    # Tente de se connecter avec un mauvais mot de passe
    login_data = {
        "email": "test@example.com",
        "password": "wrongpassword"
    }
    response = test_client.post('/login',
                                data=json.dumps(login_data),
                                content_type='application/json')
    
    assert response.status_code == 401
    assert b"Invalid credentials" in response.data
