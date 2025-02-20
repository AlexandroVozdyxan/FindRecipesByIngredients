import json

import requests
from flask import Flask, render_template, request, make_response, jsonify
import sqlite3
import random

app = Flask(__name__)
app.secret_key = 'F(HUU487gg8f*G8h*Hf48e78f8h4h87h87d8hdfh88h8s8fr8h48hgfy8uh'
API_KEY = ''
RECIPES_PER_PAGE = 5
def get_recipes(ingredients):
    url = f'https://api.spoonacular.com/recipes/findByIngredients?ingredients={ingredients}&number=100&apiKey={API_KEY}'
    response = requests.get(url)
    data = response.json()

    filtered_recipes = []
    for item in data:
        if 'usedIngredients' in item and isinstance(item['usedIngredients'], list):
            recipe_ingredients = set(ingredient['name'] for ingredient in item['usedIngredients'])
            user_ingredients_set = set(ingredients.lower().split(','))
            if user_ingredients_set and recipe_ingredients:
                recipe_id = item['id']
                nutrition = get_nutrition_info(recipe_id)
                filtered_recipes.append({
                    'title': item['title'],
                    'image': item.get('image', ""),
                    'id': item['id'],
                    'nutrition': nutrition
                })

    return filtered_recipes
def get_nutrition_info(recipe_id):
    url = f'https://api.spoonacular.com/recipes/{recipe_id}/nutritionWidget.json?apiKey={API_KEY}'
    response = requests.get(url)
    data = response.json()
    return data

@app.route('/', methods=['GET', 'POST'])
def index():
    recipes = []
    total_pages = 1
    if request.method == 'POST':
        user_ingredients = request.form['ingredients']
        recipes = get_recipes(user_ingredients)
        total_pages = (len(recipes) + RECIPES_PER_PAGE - 1) // RECIPES_PER_PAGE
        return render_template('results.html', recipes=recipes[:RECIPES_PER_PAGE], page=1, ingredients=user_ingredients, total_pages=total_pages)
    return render_template('index.html', recipes=recipes)

@app.route("/results/<int:page>")
def results(page):
    user_ingredients = request.args.get("ingredients", "")
    recipes = get_recipes(user_ingredients)
    # COUNT OF PAGES
    start = (page - 1) * RECIPES_PER_PAGE
    end = start + RECIPES_PER_PAGE
    paginated_recipes = recipes[start:end]
    # ALL PAGES
    total_pages = (len(recipes) // RECIPES_PER_PAGE) + (1 if len(recipes) % RECIPES_PER_PAGE > 0 else 0)

    return render_template(
        "results.html",
        recipes=paginated_recipes,
        ingredients=user_ingredients,
        page=page,
        total_pages=total_pages,
    )

@app.route('/favorites', methods=['GET'])
def favorites():
    favorites = request.cookies.get('favorites')
    if favorites:
        favorites = json.loads(favorites)
    else:
        favorites = []
    return render_template('favorites.html', favorites=favorites)

@app.route('/add_favorite', methods=['POST'])
def add_favorite():
    recipe = request.json
    favorites = request.cookies.get('favorites')
    if favorites:
        favorites = json.loads(favorites)
    else:
        favorites = []

    if recipe not in favorites:
        favorites.append(recipe)

    response = make_response(jsonify({"message":"Recipe added successfully"}))
    response.set_cookie('favorites', json.dumps(favorites))
    return response

@app.route('/remove_favorite', methods=['POST'])
def remove_favorite():
    recipe = request.json
    favorites = request.cookies.get('favorites')
    if favorites:
        favorites = json.loads(favorites)
        favorites = [fav for fav in favorites if fav['id'] != recipe['id']]
    else:
        favorites = []

    response = make_response(jsonify({"message":"Recipe removed successfully"}))
    response.set_cookie('favorites', json.dumps(favorites))
    return response
if __name__ == '__main__':
    app.run()
