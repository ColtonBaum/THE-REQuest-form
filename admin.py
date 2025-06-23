import csv
import io
from flask import (
    Blueprint, render_template, request as flask_req,
    redirect, url_for, flash, make_response
)
from flask import request
from models import db, Request, Job, Asset, RequestItem
from forms import JobForm, AssetForm

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


# -- Requests Routes ---------------------------------------------------------

@admin_bp.route("/requests")
def list_requests():
    all_reqs = (
        Request.query
               .order_by(Request.submitted_at.desc())
               .all()
    )
    jobs = (
        Job.query
           .filter_by(archived=False)
           .order_by(Job.start_date.desc())
           .all()
    )
    return render_template(
        "admin/requests_list.html",
        requests=all_reqs,
        jobs=jobs
    )


@admin_bp.route("/requests/<int:req_id>/delete", methods=["POST"])
def delete_request(req_id):
    req = Request.query.get_or_404(req_id)
    db.session.delete(req)
    db.session.commit()
    flash(f"Request #{req_id} deleted.", "danger")
    return redirect(url_for("admin.list_requests"))


@admin_bp.route("/requests/<int:req_id>/edit", methods=["GET", "POST"])
def edit_request(req_id):
    req = Request.query.get_or_404(req_id)
    if flask_req.method == "POST":
        # Update core fields
        req.employee_name = flask_req.form["employee_name"]
        req.job_name      = flask_req.form["job_name"]
        req.job_number    = flask_req.form["job_number"]
        req.need_by_date  = flask_req.form["need_by_date"]

        # Update or remove existing items
        for item in list(req.items):
            name = flask_req.form.get(f"item_name_{item.id}")
            qty  = flask_req.form.get(f"item_qty_{item.id}")
            if not name:
                # If name cleared, delete item
                req.items.remove(item)
                db.session.delete(item)
            else:
                item.item_name = name
                if qty and qty.isdigit():
                    item.quantity = int(qty)

        # Add new items
        new_names = flask_req.form.getlist("new_item_name")
        new_qtys  = flask_req.form.getlist("new_item_qty")
        for name, qty in zip(new_names, new_qtys):
            if name and qty.isdigit():
                req.items.append(RequestItem(item_name=name, quantity=int(qty)))

        db.session.commit()
        flash("Request updated successfully.", "success")
        return redirect(url_for("admin.list_requests"))

    return render_template("admin/edit_request.html", req=req)


@admin_bp.route("/requests/<int:req_id>")
def request_detail(req_id):
    req = Request.query.get_or_404(req_id)
    return render_template("admin/request_detail.html", req=req)


@admin_bp.route("/requests/<int:req_id>/assign", methods=["POST"])
def assign_request(req_id):
    req = Request.query.get_or_404(req_id)
    job_id = flask_req.form.get("job_id")
    req.job_id = int(job_id) if job_id else None
    db.session.commit()
    flash(f"Request #{req_id} assigned.", "success")
    return redirect(url_for("admin.list_requests"))


@admin_bp.route("/requests/<int:req_id>/fulfill", methods=["GET", "POST"])
def fulfill(req_id):
    req = Request.query.get_or_404(req_id)
    if flask_req.method == "POST":
        return redirect(url_for("admin.list_requests"))
    return render_template("admin/fulfill_request.html", request=req)


@admin_bp.route("/requests/export")
def export_csv():
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "Req ID", "Employee Name", "Job Name", "Job Number",
        "Need by Date", "Submitted At", "Status",
        "Item Name", "Quantity"
    ])
    for req in Request.query.order_by(Request.submitted_at):
        for item in req.items:
            writer.writerow([
                req.id,
                req.employee_name,
                req.job_name,
                req.job_number,
                req.need_by_date,
                req.submitted_at.strftime("%Y-%m-%d %H:%M:%S"),
                req.status,
                item.item_name,
                item.quantity,
            ])
    resp = make_response(output.getvalue())
    resp.headers["Content-Type"] = "text/csv"
    resp.headers["Content-Disposition"] = "attachment; filename=requests_export.csv"
    return resp


@admin_bp.route("/requests/<int:req_id>/status", methods=["POST"])
def update_status(req_id):
    req = Request.query.get_or_404(req_id)
    new = flask_req.form.get("status")
    if new in ["Not started", "In progress", "Complete"]:
        req.status = new
        db.session.commit()
        flash(f"Request #{req_id} set to “{new}”.", "success")
    return redirect(url_for("admin.list_requests"))


# -- Jobs Routes -------------------------------------------------------------

@admin_bp.route("/jobs")
def jobs_list():
    pm_tabs = [
        "Home",
        "Kaden Argyle", "Kade Evans", "Dan Lewis", "Jacob McNeil",
        "Tiffany Chastain", "Josh Walsh", "Tayson Scott",
        "Nate's Projects", "Other"
    ]
    jobs_by_pm = {
        "Home": (
            Job.query
               .filter_by(archived=False)
               .order_by(Job.start_date.desc())
               .all()
        )
    }
    for pm in pm_tabs[1:]:
        jobs_by_pm[pm] = (
            Job.query
               .filter_by(manager=pm, archived=False)
               .order_by(Job.start_date.desc())
               .all()
        )
    return render_template("admin/jobs_list.html", pm_tabs=pm_tabs, jobs_by_pm=jobs_by_pm)


