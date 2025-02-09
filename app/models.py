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

workout_machine_exercise = Table('workout_exercise', db.metadata, 
                                 Column('workout_id', Integer, ForeignKey('workout.id'), primary_key=True),
                                 Column('exercise_id', Integer, ForeignKey('exercise.id'), primary_key=True)
                                )

class User(UserMixin, db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(64), index=True, unique=True)
    email: Mapped[str] = mapped_column(String(120), index=True, unique=True)
    password_hash: Mapped[Optional[str]] = mapped_column(String(256))
    workouts: Mapped[List['Workout']] = relationship(back_populates='user', lazy='dynamic')
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
        return f'https://www.gravatar.com/avatar/{digest}?d=identicon&s={size}'
    
    def get_user_workouts(self):
        return self.workouts

class Workout(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(64), index=True)
    exercise_type: Mapped[str] = mapped_column(String(64))
    muscle_group: Mapped[str] = mapped_column(String(64))
    user_id: Mapped[int] = mapped_column(ForeignKey(User.id), index=True)
    user: Mapped[User] = relationship(back_populates='workouts')
    exercises: Mapped[List["Exercise"]] = relationship(secondary='workout_exercise', back_populates="workouts")

class Exercise(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    date: Mapped[datetime] = mapped_column(index=True, default=lambda: datetime.now(timezone.utc))
    reps: Mapped[int] = mapped_column(Integer, nullable=True, default=None)
    count: Mapped[int] = mapped_column(Integer, nullable=True, default=None)
    weight: Mapped[int] = mapped_column(Integer, nullable=True, default=None)
    distance: Mapped[int] = mapped_column(Integer, nullable=True, default=None)
    workouts: Mapped[List['Workout']] = relationship(secondary='workout_exercise', back_populates='exercises')

    def __repr__(self):
        return '<Exercise weight {}>'.format(self.weight)