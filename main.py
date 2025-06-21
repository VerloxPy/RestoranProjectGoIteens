from flask import Flask, render_template, request, redirect, url_for, flash
from flask_caching import Cache
import os
from dotenv import load_dotenv
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from flask_wtf.csrf import CSRFProtect

from flask_login import login_required, current_user, login_user, logout_user

from FUCKING_database import Session, Users
from flask_login import LoginManager


app = Flask(__name__)

# SECRET_KEY = os.getenv('SECRET_KEY')
app.secret_key = "SECRET_KEY"

# csrf = CSRFProtect(app)

# cache = Cache()

# app.config['CACHE_TYPE'] = 'simple'
# app.config['CACHE_DEFAULT_TIMEOUT'] = 30
# app.config['CACHE_KEY_PREFIX'] = 'myapp_'

# cache.init_app(app)


# app.config['MAX_CONTENT_LENGTH'] = 4 * 1024 * 1024  # 4MB
# app.config['MAX_FORM_MEMORY_SIZE'] = 1024 * 1024  # 1MB
# app.config['MAX_FORM_PARTS'] = 500



login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'register'

@login_manager.user_loader
def load_user(user_id):
    with Session() as session:
        user = session.query(Users).filter_by(id=user_id).first()
        if user:
            return user


@app.route('/')
@app.route('/home')
@login_required
def home():
    return render_template('index.html', username =current_user.nickname)


@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":
        nickname = request.form["nickname"]
        email = request.form["email"]
        password = request.form["password"]

        with Session() as session:
            existing_user = session.query(Users).filter((Users.nickname == nickname) | (Users.email == email)).first()
            if existing_user:
                flash("User with the same nickname or email is already existing!", "danger")
                return redirect(url_for("register"))

            new_user = Users(nickname=nickname, email=email)
            new_user.set_password(password)

            session.add(new_user)
            session.commit()

            login_user(new_user)
            return redirect(url_for("home"))

    return render_template("register.html")









if __name__ == '__main__':
    app.run(debug=True)


