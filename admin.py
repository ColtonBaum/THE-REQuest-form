import csv
import io

from flask import (
    Blueprint, render_template, request as flask_req,
    redirect, url_for, flash, make_response, current_app, jsonify
)
from sqlalchemy import and_, not_, case, or_
from sqlalchemy.orm import joinedload
from datetime import datetime
from models import db, Request, Job, Asset, RequestItem, ProjectManager, AssetAssignment, STATUS_SORT_ORDER
from forms import JobForm, AssetForm, RequestForm, ProjectManagerForm

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------
def _pm_choices():
    pms = (
        ProjectManager.query
        .filter_by(is_active=True)
        .order_by(ProjectManager.display_order, ProjectManager.name)
        .all()
    )
    return [(pm.id, pm.name) for pm in pms]


# ===========================================================================
# REQUESTS
# ===========================================================================

@admin_bp.route("/requests")
def list_requests():
    status_order = case(
        STATUS_SORT_ORDER,
        value=Request.status,
        else_=1,
    )

    all_reqs = (
        Request.query
        .filter(
            not_(
                and_(
                    Request.status == "Complete",
                    Request.job_id.isnot(None),
                )
            )
        )
        .order_by(status_order, Request.submitted_at.desc())
        .all()
    )

    jobs = (
        Job.query
        .filter_by(archived=False)
        .order_by(Job.start_date.desc())
        .all()
    )
    return render_template("admin/requests_list.html",
                           requests=all_reqs,
                           jobs=jobs)


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

    if flask_req.method == "GET":
        form = RequestForm(obj=req)
        form.items.entries = []
        for item in req.items:
            form.items.append_entry({
                "item_name": item.item_name,
                "quantity":  item.quantity,
            })
    else:
        form = RequestForm(flask_req.form)

    if form.validate_on_submit():
        req.employee_name = form.employee_name.data
        req.job_name      = form.job_name.data
        req.job_number    = form.job_number.data
        req.need_by_date  = form.need_by_date.data
        req.notes         = form.notes.data

        req.items.clear()
        for entry in form.items.data:
            name = (entry.get("item_name") or "").strip()
            qty  = (entry.get("quantity") or "").strip()
            if not name and not qty:
                continue
            req.items.append(RequestItem(item_name=name or None, quantity=qty or None))

        db.session.commit()
        flash("Request updated successfully.", "success")
        return redirect(url_for("admin.list_requests"))

    jobs = Job.query.order_by(Job.start_date.desc()).all()
    return render_template("admin/edit_request.html",
                           form=form, req=req, jobs=jobs)


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
    assets = Asset.query.order_by(Asset.group, Asset.identifier).all()

    if flask_req.method == "POST":
        # Save equipment assignment
        equipment = flask_req.form.get("equipment_assigned", "").strip()
        req.equipment_assigned = equipment if equipment else None
        req.status = "Complete"
        db.session.commit()
        flash(f"Request #{req_id} fulfilled.", "success")
        return redirect(url_for("admin.list_requests"))

    return render_template("admin/fulfill_request.html",
                           req=req, assets=assets)


@admin_bp.route("/requests/<int:req_id>/assign_equipment", methods=["POST"])
def assign_equipment(req_id):
    """Quick endpoint to assign equipment to a request without full fulfill."""
    req = Request.query.get_or_404(req_id)
    equipment = flask_req.form.get("equipment_assigned", "").strip()
    req.equipment_assigned = equipment if equipment else None
    db.session.commit()
    flash(f"Equipment updated for Request #{req_id}.", "success")
    return redirect(flask_req.referrer or url_for("admin.list_requests"))


