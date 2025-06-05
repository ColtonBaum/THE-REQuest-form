# forms.py

from flask_wtf import FlaskForm
from wtforms import (
    StringField, SelectField, DateField, DecimalField, SubmitField,
    IntegerField, FieldList, FormField
)
from wtforms.validators import DataRequired, NumberRange, Length, Optional

# define your PM tabs here so it's easy to keep in sync
PM_TABS = [
    ("Project Manager 1", "Project Manager 1"),
    ("Project Manager 2", "Project Manager 2"),
    ("Project Manager 3", "Project Manager 3"),
    ("Project Manager 4", "Project Manager 4"),
    ("Project Manager 5", "Project Manager 5"),
    ("Project Manager 6", "Project Manager 6"),
    ("Project Manager 7", "Project Manager 7"),
    ("Project Manager 8", "Project Manager 8"),
    ("Project Manager 9", "Project Manager 9"),
    ("Project Manager 10", "Project Manager 10"),
]

class RequestItemForm(FlaskForm):
    item_name = StringField(
        'Item Name',
        validators=[DataRequired(), Length(max=200)]
    )
    quantity = IntegerField(
        'Quantity',
        validators=[DataRequired(), NumberRange(min=1)]
    )

class RequestForm(FlaskForm):
    employee_name = StringField(
        'Your Name',
        validators=[DataRequired(), Length(max=100)]
    )
    job_name = StringField(
        'Job Name',
        validators=[DataRequired(), Length(max=100)]
    )
    job_number = StringField(
        'Job Number',
        validators=[DataRequired(), Length(max=50)]
    )
    need_by_date = DateField(
        'Need by Date',
        format='%Y-%m-%d',
        validators=[DataRequired()]
    )
    items = FieldList(
        FormField(RequestItemForm),
        min_entries=1
    )
    submit = SubmitField('Submit Request')

class JobForm(FlaskForm):
    name = StringField(
        'Job Name',
        validators=[DataRequired(), Length(max=100)]
    )
    number = StringField(
        'Job Number',
        validators=[DataRequired(), Length(max=50)]
    )
    location = StringField(
        'Location',
        validators=[DataRequired(), Length(max=100)]
    )
    start_date = DateField(
        'Start Date',
        format='%Y-%m-%d',
        validators=[DataRequired()]
    )
    end_date = DateField(
        'End Date',
        format='%Y-%m-%d',
        validators=[DataRequired()]
    )
    manager = SelectField(
        'Project Manager',
        choices=PM_TABS,
        validators=[DataRequired()]
    )
    budget = DecimalField(
        'Budget',
        places=2,
        validators=[DataRequired(), NumberRange(min=0)]
    )
    submit = SubmitField('Save')

class AssetForm(FlaskForm):
    group = SelectField(
        "Group",
        choices=[
            ("Welder", "Welder"),
            ("LN", "LN"),
            ("Tool Trailer", "Tool Trailer"),
            ("Flat Bed Trailer", "Flat Bed Trailer"),
            ("Specialty Tooling", "Specialty Tooling"),
        ],
        validators=[DataRequired()]
    )
    type = StringField(
        "Asset Type",
        validators=[DataRequired(), Length(max=100)],
        render_kw={"placeholder": "e.g. Trailer, Vehicle…"}
    )
    identifier = StringField(
        "Identifier",
        validators=[DataRequired(), Length(max=100)],
        render_kw={"placeholder": "Model, Plate #, etc."}
    )
    serial_number = StringField(
        "Serial Number",
        validators=[DataRequired(), Length(max=100)],
        render_kw={"placeholder": "Unique serial #"}
    )
    submit = SubmitField("Save")
