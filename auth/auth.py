from flask import Blueprint, flash, jsonify, request, redirect, render_template, url_for
from flask_login import  login_user, login_required, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import User, db, update_password, delete_user, update_username



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
            flash('You were successfully logged in')
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

        #data validation for phone number
        if len(phone) != 10 or not phone.isdigit():
            flash('Invalid phone number')
            return redirect(url_for('auth.signup'))

        user = User(username=username, password_hash=generate_password_hash(password), phone=phone)
        db.session.add(user)
        db.session.commit()

        if user:
            login_user(user)
            return redirect(url_for('schedule_view'))

    return render_template('signup.html')

@auth.route('/delete_account', methods=['DELETE'])
def delete_account():
    data = request.get_json()
    user_id = data['user_id']
    isManager = data['is_manager']
    if not isManager:
        logout_user()
    delete_user(user_id)
    return jsonify({'status': 'ok'}), 200

@auth.route('/change_password', methods=['POST'])
@login_required
def change_password():
    data = request.get_json()
    user_id = data['user_id']
    new_password = data['new_password']
    update_password(user_id, new_password)
    return jsonify({'status': 'ok'}), 200

@auth.route('/change_username', methods=['POST'])
@login_required
def change_username():
    data = request.get_json()
    user_id = data['user_id']
    new_username = data['new_username']
    update_username(user_id, new_username)
    return jsonify({'status': 'ok'}), 200


