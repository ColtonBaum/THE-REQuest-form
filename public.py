from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from models import db, Request, RequestItem
from forms import RequestForm

public_bp = Blueprint(
    "public",
    __name__,
    url_prefix=""
)

@public_bp.route("/", methods=["GET", "POST"])
@public_bp.route("/submit", methods=["GET", "POST"])
def make_request():
    form = RequestForm()
    print(f"▶️ METHOD: {request.method}")
    print(f"▶️ FORM DATA: {request.form}")

    if form.validate_on_submit():
        # Save request to the database, including notes
        req = Request(
            employee_name=form.employee_name.data,
            job_name=form.job_name.data,
            job_number=form.job_number.data,
            need_by_date=form.need_by_date.data,
            notes=form.notes.data
        )
        for item in form.items:
            req.items.append(RequestItem(
                item_name=item.item_name.data,
                quantity=item.quantity.data
            ))
        db.session.add(req)
        db.session.commit()

        # Emit SocketIO event to notify admin interface
        current_app.socketio.emit("new_request_submitted", {
            "employee_name": req.employee_name,
            "job_name": req.job_name,
            "job_number": req.job_number
        })

        # Prepare submitted data for confirmation page, including notes
        submitted_data = {
            'employee_name': form.employee_name.data,
            'job_name': form.job_name.data,
            'job_number': form.job_number.data,
            'need_by_date': form.need_by_date.data.strftime('%Y-%m-%d'),
            'notes': form.notes.data,
            'requested_items': [
                {'item_name': i.item_name.data, 'quantity': i.quantity.data}
                for i in form.items
            ]
        }

        return render_template("public/submitted.html", data=submitted_data)

    return render_template("public/request_form.html", form=form)

@public_bp.route("/submitted")
def submitted():
    # fallback if someone visits directly without data
    return redirect(url_for("public.make_request"))
