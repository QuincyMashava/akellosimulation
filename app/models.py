from datetime import datetime, timezone
from hashlib import md5
from typing import Optional
import sqlalchemy as sa
import sqlalchemy.orm as so
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login


# Association table for many-to-many relationship
workspace_members = db.Table('workspace_members',
    db.Column('workspace_id', db.Integer, db.ForeignKey('workspace.id'), primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True)
)


class User(UserMixin, db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    firstname: so.Mapped[str] = so.mapped_column(sa.String(120), index=True)
    lastname: so.Mapped[str] = so.mapped_column(sa.String(120), index=True)
    username: so.Mapped[str] = so.mapped_column(sa.String(64), index=True,
                                                unique=True)
    email: so.Mapped[str] = so.mapped_column(sa.String(120), index=True,
                                             unique=True)
    department: so.Mapped[str] = so.mapped_column(sa.String(120), index=True)
    role: so.Mapped[str] = so.mapped_column(sa.String(120), index=True)
    password_hash: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256))
    about_me: so.Mapped[Optional[str]] = so.mapped_column(sa.String(140))
    last_seen: so.Mapped[Optional[datetime]] = so.mapped_column(
        default=lambda: datetime.now(timezone.utc))
    archived = db.Column(db.Boolean, default=False)


    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return f'https://www.gravatar.com/avatar/{digest}?d=identicon&s={size}'


@login.user_loader
def load_user(id):
    return db.session.get(User, int(id))



class SchoolTracker(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    schoolname = db.Column(db.String(100), index=True, unique=True)
    province = db.Column(db.String(255))
    district = db.Column(db.String(255))
    computers = db.Column(db.Integer)
    internet = db.Column(db.String(255))
    lab = db.Column(db.String(255))
    installed = db.Column(db.String(255))
    scheduled_visit = db.Column(db.String(255))
    tech_ready = db.Column(db.String(255))
    installation_date = db.Column(db.DateTime, index=True, default=datetime.utcnow, nullable=True)
    school_contact = db.Column(db.String(255))
    archived = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return '<SchoolTracker {}>'.format(self.schoolname)
    

class Task(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    department = db.Column(db.String(255))
    taskname = db.Column(db.String(255))
    assigned_to = db.Column(db.String(255))
    task_author = db.Column(db.String(140))
    category = db.Column(db.String(255))
    status = db.Column(db.String(140))
    progress = db.Column(db.Integer)
    priority = db.Column(db.String(140))
    description = db.Column(db.Text())
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    complete_date = db.Column(db.DateTime, index=True, default=datetime.utcnow,nullable=True)
    due_date = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    archived = db.Column(db.Boolean, default=False)
    def __repr__(self):
        return '<Individual_Task {}>'.format(self.task_name)


class Workspace(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    members = db.relationship('User', secondary=workspace_members, backref=db.backref('workspaces', lazy='dynamic'))
    archived = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f'<Workspace {self.name}>'
    

class Scorecard(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    key_focus_area = db.Column(db.String(100), nullable=False)
    strategic_objective = db.Column(db.String(200), nullable=False)
    performance_measure = db.Column(db.String(200), nullable=False)
    unit_of_measure = db.Column(db.String(100), nullable=False)
    target = db.Column(db.String(100), nullable=False)
    weight = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    employee_name = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f'<Scorecard {self.id}>'
    
class WorkstreamsReport(db.Model):
    __tablename__ = 'workstreams_report'
    id = db.Column(db.Integer, primary_key=True)
    workstream = db.Column(db.String(255), nullable=False)
    progress = db.Column(db.String(50), nullable=True)
    quantity = db.Column(db.String(50), nullable=True)
    target_completion_date = db.Column(db.String(50), nullable=True)
    comments = db.Column(db.Text, nullable=True)
    employee_name = db.Column(db.String(100), nullable=False)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

class TargetsReport(db.Model):
    __tablename__ = 'targets_report'
    id = db.Column(db.Integer, primary_key=True)
    target = db.Column(db.String(255), nullable=False)
    target_completion_date = db.Column(db.String(50), nullable=True)
    employee_name = db.Column(db.String(100), nullable=False)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)


class Notifications(db.Model):
    __tablename__ = 'notifications'
    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.String(255), nullable=False)
    read = db.Column(db.Boolean, default=False)
    category = db.Column(db.String(255), nullable=False)
    sender = db.Column(db.String(255), nullable=False)
    reciever = db.Column(db.String(255), nullable=False)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

