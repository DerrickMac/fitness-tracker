from flask import render_template
from app import app, db
from sqlalchemy.exc import IntegrityError

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500

@app.errorhandler(IntegrityError)
def handle_integrity_error(error):
    db.session.rollback() 
    return render_template('500.html'), 500