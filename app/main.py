from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user

from . import db
from .models import Project, TestCase, Defect
from .permissions import admin_required

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
@login_required
def index():
    """Dashboard showing recent projects."""
    projects = Project.query.order_by(Project.created_at.desc()).limit(5).all()
    return render_template("index.html", user=current_user, projects=projects)


# ---------- PROJECT ROUTES ----------

@main_bp.route("/projects")
@login_required
def list_projects():
    projects = Project.query.order_by(Project.created_at.desc()).all()
    return render_template("projects/list.html", projects=projects)


@main_bp.route("/projects/new", methods=["GET", "POST"])
@login_required
def create_project():
    if request.method == "POST":
        name = request.form.get("name")
        description = request.form.get("description")

        if not name or len(name.strip()) < 3:
            flash("Project name must be at least 3 characters.", "danger")
            return redirect(url_for("main.create_project"))

        project = Project(
            name=name.strip(),
            description=description,
            created_by=current_user.id,
        )
        db.session.add(project)
        db.session.commit()
        flash("Project created.", "success")
        return redirect(url_for("main.list_projects"))

    return render_template("projects/form.html", action="Create")


@main_bp.route("/projects/<int:project_id>/edit", methods=["GET", "POST"])
@login_required
def edit_project(project_id):
    project = Project.query.get_or_404(project_id)

    if request.method == "POST":
        name = request.form.get("name")
        description = request.form.get("description")

        if not name or len(name.strip()) < 3:
            flash("Project name must be at least 3 characters.", "danger")
            return redirect(url_for("main.edit_project", project_id=project.id))

        project.name = name.strip()
        project.description = description
        db.session.commit()
        flash("Project updated.", "success")
        return redirect(url_for("main.list_projects"))

    return render_template("projects/form.html", action="Edit", project=project)


@main_bp.route("/projects/<int:project_id>/delete", methods=["POST"])
@login_required
@admin_required
def delete_project(project_id):
    """Only admins can delete projects."""
    project = Project.query.get_or_404(project_id)
    db.session.delete(project)
    db.session.commit()
    flash("Project deleted.", "success")
    return redirect(url_for("main.list_projects"))


# ---------- TEST CASE ROUTES ----------

@main_bp.route("/projects/<int:project_id>/testcases")
@login_required
def list_testcases(project_id):
    project = Project.query.get_or_404(project_id)
    testcases = (
        TestCase.query.filter_by(project_id=project.id)
        .order_by(TestCase.id.desc())
        .all()
    )
    return render_template(
        "testcases/list.html",
        project=project,
        testcases=testcases,
    )


@main_bp.route("/projects/<int:project_id>/testcases/new", methods=["GET", "POST"])
@login_required
def create_testcase(project_id):
    project = Project.query.get_or_404(project_id)

    if request.method == "POST":
        title = request.form.get("title")
        description = request.form.get("description")
        priority = request.form.get("priority")

        if not title or len(title.strip()) < 5:
            flash("Test case title must be at least 5 characters.", "danger")
            return redirect(url_for("main.create_testcase", project_id=project.id))

        testcase = TestCase(
            title=title.strip(),
            description=description,
            priority=priority,
            project_id=project.id,
            created_by=current_user.id,
        )
        db.session.add(testcase)
        db.session.commit()
        flash("Test case created.", "success")
        return redirect(url_for("main.list_testcases", project_id=project.id))

    return render_template(
        "testcases/form.html",
        action="Create",
        project=project,
    )


@main_bp.route("/testcases/<int:testcase_id>/edit", methods=["GET", "POST"])
@login_required
def edit_testcase(testcase_id):
    testcase = TestCase.query.get_or_404(testcase_id)
    project = testcase.project  # relationship from models

    if request.method == "POST":
        title = request.form.get("title")
        description = request.form.get("description")
        priority = request.form.get("priority")
        status = request.form.get("status")

        if not title or len(title.strip()) < 5:
            flash("Test case title must be at least 5 characters.", "danger")
            return redirect(url_for("main.edit_testcase", testcase_id=testcase.id))

        testcase.title = title.strip()
        testcase.description = description
        testcase.priority = priority
        testcase.status = status
        db.session.commit()
        flash("Test case updated.", "success")
        return redirect(url_for("main.list_testcases", project_id=project.id))

    return render_template(
        "testcases/form.html",
        action="Edit",
        project=project,
        testcase=testcase,
    )


