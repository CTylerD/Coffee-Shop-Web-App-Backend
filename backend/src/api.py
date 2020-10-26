import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS
from .database.models import db_drop_and_create_all, setup_db, Drink, db
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

#db_drop_and_create_all()

@app.route('/drinks', methods=['GET'])
def get_drinks():
    try:
        drinks_from_db = Drink.query.all()
        drinks = [drink.short() for drink in drinks_from_db]
        if len(drinks) == 0:
            
            abort(404)
        return json.dumps(
                         {"success": True,
                          "drinks": drinks
                          }), 200
    except Exception as e:
        print(e)
        abort(400)


@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def get_drinks_detail(jwt):
    try:
        drinks_from_db = Drink.query.all()
        drinks = [drink.long() for drink in drinks_from_db]
        if len(drinks) == 0:
            abort(404)
        return json.dumps(
                         {"success": True,
                          "drinks": drinks
                          }), 200
    except Exception as e:
        print(e)
        abort(400)


@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def add_drinks(jwt):
    try:
        data = json.loads(request.data.decode("utf-8"))
        title = data['title']
        recipe = json.dumps(data['recipe'])
        new_drink = Drink(title=title, recipe=recipe)
        new_drink.insert()
        return json.dumps({'success': True, "drinks": new_drink.long()}), 200
    except Exception as e:
        print(e)
        abort(400)


@app.route('/drinks/<id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def edit_drinks(jwt, id):
    drink = Drink.query.filter_by(id=id).first()
    data = json.loads(request.data)
    if drink is None:
        abort(404)
    if data.get("title"):
        drink.title = data["title"]
    if data.get("recipe"):
        drink.recipe = json.dumps(data['recipe'])
    try:
        drink.update()
        return json.dumps({'success': True, "drinks": [drink.long()]}), 200
    except Exception as e:
        print(e)
        abort(400)


@app.route('/drinks/<id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def remove_drinks(jwt, id):
    try:
        drink = Drink.query.filter_by(id=id).first()
        if drink is None:
            abort(404)
        drink.delete()
        return jsonify({
            "success": True,
            "delete": id
            }), 200
    except Exception as e:
        print(e)
        abort(400)


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
                    "success": False,
                    "error": 422,
                    "message": "unprocessable"
                    }), 422


@app.errorhandler(404)
def resource_not_found(error):
    return jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404


@app.errorhandler(400)
def resource_not_found(error):
    return jsonify({
                    "success": False,
                    "error": 400,
                    "message": "bad request"
                    }), 400


@app.errorhandler(AuthError)
def auth_error_handler(error):
    return jsonify({
                    "success": False,
                    "error": 401,
                    "message": "not authorized"
    }), 401
