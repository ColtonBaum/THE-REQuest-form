from flask_wtf import FlaskForm
from wtforms import (
    Form,             # for nested form without CSRF
    StringField,
    SelectField,
    DateField,
    DecimalField,
    SubmitField,
    IntegerField,
    FieldList,
    FormField,
    TextAreaField,    # for notes section
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

class RequestItemForm(Form):
    """Nested item form: use Form (no CSRF) so only the parent form handles CSRF."""
    item_name = StringField(
        'Item Name',
        validators=[Optional(), Length(max=200)]
    )
    # Quantity is free-text and optional
    quantity = StringField(
        'Quantity',
        validators=[Optional(), Length(max=64)]
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
        min_entries=1  # can be increased (e.g., 5) if you want more blank rows by default
    )
    notes = TextAreaField(
        'Notes',
        validators=[Optional(), Length(max=1000)],
        render_kw={"rows": 3, "placeholder": "Any special instructions or comments…"}
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
    start_date = DateField(
        'Start Date',
        format='%Y-%m-%d',
        validators=[DataRequired()]
    )
    manager = SelectField(
        'Project Manager',
        choices=PM_TABS,
        validators=[DataRequired()]
    )
    submit = SubmitField('Save')

class AssetForm(FlaskForm):
    group = SelectField(
        "Category",
        choices=[
            ("LN", "LN"),
            ("Flatbed trailer", "Flatbed trailer"),
            ("Tool Trailer", "Tool Trailer"),
            ("Welder", "Welder"),
            ("Specialty", "Specialty"),
            ("Tool shack", "Tool shack"),
            ("Gang Box", "Gang Box"),
            ("Utility Trailer", "Utility Trailer"),
            ("Semi Tool Trailer", "Semi Tool Trailer"),
        ],
        validators=[DataRequired()]
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
