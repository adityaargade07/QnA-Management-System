from datetime import datetime
from flask_login import UserMixin
from app import db  # ✅ Correct import

class Question(db.Model):
    __tablename__ = 'question'
    id = db.Column(db.Integer, primary_key=True)
    paper_unit = db.Column(db.String(100), nullable=False)  # Combined Paper/Unit
    set_code = db.Column(db.String(10), nullable=False)     # Renamed from 'paper'
    question_number = db.Column(db.String(100), nullable=False)
    question = db.Column(db.Text, nullable=False)
    answer = db.Column(db.Text, nullable=True)
    diagram_path = db.Column(db.String(255), nullable=True)
    reference_link = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Question {self.paper_unit}/{self.set_code}/{self.question_number}>"


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    role = db.Column(db.String(50), default='user')

    def __repr__(self):
        return f'<User {self.username}>'
