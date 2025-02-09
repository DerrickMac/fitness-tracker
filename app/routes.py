from flask_login import current_user, login_user, logout_user, login_required
from flask import render_template, flash, redirect, url_for, request, jsonify
from app import app
from app.forms import LoginForm, RegistrationForm, EditProfileForm, WorkoutForm, ExerciseForm
from urllib.parse import urlsplit
import sqlalchemy as sa
from app import db
from app.models import User, Workout, Exercise
from datetime import datetime, timezone


@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.now(timezone.utc)
        db.session.commit()

@app.route('/api/deleterows', methods=['GET'])
def delete_all_rows():
    db.session.query(Workout).delete()
    db.session.query(Exercise).delete()
    db.session.commit()
    return "deleted", 200

@app.route('/api/workouts', methods=['GET'])
@login_required
def get_workout_data():
    unique_dates = (
        db.session.query(sa.func.date(Exercise.date))
        .join(Exercise.workouts)  # join through the relationship
        .filter(Workout.user_id == current_user.id)
        .distinct()
        .all()
    )
    # unique_dates is a list of one-element tuples containing date objects, e.g., [(date1,), (date2,), ...]
    # Convert each date to an ISO formatted string and pair it with the value 1.
    date_value_pairs = [[d, 1] for (d,) in unique_dates if d is not None]
    
    return jsonify(date_value_pairs)

@app.route('/')
@app.route('/index')
@login_required
def index():
    return render_template('index.html', title='Home')

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
        login_user(user)
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('index'))
    return render_template('register.html', title='Register', form=form)

@app.route('/user/<username>')
@login_required
def user(username):
    if not current_user.is_authenticated:
        return redirect(url_for('index'))
    return render_template('user.html', user=current_user)

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

@app.route('/workouts', methods=['GET'])
@login_required
def workouts():
    if not current_user.is_authenticated:
        return redirect(url_for('index'))
    
    # Get sorting criteria from the request (default to 'muscle_group')
    order_by = request.args.get('order_by', 'default')

    # Define sorting logic
    if order_by == 'exercise_type':
        workouts = current_user.workouts.order_by(Workout.exercise_type.asc(), Workout.name.asc())
    elif order_by == 'name':
        workouts = current_user.workouts.order_by(Workout.name.asc())
    else:  # Default: Order by muscle_group
        workouts = current_user.workouts.order_by(Workout.muscle_group.asc(), Workout.name.asc())

    return render_template('workouts.html', title='Workouts', workouts=workouts, order_by=order_by)

@app.route('/create-workout', methods=['GET', 'POST'])
@login_required
def create_workout():
    form = WorkoutForm()
    if form.validate_on_submit():
        new_workout = Workout(
            name=form.name.data, 
            exercise_type=form.exercise_type.data,       
            muscle_group=form.muscle_group.data,
            user_id=current_user.id  
        )
        db.session.add(new_workout)
        db.session.commit()

        flash("Workout created successfully!")
        return redirect(url_for('workouts'))
    return render_template('workout_form.html', title='Create Workout', form=form, action="Create")

@app.route('/workouts/<int:workout_id>', methods=['GET', 'POST'])
@login_required
def edit_workout(workout_id):
    user_workout = Workout.query.get_or_404(workout_id)
    form = WorkoutForm()
    if form.validate_on_submit():
        user_workout.name=form.name.data, 
        user_workout.exercise_type=form.exercise_type.data,       
        user_workout.muscle_group=form.muscle_group.data,
        db.session.commit()
        flash("Workout edited successfully!")
        return redirect(url_for('workouts'))
    elif request.method == "GET":
        form.name.data = user_workout.name
        form.exercise_type.data = user_workout.exercise_type
        form.muscle_group.data = user_workout.muscle_group

    return render_template('workout_form.html', title='Create Workout', form=form, action="Edit")

