from flask import Flask, render_template, request, redirect, url_for, flash
from flask_caching import Cache
import os
from dotenv import load_dotenv
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from flask_wtf.csrf import CSRFProtect

from flask_login import login_required, current_user, login_user, logout_user

from FUCKING_database import Session, Users, Menu
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
        user = session.query(Users).filter_by(id=int(user_id)).first()
        if user:
            return user


@app.route('/')
@app.route('/home')
@login_required
def home():

    return render_template('index.html', username =current_user.nickname, current_user=current_user.nickname, admin='admin')


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        nickname = request.form["nickname"]
        email = request.form["email"]
        password = request.form["password"]

        with Session() as session:
            user = session.query(Users).filter_by(nickname=nickname, email=email).first()
            if user and user.check_password(password):
                login_user(user)
                return redirect(url_for("home"))

            existing = session.query(Users).filter((Users.nickname == nickname) | (Users.email == email)).first()
            if existing:
                flash("Користувач із таким nickname або email вже існує, але пароль не співпадає.", "danger")
                return redirect(url_for("register"))

            new_user = Users(nickname=nickname, email=email)
            new_user.set_password(password)
            session.add(new_user)
            session.commit()

            login_user(new_user)
            return redirect(url_for("home"))

    return render_template("register.html")



@app.route('/add_position', methods=['GET', 'POST'])
@login_required
def add_position():
    if request.method == "POST":
        position_name = request.form["position_name"]
        price = request.form["position_price"]
        description = request.form["position_description"]

        file = request.files['image']
        image_bytes = file.read()  # Готово для збереження як LargeBinary

        with Session() as session:
            position_exist = session.query(Menu).filter_by(positions=position_name).first()
            if position_exist:
                flash("There is already a position with this name", 'danger')
                return redirect(url_for('add_position'))

            new_item = Menu(
                positions=position_name,
                price=price,
                description=description,
                image=image_bytes  # або image=file.filename, якщо зберігаєш шлях
            )

            session.add(new_item)
            session.commit()
            flash("Position added successfully!", "success")
            return redirect(url_for("home"))

    return render_template("add_position.html")




@app.route("/log_out")
@login_required
def log_out():
    logout_user()
    return redirect(url_for("register"))


if __name__ == '__main__':
    app.run(debug=True)









if __name__ == '__main__':
    app.run(debug=True)


