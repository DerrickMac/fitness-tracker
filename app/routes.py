from flask_login import current_user, login_user, logout_user, login_required
from flask import render_template, flash, redirect, url_for, request, jsonify
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

@app.route('/api/workouts', methods=['GET'])
@login_required
def get_workout_data():
    user = db.first_or_404(sa.select(User).where(User.username == current_user.username))
    user_workouts = []
    for w in user.workouts:
        user_workouts.append([w.date, 1])

    return jsonify(user_workouts)

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
     
    page = request.args.get('page', 1, type=int)
    user = db.first_or_404(sa.select(User).where(User.username == username))
    query = user.workouts.order_by(Workout.date.desc())
    workouts = db.paginate(query, page=page, per_page=app.config['WORKOUTS_PER_PAGE'], error_out=False)
    next_url = url_for('user', username=username, page=workouts.next_num) \
        if workouts.has_next else None
    prev_url = url_for('user', username=username, page=workouts.prev_num) \
        if workouts.has_prev else None
    return render_template('user.html', user=current_user, workouts=workouts.items, next_url=next_url, prev_url=prev_url)

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
        new_workout = Workout(
            date=form.date.data,       
            user_id=current_user.id  
        )
        db.session.add(new_workout)
        db.session.flush()  

        if form.exercise_type.data == "machine":
            machine_ex = MachineExercise(
                name=form.name.data,
                weight=form.weight.data or 0,
                reps=form.reps.data or 0
            )
            db.session.add(machine_ex)
            db.session.flush()  
            new_workout.machine_exercises.append(machine_ex)

        elif form.exercise_type.data == "cardio":
            cardio_ex = CardioExercise(
                name=form.name.data,
                distance=form.distance.data or 0
            )
            db.session.add(cardio_ex)
            db.session.flush()
            new_workout.cardio_exercises.append(cardio_ex)

        db.session.commit()

        flash("New workout created successfully!")
        return redirect(url_for('index'))
        
    return render_template('workout.html', title='Create Workout', form=form, action="Create")

@app.route('/edit-workout/<workout_id>', methods=['GET', 'POST'])
@login_required
def edit_workout(workout_id):
    # fetch specific workout
    workout = Workout.query.get_or_404(workout_id)

    # verify correct user is editing workout
    if workout.user.id != current_user.id:
        flash("You do not have permission to edit this workout", "ERROR")
        return redirect(url_for('index'))
    
    form = WorkoutForm()
    if form.validate_on_submit():
        
        workout.date=form.date.data
        workout.machine_exercises.clear()
        workout.cardio_exercises.clear()              
        if form.exercise_type.data == "machine":
            machine_ex = MachineExercise(
                name=form.name.data,
                weight=form.weight.data or 0,
                reps=form.reps.data or 0
            )
            db.session.add(machine_ex)
            workout.machine_exercises.append(machine_ex)

        elif form.exercise_type.data == "cardio":
            cardio_ex = CardioExercise(
                name=form.name.data,
                distance=form.distance.data or 0
            )
            db.session.add(cardio_ex)
            workout.cardio_exercises.append(cardio_ex)

        db.session.commit()

        flash("Workout updated successfully!")
        return redirect(url_for('user', username=current_user.username))

    elif request.method == 'GET':
        if workout.machine_exercises:
            machine_ex = workout.machine_exercises[0]
            form.exercise_type.data = 'machine'
            form.name.data = machine_ex.name
            form.weight.data = machine_ex.weight
            form.reps.data = machine_ex.reps
        elif workout.cardio_exercises:
            cardio_ex = workout.cardio_exercises[0]
            form.exercise_type.data = 'cardio'
            form.name.data = cardio_ex.name
            form.distance.data = cardio_ex.distance
        
    return render_template('workout.html', title='Edit Workout', form=form, action="Edit")

@app.route('/delete-workout/<workout_id>', methods=['GET'])
@login_required
def delete_workout(workout_id):
    # fetch specific workout
    workout = Workout.query.get_or_404(workout_id)
    
    # verify correct user is deleting workout
    if workout.user.id != current_user.id:
        flash("You do not have permission to delete this workout", "ERROR")
        return redirect(url_for('index'))
    
    db.session.delete(workout)
    db.session.commit()

    flash("Workout deleted successfully!", "success")
    return redirect(url_for('user', username=current_user.username))