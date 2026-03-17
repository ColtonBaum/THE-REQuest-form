from flask_wtf import FlaskForm
from wtforms import (
    Form,
    StringField,
    SelectField,
    DateField,
    DecimalField,
    SubmitField,
    IntegerField,
    FieldList,
    FormField,
    TextAreaField,
)
from wtforms.validators import DataRequired, NumberRange, Length, Optional


# ---------------------------------------------------------------------------
# Request forms
# ---------------------------------------------------------------------------
class RequestItemForm(Form):
    """Nested item form (no CSRF — parent handles it)."""
    item_name = StringField('Item Name', validators=[Optional(), Length(max=200)])
    quantity  = StringField('Quantity',   validators=[Optional(), Length(max=64)])


class RequestForm(FlaskForm):
    employee_name = StringField('Your Name',   validators=[DataRequired(), Length(max=100)])
    job_name      = StringField('Job Name',    validators=[DataRequired(), Length(max=100)])
    job_number    = StringField('Job Number',  validators=[DataRequired(), Length(max=50)])
    need_by_date  = DateField('Need by Date',  format='%Y-%m-%d', validators=[DataRequired()])
    items         = FieldList(FormField(RequestItemForm), min_entries=1)
    notes         = TextAreaField(
        'Notes',
        validators=[Optional(), Length(max=1000)],
        render_kw={"rows": 3, "placeholder": "Any special instructions or comments…"}
    )
    submit = SubmitField('Submit Request')


# ---------------------------------------------------------------------------
# Job form  (PM choices are set dynamically in the route, not hardcoded here)
# ---------------------------------------------------------------------------
class JobForm(FlaskForm):
    name       = StringField('Job Name',   validators=[DataRequired(), Length(max=100)])
    number     = StringField('Job Number', validators=[DataRequired(), Length(max=50)])
    start_date = DateField('Start Date',   format='%Y-%m-%d', validators=[DataRequired()])
    manager    = SelectField('Project Manager', coerce=int, validators=[DataRequired()])
    submit     = SubmitField('Save')


# ---------------------------------------------------------------------------
# Asset form
# ---------------------------------------------------------------------------
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
    identifier    = StringField("Identifier",    validators=[DataRequired(), Length(max=100)],
                                render_kw={"placeholder": "Model, Plate #, etc."})
    serial_number = StringField("Serial Number", validators=[DataRequired(), Length(max=100)],
                                render_kw={"placeholder": "Unique serial #"})
    submit        = SubmitField("Save")


# ---------------------------------------------------------------------------
# PM management form (admin use)
# ---------------------------------------------------------------------------
class ProjectManagerForm(FlaskForm):
    name   = StringField('PM Name', validators=[DataRequired(), Length(max=100)])
    submit = SubmitField('Add Project Manager')
