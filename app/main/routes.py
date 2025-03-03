from flask_login import current_user, login_required
from flask import render_template, flash, redirect, url_for, request, jsonify, current_app
from collections import defaultdict
import sqlalchemy as sa
from app import db
from app.main import bp
from app.main.forms import EditProfileForm, WorkoutForm, ExerciseForm
from app.models import Workout, Exercise
from datetime import datetime, timedelta, timezone


@bp.before_request
def before_request():
    if current_user.is_authenticated:
        # Social media app feature carried over from Flask tutorial
        current_user.last_seen = datetime.now(timezone.utc)
        db.session.commit()

@bp.route('/api/workouts', methods=['GET'])
@login_required
def get_workout_data():
    # Get all user's exercises by date
    unique_dates = (
        db.session.query(sa.func.date(Exercise.date))
        .join(Exercise.workouts)
        .filter(Workout.user_id == current_user.id)
        .distinct()
        .all()
    )
    
    # Format data as [date, value] pairs to properly feed data to the Google Charts activity calendar
    date_value_pairs = [[d, 1] for (d,) in unique_dates if d is not None]
    
    return jsonify(date_value_pairs)

@bp.route('/')
@bp.route('/index')
@login_required
def index():
    return render_template('index.html', title='Home')

@bp.route('/user/<username>')
@login_required
def user(username):
    if not current_user.is_authenticated:
        return redirect(url_for('main.index'))
    return render_template('user.html', user=current_user)

