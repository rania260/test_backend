from flask import Flask, jsonify, request
import pandas as pd
from flask_jwt_extended import JWTManager, jwt_required

# Déplacer load_dataset en dehors de recipe_routes
def load_dataset():
    try:
        data = pd.read_csv("./recipes_data.csv")
        return data
    except Exception as e:
        return str(e)

def recipe_routes(app):
    @app.route('/dataset', methods=['GET'])
    def get_dataset():
        """
        Récupérer le dataset de recettes
        ---
        parameters:
          - name: ingredients
            in: query
            type: string
            required: true
            description: Comma-separated list of ingredients to search for in the recipes
        security:
          - Bearer: []  # Specify that this endpoint requires a Bearer token
 
        responses:
          200:
            description: A list of recipes
            schema:
              type: array
              items:
                type: object
                properties:
                  title:
                    type: string
                    example: "Recipe Title"
                  ingredients:
                    type: array
                    items:
                      type: string
                    example: ["ingredient1", "ingredient2"]
                  directions:
                    type: array
                    items:
                      type: string
                    example: ["step1", "step2"]
                  link:
                    type: string
                    example: "http://example.com/recipe"
                  source:
                    type: string
                    example: "Source Name"
                  NER:
                    type: string
                    example: "NER Information"
        """
        # Load the dataset
        dataset = load_dataset()

        if isinstance(dataset, str):  # Check if an error occurred
            return jsonify({"error": dataset}), 500

       # Get the ingredients from the query parameter
        ingredients = request.args.get('ingredients')

        if not ingredients:  # Check if the ingredients are provided
            return jsonify({"error": "Please provide at least one ingredient."}), 400

        # Split the ingredients into a list
        ingredient_list = [ingredient.strip() for ingredient in ingredients.split(',') if ingredient.strip()]

        if not ingredient_list:  # If no valid ingredients after stripping
            return jsonify({"error": "Please provide at least one valid ingredient."}), 400

        # Create a mask for filtering recipes containing any of the specified ingredients
        mask = dataset['ingredients'].apply(lambda x: any(ingredient.lower() in x.lower() for ingredient in ingredient_list))

        # Filter recipes that contain any of the specified ingredients
        filtered_recipes = dataset[mask]

        # Convert the relevant fields to a dictionary, limiting to 5 results
        recipes = filtered_recipes[['title', 'ingredients', 'link']].head(5).to_dict(orient='records')
        
        # Return the data in JSON format
        return jsonify(recipes)
      
         

      # Fonction de recherche avec pagination
    def search_recipes_by_ingredient(keywords, df, start=0, count=10):
        # Filter the results by keywords in the NER column
        filtered_results = df[df['NER'].str.contains('|'.join(keywords), case=False, na=False)]
        # Return the specified range of rows with all columns
        return filtered_results.iloc[start:start + count]
    # Endpoint pour rechercher des recettes par mot-clé avec pagination
    @app.route('/api/search', methods=['GET'])
    def api_search():
        df = load_dataset()

        if df is None:
            return jsonify({"error": "Dataset non disponible."}), 500

        # Récupérer les mots-clés depuis les paramètres de requête
        keyword = request.args.get('keyword')
        
        # Vérifier si keyword est None ou vide
        if not keyword:
            return jsonify({"error": "Veuillez fournir au moins un mot-clé via le paramètre 'keyword'."}), 400
            
        keywords = [k.strip() for k in keyword.split(',')]  # Split by comma
        
        # Vérifier si la liste des mots-clés est vide après le nettoyage
        if not any(keywords):
            return jsonify({"error": "Veuillez fournir au moins un mot-clé valide."}), 400

        # Paramètres de pagination
        start = int(request.args.get('start', 0))
        count = int(request.args.get('count', 10))

        results = search_recipes_by_ingredient(keywords, df, start=start, count=count)
        return jsonify(results.to_dict(orient='records'))


      
    #@jwt_required()
    @app.route('/api/recipes', methods=['POST'])
    def add_recipe():
        """
        Ajouter une nouvelle recette au dataset
        ---
        requestBody:
          required: true
          content:
            application/json:
              schema:
                type: object
                properties:
                  title:
                    type: string
                    example: "Nouvelle recette"
                  ingredients:
                    type: array
                    items:
                      type: string
                    example: ["ingrédient1", "ingrédient2"]
                  directions:
                    type: array
                    items:
                      type: string
                    example: ["étape1", "étape2"]
                  link:
                    type: string
                    example: "http://example.com/recette"
                  source:
                    type: string
                    example: "Nom de la source"
                  NER:
                    type: string
                    example: "Information NER"
                  site:
                    type: string
                    example: "Nom du site"
        responses:
          200:
            description: Recette ajoutée avec succès
            schema:
              type: object
              properties:
                message:
                  type: string
                  example: "Recette ajoutée avec succès"
          400:
            description: Erreur dans la requête
          500:
            description: Erreur du serveur
        """
        try:
            # Parse JSON input
            new_recipe = request.get_json()

            # Validate input
            required_fields = ['title', 'ingredients', 'directions', 'link', 'source', 'NER', 'site']
            for field in required_fields:
                if field not in new_recipe or not new_recipe[field]:
                    return jsonify({"error": f"'{field}' est requis."}), 400

            # Load the current dataset
            dataset = load_dataset()

            if isinstance(dataset, str):  # If an error occurred while loading the dataset
                return jsonify({"error": dataset}), 500

            # Prepare the new recipe data
            new_data = pd.DataFrame([{
                'title': new_recipe['title'],
                'ingredients': ', '.join(new_recipe['ingredients']),
                'directions': ' | '.join(new_recipe['directions']),
                'link': new_recipe['link'],
                'source': new_recipe['source'],
                'NER': new_recipe['NER'],
                'site': new_recipe['site']
            }])

            # Append the new data using pd.concat
            dataset = pd.concat([dataset, new_data], ignore_index=True)

            # Save the updated dataset back to the CSV
            dataset.to_csv("./recipes_data.csv", index=False)

            return jsonify({"message": "Recette ajoutée avec succès"}), 200

        except Exception as e:
            return jsonify({"error": f"Une erreur s'est produite : {str(e)}"}), 500

    @app.route('/api/recipes', methods=['GET'])
    def get_recipes():
        """
        Obtenir toutes les recettes ou une recette spécifique par titre.
        ---
        parameters:
          - name: title
            in: query
            type: string
            required: false
            description: Titre de la recette à rechercher
        responses:
          200:
            description: Liste des recettes
            schema:
              type: array
              items:
                type: object
                properties:
                  title:
                    type: string
                  ingredients:
                    type: string
                  directions:
                    type: string
                  link:
                    type: string
                  source:
                    type: string
                  NER:
                    type: string
                  site:
                    type: string
          500:
            description: Erreur du serveur
        """
        try:
            # Charger le dataset
            dataset = load_dataset()
            if isinstance(dataset, str):  # Si une erreur s'est produite
                return jsonify({"error": dataset}), 500

            # Optionnel : Filtrer par titre
            title = request.args.get('title')
            if title:
                dataset = dataset[dataset['title'].str.contains(title, case=False, na=False)]

            # Convertir en dictionnaire pour JSON
            recipes = dataset.to_dict(orient='records')
            return jsonify(recipes), 200

        except Exception as e:
            return jsonify({"error": f"Une erreur s'est produite : {str(e)}"}), 500

    @app.route('/api/recipes/latest', methods=['GET'])
    def get_latest_recipes():
      try:
          # Charger les données du CSV
          df = load_dataset()

          # Trier et récupérer les 3 derniers
          latest_recipes = df.tail(5).to_dict(orient='records')

          return jsonify(latest_recipes), 200
      except Exception as e:
          return jsonify({"error": str(e)}), 500