@admin_bp.route("/requests/new", methods=["GET", "POST"])
def new_request():
    form = RequestForm()
    if form.validate_on_submit():
        req = Request(
            employee_name=form.employee_name.data,
            job_name=form.job_name.data,
            job_number=form.job_number.data,
            need_by_date=form.need_by_date.data,
            notes=form.notes.data,
            status="Not started",
            submitted_at=datetime.utcnow(),
        )
        db.session.add(req)
        db.session.flush()

        for entry in form.items.data:
            name = (entry.get("item_name") or "").strip()
            qty  = (entry.get("quantity") or "").strip()
            if not name and not qty:
                continue
            db.session.add(RequestItem(
                request_id=req.id,
                item_name=name or None,
                quantity=qty or None,
            ))

        db.session.commit()
        flash("Request created.", "success")
        return redirect(url_for("admin.list_requests"))

    return render_template("request_form.html", form=form)


@admin_bp.route("/requests/export")
def export_csv():
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "Req ID", "Employee Name", "Job Name", "Job Number",
        "Need by Date", "Submitted At", "Status", "Notes",
        "Equipment Assigned", "Item Name", "Quantity"
    ])
    for r in Request.query.order_by(Request.submitted_at):
        for item in r.items:
            writer.writerow([
                r.id,
                r.employee_name,
                r.job_name,
                r.job_number,
                r.need_by_date.strftime("%Y-%m-%d") if r.need_by_date else "",
                r.submitted_at.strftime("%Y-%m-%d %H:%M:%S"),
                r.status,
                r.notes,
                r.equipment_assigned or "",
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
        flash(f"Request #{req_id} set to \u201c{new}\u201d.", "success")
    return redirect(url_for("admin.list_requests"))


# ===========================================================================
# JOBS — Restructured: PM list → click into PM → see their jobs
# ===========================================================================

@admin_bp.route("/jobs")
def jobs_list():
    """Main jobs page: shows list of PMs to click into."""
    pms = (
        ProjectManager.query
        .filter_by(is_active=True)
        .order_by(ProjectManager.display_order, ProjectManager.name)
        .all()
    )

    # Count active jobs per PM for the cards
    pm_data = []
    for pm in pms:
        active_count = (
            Job.query
            .filter_by(manager_id=pm.id, archived=False)
            .count()
        )
        pm_data.append({
            "pm": pm,
            "active_jobs": active_count,
        })

    # Equipment search
    search_query = flask_req.args.get("q", "").strip()
    search_results = []
    if search_query:
        search_results = (
            Asset.query
            .options(joinedload(Asset.current_job))
            .filter(
                or_(
                    Asset.serial_number.ilike(f"%{search_query}%"),
                    Asset.identifier.ilike(f"%{search_query}%"),
                    Asset.group.ilike(f"%{search_query}%"),
                )
            )
            .order_by(Asset.group, Asset.identifier)
            .all()
        )

    return render_template("admin/jobs_list.html",
                           pm_data=pm_data,
                           search_query=search_query,
                           search_results=search_results)


@admin_bp.route("/jobs/pm/<int:pm_id>")
def pm_jobs(pm_id):
    """View all jobs for a specific PM."""
    pm = ProjectManager.query.get_or_404(pm_id)
    active_jobs = (
        Job.query
        .filter_by(manager_id=pm.id, archived=False)
        .order_by(Job.start_date.desc())
        .all()
    )
    archived_jobs = (
        Job.query
        .filter_by(manager_id=pm.id, archived=True)
        .order_by(Job.start_date.desc())
        .all()
    )
    return render_template("admin/pm_jobs.html",
                           pm=pm,
                           active_jobs=active_jobs,
                           archived_jobs=archived_jobs)


@admin_bp.route("/jobs/new", methods=["GET", "POST"])
def new_job():
    form = JobForm()
    form.manager.choices = _pm_choices()

    # Pre-select PM if coming from a PM's page
    preselect_pm = flask_req.args.get("pm_id")
    if preselect_pm and flask_req.method == "GET":
        form.manager.data = int(preselect_pm)

    if form.validate_on_submit():
        pm = ProjectManager.query.get(form.manager.data)
        job = Job(
            name=form.name.data,
            number=form.number.data,
            start_date=form.start_date.data,
            manager_id=pm.id,
            manager=pm.name,
            status="Not started"
        )
        db.session.add(job)
        db.session.commit()
        flash("New job created.", "success")
        return redirect(url_for("admin.pm_jobs", pm_id=pm.id))

    return render_template("admin/job_form.html", form=form, job=None)


@admin_bp.route("/jobs/<int:job_id>/edit", methods=["GET", "POST"])
def edit_job(job_id):
    job = Job.query.get_or_404(job_id)
    form = JobForm(obj=job)
    form.manager.choices = _pm_choices()

    if flask_req.method == "GET" and job.manager_id:
        form.manager.data = job.manager_id

    if form.validate_on_submit():
        pm = ProjectManager.query.get(form.manager.data)
        job.name       = form.name.data
        job.number     = form.number.data
        job.start_date = form.start_date.data
        job.manager_id = pm.id
        job.manager    = pm.name
        db.session.commit()
        flash("Job updated.", "success")
        return redirect(url_for("admin.pm_jobs", pm_id=pm.id))

    return render_template("admin/job_form.html", form=form, job=job)


@admin_bp.route("/jobs/<int:job_id>/assign_manager", methods=["POST"])
def assign_manager(job_id):
    job = Job.query.get_or_404(job_id)
    pm_id = flask_req.form.get("manager_id")
    if pm_id:
        pm = ProjectManager.query.get(int(pm_id))
        if pm:
            job.manager_id = pm.id
            job.manager = pm.name
            db.session.commit()
            flash(f"Job #{job_id} re-assigned to {pm.name}.", "success")
    return redirect(url_for("admin.jobs_list"))


@admin_bp.route("/jobs/<int:job_id>/archive", methods=["POST"])
def archive_job(job_id):
    job = Job.query.get_or_404(job_id)
    job.archived = True
    db.session.commit()
    flash("Job archived.", "warning")
    return redirect(flask_req.referrer or url_for("admin.jobs_list"))


@admin_bp.route("/jobs/<int:job_id>/delete", methods=["POST"])
def delete_job(job_id):
    job = Job.query.get_or_404(job_id)
    pm_id = job.manager_id
    db.session.delete(job)
    db.session.commit()
    flash(f"Job '{job.name}' deleted.", "danger")
    if pm_id:
        return redirect(url_for("admin.pm_jobs", pm_id=pm_id))
    return redirect(url_for("admin.jobs_list"))


@admin_bp.route("/jobs/<int:job_id>")
def job_detail(job_id):
    job = Job.query.get_or_404(job_id)
    assigned_assets = Asset.query.filter_by(current_job_id=job_id).all()

    # All requests for this job (not just completed)
    job_requests = (
        Request.query
        .filter_by(job_id=job_id)
        .order_by(Request.submitted_at.desc())
        .all()
    )

    return render_template("admin/job_detail.html",
                           job=job,
                           assigned_assets=assigned_assets,
                           job_requests=job_requests)


# ===========================================================================
# EQUIPMENT SEARCH API (for AJAX autocomplete in fulfill form)
# ===========================================================================

@admin_bp.route("/api/equipment/search")
def api_equipment_search():
    """JSON endpoint for equipment search (used by fulfill form autocomplete)."""
    q = flask_req.args.get("q", "").strip()
    if not q or len(q) < 2:
        return jsonify([])

    results = (
        Asset.query
        .options(joinedload(Asset.current_job))
        .filter(
            or_(
                Asset.serial_number.ilike(f"%{q}%"),
                Asset.identifier.ilike(f"%{q}%"),
                Asset.group.ilike(f"%{q}%"),
            )
        )
        .limit(15)
        .all()
    )

    return jsonify([
        {
            "id": a.id,
            "group": a.group,
            "identifier": a.identifier,
            "serial_number": a.serial_number,
            "current_job": a.current_job.name if a.current_job else "Unassigned",
            "label": f"{a.group} - {a.identifier} (SN: {a.serial_number})",
        }
        for a in results
    ])


# ===========================================================================
# PROJECT MANAGER MANAGEMENT
# ===========================================================================

@admin_bp.route("/pms")
def pm_list():
    pms = ProjectManager.query.order_by(ProjectManager.display_order, ProjectManager.name).all()
    form = ProjectManagerForm()
    return render_template("admin/pm_list.html", pms=pms, form=form)


@admin_bp.route("/pms/add", methods=["POST"])
def pm_add():
    form = ProjectManagerForm()
    if form.validate_on_submit():
        max_order = db.session.query(db.func.max(ProjectManager.display_order)).scalar() or 0
        pm = ProjectManager(
            name=form.name.data.strip(),
            is_active=True,
            display_order=max_order + 1,
        )
        db.session.add(pm)
        db.session.commit()
        flash(f"Added PM: {pm.name}", "success")
    return redirect(url_for("admin.pm_list"))


@admin_bp.route("/pms/<int:pm_id>/deactivate", methods=["POST"])
def pm_deactivate(pm_id):
    pm = ProjectManager.query.get_or_404(pm_id)
    pm.is_active = False
    db.session.commit()
    flash(f"{pm.name} deactivated.", "warning")
    return redirect(url_for("admin.pm_list"))


@admin_bp.route("/pms/<int:pm_id>/activate", methods=["POST"])
def pm_activate(pm_id):
    pm = ProjectManager.query.get_or_404(pm_id)
    pm.is_active = True
    db.session.commit()
    flash(f"{pm.name} reactivated.", "success")
    return redirect(url_for("admin.pm_list"))


@admin_bp.route("/pms/<int:pm_id>/delete", methods=["POST"])
def pm_delete(pm_id):
    pm = ProjectManager.query.get_or_404(pm_id)
    if pm.jobs.count() > 0:
        flash(f"Can't delete {pm.name} — they have jobs assigned. Deactivate instead.", "danger")
    else:
        db.session.delete(pm)
        db.session.commit()
        flash(f"{pm.name} deleted.", "danger")
    return redirect(url_for("admin.pm_list"))


# ===========================================================================
# ASSETS (kept temporarily — will be removed in later phase)
# ===========================================================================

@admin_bp.route("/assets")
def assets_list():
    jobs = Job.query.filter_by(archived=False).order_by(Job.start_date.desc()).all()
    assets = Asset.query.options(joinedload(Asset.current_job)).all()
    shop_job = next((j for j in jobs if j.name.lower() == "shop"), None)

    if shop_job:
        on_deck = [a for a in assets if a.current_job_id == shop_job.id]
        others  = [a for a in assets if a.current_job_id != shop_job.id]
    else:
        on_deck = []
        others  = assets

    return render_template("admin/assets_list.html",
                           on_deck=on_deck, others=others, jobs=jobs)


@admin_bp.route("/assets/new", methods=["GET", "POST"])
def assets_new():
    form = AssetForm()
    if form.validate_on_submit():
        new_asset = Asset(
            type=form.group.data, group=form.group.data,
            identifier=form.identifier.data, serial_number=form.serial_number.data
        )
        db.session.add(new_asset)
        db.session.commit()
        flash(f"Asset \u201c{new_asset.group} \u2013 {new_asset.identifier}\u201d created.", "success")
        return redirect(url_for("admin.assets_list"))
    return render_template("admin/asset_form.html", form=form, asset=None)


@admin_bp.route("/assets/<int:asset_id>/edit", methods=["GET", "POST"])
def edit_asset(asset_id):
    asset = Asset.query.get_or_404(asset_id)
    form  = AssetForm(obj=asset)
    if form.validate_on_submit():
        asset.type          = form.group.data
        asset.group         = form.group.data
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
    for child in asset.children:
        child.current_job_id = job_id
    db.session.commit()
    return redirect(flask_req.referrer)


@admin_bp.route("/assets/<int:asset_id>/unassign", methods=["POST"])
def unassign_asset(asset_id):
    asset = Asset.query.get_or_404(asset_id)
    asset.current_job_id = None
    db.session.commit()
    return redirect(flask_req.referrer)


# ===========================================================================
# REPORTS
# ===========================================================================

@admin_bp.route("/reports")
def reports():
    archived_jobs = (
        Job.query.filter_by(archived=True)
        .order_by(Job.start_date.desc())
        .all()
    )
    return render_template("admin/reports.html", jobs=archived_jobs)
