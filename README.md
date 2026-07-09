# 🏥 PAAI — Patient Advocacy Alliance India
### Production-Ready Healthcare Advocacy Platform

---

## 📋 Table of Contents
1. [Project Overview](#overview)
2. [Tech Stack](#tech-stack)
3. [Project Structure](#structure)
4. [Quick Start](#quick-start)
5. [Environment Setup](#environment)
6. [Database Setup](#database)
7. [Running the App](#running)
8. [Admin Access](#admin)
9. [API Reference](#api)
10. [Deployment (Replit)](#replit)
11. [Deployment (Production)](#production)
12. [Features](#features)

---

## Overview

PAAI is a national-level healthcare advocacy and patient support platform that connects:
- Patient advocacy groups
- NGOs and foundations
- Healthcare support organizations
- Caregivers and families
- Survivor communities

---

## Tech Stack

| Layer       | Technology                        |
|-------------|-----------------------------------|
| Frontend    | HTML5, CSS3, Bootstrap 5, JS (ES6)|
| Backend     | Flask 3.0, Flask Blueprints       |
| Database    | PostgreSQL + SQLAlchemy ORM       |
| Auth        | Flask-Login, Flask-Bcrypt         |
| Forms       | Flask-WTF (CSRF protection)       |
| Migrations  | Flask-Migrate (Alembic)           |
| AI Chatbot  | OpenAI GPT-3.5 + Rule-based fallback |
| Email       | Flask-Mail (SMTP)                 |
| Security    | CSRF, bcrypt hashing, bleach sanitization |

---

## Project Structure

```
paai_project/
│
├── main.py                     # Entry point
├── config.py                   # Dev/Prod configuration
├── seed.py                     # Database seeder
├── requirements.txt
├── .env.example                # Copy to .env
│
├── app/
│   ├── __init__.py             # App factory
│   ├── extensions.py           # Flask extensions
│   │
│   ├── models/
│   │   └── __init__.py         # All SQLAlchemy models
│   │
│   ├── routes/
│   │   ├── public.py           # Public pages
│   │   ├── auth.py             # Login/Register
│   │   ├── dashboard.py        # User dashboard
│   │   ├── admin.py            # Admin CMS
│   │   └── api.py              # REST API (chatbot, newsletter)
│   │
│   ├── forms/
│   │   └── __init__.py         # All WTForms
│   │
│   ├── templates/
│   │   ├── base.html           # Master layout
│   │   ├── public/             # Public pages
│   │   ├── auth/               # Login/Register
│   │   ├── dashboard/          # User dashboard
│   │   ├── admin/              # Admin panel
│   │   └── errors/             # 404, 403, 500
│   │
│   ├── static/
│   │   ├── css/
│   │   │   └── main.css        # Global styles
│   │   ├── js/
│   │   │   ├── main.js         # Global JS
│   │   │   └── chatbot.js      # Chatbot logic
│   │   └── uploads/            # User-uploaded files
│   │
│   └── utils/
│       └── errors.py           # Error handlers
│
└── migrations/                 # Alembic migration files
```

---

## Quick Start

### Prerequisites
- Python 3.10+
- PostgreSQL 14+
- pip

### 1. Clone & Setup

```bash
git clone <repo-url>
cd paai_project

# Create virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Environment Configuration

```bash
cp .env.example .env
# Edit .env with your values (DATABASE_URL, SECRET_KEY, etc.)
```

---

## Database Setup

### Create PostgreSQL Database

```bash
# Connect to PostgreSQL
psql -U postgres

# Run these SQL commands:
CREATE USER paai_user WITH PASSWORD 'paai_pass';
CREATE DATABASE paai_db OWNER paai_user;
GRANT ALL PRIVILEGES ON DATABASE paai_db TO paai_user;
\q
```

### Run Migrations

```bash
flask db init          # First time only
flask db migrate -m "Initial migration"
flask db upgrade
```

### Seed Sample Data

```bash
python seed.py
```

This creates:
- Admin account: `admin@paai.org.in` / `Admin@PAAI2024!`
- 3 sample users (password: `User@1234!`)
- Sample news posts, events, resources, FAQs

---

## Running the App

```bash
# Development
flask run
# or
python main.py

# Production
gunicorn -w 4 -b 0.0.0.0:5000 main:app
```

App runs at: http://localhost:5000

---

## Admin Access

1. Navigate to `/auth/admin/login`
2. Login: `admin@paai.org.in` / `Admin@PAAI2024!`
3. Access full CMS at `/admin/`

### Admin capabilities:
- ✅ Approve/reject membership applications
- ✅ Add/edit/delete news posts
- ✅ Manage events
- ✅ Upload/manage resources
- ✅ View & respond to contact messages
- ✅ Manage chatbot FAQs
- ✅ User management & activation

---

## API Reference

### POST `/api/chat`
AI chatbot endpoint.
```json
Request:  { "message": "How do I join PAAI?", "session_id": "optional-uuid" }
Response: { "reply": "...", "session_id": "uuid" }
```

### POST `/api/newsletter/subscribe`
Newsletter signup.
```json
Request:  { "email": "user@example.com" }
Response: { "status": "subscribed", "email": "user@example.com" }
```

### GET `/api/stats`
Platform statistics.
```json
Response: { "members": 2400, "approved": 180 }
```

---

## Deployment on Replit

1. Create a new **Replit** (Python template)
2. Upload all project files
3. Add a `replit.nix` file:
```nix
{ pkgs }: {
  deps = [ pkgs.python310 pkgs.postgresql ];
}
```
4. Set **Secrets** in Replit (Environment tab):
   - `DATABASE_URL` — Use Replit's built-in PostgreSQL or Neon/Supabase
   - `SECRET_KEY` — Random 64-char string
   - `OPENAI_API_KEY` — Optional
5. Set **Run command**: `python main.py`
6. Run `python seed.py` once in the Shell tab

### Recommended free PostgreSQL for Replit:
- [Neon.tech](https://neon.tech) — Free PostgreSQL, gives connection string
- [Supabase](https://supabase.com) — Free tier with PostgreSQL

---

## Production Deployment

### Environment Variables (set in your server/host):

```bash
FLASK_ENV=production
SECRET_KEY=<64-char-random-string>
DATABASE_URL=postgresql://user:pass@host:5432/dbname
MAIL_USERNAME=your@email.com
MAIL_PASSWORD=app-specific-password
OPENAI_API_KEY=sk-...   # Optional for AI chatbot
```

### Nginx + Gunicorn (Ubuntu):

```nginx
server {
    listen 80;
    server_name paai.org.in www.paai.org.in;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /static/ {
        alias /var/www/paai/app/static/;
    }
}
```

```bash
# Systemd service
gunicorn -w 4 -b 127.0.0.1:5000 main:app
```

---

## Security Checklist

- [x] CSRF protection on all forms (Flask-WTF)
- [x] Password hashing with bcrypt
- [x] SQL injection prevention via SQLAlchemy ORM
- [x] XSS prevention via bleach HTML sanitization
- [x] Role-based access control (admin vs user)
- [x] Protected admin routes with decorator
- [x] Input validation via WTForms
- [x] Secure session cookies in production
- [x] File upload type validation
- [x] Environment secrets via .env (never committed)

---

## Database Models

| Model                  | Description                          |
|------------------------|--------------------------------------|
| User                   | Members and admins                   |
| MembershipApplication  | Membership requests with workflow    |
| ContactMessage         | Contact form submissions             |
| NewsPost               | CMS news articles                    |
| Event                  | Events with registrations            |
| EventRegistration      | User ↔ Event join table              |
| Resource               | Documents and guides                 |
| SavedResource          | User ↔ Resource bookmarks            |
| Notification           | User notification system             |
| FAQ                    | Chatbot knowledge base               |
| ChatSession            | Chatbot conversation sessions        |
| ChatMessage            | Individual chat messages             |

---

## License

© 2024 Patient Advocacy Alliance India. All rights reserved.
Built for healthcare advocacy and patient empowerment.
