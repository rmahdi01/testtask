from flask import Flask, render_template, jsonify, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from datetime import datetime
from flask_admin import Admin, AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView
from flask_login import UserMixin, LoginManager, login_user, login_required, current_user, logout_user
from wtforms import StringField, PasswordField, SubmitField, EmailField
from wtforms.validators import DataRequired
import sqlite3


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)
app.secret_key = '2008180804'


login_manager = LoginManager()
login_manager.init_app(app)


class LoginForm(FlaskForm):
    username = StringField('Username', default="admin")
    email = EmailField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement = True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100), unique=True)
    username = db.Column(db.String(100), default = "admin")

class MyAdminIndexView(AdminIndexView):
    @expose('/')
    def index(self):
        if current_user.is_authenticated:
            return self.render('admin/index.html')
        else:
            return redirect(url_for('login'))



@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime)
    finished_at = db.Column(db.DateTime)
    appearance_at = db.Column(db.DateTime)
    duty_id = db.Column(db.Integer)
    name = db.Column(db.String(255))
    engineer_id = db.Column(db.Integer)
    team_id = db.Column(db.Integer)
    member_id = db.Column(db.Integer)
    object_id = db.Column(db.Integer)
    location = db.Column(db.String(255))
    category_id = db.Column(db.Integer)
    sub_category_id = db.Column(db.Integer)
    accident_id = db.Column(db.Integer)
    status_id = db.Column(db.Integer)
    departure = db.Column(db.Boolean)
    comment = db.Column(db.String(255))
    
    def repr(self):
        return '<Task %r>' % self.id

@app.route('/api/data/all',methods = ['GET'])
def get_all_data():
    conn = sqlite3.connect('instance/database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM task')
    data = cursor.fetchall()
    conn.close()
    return jsonify(data)
    

@app.route('/')
def index():
    return redirect(url_for("login"))

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.password == form.password.data:
            login_user(user)
            return redirect(url_for('admin.index'))
        else:
            return 'Неверный пароль или имя пользователя'
    return render_template('auth.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


admin = Admin(app, name="Admin Panel", index_view=MyAdminIndexView(), template_mode="bootstrap3")
admin.add_view(ModelView(Task, db.session))

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)