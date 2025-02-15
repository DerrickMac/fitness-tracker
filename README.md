# Fitness Tracker

Fitness Tracker is a Flask-based web application designed for fitness enthusiasts to manage and log their workouts. The app provides features such as user registration, secure login, workout creation, and exercise logging. It uses a combination of Flask blueprints, SQLAlchemy for ORM, and various Flask extensions (Flask-Login, Flask-Migrate, Flask-Mail, and Flask-Moment) to deliver a responsive and reliable experience.

## Requirements

Before you begin using or developing the project, ensure you have the following installed:

- **Python 3.11 or later:** The project is built with modern Python features.
- **Flask and Extensions:**  
  - Flask  
  - Flask-Login  
  - Flask-Migrate  
  - Flask-Mail  
  - Flask-Moment  
- **SQLAlchemy:** Used for database interactions.
- **Relational Database:** SQLite is commonly used for development, but you can configure PostgreSQL or another supported database for production.

## Usage

Follow these step‐by‐step instructions to get the application up and running:

1. **Clone the Repository:**
   git clone https://github.com/yourusername/fitness-tracker.git
   cd fitness-tracker

2. **Set Up Virtual Environment**

    python3 -m venv venv
    source venv/bin/activate  # on Linux
    venv\Scripts\activate     # on Windows

3. **Install Dependencies**

    pip install -r requirements.txt

4. **Configure Environment Variables**

    Set these environment variables in your own .env file:

    SECRET_KEY: "enter your own secret key"  
    SQLALCHEMY_DATABASE_URI: "sqlite:///app.db" # for a local database, or add a postgresSQL URI for production.

5. **Initialize the Database**

    flask db init
    flask db migrate -m "Initial migration"
    flask db upgrade

6. **Run the Application**

    flask run

Open your web browser and navigate to http://127.0.0.1:5000/ to access the app.