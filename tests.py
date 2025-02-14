#!/usr/bin/env python
from datetime import datetime
import unittest
from app import create_app, db
from app.models import User, Workout, Exercise
from config import Config


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'

class UserModelCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
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

class WorkoutModelCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
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
        date = datetime.today()
        db.session.add(w1)
        db.session.commit()

        bench = Exercise(date=date, count=1, weight=10)
        bench_2 = Exercise(date=date, count=2, weight=20)
        walk = Exercise(date=date, distance=1)
        w1.exercises.append(bench)
        w1.exercises.append(bench_2)
        w2.exercises.append(walk)
        db.session.commit()

        self.assertEqual(len(w1.exercises), 2)
        self.assertEqual(w1.name, "Bench Press")
        self.assertEqual(w1.exercise_type, "machine")
        self.assertEqual(w1.exercises[0].date, date)
        self.assertEqual(w1.exercises[0].count, 1)
        self.assertEqual(w1.exercises[0].weight, 10)
        self.assertEqual(w1.exercises[1].date, date)
        self.assertEqual(w1.exercises[1].count, 2)
        self.assertEqual(w1.exercises[1].weight, 20)

        self.assertEqual(w2.name, "Walk")
        self.assertEqual(w2.exercise_type, "cardio")
        self.assertEqual(w2.exercises[0].date, date)
        self.assertEqual(w2.exercises[0].distance, 1)
        
def test_edit_workout(self):
    user = User(username="Alice", email="alice@example.com")
    workout = Workout(user=user, name="Initial Workout", exercise_type="machine", muscle_group="back")
    db.session.add(workout)
    db.session.commit() 

    workout.name = "Updated Workout"
    workout.exercise_type = "freeweight"
    db.session.commit() 

    updated_workout = Workout.query.get(workout.id)
    self.assertEqual(updated_workout.name, "Updated Workout")
    self.assertEqual(updated_workout.exercise_type, "freeweight")

def test_delete_workout(self):
    user = User(username="Bob", email="bob@example.com")
    workout = Workout(user=user, name="Workout To Delete", exercise_type="cardio", muscle_group="legs")
    db.session.add(workout)
    db.session.commit()

    db.session.delete(workout)
    db.session.commit()

    deleted_workout = Workout.query.get(workout.id)
    self.assertIsNone(deleted_workout)

if __name__ == '__main__':
    unittest.main(verbosity=2)
