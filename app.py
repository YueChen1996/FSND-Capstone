import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from models import setup_db, Movie, Actor
from auth import AuthError, requires_auth, get_token_auth_header

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  CORS(app)
  
  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization, true')
    response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PATCH, DELETE,OPTIONS')
    return response

  @app.route('/', methods=['GET'])
  def welcome_page():
    return jsonify({
      'success': True,
      'description':'Welcome to Casting Agency!'
    })

  @app.route('/movies', methods=['GET'])
  @requires_auth('get:movies')
  def get_movies():
    try:
        movies = Movie.query.all()

        return jsonify({
            'success': True,
            'movies': [movie.format() for movie in movies]
    })
    except:
        abort(404)
    

  
  @app.route('/actors', methods=['GET'])
  @requires_auth('get:actors')
  def get_actors():
    try:
        actors = Actor.query.all()

        return jsonify({
            'success': True,
            'actors': [actor.format() for actor in movies]
    })
    except:
        abort(404)


  @app.route('/movies', methods=['POST'])
  @requires_auth('post:movies')
  def post_movies():
    body = request.get_json()

    if not ('title' in body and 'release_date' in body):
        abort(422)

    new_title = body.get('title')
    new_release_date = body.get('release_date')

    try:
        movie = Movie(title=new_title, release_date=new_release_date)
        movie.insert()
        
        return jsonify({
            'success': True,
            'movie': movie.format
        })
    except:
        abort(422)


  @app.route('/actors', methods=['POST'])
  @requires_auth('post:actors')
  def post_actors():
    body = request.get_json()

    if not ('name' in body and 'age' in body and 'gender' in body):
        abort(422)

    new_name = body.get('name')
    new_age = body.get('age')
    new_gender = body.get('gender')

    try:
        actor = Actor(name=new_name, age=new_age, gender=new_gender)
        actor.insert()
        
        return jsonify({
            'success': True,
            'actor': actor.format
        })
    except:
        abort(422)


  @app.route('/movies/<int:movie_id>', methods=['DELETE'])
  @requires_auth('delete:movies')
  def delete_movies(movie_id):
    movie = Movie.query.get(movie_id)

    if movie:
        try:
            movie.delete()

            return jsonify({
                "success": True,
                "movie": movie_id
            })
        except:
            abort(422)
    else:
        abort(404)



  @app.route('/actors/<int:actor_id>', methods=['DELETE'])
  @requires_auth('delete:actors')
  def delete_actors(actor_id):
    actor = Actor.query.get(actor_id)

    if actor:
        try:
            actor.delete()

            return jsonify({
                "success": True,
                "actor": actor_id
            })
        except:
            abort(422)
    else:
        abort(404)

  @app.route('/movies/<int:movie_id>', methods=['PATCH'])
  @requires_auth('patch:movies')
  def patch_movie_id(movie_id):
    movie = Movie.query.get(movie_id)

    if movie:
        try:
            body = request.get_json()

            title = body.get('title')
            release_date = body.get('release_date')

            if title:
                movie.title = title
            if release_date:
                movie.release_date = release_date

            movie.update()

            return jsonify({
                "success": True,
                "movie": movie.format()
            })
        except:
            abort(422)
    else:
        abort(404)

  @app.route('/actors/<int:actor_id>', methods=['PATCH'])
  @requires_auth('patch:actors')
  def patch_actor_id(actor_id):
    actor = Actor.query.get(actor_id)

    if actor:
        try:
            body = request.get_json()

            name = body.get('name')
            age = body.get('age')
            gender = body.get('gender')

            if name:
                actor.name = name
            if age:
                actor.age = age
            if gender:
                actor.gender = gender

            actor.update()

            return jsonify({
                "success": True,
                "actor": actor.format()
            })
        except:
            abort(422)
    else:
        abort(404)


# Error handling

  @app.errorhandler(422)
  def unprocessable(error):
    return jsonify({
                    "success": False, 
                    "error": 422,
                    "message": "unprocessable"
                    }), 422

  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
                    "success": False, 
                    "error": 404,
                    "message": "resource not found"
                    }), 404

  @app.errorhandler(AuthError)
  def handle_auth_error(ex):
    return jsonify({
                    "success": False, 
                    "error": ex.status_code,
                    "message": ex.error
                    }), 401


  return app

APP = create_app()

if __name__ == '__main__':
    APP.run(host='0.0.0.0', port=8080, debug=True)