@admin_bp.route("/jobs/new", methods=["GET", "POST"])
def new_job():
    pm_choices = [(pm, pm) for pm in [
        "Kaden Argyle", "Kade Evans", "Dan Lewis", "Jacob McNeil",
        "Tiffany Chastain", "Josh Walsh", "Tayson Scott",
        "Nate's Projects", "Other"
    ]]
    form = JobForm()
    form.manager.choices = pm_choices
    if form.validate_on_submit():
        job = Job(
            name       = form.name.data,
            number     = form.number.data,
            location   = form.location.data,
            start_date = form.start_date.data,
            end_date   = form.end_date.data,
            manager    = form.manager.data,
            budget     = form.budget.data,
            status     = "Not started"
        )
        db.session.add(job)
        db.session.commit()
        flash("New job created.", "success")
        return redirect(url_for("admin.jobs_list"))
    return render_template("admin/job_form.html", form=form, job=None)


@admin_bp.route("/jobs/<int:job_id>/edit", methods=["GET", "POST"])
def edit_job(job_id):
    job = Job.query.get_or_404(job_id)
    pm_choices = [(pm, pm) for pm in [
        "Kaden Argyle", "Kade Evans", "Dan Lewis", "Jacob McNeil",
        "Tiffany Chastain", "Josh Walsh", "Tayson Scott",
        "Nate's Projects", "Other"
    ]]
    form = JobForm(obj=job)
    form.manager.choices = pm_choices
    if form.validate_on_submit():
        form.populate_obj(job)
        db.session.commit()
        flash("Job updated.", "success")
        return redirect(url_for("admin.jobs_list"))
    return render_template("admin/job_form.html", form=form, job=job)


@admin_bp.route("/jobs/<int:job_id>/assign_manager", methods=["POST"])
def assign_manager(job_id):
    job = Job.query.get_or_404(job_id)
    job.manager = flask_req.form.get("manager")
    db.session.commit()
    flash(f"Job #{job_id} re-assigned to {job.manager}.", "success")
    return redirect(url_for("admin.jobs_list"))


@admin_bp.route("/jobs/<int:job_id>/archive", methods=["POST"])
def archive_job(job_id):
    job = Job.query.get_or_404(job_id)
    job.archived = True
    db.session.commit()
    flash("Job archived.", "warning")
    return redirect(url_for("admin.jobs_list"))


@admin_bp.route("/jobs/<int:job_id>/delete", methods=["POST"])
def delete_job(job_id):
    job = Job.query.get_or_404(job_id)
    db.session.delete(job)
    db.session.commit()
    flash(f"Job '{job.name}' deleted.", "danger")
    return redirect(url_for("admin.jobs_list"))


@admin_bp.route("/jobs/<int:job_id>")
def job_detail(job_id):
    job = Job.query.get_or_404(job_id)
    assigned_assets = Asset.query.filter_by(current_job_id=job_id).all()
    completed_reqs  = (
        Request.query
               .filter_by(job_id=job_id, status="Complete")
               .order_by(Request.submitted_at.desc())
               .all()
    )
    return render_template(
        "admin/job_detail.html",
        job=job,
        assigned_assets=assigned_assets,
        completed_reqs=completed_reqs
    )


@admin_bp.route("/jobs/<int:job_id>/requests")
def job_requests(job_id):
    job = Job.query.get_or_404(job_id)
    reqs = Request.query.filter_by(job_id=job_id).order_by(Request.submitted_at.desc()).all()
    return render_template("admin/job_requests.html", job=job, requests=reqs)


@admin_bp.route("/jobs/<int:job_id>/assets")
def job_assets(job_id):
    job = Job.query.get_or_404(job_id)
    assets = Asset.query.filter_by(current_job_id=job_id).all()
    return render_template("admin/job_assets.html", job=job, assets=assets)


# -- Assets Routes -----------------------------------------------------------

@admin_bp.route("/assets")
def assets_list():
    assets = Asset.query.all()
    jobs   = Job.query.filter_by(archived=False).order_by(Job.start_date.desc()).all()
    return render_template("admin/assets_list.html", assets=assets, jobs=jobs)


@admin_bp.route("/assets/new", methods=["GET", "POST"])
def assets_new():
    form = AssetForm()
    if form.validate_on_submit():
        new_asset = Asset(
            group         = form.group.data,
            type          = form.type.data,
            identifier    = form.identifier.data,
            serial_number = form.serial_number.data
        )
        db.session.add(new_asset)
        db.session.commit()
        flash(f"Asset “{new_asset.group} – {new_asset.type}” created.", "success")
        return redirect(url_for("admin.assets_list"))
    return render_template("admin/asset_form.html", form=form, asset=None)


@admin_bp.route("/assets/<int:asset_id>/edit", methods=["GET", "POST"])
def edit_asset(asset_id):
    asset = Asset.query.get_or_404(asset_id)
    form  = AssetForm(obj=asset)
    if form.validate_on_submit():
        asset.group         = form.group.data
        asset.type          = form.type.data
        asset.identifier    = form.identifier.data
        asset.serial_number = form.serial_number.data
        db.session.commit()
        flash("Asset updated.", "success")
        return redirect(url_for("admin.assets_list"))
    return render_template("admin/asset_form.html", form=form, asset=asset)


@admin_bp.route("/assets/<int:asset_id>/assign", methods=["POST"])
def assign_asset(asset_id):
    asset = Asset.query.get_or_404(asset_id)
    job_id = flask_req.form.get("job_id") or None
    asset.current_job_id = job_id
    db.session.commit()
    return redirect(flask_req.referrer)


@admin_bp.route("/assets/<int:asset_id>/unassign", methods=["POST"])
def unassign_asset(asset_id):
    asset = Asset.query.get_or_404(asset_id)
    asset.current_job_id = None
    db.session.commit()
    return redirect(flask_req.referrer)


# -- Reports Routes ---------------------------------------------------------

@admin_bp.route("/reports")
def reports():
    archived_jobs = (
        Job.query
           .filter_by(archived=True)
           .order_by(Job.start_date.desc())
           .all()
    )
    return render_template("admin/reports.html", jobs=archived_jobs)
