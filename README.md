# 🚆 RailOps Enterprise DBMS

### Smart Railway Operations & Management System

> A full-stack railway operations platform for managing **trains, stations, routes, schedules, employees, reports, and AWS-powered operational insights**.

<p align="center">

🚀 [Live Demo](https://rail-ops-enterprise-dbms.vercel.app/)

</p>

![Python](https://img.shields.io/badge/Python-3.x-3776AB?logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.x-black?logo=flask&logoColor=white)
![AWS Lambda](https://img.shields.io/badge/AWS-Lambda-FF9900?logo=awslambda&logoColor=white)
![AWS SAM](https://img.shields.io/badge/AWS-SAM-FF9900?logo=amazonaws&logoColor=white)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-7952B3?logo=bootstrap&logoColor=white)
![Vercel](https://img.shields.io/badge/Deployed-Vercel-black?logo=vercel&logoColor=white)

---

## 🚆 About

RailOps focuses on the **operational layer behind railway journeys**.

**Trains → Routes → Stations → Schedules → Platforms → Employees → Reports**

It provides a centralized web platform for railway administration, database management, scheduling, reporting, and operational analytics.

---

## ✨ Features

- 🚆 **Train Management** — CRUD, search, sorting & pagination
- 📍 **Station Management** — stations, codes, locations & platforms
- 🛤️ **Route Management** — railway connections & distances
- 🕐 **Schedule Management** — trains, routes, timings & platforms
- 👥 **Employee Management** — roles, departments & status
- 📊 **Reports** — PDF, Excel & CSV exports
- 📈 **Dashboard** — statistics, latest records & quick actions
- 🔐 **Admin Authentication** — protected administrative workflows
- 💡 **Operational Insights** — fleet, network & scheduling analytics

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
🧪 Run locally
cd aws
sam validate --lint
sam local invoke RailOpsStatsFunction --event events/stats-event.json
sam local start-api --port 3000

The Lambda processes a read-only operational snapshot and returns structured insights to the RailOps dashboard.

🏗️ Architecture
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
       └──────► ☁️ AWS Lambda
                    │
                    ▼
               💡 Insights
🛠️ Tech Stack
Layer	Technology
🐍 Backend	Python, Flask
🗄️ Database	SQLite / MySQL
🎨 Frontend	HTML, CSS, JavaScript, Bootstrap 5.3
☁️ AWS	Lambda, SAM CLI
📊 Reports	PDF, Excel, CSV
🚀 Deployment	Vercel
📸 Screenshots
🖥️ Dashboard

⚙️ Management Module

🚀 Run Locally
git clone https://github.com/ShambhaviCode/RailOps-Enterprise-DBMS-Hackathon.git
cd RailOps-Enterprise-DBMS-Hackathon

python -m venv .venv
.\.venv\Scripts\Activate.ps1

pip install -r requirements.txt
python run.py

Open http://127.0.0.1:5000

🔑 Demo Login
👤 Username: admin
🔐 Password: admin123
🏆 Hackathon

Built as a solo project for the WeMakeDevs × AWS First Commit Hackathon under the Build It direction.

🗄️ Database Engineering + 🐍 Full-Stack Development + ☁️ AWS Serverless + 📊 Operational Analytics

👩‍💻 Built By
Shambhavi M K

Solo Developer & Team Leader

💻 GitHub
💼 LinkedIn

<p align="center">
🚆 Connected Data. Smarter Operations. Better Railway Management.

⭐ Star the repository if you like RailOps!

</p>
📜 License

MIT License © Shambhavi
