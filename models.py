from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date

db = SQLAlchemy()


# ---------------------------------------------------------------------------
# Project Manager
# ---------------------------------------------------------------------------
class ProjectManager(db.Model):
    __tablename__ = 'project_manager'
    id            = db.Column(db.Integer, primary_key=True)
    name          = db.Column(db.String(100), nullable=False, unique=True)
    is_active     = db.Column(db.Boolean, default=True, nullable=False)
    display_order = db.Column(db.Integer, default=0, nullable=False)

    jobs = db.relationship('Job', back_populates='pm', lazy='dynamic')

    def __repr__(self):
        return f'<PM {self.name}>'


# ---------------------------------------------------------------------------
# Job
# ---------------------------------------------------------------------------
class Job(db.Model):
    __tablename__ = 'job'
    id          = db.Column(db.Integer, primary_key=True)
    name        = db.Column(db.String(100), nullable=False)
    number      = db.Column(db.String(50),  nullable=False)
    start_date  = db.Column(db.Date,        nullable=False, default=date.today)
    created_at  = db.Column(db.DateTime,    default=datetime.utcnow, nullable=False)
    status      = db.Column(db.String(20),  default="Not started")
    archived    = db.Column(db.Boolean,     default=False)

    # Legacy string column (kept for backward compat)
    manager     = db.Column(db.String(100), nullable=True)

    # FK to project_manager table
    manager_id  = db.Column(db.Integer, db.ForeignKey('project_manager.id'), nullable=True)
    pm          = db.relationship('ProjectManager', back_populates='jobs')

    # Relationships
    requests = db.relationship(
        'Request', back_populates='job',
        cascade='all, delete-orphan'
    )
    assets = db.relationship(
        'Asset', back_populates='current_job',
        cascade='save-update, merge',
        passive_deletes=True,
    )
    asset_assignments = db.relationship(
        'AssetAssignment', back_populates='job',
        cascade='all, delete-orphan'
    )


# ---------------------------------------------------------------------------
# Request
# ---------------------------------------------------------------------------

STATUS_SORT_ORDER = {
    "Not started": 0,
    "pending":     0,
    "In progress": 1,
    "Complete":    2,
}


class Request(db.Model):
    __tablename__ = 'request'
    id            = db.Column(db.Integer, primary_key=True)
    employee_name = db.Column(db.String(100), nullable=False)
    job_name      = db.Column(db.String(100), nullable=False)
    job_number    = db.Column(db.String(50),  nullable=False)
    need_by_date  = db.Column(db.Date, nullable=True)
    notes         = db.Column(db.Text, nullable=True)
    submitted_at  = db.Column(db.DateTime, default=datetime.utcnow)
    status        = db.Column(db.String(20), default="Not started")

    # NEW: equipment/trailer assigned when fulfilling this request
    equipment_assigned = db.Column(db.Text, nullable=True)

    job_id = db.Column(db.Integer, db.ForeignKey('job.id'), nullable=True)
    job    = db.relationship('Job', back_populates='requests')

    items = db.relationship(
        'RequestItem', backref='request', cascade='all, delete-orphan'
    )

    @property
    def status_sort_key(self):
        return STATUS_SORT_ORDER.get(self.status, 1)


class RequestItem(db.Model):
    __tablename__ = 'request_item'
    id         = db.Column(db.Integer, primary_key=True)
    request_id = db.Column(db.Integer, db.ForeignKey('request.id'), nullable=False)
    item_name  = db.Column(db.String(200), nullable=True)
    quantity   = db.Column(db.Integer, nullable=True)
    unit_price = db.Column(db.Numeric(10, 2), nullable=True)


# ---------------------------------------------------------------------------
# Asset
# ---------------------------------------------------------------------------
class Asset(db.Model):
    __tablename__   = 'asset'
    id              = db.Column(db.Integer, primary_key=True)
    type            = db.Column(db.String(100), nullable=False)
    group           = db.Column(db.String(50),  nullable=True, index=True)
    identifier      = db.Column(db.String(100), nullable=False, index=True)
    serial_number   = db.Column(db.String(100), nullable=False, index=True)
    current_job_id  = db.Column(
        db.Integer, db.ForeignKey('job.id', ondelete='SET NULL'), nullable=True
    )

    parent_id = db.Column(db.Integer, db.ForeignKey('asset.id'), nullable=True)
    children  = db.relationship(
        'Asset',
        backref=db.backref('parent', remote_side=[id]),
        cascade='all, delete-orphan'
    )

    current_job = db.relationship('Job', back_populates='assets')
    assignments = db.relationship(
        'AssetAssignment', back_populates='asset', cascade='all, delete-orphan'
    )


class AssetAssignment(db.Model):
    __tablename__  = 'asset_assignment'
    id             = db.Column(db.Integer, primary_key=True)
    asset_id       = db.Column(db.Integer, db.ForeignKey('asset.id'), nullable=False)
    job_id         = db.Column(db.Integer, db.ForeignKey('job.id'),   nullable=False)
    assigned_at    = db.Column(db.DateTime, default=datetime.utcnow)
    returned_at    = db.Column(db.DateTime, nullable=True)

    asset = db.relationship('Asset', back_populates='assignments')
    job   = db.relationship('Job',   back_populates='asset_assignments')
