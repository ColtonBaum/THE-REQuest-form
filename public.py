import os
import uuid
from flask import (
    Blueprint, render_template, redirect, url_for, flash,
    request, current_app
)
from werkzeug.utils import secure_filename
from models import db, Request, RequestItem, RequestFile
from forms import RequestForm
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime

public_bp = Blueprint("public", __name__, url_prefix="")

ALLOWED_EXTENSIONS = {
    'png', 'jpg', 'jpeg', 'gif', 'heic', 'webp',
    'xlsx', 'xls', 'csv',
    'pdf', 'doc', 'docx',
}

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB per file
MAX_FILES = 10


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def _clean_int(val):
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


def _save_upload(file_obj):
    if not file_obj or not file_obj.filename:
        return None

    original = file_obj.filename
    if not allowed_file(original):
        return None

    file_obj.seek(0, os.SEEK_END)
    size = file_obj.tell()
    file_obj.seek(0)

    if size > MAX_FILE_SIZE:
        return None

    ext = original.rsplit('.', 1)[1].lower()
    stored_name = f"{uuid.uuid4().hex}.{ext}"

    upload_dir = current_app.config.get('UPLOAD_FOLDER', 'uploads')
    os.makedirs(upload_dir, exist_ok=True)

    filepath = os.path.join(upload_dir, stored_name)
    file_obj.save(filepath)

    return (stored_name, secure_filename(original), file_obj.content_type, size)


@public_bp.route("/", methods=["GET", "POST"])
@public_bp.route("/submit", methods=["GET", "POST"])
def make_request():
    form = RequestForm()

    if form.validate_on_submit():
        req = Request(
            employee_name=form.employee_name.data,
            job_name=form.job_name.data,
            job_number=form.job_number.data,
            need_by_date=form.need_by_date.data,
            notes=form.notes.data,
            status="Not started",
        )

        saved_any = False
        for item in form.items:
            name = (item.item_name.data or "").strip()
            qty  = _clean_int(item.quantity.data)

            if not name and qty is None:
                continue

            if qty is None:
                flash(f"Quantity for '{name or 'item'}' must be numbers only.", "warning")
                return render_template("public/request_form.html", form=form)

            req.items.append(RequestItem(item_name=name or None, quantity=qty))
            saved_any = True

        if not saved_any:
            flash("Please add at least one item with a numeric quantity.", "warning")
            return render_template("public/request_form.html", form=form)

        # Handle file uploads
        uploaded_files = request.files.getlist("attachments")
        file_count = 0
        for f in uploaded_files:
            if file_count >= MAX_FILES:
                flash(f"Maximum {MAX_FILES} files allowed. Extra files were skipped.", "warning")
                break
            result = _save_upload(f)
            if result:
                stored_name, orig_name, ctype, size = result
                req.files.append(RequestFile(
                    filename=stored_name,
                    original_filename=orig_name,
                    content_type=ctype,
                    file_size=size,
                ))
                file_count += 1

        try:
            db.session.add(req)
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            current_app.logger.exception("Failed to save request")
            flash("There was a problem saving your request. Please try again.", "danger")
            return render_template("public/request_form.html", form=form)

        current_app.socketio.emit("new_request_submitted", {
            "employee_name": req.employee_name,
            "job_name": req.job_name,
            "job_number": req.job_number,
        })

        submitted_data = {
            "employee_name": req.employee_name,
            "job_name": req.job_name,
            "job_number": req.job_number,
            "need_by_date": req.need_by_date.strftime("%Y-%m-%d") if req.need_by_date else "",
            "notes": req.notes,
            "requested_items": [
                {"item_name": it.item_name or "", "quantity": it.quantity}
                for it in req.items
            ],
            "file_count": file_count,
        }
        return render_template("public/submitted.html", data=submitted_data)

    return render_template("public/request_form.html", form=form)


@public_bp.route("/submitted")
def submitted():
    return redirect(url_for("public.make_request"))
