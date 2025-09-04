from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from models import db, Request, RequestItem
from forms import RequestForm
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime, date

public_bp = Blueprint("public", __name__, url_prefix="")

def _clean_int(val):
    """Return int from any input containing digits; None if empty/invalid."""
    if val is None:
        return None
    s = str(val).strip()
    digits = "".join(ch for ch in s if ch.isdigit())
    if digits == "":
        return None
    try:
        return int(digits)
    except ValueError:
        return None

def _to_yyyy_mm_dd(value):
    """
    Accepts either a WTForms date (datetime.date), a string 'YYYY-MM-DD',
    or something else. Returns a validated 'YYYY-MM-DD' string or None.
    """
    if isinstance(value, date):
        return value.strftime("%Y-%m-%d")
    if isinstance(value, str):
        s = value.strip()
        try:
            # validate format
            datetime.strptime(s, "%Y-%m-%d")
            return s
        except ValueError:
            return None
    return None

@public_bp.route("/", methods=["GET", "POST"])
@public_bp.route("/submit", methods=["GET", "POST"])
def make_request():
    form = RequestForm()
    print(f"▶️ METHOD: {request.method}")
    print(f"▶️ FORM DATA: {request.form}")

    if form.validate_on_submit():
        # Normalize need_by_date to a YYYY-MM-DD string (since the column is String)
        nbd_str = _to_yyyy_mm_dd(form.need_by_date.data)
        if not nbd_str:
            flash("Please select a valid date.", "warning")
            return render_template("public/request_form.html", form=form)

        req = Request(
            employee_name=form.employee_name.data,
            job_name=form.job_name.data,
            job_number=form.job_number.data,
            need_by_date=nbd_str,   # store as string
            notes=form.notes.data,
        )

        saved_any = False
        for item in form.items:
            name = (item.item_name.data or "").strip()
            qty  = _clean_int(item.quantity.data)

            # Skip truly blank rows
            if not name and qty is None:
                continue

            # If they typed something but qty didn't parse, fail fast with a message
            if qty is None:
                flash(f"Quantity for '{name or 'item'}' must be numbers only.", "warning")
                return render_template("public/request_form.html", form=form)

            req.items.append(RequestItem(item_name=name or None, quantity=qty))
            saved_any = True

        if not saved_any:
            flash("Please add at least one item with a numeric quantity.", "warning")
            return render_template("public/request_form.html", form=form)

        try:
            db.session.add(req)
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            current_app.logger.exception("Failed to save request")
            flash("There was a problem saving your request. Please try again.", "danger")
            return render_template("public/request_form.html", form=form)

        # Notify admin UI
        current_app.socketio.emit("new_request_submitted", {
            "employee_name": req.employee_name,
            "job_name": req.job_name,
            "job_number": req.job_number
        })

        # Build confirmation payload using the normalized string date
        submitted_data = {
            "employee_name": req.employee_name,
            "job_name": req.job_name,
            "job_number": req.job_number,
            "need_by_date": nbd_str,
            "notes": req.notes,
            "requested_items": [
                {"item_name": it.item_name or "", "quantity": it.quantity}
                for it in req.items
            ],
        }
        return render_template("public/submitted.html", data=submitted_data)

    return render_template("public/request_form.html", form=form)

@public_bp.route("/submitted")
def submitted():
    return redirect(url_for("public.make_request"))
