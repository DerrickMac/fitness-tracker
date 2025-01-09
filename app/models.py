from werkzeug.security import generate_password_hash, check_password_hash
from hashlib import md5
from datetime import datetime, timezone
from flask_login import UserMixin
from typing import Optional, List
from sqlalchemy import String, Integer, ForeignKey, Table, Column
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app import db, login

@login.user_loader
def load_user(id):
    return db.session.get(User, int(id))

workout_machine_exercise = Table('workout_machine_exercise', db.metadata, 
                                 Column('workout_id', Integer, ForeignKey('workout.id'), primary_key=True),
                                 Column('machine_exercise_id', Integer, ForeignKey('machine_exercise.id'), primary_key=True)
                                )

workout_cardio_exercise = Table('workout_cardio_exercise', db.metadata, 
                                 Column('workout_id', Integer, ForeignKey('workout.id'), primary_key=True),
                                 Column('cardio_exercise_id', Integer, ForeignKey('cardio_exercise.id'), primary_key=True)
                                )

class User(UserMixin, db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(64), index=True, unique=True)
    email: Mapped[str] = mapped_column(String(120), index=True, unique=True)
    password_hash: Mapped[Optional[str]] = mapped_column(String(256))
    workouts: Mapped[List['Workout']] = relationship(back_populates='user')
    about_me: Mapped[Optional[str]] = mapped_column(String(140))
    last_seen: Mapped[Optional[datetime]] = mapped_column(
        default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        print(f'https://www.gravatar.com/avatar/{digest}?d=identicon&s={size}')
        return f'https://www.gravatar.com/avatar/{digest}?d=identicon&s={size}'

class Workout(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    date: Mapped[datetime] = mapped_column(index=True, default=lambda: datetime.now(timezone.utc))
    user_id: Mapped[int] = mapped_column(ForeignKey(User.id), index=True)
    user: Mapped[User] = relationship(back_populates='workouts')

    machine_exercises: Mapped[List["MachineExercise"]] = relationship(secondary='workout_machine_exercise', back_populates="workouts")
    cardio_exercises: Mapped[List["CardioExercise"]] = relationship(secondary='workout_cardio_exercise', back_populates="workouts")

class MachineExercise(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(64), index=True, unique=True)
    reps: Mapped[int] = mapped_column(Integer, default=1)
    weight: Mapped[int] = mapped_column(Integer, default=0)
    workouts: Mapped[List['Workout']] = relationship(secondary='workout_machine_exercise', back_populates='machine_exercises')

    def __repr__(self):
        return '<Machine {}>'.format(self.name)
    
class CardioExercise(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(64), index=True, unique=True)
    distance: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    workouts: Mapped[List['Workout']] = relationship(secondary='workout_cardio_exercise', back_populates='cardio_exercises')

    def __repr__(self):
        return '<Cardio {}>'.format(self.name)
