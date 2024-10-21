from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Secret key for session management

# Set up SQLite database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///school.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads'

# Initialize the database
db = SQLAlchemy(app)

# Define models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(10), nullable=False)  # 'admin' or 'student'
    class_id = db.Column(db.Integer, db.ForeignKey('class.id'))

class Class(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    class_name = db.Column(db.String(50), nullable=False, unique=True)
    students = db.relationship('User', backref='class_', lazy=True)

class Test(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    test_name = db.Column(db.String(120), nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    questions = db.relationship('Question', backref='test', lazy=True)
    assigned_class_id = db.Column(db.Integer, db.ForeignKey('class.id'))

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    test_id = db.Column(db.Integer, db.ForeignKey('test.id'))
    question_text = db.Column(db.String(255), nullable=False)
    option_a = db.Column(db.String(255), nullable=False)
    option_b = db.Column(db.String(255), nullable=False)
    option_c = db.Column(db.String(255), nullable=False)
    option_d = db.Column(db.String(255), nullable=False)
    correct_option = db.Column(db.String(1), nullable=False)  # 'A', 'B', 'C', 'D'

# Create the database and tables if they don't exist
with app.app_context():
    db.create_all()

# Route for landing page
@app.route('/')
def index():
    return render_template('index.html')

# Route for Admin Login Page
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username, password=password, role='admin').first()
        if user:
            session['user_id'] = user.id
            session['role'] = user.role
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid Credentials')
    return render_template('admin_login.html')

# Route for Student Login Page
@app.route('/student/login', methods=['GET', 'POST'])
def student_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username, password=password, role='student').first()
        if user:
            session['user_id'] = user.id
            session['role'] = user.role
            return redirect(url_for('student_dashboard'))
        else:
            flash('Invalid Credentials')
    return render_template('student_login.html')

# Route for Admin Dashboard
@app.route('/admin/dashboard')
def admin_dashboard():
    if 'role' in session and session['role'] == 'admin':
        return render_template('admin_dashboard.html')
    return redirect(url_for('admin_login'))

# Route for Student Dashboard
@app.route('/student/dashboard')
def student_dashboard():
    if 'role' in session and session['role'] == 'student':
        student = User.query.filter_by(id=session['user_id']).first()
        student_class = student.class_
        tests = Test.query.filter_by(assigned_class_id=student_class.id).all() if student_class else []
        return render_template('student_dashboard.html', tests=tests)
    return redirect(url_for('student_login'))

# Route for Admin Upload Test Page
@app.route('/admin/upload_test', methods=['GET', 'POST'])
def upload_test():
    if 'role' in session and session['role'] == 'admin':
        classes = Class.query.all()
        if request.method == 'POST':
            file = request.files['file']
            class_id = request.form['class_id']
            test_name = request.form['test_name']
            if file and test_name and class_id:
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)

                # Process the file and extract questions (use previously implemented logic)
                questions = extract_mcqs_from_file(file_path)
                new_test = Test(test_name=test_name, created_by=session['user_id'], assigned_class_id=class_id)
                db.session.add(new_test)
                db.session.commit()

                for question in questions:
                    new_question = Question(
                        test_id=new_test.id,
                        question_text=question['question_text'],
                        option_a=question['option_a'],
                        option_b=question['option_b'],
                        option_c=question['option_c'],
                        option_d=question['option_d'],
                        correct_option=question['correct_option']
                    )
                    db.session.add(new_question)
                db.session.commit()

                flash('Test uploaded successfully!')
                return redirect(url_for('admin_dashboard'))

        return render_template('admin_dashboard.html', classes=classes)
    return redirect(url_for('admin_login'))

# Route for Student to Take Test
@app.route('/student/test/<int:test_id>', methods=['GET', 'POST'])
def take_test(test_id):
    test = Test.query.get(test_id)
    questions = Question.query.filter_by(test_id=test_id).all()

    if request.method == 'POST':
        # Collect and evaluate answers
        submitted_answers = {}
        for question in questions:
            submitted_answer = request.form.get(f'{question.id}')
            submitted_answers[question.id] = submitted_answer

        # Evaluate test results (placeholder logic)
        correct_count = sum(1 for question in questions if submitted_answers.get(question.id) == question.correct_option)
        flash(f'You answered {correct_count} out of {len(questions)} correctly!')

        return redirect(url_for('student_dashboard'))

    return render_template('take_test.html', test=test, questions=questions)

# Route for Test Submission
@app.route('/student/submit_test/<int:test_id>', methods=['POST'])
def submit_test(test_id):
    test = Test.query.get(test_id)
    questions = Question.query.filter_by(test_id=test_id).all()

    submitted_answers = {}
    for question in questions:
        submitted_answer = request.form.get(f'{question.id}')
        submitted_answers[question.id] = submitted_answer

    # Logic to evaluate the test and compute results
    correct_count = sum(1 for question in questions if submitted_answers.get(question.id) == question.correct_option)

    flash(f'Test submitted successfully! You answered {correct_count} out of {len(questions)} correctly!')
    return redirect(url_for('student_dashboard'))

# Route for Admin Logout
@app.route('/admin/logout')
def admin_logout():
    session.pop('user_id', None)
    session.pop('role', None)
    return redirect(url_for('admin_login'))

# Route for Student Logout
@app.route('/student/logout')
def student_logout():
    session.pop('user_id', None)
    session.pop('role', None)
    return redirect(url_for('student_login'))

if __name__ == '__main__':
    app.run(debug=True)