@main_bp.route("/testcases/<int:testcase_id>/delete", methods=["POST"])
@login_required
def delete_testcase(testcase_id):
    testcase = TestCase.query.get_or_404(testcase_id)
    project_id = testcase.project_id

    # Only admins or creator can delete
    if current_user.role != "admin" and current_user.id != testcase.created_by:
        flash("You do not have permission to delete this test case.", "danger")
        return redirect(url_for("main.list_testcases", project_id=project_id))

    db.session.delete(testcase)
    db.session.commit()
    flash("Test case deleted.", "success")
    return redirect(url_for("main.list_testcases", project_id=project_id))


# ---------- DEFECT ROUTES ----------

@main_bp.route("/projects/<int:project_id>/defects")
@login_required
def list_defects(project_id):
    project = Project.query.get_or_404(project_id)
    defects = (
        Defect.query.filter_by(project_id=project.id)
        .order_by(Defect.created_at.desc())
        .all()
    )
    return render_template(
        "defects/list.html",
        project=project,
        defects=defects,
    )


@main_bp.route("/projects/<int:project_id>/defects/new", methods=["GET", "POST"])
@login_required
def create_defect(project_id):
    project = Project.query.get_or_404(project_id)
    testcases = TestCase.query.filter_by(project_id=project.id).all()

    if request.method == "POST":
        title = request.form.get("title")
        description = request.form.get("description")
        severity = request.form.get("severity")
        test_case_id = request.form.get("test_case_id") or None

        if not title or len(title.strip()) < 5:
            flash("Defect title must be at least 5 characters.", "danger")
            return redirect(url_for("main.create_defect", project_id=project.id))

        defect = Defect(
            title=title.strip(),
            description=description,
            severity=severity,
            project_id=project.id,
            test_case_id=int(test_case_id) if test_case_id else None,
            created_by=current_user.id,
        )
        db.session.add(defect)
        db.session.commit()
        flash("Defect logged.", "success")
        return redirect(url_for("main.list_defects", project_id=project.id))

    return render_template(
        "defects/form.html",
        action="Create",
        project=project,
        testcases=testcases,
    )


@main_bp.route("/defects/<int:defect_id>/edit", methods=["GET", "POST"])
@login_required
def edit_defect(defect_id):
    defect = Defect.query.get_or_404(defect_id)
    project = defect.project
    testcases = TestCase.query.filter_by(project_id=project.id).all()

    if request.method == "POST":
        title = request.form.get("title")
        description = request.form.get("description")
        severity = request.form.get("severity")
        status = request.form.get("status")
        test_case_id = request.form.get("test_case_id") or None

        if not title or len(title.strip()) < 5:
            flash("Defect title must be at least 5 characters.", "danger")
            return redirect(url_for("main.edit_defect", defect_id=defect.id))

        # Business rule: defect should be fixed before it can be closed
        if status == "closed" and defect.status != "fixed":
            flash(
                "Defect must be marked as 'fixed' before it can be closed.",
                "warning",
            )
            return redirect(url_for("main.edit_defect", defect_id=defect.id))

        defect.title = title.strip()
        defect.description = description
        defect.severity = severity
        defect.status = status
        defect.test_case_id = int(test_case_id) if test_case_id else None

        db.session.commit()
        flash("Defect updated.", "success")
        return redirect(url_for("main.list_defects", project_id=project.id))

    return render_template(
        "defects/form.html",
        action="Edit",
        project=project,
        defect=defect,
        testcases=testcases,
    )


@main_bp.route("/defects/<int:defect_id>/delete", methods=["POST"])
@login_required
def delete_defect(defect_id):
    defect = Defect.query.get_or_404(defect_id)
    project_id = defect.project_id

    # Only admins or creator can delete defects
    if current_user.role != "admin" and current_user.id != defect.created_by:
        flash("You do not have permission to delete this defect.", "danger")
        return redirect(url_for("main.list_defects", project_id=project_id))

    db.session.delete(defect)
    db.session.commit()
    flash("Defect deleted.", "success")
    return redirect(url_for("main.list_defects", project_id=project_id))
