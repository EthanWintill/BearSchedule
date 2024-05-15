from flask import Blueprint, jsonify, request, redirect, render_template, url_for
from flask_login import  login_user, login_required, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import User, db, update_password



auth = Blueprint('auth', __name__)

def init_auth_routes(login_manager):
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('schedule_view'))
        
    return render_template('login.html')


@auth.route('/logout')
@login_required
def logout():
    logout_user()  # Log out the user
    return redirect(url_for('index'))


@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        phone = request.form['phone']

        user = User(username=username, password_hash=generate_password_hash(password), phone=phone)
        db.session.add(user)
        db.session.commit()

        if user:
            login_user(user)
            return redirect(url_for('schedule_view'))

    return render_template('signup.html')

@login_required
@auth.route('/change_password', methods=['POST'])
def change_password():
    data = request.get_json()
    user_id = data['user_id']
    new_password = data['new_password']
    update_password(user_id, new_password)
    return jsonify({'status': 'ok'}), 200
