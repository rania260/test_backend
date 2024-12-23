import pytest
from flask import Flask
import pandas as pd
from routes.recipeRoute import recipe_routes
import json

@pytest.fixture
def app():
    app = Flask(__name__)
    app.config['TESTING'] = True
    recipe_routes(app)
    return app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def mock_dataset(monkeypatch):
    # Créer un DataFrame de test
    test_data = {
        'title': ['Recipe 1', 'Recipe 2'],
        'ingredients': ['tomato, pasta', 'chicken, rice'],
        'directions': ['step1 | step2', 'step1 | step2'],
        'link': ['http://test1.com', 'http://test2.com'],
        'source': ['source1', 'source2'],
        'NER': ['tomato, pasta', 'chicken, rice'],
        'site': ['site1', 'site2']
    }
    df = pd.DataFrame(test_data)
    
    def mock_load():
        return df
    
    # Remplacer la fonction load_dataset
    monkeypatch.setattr('routes.recipeRoute.load_dataset', mock_load)
    return df

def test_get_dataset(client, mock_dataset):
    # Test avec des ingrédients valides
    response = client.get('/dataset?ingredients=tomato')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data) > 0
    assert 'title' in data[0]

    # Test sans ingrédients
    response = client.get('/dataset')
    assert response.status_code == 400

def test_api_search(client, mock_dataset):
    # Test de recherche avec un mot-clé valide
    response = client.get('/api/search?keyword=tomato')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data) > 0

    # Test sans mot-clé
    response = client.get('/api/search')
    assert response.status_code == 400

def test_add_recipe(client, mock_dataset):
    new_recipe = {
        'title': 'Test Recipe',
        'ingredients': ['ingredient1', 'ingredient2'],
        'directions': ['step1', 'step2'],
        'link': 'http://test.com',
        'source': 'test_source',
        'NER': 'test NER',
        'site': 'test_site'
    }
    
    response = client.post('/api/recipes', 
                          json=new_recipe,
                          content_type='application/json')
    assert response.status_code == 200
    
    # Test avec données manquantes
    invalid_recipe = {'title': 'Test Recipe'}
    response = client.post('/api/recipes', 
                          json=invalid_recipe,
                          content_type='application/json')
    assert response.status_code == 400

def test_get_recipes(client, mock_dataset):
    # Test récupération de toutes les recettes
    response = client.get('/api/recipes')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data) > 0

    # Test recherche par titre
    response = client.get('/api/recipes?title=Recipe 1')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data) > 0
    assert data[0]['title'] == 'Recipe 1'

def test_get_latest_recipes(client, mock_dataset):
    response = client.get('/api/recipes/latest')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data) > 0