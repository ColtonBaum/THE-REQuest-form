from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Initialize SQLAlchemy
db = SQLAlchemy()

class Job(db.Model):
    __tablename__ = 'job'
    id          = db.Column(db.Integer, primary_key=True)
    name        = db.Column(db.String(100), nullable=False)
    number      = db.Column(db.String(50),  nullable=False)
    created_at  = db.Column(db.DateTime,     default=datetime.utcnow, nullable=False)
    manager     = db.Column(db.String(100), nullable=False)
    status      = db.Column(db.String(20),  default="Not started")
    archived    = db.Column(db.Boolean,     default=False)

    # Relationships
    requests           = db.relationship(
        'Request', back_populates='job', cascade='all, delete-orphan'
    )
    assets             = db.relationship(
        'Asset', back_populates='current_job', cascade='all, delete-orphan'
    )
    asset_assignments  = db.relationship(
        'AssetAssignment', back_populates='job', cascade='all, delete-orphan'
    )

class Request(db.Model):
    __tablename__ = 'request'
    id            = db.Column(db.Integer, primary_key=True)
    employee_name = db.Column(db.String(100), nullable=False)
    job_name      = db.Column(db.String(100), nullable=False)
    job_number    = db.Column(db.String(50),  nullable=False)
    need_by_date  = db.Column(db.String(50),  nullable=False)
    submitted_at  = db.Column(db.DateTime,     default=datetime.utcnow)
    status        = db.Column(db.String(20),   default="pending")

    job_id        = db.Column(db.Integer, db.ForeignKey('job.id'), nullable=True)
    job           = db.relationship('Job', back_populates='requests')

    items         = db.relationship(
        'RequestItem', backref='request', cascade='all, delete-orphan'
    )

class RequestItem(db.Model):
    __tablename__ = 'request_item'
    id           = db.Column(db.Integer, primary_key=True)
    request_id   = db.Column(db.Integer, db.ForeignKey('request.id'), nullable=False)
    item_name    = db.Column(db.String(200), nullable=False)
    quantity     = db.Column(db.Integer,     nullable=False)
    unit_price   = db.Column(db.Numeric(10,2), nullable=True)

class Asset(db.Model):
    __tablename__   = 'asset'
    id              = db.Column(db.Integer, primary_key=True)
    type            = db.Column(db.String(100), nullable=False)
    group           = db.Column(db.String(50),  nullable=True)
    identifier      = db.Column(db.String(100), nullable=False)
    serial_number   = db.Column(db.String(100), nullable=False)
    current_job_id  = db.Column(db.Integer, db.ForeignKey('job.id'), nullable=True)

    # Current assignment lookup
    current_job     = db.relationship('Job', back_populates='assets')

    # Historical assignment records
    assignments     = db.relationship(
        'AssetAssignment', back_populates='asset', cascade='all, delete-orphan'
    )

class AssetAssignment(db.Model):
    __tablename__  = 'asset_assignment'
    id             = db.Column(db.Integer, primary_key=True)
    asset_id       = db.Column(db.Integer, db.ForeignKey('asset.id'), nullable=False)
    job_id         = db.Column(db.Integer, db.ForeignKey('job.id'),   nullable=False)
    assigned_at    = db.Column(db.DateTime, default=datetime.utcnow)
    returned_at    = db.Column(db.DateTime, nullable=True)

    asset          = db.relationship('Asset', back_populates='assignments')
    job            = db.relationship('Job',   back_populates='asset_assignments')