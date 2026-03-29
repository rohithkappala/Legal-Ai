# LegalAI — AI Legal Assistance Platform

## Quick Setup (paste in terminal)

```bash
# 1. Go into the project folder
cd LegalAI

# 2. Create virtual environment
python -m venv venv

# 3. Activate it
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Run the app
python app.py
```

Open browser: http://127.0.0.1:5000

## Project Structure

```
LegalAI/
├── app.py                          ← Main Flask application (all routes + logic)
├── requirements.txt                ← pip install -r requirements.txt
├── database.db                     ← Auto-created on first run
│
├── templates/
│   ├── layout.html                 ← Base template (navbar, flash, footer)
│   ├── index.html                  ← Home page + case input
│   ├── result.html                 ← AI analysis results
│   ├── more_info.html              ← Legal sections + documents
│   ├── login.html                  ← Login page
│   ├── register.html               ← Register (User / Lawyer / Student)
│   ├── profile.html                ← User profile + activity
│   ├── select_location.html        ← City picker
│   ├── explore_results.html        ← Lawyers + courts list
│   └── dashboards/
│       ├── user_dashboard.html     ← User dashboard (cases + bookings)
│       ├── lawyer_dashboard.html   ← Lawyer panel (requests)
│       └── student_dashboard.html  ← Learning panel (cases + IPC + quiz)
│
└── static/
    ├── css/style.css               ← Full professional stylesheet
    └── js/main.js                  ← UI interactions

## Test Accounts (register first)
- Role: user    → gets case analysis + lawyer booking
- Role: lawyer  → gets lawyer dashboard + client requests
- Role: student → gets learning panel + IPC sections + quiz

## Flow
Home → Enter Case → Result → More Information (login required) → Legal Sections + Docs → Explore Lawyers → Select City → Book Consultation
```
