from flask import request, redirect, url_for, Blueprint, render_template, flash, Response
from flask_login import login_required
from app import db, role_required
from ..models import Question
import csv
from io import StringIO
import pandas as pd
from werkzeug.utils import secure_filename
import os

admin_bp = Blueprint('admin', __name__)

# Admin Dashboard
@admin_bp.route('/admin/dashboard')
@login_required
@role_required('admin')
def admin_dashboard():
    sample_questions = Question.query.all()  # You can adjust the query to fetch a subset or apply filters
    
    return render_template('admin/dashboard.html', sample_questions=sample_questions)

# Add Single Q&A
@admin_bp.route('/admin/add_qa', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def add_qa():
    if request.method == 'POST':
        new_question = Question(
            paper_unit=request.form['paper_unit'],
            set_code=request.form['set_code'],
            question_number=request.form['question_number'],
            question=request.form['question'],
            answer=request.form['answer'],
            diagram_path=request.form.get('diagram_path'),
            reference_link=request.form.get('reference_link')
        )
        db.session.add(new_question)
        db.session.commit()
        flash('Question added successfully!', 'success')
        return redirect(url_for('admin.admin_dashboard'))
    return render_template('admin/admin_add_qa.html')

# Export Questions to CSV
@admin_bp.route('/admin/export', methods=['GET'])
@login_required
@role_required('admin')
def export_csv():
    questions = Question.query.all()
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(['Paper/Unit', 'Set', 'Qno', 'Question', 'Answer', 'Diagram Path', 'Reference Link'])
    for q in questions:
        writer.writerow([q.paper_unit, q.set_code, q.question_number, q.question, q.answer, q.diagram_path, q.reference_link])
    output.seek(0)
    return Response(
        output,
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=dataset.csv'}
    )

UPLOAD_FOLDER = 'app/static/diagrams'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Function to check allowed file extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Bulk Upload Function
@admin_bp.route('/admin/bulk_upload', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def bulk_upload():
    if request.method == 'POST':
        file = request.files['csv_file']
        
        if file and file.filename.endswith('.csv'):
            try:
                df = pd.read_csv(file, encoding='ISO-8859-1')  # handles non-UTF-8 files
                print(df.head())

                uploaded_count = 0
                skipped_count = 0

                for _, row in df.iterrows():
                    paper_unit = row.get('Paper/Unit')
                    set_code = row.get('Set')
                    question_number = row.get('Qno')
                    question = row.get('Question')

                    # Handle 'Answer' or 'Answers' column
                    raw_answer = row.get('Answer') if 'Answer' in row else row.get('Answers')
                    answer = '' if pd.isna(raw_answer) else str(raw_answer)

                    diagram_path = None if pd.isna(row.get('Diagram Path')) else row['Diagram Path']
                    reference_link = None if pd.isna(row.get('Reference Link')) else row['Reference Link']

                    # Skip incomplete rows
                    if pd.isna(paper_unit) or pd.isna(set_code) or pd.isna(question_number) or pd.isna(question):
                        print(f"Skipping incomplete row: {row}")
                        skipped_count += 1
                        continue

                    # Create a new Question object and add it to the database
                    new_question = Question(
                        paper_unit=str(paper_unit),
                        set_code=str(set_code),
                        question_number=str(question_number),
                        question=str(question),
                        answer=answer,
                        diagram_path=diagram_path,
                        reference_link=reference_link
                    )
                    db.session.add(new_question)
                    uploaded_count += 1

                db.session.commit()
                flash(f'Bulk upload successful! {uploaded_count} uploaded, {skipped_count} skipped.', 'success')
                print(f"{uploaded_count} questions uploaded successfully.")

            except Exception as e:
                flash(f'Error processing CSV: {str(e)}', 'danger')
                print(f"Error: {str(e)}")
        else:
            flash('Please upload a valid CSV file.', 'danger')

        return redirect(url_for('admin.admin_dashboard'))

    return render_template('admin/admin_bulk_upload.html')



# Search Questions
@admin_bp.route('/admin/search', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def search_questions():
    if request.method == 'POST':
        paper_unit = request.form.get('paper_unit')
        set_code = request.form.get('set_code')
        qno = request.form.get('qno')

        # Start building the query
        query = Question.query

        # Apply filters based on the form data
        if paper_unit:
            query = query.filter(Question.paper_unit.ilike(f'%{paper_unit}%'))
        if set_code:
            query = query.filter(Question.set_code.ilike(f'%{set_code}%'))
        if qno:
            query = query.filter(Question.question_number.ilike(f'%{qno}%'))

        # Execute the query and get results
        results = query.all()
        return render_template('admin/admin_search_results.html', results=results)

    return render_template('admin/admin_search.html')

# Delete Questions
@admin_bp.route('/admin/delete_questions', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def delete_questions():
    if request.method == 'POST':
        question_ids = request.form.getlist('questions_to_delete')
        
        if question_ids:
            # Convert the list of string IDs to integers
            question_ids = [int(id) for id in question_ids]
            
            # Delete the selected questions from the database
            questions_to_delete = Question.query.filter(Question.id.in_(question_ids)).all()
            for question in questions_to_delete:
                db.session.delete(question)
            db.session.commit()
            flash('Selected questions have been deleted successfully!', 'success')
        else:
            flash('No questions selected for deletion.', 'danger')
        return redirect(url_for('admin.delete_questions'))

    # Display all questions to the admin
    questions = Question.query.all()
    return render_template('admin/delete_question.html', questions=questions)
