import csv
import io
import os
from datetime import datetime
from functools import wraps
from zoneinfo import ZoneInfo

from flask import (
    Flask,
    flash,
    make_response,
    redirect,
    render_template,
    request,
    send_file,
    session,
    url_for,
)
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash

from railops_stats_client import get_stats, stats_url

try:
    from openpyxl import Workbook
except ImportError:
    Workbook = None


db = SQLAlchemy()
APP_VERSION = "1.0.0"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IST = ZoneInfo("Asia/Kolkata")


def create_app():
    template_folder = "templates" if os.path.isdir(os.path.join(BASE_DIR, "templates")) else "."
    static_folder = "static" if os.path.isdir(os.path.join(BASE_DIR, "static")) else "."
    app = Flask(__name__, template_folder=template_folder, static_folder=static_folder)
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "railway-dbms-dev-key")

    if os.getenv("DB_ENGINE", "sqlite").lower() == "mysql":
        user = os.getenv("MYSQL_USER", "root")
        password = os.getenv("MYSQL_PASSWORD", "")
        host = os.getenv("MYSQL_HOST", "localhost")
        port = os.getenv("MYSQL_PORT", "3306")
        database = os.getenv("MYSQL_DATABASE", "railway_dbms")
        app.config["SQLALCHEMY_DATABASE_URI"] = (
            f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}"
        )
        app.config["DATABASE_LABEL"] = database
    else:
        if os.getenv("VERCEL"):
            db_path = "/tmp/railway_dbms.sqlite"
        else:
            db_path = os.path.join(app.instance_path, "railway_dbms.sqlite")
            os.makedirs(app.instance_path, exist_ok=True)
        app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"
        app.config["DATABASE_LABEL"] = "railway_dbms"

    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)
    register_routes(app)

    with app.app_context():
        db.create_all()
        seed_data()

    return app


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(120), nullable=False)
    user_type = db.Column(db.String(40), nullable=False, default="Admin")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Train(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    train_number = db.Column(db.String(30), unique=True, nullable=False)
    train_name = db.Column(db.String(120), nullable=False)
    source = db.Column(db.String(120), nullable=False)
    destination = db.Column(db.String(120), nullable=False)
    capacity = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Station(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    station_code = db.Column(db.String(20), unique=True, nullable=False)
    station_name = db.Column(db.String(120), nullable=False)
    city = db.Column(db.String(90), nullable=False)
    state = db.Column(db.String(90), nullable=False)
    platforms = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Route(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    route_code = db.Column(db.String(30), unique=True, nullable=False)
    route_name = db.Column(db.String(120), nullable=False)
    source_station = db.Column(db.String(120), nullable=False)
    destination_station = db.Column(db.String(120), nullable=False)
    distance_km = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Schedule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    train_id = db.Column(db.Integer, db.ForeignKey("train.id"), nullable=False)
    route_id = db.Column(db.Integer, db.ForeignKey("route.id"), nullable=False)
    arrival_time = db.Column(db.String(10), nullable=False)
    departure_time = db.Column(db.String(10), nullable=False)
    platform_number = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    train = db.relationship("Train")
    route = db.relationship("Route")


class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    employee_code = db.Column(db.String(30), unique=True, nullable=False)
    full_name = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(80), nullable=False)
    department = db.Column(db.String(80), nullable=False)
    phone = db.Column(db.String(30), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    status = db.Column(db.String(30), nullable=False, default="Active")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Report(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    report_type = db.Column(db.String(40), nullable=False)
    generated_by = db.Column(db.String(80), nullable=False)
    export_format = db.Column(db.String(20), nullable=False)
    generated_at = db.Column(db.DateTime, default=datetime.utcnow)


MODULES = {
    "trains": {
        "title": "Train Management",
        "singular": "Train",
        "icon": "fa-train",
        "model": Train,
        "columns": [
            ("train_number", "Train Number"),
            ("train_name", "Train Name"),
            ("source", "Source"),
            ("destination", "Destination"),
            ("capacity", "Capacity"),
        ],
        "fields": [
            ("train_number", "Train Number", "text", True),
            ("train_name", "Train Name", "text", True),
            ("source", "Source", "text", True),
            ("destination", "Destination", "text", True),
            ("capacity", "Capacity", "number", True),
        ],
    },
    "stations": {
        "title": "Station Management",
        "singular": "Station",
        "icon": "fa-location-dot",
        "model": Station,
        "columns": [
            ("station_code", "Station Code"),
            ("station_name", "Station Name"),
            ("city", "City"),
            ("state", "State"),
            ("platforms", "Platforms"),
        ],
        "fields": [
            ("station_code", "Station Code", "text", True),
            ("station_name", "Station Name", "text", True),
            ("city", "City", "text", True),
            ("state", "State", "text", True),
            ("platforms", "Platforms", "number", True),
        ],
    },
    "routes": {
        "title": "Route Management",
        "singular": "Route",
        "icon": "fa-route",
        "model": Route,
        "columns": [
            ("route_code", "Route Code"),
            ("route_name", "Route Name"),
            ("source_station", "Source Station"),
            ("destination_station", "Destination Station"),
            ("distance_km", "Distance KM"),
        ],
        "fields": [
            ("route_code", "Route Code", "text", True),
            ("route_name", "Route Name", "text", True),
            ("source_station", "Source Station", "text", True),
            ("destination_station", "Destination Station", "text", True),
            ("distance_km", "Distance KM", "number", True),
        ],
    },
    "employees": {
        "title": "Employee Management",
        "singular": "Employee",
        "icon": "fa-users-gear",
        "model": Employee,
        "columns": [
            ("employee_code", "Employee Code"),
            ("full_name", "Full Name"),
            ("role", "Role"),
            ("department", "Department"),
            ("phone", "Phone"),
            ("email", "Email"),
            ("status", "Status"),
        ],
        "fields": [
            ("employee_code", "Employee Code", "text", True),
            ("full_name", "Full Name", "text", True),
            ("role", "Role", "text", True),
            ("department", "Department", "text", True),
            ("phone", "Phone", "tel", True),
            ("email", "Email", "email", True),
            ("status", "Status", "select", True),
        ],
        "choices": {"status": ["Active", "On Leave", "Retired"]},
    },
}


SCHEDULE_CONFIG = {
    "title": "Schedule Management",
    "singular": "Schedule",
    "icon": "fa-calendar-days",
    "columns": [
        ("train_label", "Train"),
        ("route_label", "Route"),
        ("arrival_time", "Arrival Time"),
        ("departure_time", "Departure Time"),
        ("platform_number", "Platform"),
    ],
    "fields": [
        ("train_id", "Train", "select", True),
        ("route_id", "Route", "select", True),
        ("arrival_time", "Arrival Time", "time", True),
        ("departure_time", "Departure Time", "time", True),
        ("platform_number", "Platform Number", "text", True),
    ],
}


def seed_data():
    if not User.query.filter_by(username="admin").first():
        db.session.add(
            User(
                username="admin",
                password_hash=generate_password_hash("admin123"),
                full_name="Admin",
                user_type="Admin",
            )
        )
    if Train.query.count() == 0:
        db.session.add_all(
            [
                Train(train_number="12951", train_name="Mumbai Rajdhani", source="Mumbai Central", destination="New Delhi", capacity=1150),
                Train(train_number="12002", train_name="Shatabdi Express", source="New Delhi", destination="Bhopal", capacity=900),
                Train(train_number="12627", train_name="Karnataka Express", source="Bengaluru", destination="New Delhi", capacity=1250),
            ]
        )
    if Station.query.count() == 0:
        db.session.add_all(
            [
                Station(station_code="NDLS", station_name="New Delhi", city="Delhi", state="Delhi", platforms=16),
                Station(station_code="MMCT", station_name="Mumbai Central", city="Mumbai", state="Maharashtra", platforms=9),
                Station(station_code="SBC", station_name="KSR Bengaluru", city="Bengaluru", state="Karnataka", platforms=10),
            ]
        )
    if Route.query.count() == 0:
        db.session.add_all(
            [
                Route(route_code="R-NDLS-MMCT", route_name="Delhi Mumbai Corridor", source_station="New Delhi", destination_station="Mumbai Central", distance_km=1384),
                Route(route_code="R-NDLS-BPL", route_name="Delhi Bhopal Expressway", source_station="New Delhi", destination_station="Bhopal", distance_km=707),
            ]
        )
    if Employee.query.count() == 0:
        db.session.add_all(
            [
                Employee(employee_code="EMP001", full_name="Amit Sharma", role="Station Master", department="Operations", phone="9876543210", email="amit@railway.local"),
                Employee(employee_code="EMP002", full_name="Neha Singh", role="Route Controller", department="Traffic", phone="9876501234", email="neha@railway.local"),
            ]
        )
    db.session.commit()
    if Schedule.query.count() == 0 and Train.query.first() and Route.query.first():
        db.session.add(
            Schedule(
                train_id=Train.query.first().id,
                route_id=Route.query.first().id,
                arrival_time="08:15",
                departure_time="08:35",
                platform_number="4",
            )
        )
        db.session.commit()


def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        return func(*args, **kwargs)

    return wrapper


def current_user():
    if "user_id" not in session:
        return None
    return db.session.get(User, session["user_id"])


def coerce_value(raw, field_type):
    if field_type == "number":
        return int(raw)
    return raw.strip() if isinstance(raw, str) else raw


def validate_payload(config):
    payload = {}
    errors = []
    choices = config.get("choices", {})
    for name, label, field_type, required in config["fields"]:
        raw = request.form.get(name, "")
        if required and not str(raw).strip():
            errors.append(f"{label} is required.")
            continue
        if field_type == "number":
            try:
                value = coerce_value(raw, field_type)
                if value < 0:
                    errors.append(f"{label} cannot be negative.")
            except ValueError:
                errors.append(f"{label} must be a number.")
                continue
        else:
            value = coerce_value(raw, field_type)
        if name in choices and value not in choices[name]:
            errors.append(f"{label} has an invalid value.")
        payload[name] = value
    return payload, errors


def apply_query(model, config):
    query = model.query
    search = request.args.get("search", "").strip()
    if search:
        conditions = []
        for name, _label in config["columns"]:
            column = getattr(model, name, None)
            if column is not None:
                conditions.append(column.cast(db.String).ilike(f"%{search}%"))
        if conditions:
            query = query.filter(db.or_(*conditions))
    sort = request.args.get("sort", config["columns"][0][0])
    direction = request.args.get("direction", "asc")
    allowed = [name for name, _label in config["columns"] if hasattr(model, name)]
    sort = sort if sort in allowed else allowed[0]
    column = getattr(model, sort)
    query = query.order_by(column.desc() if direction == "desc" else column.asc())
    page = request.args.get("page", 1, type=int)
    return query.paginate(page=max(page, 1), per_page=8, error_out=False), search, sort, direction


def schedule_rows():
    return [
        {
            "id": item.id,
            "train_id": item.train_id,
            "route_id": item.route_id,
            "train_label": f"{item.train.train_number} - {item.train.train_name}",
            "route_label": item.route.route_name,
            "arrival_time": item.arrival_time,
            "departure_time": item.departure_time,
            "platform_number": item.platform_number,
        }
        for item in Schedule.query.order_by(Schedule.created_at.desc()).all()
    ]


def register_routes(app):
    @app.context_processor
    def inject_globals():
        return {
            "current_user": current_user(),
            "current_date": datetime.now(IST).strftime("%d %B %Y"),
            "app_version": APP_VERSION,
            "modules": MODULES,
        }

    @app.get("/")
    def index():
        return redirect(url_for("dashboard") if "user_id" in session else url_for("login"))

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            user = User.query.filter_by(username=request.form.get("username", "").strip()).first()
            if user and check_password_hash(user.password_hash, request.form.get("password", "")):
                session["user_id"] = user.id
                flash("Login successful. Welcome back.", "success")
                return redirect(url_for("dashboard"))
            flash("Invalid username or password.", "danger")
        return render_template("login.html")

    @app.get("/logout")
    @login_required
    def logout():
        session.clear()
        flash("You have been logged out.", "info")
        return redirect(url_for("login"))

    @app.get("/dashboard")
    @login_required
    def dashboard():
        counts = {
            "trains": Train.query.count(),
            "stations": Station.query.count(),
            "routes": Route.query.count(),
            "employees": Employee.query.count(),
        }
        latest = {
            "Trains": Train.query.order_by(Train.created_at.desc()).limit(5).all(),
            "Stations": Station.query.order_by(Station.created_at.desc()).limit(5).all(),
            "Routes": Route.query.order_by(Route.created_at.desc()).limit(5).all(),
            "Employees": Employee.query.order_by(Employee.created_at.desc()).limit(5).all(),
        }
        return render_template(
            "dashboard.html",
            counts=counts,
            latest=latest,
            db_status="Connected",
            db_name=app.config["DATABASE_LABEL"],
        )

    @app.get("/settings")
    @login_required
    def settings():
        return render_template("settings.html", db_name=app.config["DATABASE_LABEL"])

    @app.get("/insights")
    @login_required
    def insights():
        """Operational Insights: RailOps data -> railops-stats AWS Lambda (AWS SAM local) -> statistics."""
        snapshot = operations_snapshot()
        stats, source, error = get_stats(snapshot)
        return render_template("insights.html", stats=stats, source=source, error=error, stats_url=stats_url(), snapshot=snapshot)

    @app.get("/api/insights")
    @login_required
    def insights_api():
        stats, source, error = get_stats(operations_snapshot())
        return {"source": source, "error": error, "stats": stats}

    @app.route("/<module>")
    @login_required
    def module_list(module):
        if module not in MODULES:
            return redirect(url_for("dashboard"))
        config = MODULES[module]
        pagination, search, sort, direction = apply_query(config["model"], config)
        return render_template(
            "crud.html",
            module=module,
            config=config,
            rows=pagination.items,
            pagination=pagination,
            search=search,
            sort=sort,
            direction=direction,
        )

    @app.post("/<module>/create")
    @login_required
    def module_create(module):
        if module not in MODULES:
            return redirect(url_for("dashboard"))
        config = MODULES[module]
        payload, errors = validate_payload(config)
        if errors:
            for error in errors:
                flash(error, "danger")
        else:
            db.session.add(config["model"](**payload))
            try:
                db.session.commit()
                flash(f"{config['singular']} added successfully.", "success")
            except Exception as exc:
                db.session.rollback()
                flash(f"Unable to add {config['singular']}: {exc}", "danger")
        return redirect(url_for("module_list", module=module))

    @app.post("/<module>/<int:item_id>/update")
    @login_required
    def module_update(module, item_id):
        if module not in MODULES:
            return redirect(url_for("dashboard"))
        config = MODULES[module]
        item = db.session.get(config["model"], item_id)
        if not item:
            flash("Record not found.", "danger")
            return redirect(url_for("module_list", module=module))
        payload, errors = validate_payload(config)
        if errors:
            for error in errors:
                flash(error, "danger")
        else:
            for key, value in payload.items():
                setattr(item, key, value)
            try:
                db.session.commit()
                flash(f"{config['singular']} updated successfully.", "success")
            except Exception as exc:
                db.session.rollback()
                flash(f"Unable to update {config['singular']}: {exc}", "danger")
        return redirect(url_for("module_list", module=module))

    @app.post("/<module>/<int:item_id>/delete")
    @login_required
    def module_delete(module, item_id):
        if module not in MODULES:
            return redirect(url_for("dashboard"))
        config = MODULES[module]
        item = db.session.get(config["model"], item_id)
        if item:
            db.session.delete(item)
            try:
                db.session.commit()
                flash(f"{config['singular']} deleted successfully.", "warning")
            except Exception as exc:
                db.session.rollback()
                flash(f"Unable to delete {config['singular']}: {exc}", "danger")
        return redirect(url_for("module_list", module=module))

    @app.get("/schedules")
    @login_required
    def schedules():
        rows = schedule_rows()
        search = request.args.get("search", "").strip().lower()
        if search:
            rows = [row for row in rows if search in " ".join(str(v).lower() for v in row.values())]
        sort = request.args.get("sort", "arrival_time")
        direction = request.args.get("direction", "asc")
        if sort in [name for name, _label in SCHEDULE_CONFIG["columns"]]:
            rows.sort(key=lambda row: str(row.get(sort, "")), reverse=direction == "desc")
        page = request.args.get("page", 1, type=int)
        total = len(rows)
        start = (max(page, 1) - 1) * 8
        page_rows = rows[start:start + 8]
        pages = max((total + 7) // 8, 1)
        return render_template(
            "schedules.html",
            config=SCHEDULE_CONFIG,
            rows=page_rows,
            trains=Train.query.order_by(Train.train_number).all(),
            routes=Route.query.order_by(Route.route_name).all(),
            page=max(page, 1),
            pages=pages,
            search=search,
            sort=sort,
            direction=direction,
        )

    @app.post("/schedules/create")
    @login_required
    def schedule_create():
        payload, errors = validate_payload(SCHEDULE_CONFIG)
        if errors:
            for error in errors:
                flash(error, "danger")
        else:
            db.session.add(Schedule(**payload))
            db.session.commit()
            flash("Schedule added successfully.", "success")
        return redirect(url_for("schedules"))

    @app.post("/schedules/<int:item_id>/update")
    @login_required
    def schedule_update(item_id):
        item = db.session.get(Schedule, item_id)
        payload, errors = validate_payload(SCHEDULE_CONFIG)
        if item and not errors:
            for key, value in payload.items():
                setattr(item, key, value)
            db.session.commit()
            flash("Schedule updated successfully.", "success")
        else:
            for error in errors or ["Schedule not found."]:
                flash(error, "danger")
        return redirect(url_for("schedules"))

    @app.post("/schedules/<int:item_id>/delete")
    @login_required
    def schedule_delete(item_id):
        item = db.session.get(Schedule, item_id)
        if item:
            db.session.delete(item)
            db.session.commit()
            flash("Schedule deleted successfully.", "warning")
        return redirect(url_for("schedules"))

    @app.route("/reports", methods=["GET", "POST"])
    @login_required
    def reports():
        if request.method == "POST":
            report_type = request.form["report_type"]
            export_format = request.form["export_format"]
            db.session.add(
                Report(
                    report_type=report_type,
                    generated_by=current_user().username,
                    export_format=export_format.upper(),
                )
            )
            db.session.commit()
            return redirect(url_for("export_report", report_type=report_type, export_format=export_format))
        return render_template(
            "reports.html",
            reports=Report.query.order_by(Report.generated_at.desc()).limit(20).all(),
        )

    @app.get("/reports/export/<report_type>/<export_format>")
    @login_required
    def export_report(report_type, export_format):
        headers, rows = report_dataset(report_type)
        filename = f"{report_type}_report.{export_format}"
        if export_format == "csv":
            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerow(headers)
            writer.writerows([csv_safe(value) for value in row] for row in rows)
            response = make_response(output.getvalue())
            response.headers["Content-Disposition"] = f"attachment; filename={filename}"
            response.headers["Content-Type"] = "text/csv"
            return response
        if export_format == "xlsx":
            if Workbook is None:
                flash("Excel export requires openpyxl.", "danger")
                return redirect(url_for("reports"))
            workbook = Workbook()
            sheet = workbook.active
            sheet.title = report_type.title()
            sheet.append(headers)
            for row in rows:
                sheet.append(row)
                # openpyxl turns any string starting with "=" into a live
                # formula; store user-entered values as plain text instead.
                for cell in sheet[sheet.max_row]:
                    if cell.data_type == "f":
                        cell.data_type = "s"
            stream = io.BytesIO()
            workbook.save(stream)
            stream.seek(0)
            return send_file(stream, as_attachment=True, download_name=filename, mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        if export_format == "pdf":
            stream = build_simple_pdf(f"{report_type.title()} Report", headers, rows)
            stream.seek(0)
            return send_file(stream, as_attachment=True, download_name=filename, mimetype="application/pdf")
        return redirect(url_for("reports"))


def operations_snapshot():
    """Read-only snapshot of RailOps data sent to the railops-stats Lambda (no contact details)."""
    return {
        "trains": [{"number": t.train_number, "name": t.train_name, "source": t.source, "destination": t.destination, "capacity": t.capacity} for t in Train.query.order_by(Train.train_number).all()],
        "stations": [{"code": s.station_code, "name": s.station_name, "city": s.city, "state": s.state, "platforms": s.platforms} for s in Station.query.order_by(Station.station_code).all()],
        "routes": [{"code": r.route_code, "name": r.route_name, "source": r.source_station, "destination": r.destination_station, "distance_km": r.distance_km} for r in Route.query.order_by(Route.route_code).all()],
        "schedules": [{"train": f"{sc.train.train_number} {sc.train.train_name}", "route": sc.route.route_name, "arrival": sc.arrival_time, "departure": sc.departure_time, "platform": sc.platform_number} for sc in Schedule.query.all()],
        "employees": [{"code": e.employee_code, "name": e.full_name, "role": e.role, "department": e.department, "status": e.status} for e in Employee.query.order_by(Employee.employee_code).all()],
    }


def report_dataset(report_type):
    datasets = {
        "train": (["Number", "Name", "Source", "Destination", "Capacity"], [[t.train_number, t.train_name, t.source, t.destination, t.capacity] for t in Train.query.all()]),
        "station": (["Code", "Name", "City", "State", "Platforms"], [[s.station_code, s.station_name, s.city, s.state, s.platforms] for s in Station.query.all()]),
        "route": (["Code", "Name", "Source", "Destination", "Distance KM"], [[r.route_code, r.route_name, r.source_station, r.destination_station, r.distance_km] for r in Route.query.all()]),
        "employee": (["Code", "Name", "Role", "Department", "Phone", "Email", "Status"], [[e.employee_code, e.full_name, e.role, e.department, e.phone, e.email, e.status] for e in Employee.query.all()]),
    }
    return datasets.get(report_type, datasets["train"])


FORMULA_PREFIXES = ("=", "+", "-", "@", "\t", "\r")


def csv_safe(value):
    """Stop spreadsheet apps evaluating user-entered text as a formula.

    Prefixes text that starts with a formula trigger with a single quote,
    as recommended by OWASP for CSV injection. Numbers are left as-is.
    """
    if isinstance(value, str) and value.startswith(FORMULA_PREFIXES):
        return "'" + value
    return value


def pdf_escape(value):
    return str(value).replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def build_simple_pdf(title, headers, rows):
    lines = [title, "", " | ".join(headers)]
    lines.extend(" | ".join(str(value) for value in row) for row in rows)
    y = 760
    content_lines = ["BT", "/F1 16 Tf", f"50 {y} Td", f"({pdf_escape(lines[0])}) Tj"]
    content_lines.extend(["/F1 9 Tf"])
    for line in lines[2:]:
        y -= 18
        content_lines.append(f"50 {y} Td")
        content_lines.append(f"({pdf_escape(line[:130])}) Tj")
        if y < 60:
            break
    content_lines.append("ET")
    content = "\n".join(content_lines).encode("latin-1", "replace")
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
        b"<< /Length " + str(len(content)).encode() + b" >>\nstream\n" + content + b"\nendstream",
    ]
    output = io.BytesIO()
    output.write(b"%PDF-1.4\n")
    offsets = [0]
    for index, obj in enumerate(objects, start=1):
        offsets.append(output.tell())
        output.write(f"{index} 0 obj\n".encode())
        output.write(obj)
        output.write(b"\nendobj\n")
    xref = output.tell()
    output.write(f"xref\n0 {len(objects) + 1}\n0000000000 65535 f \n".encode())
    for offset in offsets[1:]:
        output.write(f"{offset:010d} 00000 n \n".encode())
    output.write(f"trailer << /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF".encode())
    output.seek(0)
    return output


app = create_app()


if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)
