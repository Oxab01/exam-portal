from flask import Blueprint, render_template, request, redirect, url_for, session
from models import User
from extensions import db

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username, password=password, role='admin').first()
        if user:
            session['user_id'] = user.id
            session['role'] = user.role
            return redirect(url_for('dashboard.admin_dashboard'))
        else:
            return 'Invalid Credentials'
    return render_template('admin_login.html')

@auth_bp.route('/student/login', methods=['GET', 'POST'])
def student_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username, password=password, role='student').first()
        if user:
            session['user_id'] = user.id
            session['role'] = user.role
            return redirect(url_for('dashboard.student_dashboard'))
        else:
            return 'Invalid Credentials'
    return render_template('student_login.html')

@auth_bp.route('/admin/logout')
def admin_logout():
    session.pop('user_id', None)
    session.pop('role', None)
    return redirect(url_for('auth.admin_login'))

@auth_bp.route('/student/logout')
def student_logout():
    session.pop('user_id', None)
    session.pop('role', None)
    return redirect(url_for('auth.student_login'))
