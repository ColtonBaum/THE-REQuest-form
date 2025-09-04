from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from models import db, Request, RequestItem
from forms import RequestForm
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime, date

public_bp = Blueprint("public", __name__, url_prefix="")

def _clean_int(val):
    """
    Return an int made from the digits in `val` (e.g., "50'", "2ea" -> 50, 2).
    Returns None if no digits are present.
    """
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

def _parse_need_by(val):
    """
    Normalize the need_by_date from the form to a `date` object.
    Accepts date, datetime, or 'YYYY-MM-DD' string. Returns None if invalid/empty.
    """
    if isinstance(val, date) and not isinstance(val, datetime):
        return val
    if isinstance(val, datetime):
        return val.date()
    if isinstance(val, str):
        s = val.strip()
        if not s:
            return None
        try:
            return datetime.strptime(s, "%Y-%m-%d").date()
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
        need_by = _parse_need_by(form.need_by_date.data)
        if need_by is None:
            flash("Please provide a valid Need By Date.", "warning")
            return render_template("public/request_form.html", form=form)

        req = Request(
            employee_name=form.employee_name.data,
            job_name=form.job_name.data,
            job_number=form.job_number.data,
            need_by_date=need_by,  # ✅ date object for DB
            notes=form.notes.data,
        )

        saved_any = False

        for idx, item in enumerate(form.items, start=1):
            name_raw = item.item_name.data or ""
            name = name_raw.strip()
            qty_raw = item.quantity.data
            qty = _clean_int(qty_raw)

            # Skip truly blank rows
            if not name and qty is None:
                continue

            if qty is None:
                display_name = name if name else "item"
                flash(f"Row {idx}: Quantity for '{display_name}' must be numbers only.", "warning")
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

        submitted_data = {
            "employee_name": req.employee_name,
            "job_name": req.job_name,
            "job_number": req.job_number,
            "need_by_date": req.need_by_date.strftime("%Y-%m-%d"),  # ✅ safe; it's a date
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
