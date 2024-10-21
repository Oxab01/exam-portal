from flask import Blueprint, render_template
from app import db, Test, StudentResponse, User

teacher_bp = Blueprint('teacher_bp', __name__)

# Route for viewing the test report for a class
@teacher_bp.route('/admin/view_report/<int:test_id>', methods=['GET'])
def view_report(test_id):
    students = db.session.query(User).filter_by(role='student').all()
    report_data = []

    for student in students:
        total_questions = db.session.query(StudentResponse).filter_by(student_id=student.id, test_id=test_id).count()
        correct_answers = db.session.query(StudentResponse).filter_by(student_id=student.id, test_id=test_id, is_correct=True).count()

        report_data.append({
            'student_name': student.username,
            'total_questions': total_questions,
            'correct_answers': correct_answers,
            'incorrect_answers': total_questions - correct_answers
        })

    return render_template('admin_view_report.html', report_data=report_data)
