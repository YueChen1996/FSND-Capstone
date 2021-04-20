import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from app import create_app
from models import setup_db, Actor, Movie

ASSISTANT_TOKEN = str('Bearer ' + os.environ['ASSISTANT_TOKEN'])
DIRECTOR_TOKEN = str('Bearer ' + os.environ['DIRECTOR_TOKEN'])
PRODUCER_TOKEN = str('Bearer ' + os.environ['PRODUCER_TOKEN'])


class CastingAgencyTestCase(unittest.TestCase):

    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = 'agency'
        self.database_path = "postgres://{}/{}".format('postgres:123@localhost:5432', self.database_name)

        self.assistant = {'Content-Type': 'application/json',
                          'Authorization': ASSISTANT_TOKEN}
        self.director = {'Content-Type': 'application/json',
                         'Authorization': DIRECTOR_TOKEN}
        self.producer = {'Content-Type': 'application/json',
                         'Authorization': PRODUCER_TOKEN}
        setup_db(self.app, self.database_path)

        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            self.db.create_all()

    def tearDown(self):
        """Executed after reach test"""
        pass

    def test_welcome_pate(self):
        response = self.client().get('/')
        self.assertEqual(response.status_code, 200)

    def test_get_movies_200(self):
        movie = Movie(title='Hello', release_date='2012-01-15')
        movie.insert()
        response = self.client().get('/movies', headers=self.assistant)
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
    
    def test_get_actors_200(self):
        actor = Actor(name='Tom', age=15, gender='Male')
        actor.insert()
        response = self.client().get('/actors', headers=self.assistant)
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_post_movie_200(self):
        response = self.client().post('/movies', headers=self.producer, json={'title': 'Bye Bye', 'release_date': '2001-1-1'})
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
    
    def test_post_actor_200(self):
        response = self.client().post('/actors', headers=self.producer, json={'name': 'Anna', 'age': 43, 'gender': 'Female'})
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
    
    def test_delete_movie_200(self):
        movie = Movie(title='Bye Bye', release_date='2001-1-1')
        movie.insert()
        movie_id = movie.id
        response = self.client().delete('/movies/'+str(movie_id)+'', headers=self.producer)
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_delete_actor_200(self):
        actor = Actor(name='Anna', age=43, gender='Female')
        actor.insert()
        actor_id = actor.id
        response = self.client().delete('/actors/'+str(actor_id)+'', headers=self.producer)
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_patch_movie_200(self):
        movie = Movie(title='Hello', release_date='2012-01-15')
        movie.insert()
        movie_id = movie.id
        response = self.client().patch('/movies/'+str(movie_id) + '', headers=self.director, json={'title': 'HelloHello', 'release_date': '2012-01-15'})
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_patch_actor_200(self):
        actor = Actor(name='Tom', age=21, gender='Male')
        actor.insert()
        actor_id = actor.id
        response = self.client().patch('/actors/'+str(actor_id)+'', headers=self.director, json={'name': 'Andy', 'age': 43, 'gender': 'Male'})
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)

    def test_get_movies_401(self):
        response = self.client().get('/movies')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 401)

    def test_get_movies_404(self):
        Movie.query.delete()
        response = self.client().get('/movies', headers=self.assistant)
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['success'], False)

    def test_get_actors_401(self):
        response = self.client().get('/actors')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 401)

    def test_get_actors_404(self):
        Actor.query.delete()
        response = self.client().get('/actors', headers=self.assistant)
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['success'], False)


    def test_delete_movie_401(self):
        response = self.client().delete('/movies/1', headers=self.assistant)
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 401)

    def test_delete_movie_404(self):
        response = self.client().delete('/movies/100000', headers=self.producer)
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['success'], False)



    def test_delete_actor_401(self):
        response = self.client().delete('/actors/1', headers=self.assistant)
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 401)

    def test_delete_actor_404(self):
        response = self.client().delete('/actors/100000', headers=self.producer)
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['success'], False)

    def test_post_movie_401(self):
        response = self.client().post('/movies', headers=self.assistant, json={'title': 'ABC', 'release_date': '1996-1-15'})
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 401)

    def test_post_movie_422(self):
        response = self.client().post('/movies', headers=self.producer, json={'title': 'ABC'})
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 422)
        self.assertEqual(data['success'], False)


    def test_post_actor_401(self):
        response = self.client().post('/actors', headers=self.assistant, json={'name': 'Julia', 'age': 54, 'gender': 'Female'})
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 401)

    def test_post_actor_422(self):
        response = self.client().post('/actors', headers=self.producer, json={'height': 165, 'gender': 'Female'})
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 422)
        self.assertEqual(data['success'], False)


    def test_patch_movie_401(self):
        response = self.client().patch('/movies/1', headers=self.assistant, json={'title': 'HelloHello', 'release_date': '2012-1-15'})
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 401)

    def test_patch_movie_422(self):
        movie = Movie(title='LLKK', release_date='2012-1-15')
        movie.insert()
        movie_id = movie.id
        response = self.client().patch('/movies/'+str(movie_id)+'', headers=self.director)

        data = json.loads(response.data)
        self.assertEqual(response.status_code, 422)
        self.assertEqual(data['success'], False)

    

    def test_patch_actor_401(self):
        response = self.client().patch('/actors/1', headers=self.assistant, json={'name': 'Yaya', 'age': 87, 'gender': 'Female'})
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 401)

    def test_patch_actor_422(self):
        actor = Actor(name='Andt', age=43, gender='Male')
        actor.insert()
        actor_id = actor.id
        response = self.client().patch('/actors/'+str(actor_id)+'', headers=self.director)
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 422)
        self.assertEqual(data['success'], False)


    # Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
