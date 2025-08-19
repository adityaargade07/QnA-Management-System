from flask import Blueprint, render_template, request
from flask_login import login_required, current_user
from app.models import Question  # ✅ Correct model import
from app import db

user_bp = Blueprint('user', __name__)

@user_bp.route('/dashboard')
@login_required
def user_dashboard():
    return render_template('user/dashboard.html')  # should extend user_base.html


@user_bp.route('/search', methods=['GET'])
@login_required
def search_qa():
    paper = request.args.get('paper', '').strip()
    set_code = request.args.get('set', '').strip()
    qno = request.args.get('qno', '').strip()
    keyword = request.args.get('search', '').strip()

    query = Question.query

    if paper:
        query = query.filter(Question.paper_unit.ilike(f'%{paper}%'))
    if set_code:
        query = query.filter(Question.set_code.ilike(f'%{set_code}%'))
    if qno:
        query = query.filter(Question.question_number.ilike(f'%{qno}%'))

    if keyword:
        query = query.filter(
            (Question.question.ilike(f'%{keyword}%')) |
            (Question.answer.ilike(f'%{keyword}%')) |
            (Question.diagram_path.ilike(f'%{keyword}%')) |
            (Question.reference_link.ilike(f'%{keyword}%'))
        )

    results = query.all()
    return render_template('user/search_results.html', results=results, query=keyword)
