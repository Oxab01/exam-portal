from flask import Blueprint, render_template, request, redirect, url_for, session
from models import User

student_bp = Blueprint('student', __name__)

# Student Login Route
@student_bp.route('/student/login', methods=['GET', 'POST'])
def student_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username, password=password, role='student').first()
        if user:
            session['user_id'] = user.id
            session['role'] = user.role
            return redirect(url_for('student.student_dashboard'))
        else:
            return 'Invalid Credentials'
    return render_template('student_login.html')

# Student Dashboard Route
@student_bp.route('/student/dashboard')
def student_dashboard():
    if 'role' in session and session['role'] == 'student':
        return render_template('student_dashboard.html')
    return redirect(url_for('student.student_login'))


from flask import Blueprint, request, redirect, url_for, session
from app import db, Question, StudentResponse

student_bp = Blueprint('student_bp', __name__)

# Route to submit student's test answers
@student_bp.route('/student/submit_test/<int:test_id>', methods=['POST'])
def submit_test(test_id):
    student_id = session.get('user_id')  # Assuming session holds logged-in student info
    questions = Question.query.filter_by(test_id=test_id).all()

    for question in questions:
        selected_option = request.form.get(f'q{question.id}')
        is_correct = selected_option == question.correct_option

        response = StudentResponse(
            student_id=student_id,
            question_id=question.id,
            selected_option=selected_option,
            is_correct=is_correct
        )
        db.session.add(response)

    db.session.commit()
    return redirect(url_for('student_bp.view_report', test_id=test_id))
