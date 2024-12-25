from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import Recipe
from app.extensions import db
import requests
from .services_urls import user_service_urls

recipe_bp = Blueprint('recipes', __name__, url_prefix='/recipes')


@recipe_bp.route('/list/<int:user_id>', methods=['GET'])
@jwt_required()
def get_recipes():
    user_id = get_jwt_identity()

    current_user = requests.get(url=user_service_urls.get_profile_url)
    
    recipes = Recipe.query.all()
    return jsonify([{
        'id': recipe.id,
        'title': recipe.title,
        'description': recipe.description,
        'ingredients': recipe.ingredients,
        'instructions': recipe.instructions,
        'accessed_by': current_user
    } for recipe in recipes])


@recipe_bp.route('/<int:id>', methods=['GET'])
@jwt_required()
def get_recipe(id):
    recipe = Recipe.query.get_or_404(id)
    return jsonify({
        'id': recipe.id,
        'title': recipe.title,
        'description': recipe.description,
        'ingredients': recipe.ingredients,
        'instructions': recipe.instructions
    })


@recipe_bp.route('/create', methods=['POST'])
@jwt_required()
def create_recipe():
    current_user = kwargs.get("current_user", {})
    data = request.get_json()
    recipe = Recipe(
        title=data['title'],
        description=data['description'],
        ingredients=data['ingredients'],
        instructions=data['instructions']
    )
    db.session.add(recipe)
    db.session.commit()
    return jsonify({'message': f'Recipe created by user {current_user.get("first_name")}'}), 201


@recipe_bp.route('/update', methods=['POST'])
@jwt_required()
def update_recipe():
    data = request.get_json()
    recipe = Recipe.query.get_or_404(data.get("id"))
    recipe.title = data.get('title', recipe.title)
    recipe.description = data.get('description', recipe.description)
    recipe.ingredients = data.get('ingredients', recipe.ingredients)
    recipe.instructions = data.get('instructions', recipe.instructions)
    db.session.commit()
    return jsonify({'message': 'Recipe updated successfully!'})


@recipe_bp.route('/delete/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_recipe(id):
    recipe = Recipe.query.get_or_404(id)
    db.session.delete(recipe)
    db.session.commit()
    return jsonify({'message': 'Recipe deleted successfully!'})


# def fetch_user_details(token):
#     """Fetch user details from User Service using JWT token."""
#     user_service_url = "http://user-service-url/user/profile"
#     headers = {"Authorization": f"Bearer {token}"}

#     response = requests.get(user_service_url, headers=headers)
#     if response.status_code == 200:
#         return response.json()
#     return None