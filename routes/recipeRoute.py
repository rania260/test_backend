from flask import Flask, jsonify,request
import pandas as pd
from flask_jwt_extended import JWTManager, jwt_required

def recipe_routes(app):
  
    @jwt_required()
    # Load the dataset from CSV
    def load_dataset():
        try:
            data = pd.read_csv("./recipes_data.csv")
            return data
        except Exception as e:
            return str(e)  # Return the error as a string

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