@app.route('/workouts/<int:workout_id>/delete', methods=['GET', 'POST'])
@login_required
def delete_workout(workout_id):
    user_workout = Workout.query.get_or_404(workout_id)
    
    # verify correct user is deleting workout
    if user_workout.user.id != current_user.id:
        flash("You do not have permission to delete this workout", "ERROR")
        return redirect(url_for('index'))
    
    db.session.delete(user_workout)
    db.session.commit()
    return redirect(url_for('workouts'))

@app.route('/log-exercise/<int:workout_id>', methods=['GET', 'POST'])
@login_required
def log_exercise(workout_id):
    user_workout = Workout.query.get_or_404(workout_id)

    # verify correct user is editing exercise
    if user_workout.user.id != current_user.id:
        flash("You do not have permission to create this exercise", "ERROR")
        return redirect(url_for('index'))
    
    form = ExerciseForm()
    if form.validate_on_submit():
        exercise = Exercise(
                    date=form.date.data,
                    weight=form.weight.data,
                    reps=form.reps.data,
                    count=form.count.data,
                    distance=form.distance.data
                    )
        user_workout.exercises.append(exercise)
        db.session.commit()
        return redirect(url_for('log_exercise', workout_id=workout_id))
    
    page = request.args.get('page', 1, type=int)
    exercises_paginated  = (
        Exercise.query
        .join(Workout.exercises)
        .filter(Workout.id == workout_id)
        .order_by(Exercise.date.desc())
        .paginate(page=page, per_page=app.config['WORKOUTS_PER_PAGE'], error_out=False)
    )
    next_url = url_for('log_exercise', workout_id=workout_id, page=exercises_paginated.next_num) \
        if exercises_paginated.has_next else None
    prev_url = url_for('log_exercise', workout_id=workout_id, page=exercises_paginated.prev_num) \
        if exercises_paginated.has_prev else None
    return render_template('log_exercise.html', title='Log Exercise', workout_id=workout_id, workout_name=user_workout.name, exercise_type=user_workout.exercise_type, form=form, exercises=exercises_paginated.items, next_url=next_url, prev_url=prev_url)

@app.route('/edit-exercise/<int:workout_id>/<int:exercise_id>', methods=['GET', 'POST'])
@login_required
def edit_exercise(workout_id, exercise_id):
    # fetch specific workout
    user_workout = Workout.query.get_or_404(workout_id)

    # verify correct user is editing workout
    if user_workout.user.id != current_user.id:
        flash("You do not have permission to edit this workout", "ERROR")
        return redirect(url_for('index'))
    
    exercise = Exercise.query.filter_by(id=exercise_id).first_or_404()
    print(exercise)

    form = ExerciseForm()
    if form.validate_on_submit():
        exercise.date=form.date.data
        exercise.weight=form.weight.data
        exercise.reps=form.reps.data
        exercise.distance=form.distance.data
        db.session.commit()
        flash("Exercise updated successfully!")
        return redirect(url_for('log_exercise', workout_id=workout_id))

    elif request.method == 'GET':
        form.date.data = exercise.date
        form.weight.data = exercise.weight
        form.reps.data = exercise.reps
        form.distance.data = exercise.distance
    return render_template('log_exercise.html', form=form, workout_id=workout_id, workout_name=user_workout.name, exercise_id=exercise_id, exercise_type=user_workout.exercise_type, action="edit")

@app.route('/delete-exercise/<int:workout_id>/<int:exercise_id>', methods=['GET'])
@login_required
def delete_exercise(workout_id, exercise_id):
    # fetch specific workout
    workout = Workout.query.get_or_404(workout_id)
    
    # verify correct user is deleting exercise
    if workout.user.id != current_user.id:
        flash("You do not have permission to delete this exercise", "ERROR")
        return redirect(url_for('index'))
    
    exercise = Exercise.query.filter_by(id=exercise_id).first_or_404()

    db.session.delete(exercise)
    db.session.commit()

    flash("Exercise deleted successfully!", "success")
    return redirect(url_for('log_exercise', workout_id=workout_id))
