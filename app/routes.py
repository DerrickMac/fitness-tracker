from flask_login import current_user, login_user, logout_user, login_required
from flask import render_template, flash, redirect, url_for, request
from app import app
from app.forms import LoginForm, RegistrationForm, EditProfileForm, WorkoutForm
from urllib.parse import urlsplit
import sqlalchemy as sa
from app import db
from app.models import User, Workout, MachineExercise, CardioExercise
from datetime import datetime, timezone

@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.now(timezone.utc)
        db.session.commit()

@app.route('/')
@app.route('/index')
@login_required
def index():
    query_workouts = db.session.scalars(sa.select(Workout).where(Workout.user == current_user)).all()
    user_workouts = []
    cardio_workouts = []
    for workout in query_workouts:
        for machine in workout.machine_exercises:
            user_workouts.append({"name": machine.name, "reps": machine.reps, "weight": machine.weight, "date": workout.date})
        for cardio in workout.cardio_exercises:
            cardio_workouts.append({"name": cardio.name, "distance": cardio.distance, "date": workout.date})

    return render_template('index.html', title='Home', workouts=user_workouts, cardios=cardio_workouts)

@app.route('/login', methods=['GET', 'POST'])
def login():
    
    # Already authenticated users go to dashboard
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    # Validate user credentials
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.scalar(sa.select(User).where(User.username == form.username.data))
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or urlsplit(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(url_for('index'))
    
    # First time visitors go to login page
    return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route('/user/<username>')
@login_required
def user(username):
    user = db.first_or_404(sa.select(User).where(User.username == username))
    query_workouts = db.session.scalars(sa.select(Workout).where(Workout.user == current_user)).all()
    user_workouts = []
    cardio_workouts = []
    for workout in query_workouts:
        for machine in workout.machine_exercises:
            user_workouts.append({"name": machine.name, "reps": machine.reps, "weight": machine.weight, "date": workout.date})
        for cardio in workout.cardio_exercises:
            cardio_workouts.append({"name": cardio.name, "distance": cardio.distance, "date": workout.date})

    return render_template('user.html', user=user, workouts=user_workouts, cardios=cardio_workouts)

@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='Edit Profile', form=form)

@app.route('/workout', methods=['GET', 'POST'])
@login_required
def create_workout():
    form = WorkoutForm()
    if form.validate_on_submit():
        # 1. Create a new workout row
        new_workout = Workout(
            date=form.date.data,        # form.date is a DateField
            user_id=current_user.id     # Link to current user
        )
        db.session.add(new_workout)
        db.session.flush()  
        # flush to get new_workout.id, though you can do it after as well

        # 2. Depending on exercise_type, create a new exercise object
        if form.exercise_type.data == "machine":
            machine_ex = MachineExercise(
                name=form.name.data,
                weight=form.weight.data or 0,
                reps=form.reps.data or 0
            )
            db.session.add(machine_ex)
            db.session.flush()  

            # Link it
            new_workout.machine_exercises.append(machine_ex)

        elif form.exercise_type.data == "cardio":
            cardio_ex = CardioExercise(
                name=form.name.data,
                distance=form.distance.data or 0
            )
            db.session.add(cardio_ex)
            db.session.flush()

            # Link it
            new_workout.cardio_exercises.append(cardio_ex)

        # 3. Commit all changes (workout + exercise + relationship)
        db.session.commit()

        flash("New workout created successfully!")
        return redirect(url_for('index'))
        
    return render_template('create_workout.html', title='Create Workout', form=form)