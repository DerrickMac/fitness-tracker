import os
os.environ['DATABASE_URL'] = 'sqlite://'

import unittest
from app import app, db
from app.models import User, Workout, Exercise
from datetime import datetime

class UserModelCase(unittest.TestCase):
    def setUp(self):
        self.app_context = app.app_context()
        self.app_context.push()
        db.create_all()
    
    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def test_password_hashing(self):
        u = User(username='Derrick', email='derrick@example.com')
        u.set_password('cat')
        self.assertFalse(u.check_password('dog'))
        self.assertTrue(u.check_password('cat'))
    
    def test_avatar(self):
        u = User(username='john', email='john@example.com')
        self.assertEqual(u.avatar(128), ('https://www.gravatar.com/avatar/'
                                         'd4c74594d841139328695756648b6bd6'
                                         '?d=identicon&s=128'))

class WorkoutModelCast(unittest.TestCase):
    def setUp(self):
        self.app_context = app.app_context()
        self.app_context.push()
        db.create_all()
    
    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def test_create_workout(self):
        u = User(username='Derrick', email='derrick@example.com')
        w1 = Workout(user=u, name="Bench Press", exercise_type="machine", muscle_group="chest")
        w2 = Workout(user=u, name="Walk", exercise_type="cardio", muscle_group="heart")
        db.session.add(w)
        db.session.commit()

        bench = Exercise(date=datetime.now(), count=1, weight=10)
        walk = Exercise(date=datetime.now(), distance=1)
        w1.exercises.append(bench)
        w2.exercises.append(walk)
        db.session.commit()

        self.assertEqual(len(w1.exercises), 1)
        self.assertEqual(w1.name, "Bench Press")
        self.assertEqual(w1.exercise_type, "machine")
        self.assertEqual(w1.exercises[0].date, datetime.now())
        self.assertEqual(w1.exercises[0].count, 1)
        self.assertEqual(w1.exercises[0].weight, 10)

        self.assertEqual(w2.name, "Walk")
        self.assertEqual(w2.exercise_type, "cardio")
        self.assertEqual(w2.exercises[0].date, datetime.now())
        self.assertEqual(w2.exercises[0].distance, 1)
        

if __name__ == '__main__':
    unittest.main(verbosity=2)
