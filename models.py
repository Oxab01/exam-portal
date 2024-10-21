from app import db
from datetime import datetime

class User(db.Model):
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(10), nullable=False)  # 'admin' or 'student'
    class_id = db.Column(db.Integer, db.ForeignKey('class.id'))  # Foreign key to the class table

    def __repr__(self):
        return f'<User {self.username}>'

class Class(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    class_name = db.Column(db.String(50), nullable=False, unique=True)
    students = db.relationship('User', backref='class', lazy=True)

    def __repr__(self):
        return f'<Class {self.class_name}>'

class Test(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    test_name = db.Column(db.String(120), nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    questions = db.relationship('Question', backref='test', lazy=True)
    assigned_class_id = db.Column(db.Integer, db.ForeignKey('class.id'))

    def __repr__(self):
        return f'<Test {self.test_name}>'

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    test_id = db.Column(db.Integer, db.ForeignKey('test.id'))
    question_text = db.Column(db.String(255), nullable=False)
    option_a = db.Column(db.String(255), nullable=False)
    option_b = db.Column(db.String(255), nullable=False)
    option_c = db.Column(db.String(255), nullable=False)
    option_d = db.Column(db.String(255), nullable=False)
    correct_option = db.Column(db.String(1), nullable=False)

    def __repr__(self):
        return f'<Question {self.question_text[:50]}...>'
