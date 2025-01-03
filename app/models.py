from datetime import datetime, timezone
from typing import Optional
import sqlalchemy as sa
import sqlalchemy.orm as so
from app import db

class User(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    username: so.Mapped[str] = so.mapped_column(sa.String(64), index=True, unique=True)
    email: so.Mapped[str] = so.mapped_column(sa.String(120), index=True, unique=True)
    password_hash: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256))
    workouts: so.WriteOnlyMapped['Workout'] = so.relationship(back_populates='owner')

    def __repr__(self):
        return '<User {}>'.format(self.username)

class Workout(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    name: so.Mapped[str] = so.mapped_column(sa.String(64), index=True, unique=True)
    reps: so.Mapped[int] = so.mapped_column(sa.Integer, nullable=False, default=1)
    weight: so.Mapped[int] = so.mapped_column(sa.Integer, nullable=False, default=0)
    date: so.Mapped[datetime] = so.mapped_column(index=True, default=lambda: datetime.now(timezone.utc))
    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(User.id), index=True)

    owner: so.Mapped[User] = so.relationship(back_populates='workouts')

    def __repr__(self):
        return '<Workout {}>'.format(self.name)