@bp.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('main.edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='Edit Profile', form=form)

@bp.route('/workouts', methods=['GET'])
@login_required
def workouts():
    if not current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    today = datetime.today()

    # If specific filtering in the Workouts page is requested, change this section
    workouts = current_user.workouts.order_by(
        Workout.muscle_group.asc(), 
        Workout.name.asc()
    ).all()

    # Track the last completion date for each workout to guide future sessions
    for workout in workouts:
        exercise_dates = [ex.date for ex in workout.exercises if ex.date is not None]
        if exercise_dates:
            workout.last_done = max(exercise_dates)
        else:
            workout.last_done = None
        
        if not workout.last_done:
            workout.is_stale = True
        else:
            workout.is_stale = (today - workout.last_done) > timedelta(days=14)

    # Categorize workouts by muscle group so frontend can organize workouts appropriately
    grouped_workouts = defaultdict(list)
    for workout in workouts:
        group = workout.muscle_group or 'other'
        grouped_workouts[group].append(workout)

    return render_template('workouts.html', title='Workouts', grouped_workouts=grouped_workouts)

@bp.route('/create-workout', methods=['GET', 'POST'])
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
        return redirect(url_for('main.workouts'))
    
    return render_template('workout_form.html', title='Create Workout', form=form, action="Create")

@bp.route('/workouts/<int:workout_id>', methods=['GET', 'POST'])
@login_required
def edit_workout(workout_id):
    user_workout = Workout.query.get_or_404(workout_id)

    # verify correct user is editing workout
    if user_workout.user.id != current_user.id:
        flash("You do not have permission to edit this workout", "ERROR")
        return redirect(url_for('main.index'))
    
    form = WorkoutForm()
    if form.validate_on_submit():
        user_workout.name=form.name.data, 
        user_workout.exercise_type=form.exercise_type.data,       
        user_workout.muscle_group=form.muscle_group.data,
        db.session.commit()
        flash("Workout edited successfully!")
        return redirect(url_for('main.workouts'))
    
    # Pre-populate edit form with existing workout data
    elif request.method == "GET":
        form.name.data = user_workout.name
        form.exercise_type.data = user_workout.exercise_type
        form.muscle_group.data = user_workout.muscle_group

    return render_template('workout_form.html', title='Create Workout', form=form, action="Edit")

@bp.route('/workouts/<int:workout_id>/delete', methods=['GET', 'POST'])
@login_required
def delete_workout(workout_id):
    user_workout = Workout.query.get_or_404(workout_id)
    
    # verify correct user is deleting workout
    if user_workout.user.id != current_user.id:
        flash("You do not have permission to delete this workout", "ERROR")
        return redirect(url_for('main.index'))
    
    db.session.delete(user_workout)
    db.session.commit()
    return redirect(url_for('main.workouts'))

@bp.route('/log-exercise/<int:workout_id>', methods=['GET', 'POST'])
@login_required
def log_exercise(workout_id):
    user_workout = Workout.query.get_or_404(workout_id)

    # verify correct user is editing exercise
    if user_workout.user.id != current_user.id:
        flash("You do not have permission to create this exercise", "ERROR")
        return redirect(url_for('main.index'))
    
    form = ExerciseForm()
    if form.validate_on_submit():
        exercise = Exercise(
                    date=form.date.data,
                    weight=form.weight.data,
                    count=form.count.data,
                    distance=form.distance.data
                    )
        user_workout.exercises.append(exercise)
        db.session.commit()
        return redirect(url_for('main.log_exercise', workout_id=workout_id))
    
    page = request.args.get('page', 1, type=int)
    exercises_paginated  = (
        Exercise.query
        .join(Workout.exercises)
        .filter(Workout.id == workout_id)
        .order_by(Exercise.date.desc())
        .paginate(page=page, per_page=current_app.config['WORKOUTS_PER_PAGE'], error_out=False)
    )
    next_url = url_for('main.log_exercise', workout_id=workout_id, page=exercises_paginated.next_num) \
        if exercises_paginated.has_next else None
    prev_url = url_for('main.log_exercise', workout_id=workout_id, page=exercises_paginated.prev_num) \
        if exercises_paginated.has_prev else None
    return render_template('log_exercise.html', title='Log Exercise', workout_id=workout_id, \
        workout_name=user_workout.name, exercise_type=user_workout.exercise_type, form=form, \
        exercises=exercises_paginated.items, next_url=next_url, prev_url=prev_url)


@bp.route('/edit-exercise/<int:workout_id>/<int:exercise_id>', methods=['GET', 'POST'])
@login_required
def edit_exercise(workout_id, exercise_id):
    user_workout = Workout.query.get_or_404(workout_id)

    # verify correct user is editing workout
    if user_workout.user.id != current_user.id:
        flash("You do not have permission to edit this workout", "ERROR")
        return redirect(url_for('main.index'))
    
    exercise = Exercise.query.filter_by(id=exercise_id).first_or_404()
    form = ExerciseForm()
    if form.validate_on_submit():
        exercise.date=form.date.data
        exercise.weight=form.weight.data
        exercise.count=form.count.data
        exercise.distance=form.distance.data
        db.session.commit()
        flash("Exercise updated successfully!")
        return redirect(url_for('main.log_exercise', workout_id=workout_id))

    # Pre-populate form data with existing exercise data
    elif request.method == 'GET':
        form.date.data = exercise.date
        form.weight.data = exercise.weight
        form.count.data = exercise.count
        form.distance.data = exercise.distance

    return render_template('log_exercise.html', form=form, workout_id=workout_id, \
        workout_name=user_workout.name, exercise_id=exercise_id, \
        exercise_type=user_workout.exercise_type, action="edit")


@bp.route('/delete-exercise/<int:workout_id>/<int:exercise_id>', methods=['GET'])
@login_required
def delete_exercise(workout_id, exercise_id):
    workout = Workout.query.get_or_404(workout_id)
    
    # verify correct user is deleting exercise
    if workout.user.id != current_user.id:
        flash("You do not have permission to delete this exercise", "ERROR")
        return redirect(url_for('main.index'))
    
    exercise = Exercise.query.filter_by(id=exercise_id).first_or_404()
    db.session.delete(exercise)
    db.session.commit()
    flash("Exercise deleted successfully!", "success")

    return redirect(url_for('main.log_exercise', workout_id=workout_id))
