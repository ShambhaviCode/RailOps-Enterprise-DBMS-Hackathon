
# 🚆 RailOps Enterprise DBMS

### Smart Railway Operations & Management System

> A full-stack Railway Database Management System for **railway operations and administration** covering trains, stations, routes, schedules, employees, reports, and **AWS-powered Operational Insights**.

<p align="center">

🚀 [Live Demo](https://rail-ops-enterprise-dbms.vercel.app) •
💻 [GitHub](https://github.com/ShambhaviCode/RailOps-Enterprise-DBMS-Hackathon)

</p>

![Python](https://img.shields.io/badge/Python-3.x-3776AB?logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.x-black?logo=flask&logoColor=white)
![AWS Lambda](https://img.shields.io/badge/AWS-Lambda-FF9900?logo=awslambda&logoColor=white)
![AWS SAM](https://img.shields.io/badge/AWS-SAM-FF9900?logo=amazonaws&logoColor=white)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-7952B3?logo=bootstrap&logoColor=white)
![Vercel](https://img.shields.io/badge/Deployment-Vercel-black?logo=vercel&logoColor=white)

---

## 🚆 About

RailOps focuses on the **operational layer behind railway journeys**.

**Trains → Routes → Stations → Schedules → Platforms → Employees → Reports**

It provides a centralized web application for railway administration, database management, scheduling, reporting, and operational analytics.

---

## ✨ Features

- 🚆 **Train Management** — CRUD, search, sorting & pagination
- 📍 **Station Management** — station codes, locations & platforms
- 🛤️ **Route Management** — railway connections & distances
- 🕐 **Schedule Management** — trains, routes, timings & platforms
- 👥 **Employee Management** — roles, departments & status
- 📊 **Reports** — PDF, Excel & CSV exports
- 📈 **Dashboard** — statistics, latest records & quick actions
- 🔐 **Admin Authentication** — secure administrator login
- 💡 **Operational Insights** — fleet, network, scheduling & attention analysis

---

## ☁️ AWS Integration

### ⚡ `railops-stats`

RailOps includes an **AWS Lambda** operational-insights component built with **AWS SAM** and **Python 3.12**.

```text
🌐 RailOps Flask App
        │
        │ POST /stats
        ▼
☁️ AWS SAM CLI
        │
        ▼
⚡ AWS Lambda
   railops-stats
        │
        ▼
💡 Operational Insights
   ├── 🚆 Fleet Statistics
   ├── 🛤️ Network Statistics
   ├── 🕐 Scheduling Analysis
   └── ⚠️ Attention List
````

### 🧪 Run AWS Locally

```powershell
cd aws

sam validate --lint

sam local invoke RailOpsStatsFunction --event events/stats-event.json

sam local start-api --port 3000
```

The Lambda processes a **read-only operational snapshot** and returns structured insights to the RailOps dashboard.

---

## 🏗️ Architecture

```text
👤 Administrator
       │
       ▼
🌐 Bootstrap UI
       │
       ▼
🐍 Flask Application
       │
       ├──────► 🗄️ SQLite / MySQL
       │
       └──────► ☁️ AWS SAM
                    │
                    ▼
                 ⚡ Lambda
               railops-stats
                    │
                    ▼
               💡 Insights
```

---

## 🛠️ Tech Stack

| Layer         | Technology                           |
| ------------- | ------------------------------------ |
| 🐍 Backend    | Python, Flask, Flask-SQLAlchemy      |
| 🗄️ Database  | SQLite / MySQL                       |
| 🎨 Frontend   | HTML, CSS, JavaScript, Bootstrap 5.3 |
| ☁️ AWS        | Lambda, SAM CLI                      |
| 📊 Reports    | PDF, Excel, CSV                      |
| 🚀 Deployment | Vercel                               |

---

## 🗄️ Database Design

| Entity        | Purpose                                  |
| ------------- | ---------------------------------------- |
| 👤 `User`     | Administrator accounts                   |
| 🚆 `Train`    | Fleet master data                        |
| 📍 `Station`  | Railway network nodes                    |
| 🛤️ `Route`   | Railway network connections              |
| 🕐 `Schedule` | Train timetable and platform assignments |
| 👥 `Employee` | Workforce management                     |
| 📊 `Report`   | Report generation and audit data         |

---

## 📸 Screenshots

### 🖥️ Dashboard
<img width="1900" height="796" alt="image" src="https://github.com/user-attachments/assets/7b635a9f-9032-48df-bde4-4cd3cca86622" />

---

## 🚀 Run Locally

```powershell
git clone https://github.com/ShambhaviCode/RailOps-Enterprise-DBMS-Hackathon.git

cd RailOps-Enterprise-DBMS-Hackathon

python -m venv .venv

.\.venv\Scripts\Activate.ps1

pip install -r requirements.txt

python run.py
```

Run the tests:

```powershell
pip install pytest
python -m pytest
```


### 🔑 Demo Login

```text
👤 Username: admin
🔐 Password: admin123
```

---

## 🏆 Hackathon

Built as a **solo project for the WeMakeDevs × AWS First Commit Hackathon** under the **Build It** direction.

**🗄️ Database Engineering + 🐍 Full-Stack Development + ☁️ AWS Serverless + 📊 Operational Analytics**

---

## 👩‍💻 Built By

### Shambhavi M K

**Solo Developer & Team Leader**

💻 [GitHub](https://github.com/ShambhaviCode)

💼 [LinkedIn](https://www.linkedin.com/in/shambhavi-m-k-1b6677378)

---

<p align="center">

### 🚆 Connected Data. Smarter Operations. Better Railway Management.

⭐ Star the repository if you like RailOps!

</p>

---

## 📜 License

MIT License © Shambhavi


