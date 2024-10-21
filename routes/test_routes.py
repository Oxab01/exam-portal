from flask import Blueprint, render_template, request, redirect, url_for, session
from werkzeug.utils import secure_filename
import os
import pandas as pd
from app import db, Class, Test, Question

test_bp = Blueprint('test_bp', __name__)

# Allowed file extensions for upload
ALLOWED_EXTENSIONS = {'csv', 'xlsx'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Route to upload a test
@test_bp.route('/admin/upload_test', methods=['POST'])
def upload_test():
    if 'file' not in request.files:
        return 'No file part'
    file = request.files['file']
    if file.filename == '':
        return 'No selected file'
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join('uploads', filename)
        file.save(file_path)
        
        # Save Test Info
        class_id = request.form['class_id']
        new_test = Test(class_id=class_id, file_path=file_path)
        db.session.add(new_test)
        db.session.commit()

        # Process the file (read CSV or Excel and save questions to DB)
        if filename.endswith('.csv'):
            df = pd.read_csv(file_path)
        else:
            df = pd.read_excel(file_path)

        for index, row in df.iterrows():
            new_question = Question(
                test_id=new_test.id,
                question_text=row['question'],
                option_a=row['option_a'],
                option_b=row['option_b'],
                option_c=row['option_c'],
                option_d=row['option_d'],
                correct_option=row['correct_option']
            )
            db.session.add(new_question)
        db.session.commit()

        return 'Test uploaded and questions saved!'
    return 'Invalid file format'
