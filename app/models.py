from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash
from . import db, login_manager


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="tester")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)

    def __repr__(self):
        return f"<User {self.email}>"


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Project(db.Model):
    __tablename__ = "projects"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey("users.id"))

    test_cases = db.relationship("TestCase", backref="project", lazy=True)
    defects = db.relationship("Defect", backref="project", lazy=True)


class TestCase(db.Model):
    __tablename__ = "test_cases"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), nullable=False, default="not_run")
    priority = db.Column(db.String(20), nullable=False, default="medium")

    project_id = db.Column(db.Integer, db.ForeignKey("projects.id"), nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    last_run_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    last_run_at = db.Column(db.DateTime, nullable=True)


class Defect(db.Model):
    __tablename__ = "defects"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    severity = db.Column(db.String(20), nullable=False, default="major")
    status = db.Column(db.String(20), nullable=False, default="open")

    project_id = db.Column(db.Integer, db.ForeignKey("projects.id"), nullable=False)
    test_case_id = db.Column(db.Integer, db.ForeignKey("test_cases.id"), nullable=True)
    created_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    assigned_to = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    test_case = db.relationship("TestCase", backref="defects", lazy=True)
