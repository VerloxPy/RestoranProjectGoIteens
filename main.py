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
import base64

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



@app.template_filter('b64encode')
def b64encode_filter(data):
    if data:
        return base64.b64encode(data).decode('utf-8')
    return ''

@app.route('/')
@app.route('/home')
@login_required
def home():

    return render_template('index.html', title="Welcome Page", username =current_user.nickname, current_user=current_user.nickname, admin='admin')


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

    return render_template("register.html", tittle='registration')



@app.route('/add_position', methods=['GET', 'POST'])
@login_required
def add_position():
    if current_user.nickname == 'admin':
        if request.method == "POST":
            position_name = request.form["position_name"]
            price = request.form["position_price"]
            description = request.form["position_description"]

            file = request.files['image']
            image_bytes = file.read()

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
        return render_template("add_position.html", title="Add position Boss panel")




@app.route('/menu')
@login_required
def menu():
    with Session() as session:
        all_positions = session.query(Menu).all()
    return render_template('menu.html', menu_items=all_positions)


@app.route("/log_out")
@login_required
def log_out():
    logout_user()
    return redirect(url_for("register"))


if __name__ == '__main__':
    app.run(debug=True)


