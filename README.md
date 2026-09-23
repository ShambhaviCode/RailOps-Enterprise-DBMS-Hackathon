# RailOps Enterprise DBMS: Smart Railway Operations & Management System

A full-stack Railway Database Management System for **railway operations and administration** - trains, stations, routes, schedules, employees and reports - with an **Operational Insights** feature implemented as an AWS Lambda function and run locally through the **AWS SAM CLI**.

Submitted to the **WeMakeDevs x AWS First Commit** hackathon (Build It direction).

| | |
|---|---|
| **Live demo** | https://rail-ops-enterprise-dbms.vercel.app |
| **Demo login** | `admin` / `admin123` (demo credentials only - public sample account, not a production secret) |
| **Stack** | Python Flask, Flask-SQLAlchemy, SQLite/MySQL, Bootstrap 5, AWS SAM CLI, AWS Lambda (Python 3.12) |
| **Author** | Shambhavi ([@ShambhaviCode](https://github.com/ShambhaviCode)) |

> **RailOps is not a ticket-booking site.** Passenger platforms (IRCTC-style apps) sell seats to travellers. RailOps is the *back-office* system: it manages the operational and administrative data that a railway needs to run - the fleet, the network, the timetable, the workforce and management reporting.

---

## Table of contents

1. [The problem](#the-problem)
2. [What RailOps does](#what-railops-does)
3. [Target users](#target-users)
4. [Key features](#key-features)
5. [Architecture](#architecture)
6. [Technology stack](#technology-stack)
7. [Database design](#database-design)
8. [AWS SAM / Lambda implementation](#aws-sam--lambda-implementation)
9. [Local development](#local-development)
10. [Demo instructions](#demo-instructions)
11. [Deployment](#deployment)
12. [Project structure](#project-structure)
13. [Screenshots](#screenshots)
14. [Future scope](#future-scope)
15. [Author](#author)

---

## The problem

Railway operational data is usually scattered across spreadsheets, paper registers and disconnected tools:

- Train, station and route master data drifts out of sync (a train's destination that no longer matches any station record, routes that nobody scheduled).
- Timetable changes are made without validation, so platform clashes and impossible times slip through.
- Staff records live in yet another system.
- Management reports are assembled by hand, and nobody has a quick answer to "what needs attention today?"

## What RailOps does

RailOps Enterprise DBMS gives railway administrators **one centralized, validated web application** to:

- manage **trains, stations, routes, schedules and employees** with full CRUD, search, sorting, pagination and server-side validation;
- **generate and export reports** (PDF, Excel, CSV) for every module;
- see live **dashboard statistics**, latest records and an IST clock;
- get **Operational Insights** - fleet, network and scheduling statistics plus a prioritised *needs-attention* list - computed by an AWS Lambda function (`railops-stats`) that runs through the AWS SAM CLI.

## Target users

| User | What they use RailOps for |
|---|---|
| Railway operations administrators | Maintain master data for trains, stations and routes |
| Timetable / traffic controllers | Assign trains to routes, arrival/departure times and platforms |
| HR / station management | Keep employee roles, departments and status current |
| Management | Export reports and review the Operational Insights health score and attention list |

## Key features

- Secure administrator login with hashed passwords and Flask session handling
- Enterprise-style dashboard: hero banner, system information, live IST clock, module statistics, quick actions, latest records
- Train, station, route, schedule and employee management (create, edit, delete) through modal forms
- Search, column sorting, pagination and server-side validation on every list
- Schedule management linking trains to routes with platform assignment
- Report generation for trains, stations, routes and employees with **PDF, Excel (xlsx) and CSV** export
- **Operational Insights** page backed by the `railops-stats` AWS Lambda function (fleet capacity, network length, scheduling coverage, attention list, health score)
- Toast notifications, responsive Bootstrap 5 layout, Font Awesome icons
- SQLite for local/demo use, MySQL for production, Vercel serverless deployment

## Architecture

```text
                          +--------------------------------------------+
   Administrator  ----->  |  RailOps Flask application  (app.py)        |
   (browser)              |  - auth & sessions   - CRUD modules         |
                          |  - dashboard         - reports & exports    |
                          |  - /insights         - Jinja2 templates     |
                          +----------+-------------------+-------------+
                                     |                   |
                        SQLAlchemy   |                   |  POST /stats  (JSON snapshot: trains, stations,
                                     v                   |               routes, schedules, employees)
                          +------------------+           v
                          | SQLite (demo) /  |   +-----------------------------------------------+
                          | MySQL (prod)     |   |  AWS SAM CLI  -  sam local start-api  (:3000)   |
                          +------------------+   |  API Gateway emulation                         |
                                                 |        |                                       |
                                                 |        v                                       |
                                                 |  AWS Lambda  railops-stats  (python3.12)       |
                                                 |  official runtime image                        |
                                                 |  public.ecr.aws/lambda/python:3.12             |
                                                 |  defined in aws/template.yaml                  |
                                                 +-----------------------------------------------+
                                                          |
                                                          v
                                   statistics + attention list + health score -> /insights page
```

- The Flask application is the product; the relational database is the system of record.
- The AWS layer is a **read-only** consumer: it receives a snapshot of operational data and returns analysis. It never writes to the database and never receives employee contact details.
- If the SAM local API is not running (for example on the Vercel demo), `/insights` runs the **same Lambda handler module in-process** and labels the result as an in-process fallback, so the application never breaks.

## Technology stack

| Layer | Technology |
|---|---|
| Backend | Python 3, Flask 3, Flask-SQLAlchemy, Werkzeug security |
| Database | SQLite (local/demo), MySQL via PyMySQL (production), `schema.sql` |
| Frontend | HTML5, CSS3, JavaScript, Bootstrap 5.3, Font Awesome 6 |
| Reports | CSV (stdlib), Excel via openpyxl, PDF generated natively |
| AWS | AWS SAM CLI, AWS Lambda (Python 3.12 runtime), SAM template (`AWS::Serverless::Function` + API event) |
| Deployment | Vercel (Python serverless functions), Gunicorn `Procfile` for traditional hosts |

## Database design

Entities (SQLAlchemy models in `app.py`, DDL in `schema.sql`):

| Entity | Key fields | Purpose |
|---|---|---|
| `User` | username (unique), password_hash, full_name, user_type | Administrator accounts |
| `Train` | train_number (unique), train_name, source, destination, capacity | Fleet master data |
| `Station` | station_code (unique), station_name, city, state, platforms | Network nodes |
| `Route` | route_code (unique), route_name, source_station, destination_station, distance_km | Network edges |
| `Schedule` | train_id -> Train, route_id -> Route, arrival_time, departure_time, platform_number | Timetable |
| `Employee` | employee_code (unique), full_name, role, department, phone, email, status | Workforce |
| `Report` | report_type, generated_by, export_format, generated_at | Report audit trail |

Relationships: `Schedule` has foreign keys to `Train` and `Route` (many schedules per train / per route). All tables carry `created_at` timestamps. Validation rules (required fields, non-negative numbers, allowed status values) are enforced server-side before any write.

## AWS SAM / Lambda implementation

### What is actually implemented (and verified)

| Item | Status |
|---|---|
| AWS SAM template `aws/template.yaml` defining Lambda `railops-stats` (`AWS::Serverless::Function`, runtime `python3.12`, API event `POST /stats`) | Implemented, passes `cfn-lint` / `sam validate --lint` |
| Lambda handler `aws/functions/stats/app.py` (pure Python, no dependencies) | Implemented |
| `sam local invoke RailOpsStatsFunction --event events/stats-event.json` | Verified: function executed inside the official Lambda Python 3.12 runtime container (`START/END/REPORT RequestId`, HTTP 200 body) |
| `sam local start-api --port 3000` (SAM-emulated API Gateway + Lambda) | Verified: Flask `/insights` calls `POST http://127.0.0.1:3000/stats` and shows "Executed in AWS Lambda runtime" |
| Recorded API Gateway event with real RailOps data `aws/events/stats-event.json` | Included |
| Demo script `aws/demo.ps1` | Included |

### What is *not* claimed

The application is deployed on **Vercel**, not on AWS. No AWS cloud resources (Lambda, API Gateway, DynamoDB, S3, Cognito, Bedrock, EventBridge, Step Functions, Amplify, App Runner) are deployed. LocalStack, Strands Agents, Cedar and OpenSearch are not used. The Lambda workflow was validated **locally** with the official AWS Lambda runtime through the SAM CLI; the same template deploys unchanged with `sam deploy` once an AWS account is available.

### How the Lambda is used

1. `app.py` builds a read-only snapshot (`operations_snapshot()`): trains, stations, routes, schedules, employees (code, name, role, department, status - **no phone/email**).
2. `railops_stats_client.py` POSTs the snapshot to `RAILOPS_STATS_URL` (default `http://127.0.0.1:3000/stats`, served by `sam local start-api`).
3. `railops-stats` computes:
   - **fleet**: total and average seat capacity, largest train
   - **network**: total route km, longest route, total platforms, states covered
   - **scheduling**: routes/trains with and without schedules, busiest platform
   - **attention list**: trains whose source/destination matches no station, duplicate train numbers, routes without schedules, unscheduled trains, stations with fewer than 5 platforms, employees not active, schedules whose departure precedes arrival
   - **health score** (0-100) derived from the attention list
4. `templates/insights.html` renders the response, shows the raw Lambda JSON, and states whether it came from the SAM-hosted Lambda or the in-process fallback.

## Local development

Prerequisites: Python 3.10+ (developed on 3.14), pip. For the AWS part: Docker Desktop and `pip install aws-sam-cli`.

```powershell
git clone https://github.com/ShambhaviCode/RailOps-Enterprise-DBMS-Hackathon.git
cd RailOps-Enterprise-DBMS-Hackathon
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python run.py            # http://127.0.0.1:5000  -> login admin / admin123 (demo credentials)
```

SQLite is used automatically (`instance/railway_dbms.sqlite`). To use MySQL:

```powershell
mysql -u root -p < schema.sql
$env:DB_ENGINE="mysql"; $env:MYSQL_HOST="localhost"; $env:MYSQL_PORT="3306"
$env:MYSQL_DATABASE="railway_dbms"; $env:MYSQL_USER="root"; $env:MYSQL_PASSWORD="your_password"
python run.py
```

Environment variables (see `.env.example`): `SECRET_KEY`, `DB_ENGINE`, `MYSQL_*`, optional `RAILOPS_STATS_URL`. Never commit a real `.env`.

### Run the AWS Lambda through SAM

```powershell
cd aws
sam validate --lint
sam local invoke RailOpsStatsFunction --event events/stats-event.json   # one-shot run in the Lambda runtime container
sam local start-api --port 3000                                          # emulated API Gateway -> POST /stats
```

Then open http://127.0.0.1:5000/insights - the badge reads **"Executed in AWS Lambda runtime via sam local start-api"**.

## Demo instructions

30-second AWS demo sequence (`aws/demo.ps1` runs steps 2-3):

1. Open the dashboard (`/dashboard`) - trains, stations, routes, schedules, employees, reports.
2. Terminal: `sam local invoke RailOpsStatsFunction --event events/stats-event.json` - watch the `START / END / REPORT RequestId` lines and the JSON result (`health_score`, `attention`).
3. Terminal: `sam local start-api --port 3000`.
4. Click **Operational Insights (Lambda)** on the dashboard - green badge, health score, attention list (e.g. "Shatabdi Express destination 'Bhopal' has no matching station record", "Delhi Bhopal Expressway has no schedule assigned").
5. Explain: the function is defined in `aws/template.yaml`; SAM CLI runs it locally in the real Lambda runtime; the identical template is what `sam deploy` would ship to AWS.

Without SAM (e.g. on the live Vercel demo), `/insights` still works and clearly says it used the in-process fallback.

## Deployment

- **Vercel** (current live deployment): `vercel.json` routes static assets and sends everything else to `api/index.py`, which imports the Flask app. Set `SECRET_KEY` (and the MySQL variables for a persistent database; the SQLite fallback on Vercel is ephemeral).
- **Traditional host**: `Procfile` runs `gunicorn app:app`.
- **AWS (future)**: `cd aws && sam deploy --guided` deploys `railops-stats` behind API Gateway; then set `RAILOPS_STATS_URL` on the web app.

## Project structure

```text
RailOps-Enterprise-DBMS-Hackathon/
├── app.py                      # Flask app: models, CRUD modules, schedules, reports, insights
├── railops_stats_client.py     # Calls the railops-stats Lambda via SAM local (in-process fallback)
├── run.py                      # Local dev server
├── schema.sql                  # MySQL DDL
├── requirements.txt
├── aws/                        # AWS SAM application
│   ├── template.yaml           # Lambda railops-stats (python3.12) + API event POST /stats
│   ├── samconfig.toml
│   ├── demo.ps1                # 30-second demo script
│   ├── events/stats-event.json # Recorded API Gateway event with real RailOps data
│   └── functions/stats/app.py  # Lambda handler
├── templates/                  # Jinja2 templates
│   ├── base.html  dashboard.html  login.html  crud.html
│   ├── schedules.html  reports.html  insights.html  settings.html
├── static/                     # css/, js/, img/
├── public/                     # Static assets served by Vercel
├── api/index.py                # Vercel entry point
├── vercel.json  Procfile  .vercelignore  .python-version
├── .env.example                # Environment variable template (no secrets)
├── .github/FUNDING.yml
├── LICENSE                     # MIT
└── README.md
```

Root-level copies of the HTML/CSS/JS files mirror `templates/`, `static/` and `public/` for the Vercel static routing setup.

## Screenshots

<img width="1392" height="776" alt="RailOps dashboard" src="https://github.com/user-attachments/assets/80a22fb6-a6fd-47fe-ac0d-67d0501fc9f7" />
<img width="1887" height="867" alt="RailOps management module" src="https://github.com/user-attachments/assets/dbfc3f43-f6b4-428b-9cb9-245c63f36274" />

## Future scope

- Deploy `railops-stats` to AWS with `sam deploy` and point the live app at the API Gateway URL
- Persist the audit trail of record changes and report exports (e.g. DynamoDB) once cloud resources are available
- Role-based access (viewer / controller / administrator) with explicit authorization policies
- Full-text search across trains, stations, routes and employees
- Real-time train running status and delay tracking
- Multi-language UI and accessibility improvements

## Author

**Shambhavi** - [github.com/ShambhaviCode](https://github.com/ShambhaviCode)

Licensed under the MIT License (see `LICENSE`).

*Repository note: this repository was published for the hackathon submission from the working RailOps project ([original repository](https://github.com/ShambhaviCode/RailOps-Enterprise-DBMS)) with its real commit history preserved.*
