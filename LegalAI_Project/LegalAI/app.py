from flask import Flask, render_template, request, redirect, session, url_for, flash
import sqlite3
import pickle
import os
import json
from datetime import datetime

app = Flask(__name__)
app.secret_key = "legal_ai_secret_key_2025"

# ─── LEGAL DATA ───────────────────────────────────────────────────────────────

LEGAL_DATA = {
    "civil": {
        "section": "Civil Procedure Code (CPC), 1908",
        "laws": ["CPC Order VII Rule 1", "Transfer of Property Act §54", "Specific Relief Act §10", "Limitation Act Art. 54"],
        "documents": ["Sale Deed / Agreement", "Identity Proof (Aadhaar/PAN)", "Address Proof", "Property Tax Receipts", "All Written Correspondence", "Bank Statements / Payment Records", "Photographs / Video Evidence", "Legal Notice (if sent)"],
        "suggestion": "Prepare a civil plaint and file in the appropriate civil court. Send a legal notice via registered post first — it often prompts resolution without litigation. Consider mediation through DLSA for faster resolution.",
        "complexity_note": "Civil cases can take 2–5 years. Collect all documents before filing."
    },
    "criminal": {
        "section": "Indian Penal Code (IPC), 1860",
        "laws": ["IPC §420 (Cheating)", "IPC §406 (Criminal Breach of Trust)", "CrPC §154 (FIR)", "IPC §379 (Theft)", "IPC §498A (Domestic Violence)"],
        "documents": ["FIR Copy", "Police Complaint", "Medical Report (if applicable)", "Witness Details & Statements", "CCTV / Digital Evidence", "Identity Proof", "Incident Timeline Document"],
        "suggestion": "Ensure FIR is registered at the nearest police station. If police refuse, file a complaint directly to the Magistrate under CrPC §156(3). Preserve all physical evidence immediately.",
        "complexity_note": "Criminal matters require immediate action. Contact a lawyer before making any statements."
    },
    "consumer": {
        "section": "Consumer Protection Act, 2019",
        "laws": ["Consumer Protection Act §35", "Consumer Protection Act §39", "CPA §47 (NCDRC)", "CPA §51 (National Commission)"],
        "documents": ["Purchase Receipt / Invoice", "Product / Service Agreement", "Communication with Company", "Identity Proof", "Bank Statements", "Medical Reports (if health issue)", "Warranty / Guarantee Card"],
        "suggestion": "File complaint in District Consumer Forum (for claims up to ₹50 lakh), State Commission (₹50L–₹2Cr), or NCDRC (above ₹2Cr). You can represent yourself — no lawyer required at district level.",
        "complexity_note": "Consumer cases are usually resolved within 90–150 days. No court fee for claims below ₹5 lakh."
    },
    "family": {
        "section": "Hindu Marriage Act, 1955 / Family Courts Act, 1984",
        "laws": ["Hindu Marriage Act §13 (Divorce)", "HMA §26 (Child Custody)", "Guardians & Wards Act §17", "Domestic Violence Act §12", "CrPC §125 (Maintenance)"],
        "documents": ["Marriage Certificate", "Birth Certificate of Children", "Income Proof of Both Parties", "Address Proof", "Bank Statements", "Property Documents", "School Records of Children"],
        "suggestion": "Approach the Family Court in your district. Mandatory mediation is required in most family cases. File for interim maintenance under CrPC §125 if needed urgently.",
        "complexity_note": "Mediation under Family Courts Act is compulsory. Welfare of children is the court's primary concern."
    },
    "labour": {
        "section": "Industrial Disputes Act, 1947 / Labour Laws",
        "laws": ["Industrial Disputes Act §2A", "Employees' Provident Fund Act", "Payment of Wages Act", "Minimum Wages Act", "Shops & Establishments Act"],
        "documents": ["Employment Contract / Offer Letter", "Salary Slips (last 6 months)", "Termination Letter", "PF Account Details", "Bank Statements", "HR Communication"],
        "suggestion": "File a complaint with the Labour Commissioner before approaching court. Wrongful termination entitles you to reinstatement and back wages. Check if your employer is covered under the Industrial Disputes Act.",
        "complexity_note": "Labour disputes can be resolved quickly through the Labour Commissioner. File within 3 years."
    },
    "cyber": {
        "section": "Information Technology Act, 2000",
        "laws": ["IT Act §66 (Cyber Crime)", "IT Act §66C (Identity Theft)", "IT Act §67 (Obscene Material)", "IPC §420", "IT Act §43A (Data Protection)"],
        "documents": ["Screenshots / Digital Evidence", "Email / Chat Records", "Bank Transaction Proof (if financial fraud)", "Website URLs / Account Links", "Complaint to cybercrime.gov.in (acknowledgement)"],
        "suggestion": "Report immediately on cybercrime.gov.in. Contact the local cyber cell. Preserve all digital evidence before reporting. Do not delete any messages or screenshots.",
        "complexity_note": "Report within 72 hours for financial fraud. Cyber cell has special investigation powers."
    }
}

LAWYERS_DATA = {
    "Hyderabad": [
        {"name": "Adv. Suresh Rao", "spec": "Property & Civil Law", "exp": 15, "rating": 4.9, "fee": 1500, "cases": 320, "phone": "+91 98765 43210", "court": "Telangana High Court"},
        {"name": "Adv. Priya Menon", "spec": "Civil Law & Mediation", "exp": 11, "rating": 4.8, "fee": 1000, "cases": 215, "phone": "+91 98765 43211", "court": "District Court, Hyderabad"},
        {"name": "Adv. Nalini Reddy", "spec": "Family Law & Women's Rights", "exp": 20, "rating": 5.0, "fee": 2000, "cases": 450, "phone": "+91 98765 43212", "court": "Family Court, Hyderabad"},
        {"name": "Adv. Arjun Kulkarni", "spec": "Criminal Law & Bail", "exp": 8, "rating": 4.6, "fee": 800, "cases": 180, "phone": "+91 98765 43213", "court": "Sessions Court"},
        {"name": "Adv. Ramesh Iyer", "spec": "Consumer & Labour Law", "exp": 12, "rating": 4.7, "fee": 1200, "cases": 260, "phone": "+91 98765 43214", "court": "Consumer Forum"},
    ],
    "Delhi": [
        {"name": "Adv. Anita Sharma", "spec": "Constitutional & Criminal Law", "exp": 18, "rating": 4.9, "fee": 3000, "cases": 500, "phone": "+91 98765 43220", "court": "Delhi High Court"},
        {"name": "Adv. Vikram Singh", "spec": "Corporate & Contract Law", "exp": 14, "rating": 4.7, "fee": 2500, "cases": 380, "phone": "+91 98765 43221", "court": "Tis Hazari Courts"},
        {"name": "Adv. Deepa Nair", "spec": "Family & Property Law", "exp": 10, "rating": 4.6, "fee": 1800, "cases": 220, "phone": "+91 98765 43222", "court": "Family Court, Delhi"},
    ],
    "Mumbai": [
        {"name": "Adv. Rohit Desai", "spec": "Corporate & Commercial Law", "exp": 22, "rating": 4.9, "fee": 4000, "cases": 600, "phone": "+91 98765 43230", "court": "Bombay High Court"},
        {"name": "Adv. Meera Joshi", "spec": "Consumer & Labour Law", "exp": 9, "rating": 4.7, "fee": 1500, "cases": 190, "phone": "+91 98765 43231", "court": "District Consumer Forum"},
        {"name": "Adv. Arun Patil", "spec": "Criminal & Cyber Law", "exp": 16, "rating": 4.8, "fee": 2200, "cases": 410, "phone": "+91 98765 43232", "court": "Sessions Court, Mumbai"},
    ],
    "Bengaluru": [
        {"name": "Adv. Kiran Hegde", "spec": "IT & Cyber Law", "exp": 12, "rating": 4.8, "fee": 2000, "cases": 280, "phone": "+91 98765 43240", "court": "Karnataka High Court"},
        {"name": "Adv. Sunita Rao", "spec": "Property & Civil Law", "exp": 17, "rating": 4.9, "fee": 1800, "cases": 390, "phone": "+91 98765 43241", "court": "City Civil Court"},
    ],
    "Chennai": [
        {"name": "Adv. Murugan K.", "spec": "Criminal & Family Law", "exp": 20, "rating": 4.7, "fee": 1500, "cases": 420, "phone": "+91 98765 43250", "court": "Madras High Court"},
        {"name": "Adv. Lakshmi S.", "spec": "Labour & Consumer Law", "exp": 8, "rating": 4.6, "fee": 1000, "cases": 160, "phone": "+91 98765 43251", "court": "Labour Court, Chennai"},
    ],
}

COURTS_DATA = {
    "Hyderabad": ["Telangana High Court", "City Civil Court", "District Consumer Forum", "Family Court", "Sessions Court", "Labour Court"],
    "Delhi": ["Delhi High Court", "Tis Hazari District Courts", "Family Court Dwarka", "Consumer Disputes Redressal Forum", "Sessions Court"],
    "Mumbai": ["Bombay High Court", "City Civil & Sessions Court", "Family Court Bandra", "Consumer Forum Andheri", "Labour Court"],
    "Bengaluru": ["Karnataka High Court", "City Civil Court", "Consumer Forum", "Family Court", "Sessions Court"],
    "Chennai": ["Madras High Court", "City Civil Court", "Consumer Forum", "Family Court", "Sessions Court"],
}

FAMOUS_CASES = [
    {"title": "Kesavananda Bharati v. State of Kerala (1973)", "type": "Constitutional", "court": "Supreme Court", "summary": "Established the Basic Structure doctrine — Parliament cannot alter the fundamental framework of the Constitution.", "impact": "Landmark"},
    {"title": "Vishaka v. State of Rajasthan (1997)", "type": "Constitutional", "court": "Supreme Court", "summary": "Established guidelines for sexual harassment at workplace before POSH Act was enacted.", "impact": "Landmark"},
    {"title": "Maneka Gandhi v. Union of India (1978)", "type": "Constitutional", "court": "Supreme Court", "summary": "Expanded the scope of Article 21 — Right to Life includes right to live with dignity.", "impact": "Landmark"},
    {"title": "M.C. Mehta v. Union of India (1986)", "type": "Environmental", "court": "Supreme Court", "summary": "Absolute liability for hazardous industries — introduced the polluter pays principle in India.", "impact": "Landmark"},
    {"title": "Shah Bano Case (1985)", "type": "Family", "court": "Supreme Court", "summary": "Muslim divorced woman entitled to maintenance under CrPC §125. Led to the Muslim Women Act, 1986.", "impact": "Historic"},
]

IPC_SECTIONS = [
    {"section": "§302", "title": "Murder", "punishment": "Death or life imprisonment + fine"},
    {"section": "§307", "title": "Attempt to Murder", "punishment": "Up to 10 years, or life if injury caused"},
    {"section": "§376", "title": "Rape", "punishment": "Minimum 7 years, may extend to life"},
    {"section": "§420", "title": "Cheating & Dishonesty", "punishment": "Up to 7 years + fine"},
    {"section": "§406", "title": "Criminal Breach of Trust", "punishment": "Up to 3 years or fine or both"},
    {"section": "§498A", "title": "Cruelty by Husband / Relatives", "punishment": "Up to 3 years + fine"},
    {"section": "§354", "title": "Assault on Woman", "punishment": "1 to 5 years + fine"},
    {"section": "§379", "title": "Theft", "punishment": "Up to 3 years + fine"},
    {"section": "§392", "title": "Robbery", "punishment": "Up to 10 years + fine"},
    {"section": "§120B", "title": "Criminal Conspiracy", "punishment": "As per offence conspired"},
]

# ─── DB HELPERS ───────────────────────────────────────────────────────────────

def get_db():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT NOT NULL DEFAULT 'user',
        first_name TEXT,
        last_name TEXT,
        phone TEXT,
        location TEXT,
        dob TEXT,
        gender TEXT,
        occupation TEXT,
        bar_number TEXT,
        specialisation TEXT,
        university TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS bookings(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        lawyer_name TEXT,
        location TEXT,
        message TEXT,
        status TEXT DEFAULT 'pending',
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS cases(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        case_text TEXT,
        category TEXT,
        court TEXT,
        complexity TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )""")
    conn.commit()
    conn.close()

init_db()

# ─── ML PREDICTION ────────────────────────────────────────────────────────────

def predict_case(text):
    """Rule-based prediction — replace with ML model when available."""
    text_lower = text.lower()
    keywords = {
        "civil":    ["property", "land", "possession", "title", "ownership", "contract", "agreement", "money", "debt", "loan", "rent", "tenant"],
        "criminal": ["assault", "theft", "robbery", "murder", "cheating", "fraud", "fir", "police", "attack", "threat", "blackmail", "kidnap"],
        "consumer": ["product", "defective", "service", "refund", "company", "amazon", "online", "purchase", "warranty", "insurance"],
        "family":   ["divorce", "custody", "maintenance", "husband", "wife", "marriage", "domestic", "child", "alimony", "separation"],
        "labour":   ["job", "salary", "employer", "termination", "fired", "pf", "provident", "workplace", "employee", "wage"],
        "cyber":    ["hacked", "fraud", "online", "phishing", "password", "bank transfer", "otp", "scam", "social media", "data"],
    }
    courts = {
        "civil": "District Civil Court",
        "criminal": "Sessions Court / Magistrate Court",
        "consumer": "District Consumer Forum",
        "family": "Family Court",
        "labour": "Labour Court / Industrial Tribunal",
        "cyber": "Cyber Cell / Sessions Court",
    }
    complexity_map = {
        "civil": "High", "criminal": "High", "consumer": "Low",
        "family": "Moderate", "labour": "Moderate", "cyber": "Moderate",
    }
    scores = {k: sum(1 for kw in v if kw in text_lower) for k, v in keywords.items()}
    category = max(scores, key=scores.get) if max(scores.values()) > 0 else "civil"
    return category, courts[category], complexity_map[category]

# ─── ROUTES ───────────────────────────────────────────────────────────────────

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        case_text = request.form.get("case_summary", "").strip()
        if not case_text:
            flash("Please describe your case.", "error")
            return redirect("/")
        category, court, complexity = predict_case(case_text)
        # Save case to DB
        if "user_id" in session:
            conn = get_db()
            conn.execute("INSERT INTO cases(user_id,case_text,category,court,complexity) VALUES(?,?,?,?,?)",
                         (session["user_id"], case_text, category, court, complexity))
            conn.commit()
            conn.close()
        return render_template("result.html", category=category, court=court,
                               complexity=complexity, case_text=case_text)
    return render_template("index.html")

@app.route("/more_info/<category>")
def more_info(category):
    if "user" not in session:
        session["next"] = f"/more_info/{category}"
        return redirect("/login")
    data = LEGAL_DATA.get(category.lower(), LEGAL_DATA["civil"])
    return render_template("more_info.html", data=data, category=category.title())

@app.route("/explore")
def explore():
    if "user" not in session:
        session["next"] = "/explore"
        return redirect("/login")
    return render_template("select_location.html", cities=list(LAWYERS_DATA.keys()))

@app.route("/show_lawyers", methods=["POST"])
def show_lawyers():
    if "user" not in session:
        return redirect("/login")
    location = request.form.get("location", "Hyderabad")
    lawyers = LAWYERS_DATA.get(location, [])
    courts = COURTS_DATA.get(location, [])
    return render_template("explore_results.html", lawyers=lawyers, courts=courts, location=location)

@app.route("/book", methods=["POST"])
def book():
    if "user" not in session:
        return redirect("/login")
    lawyer_name = request.form.get("lawyer_name")
    location = request.form.get("location")
    message = request.form.get("message", "Consultation request")
    conn = get_db()
    conn.execute("INSERT INTO bookings(user_id,lawyer_name,location,message) VALUES(?,?,?,?)",
                 (session["user_id"], lawyer_name, location, message))
    conn.commit()
    conn.close()
    flash(f"Booking request sent to {lawyer_name}! They will contact you within 24 hours.", "success")
    return redirect(f"/show_lawyers_get/{location}")

@app.route("/show_lawyers_get/<location>")
def show_lawyers_get(location):
    if "user" not in session:
        return redirect("/login")
    lawyers = LAWYERS_DATA.get(location, [])
    courts = COURTS_DATA.get(location, [])
    return render_template("explore_results.html", lawyers=lawyers, courts=courts, location=location)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        conn = get_db()
        user = conn.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password)).fetchone()
        conn.close()
        if user:
            session["user"] = user["username"]
            session["user_id"] = user["id"]
            session["role"] = user["role"]
            session["first_name"] = user["first_name"] or user["username"]
            next_url = session.pop("next", "/")
            flash(f"Welcome back, {session['first_name']}!", "success")
            return redirect(next_url)
        flash("Invalid username or password.", "error")
    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        data = {k: request.form.get(k, "").strip() for k in
                ["username","email","password","role","first_name","last_name",
                 "phone","location","dob","gender","occupation","bar_number","specialisation","university"]}
        try:
            conn = get_db()
            conn.execute("""INSERT INTO users(username,email,password,role,first_name,last_name,
                phone,location,dob,gender,occupation,bar_number,specialisation,university)
                VALUES(:username,:email,:password,:role,:first_name,:last_name,
                :phone,:location,:dob,:gender,:occupation,:bar_number,:specialisation,:university)""", data)
            conn.commit()
            conn.close()
            flash("Account created! Please login.", "success")
            return redirect("/login")
        except sqlite3.IntegrityError:
            flash("Username or email already exists.", "error")
    return render_template("register.html")

@app.route("/profile")
def profile():
    if "user" not in session:
        return redirect("/login")
    conn = get_db()
    user = conn.execute("SELECT * FROM users WHERE id=?", (session["user_id"],)).fetchone()
    cases = conn.execute("SELECT * FROM cases WHERE user_id=? ORDER BY created_at DESC LIMIT 5", (session["user_id"],)).fetchall()
    bookings = conn.execute("SELECT * FROM bookings WHERE user_id=? ORDER BY created_at DESC LIMIT 5", (session["user_id"],)).fetchall()
    conn.close()
    return render_template("profile.html", user=user, cases=cases, bookings=bookings)

@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/login")
    role = session.get("role", "user")
    if role == "lawyer":
        return redirect("/lawyer_dashboard")
    elif role == "student":
        return redirect("/student_dashboard")
    else:
        conn = get_db()
        cases = conn.execute("SELECT * FROM cases WHERE user_id=? ORDER BY created_at DESC", (session["user_id"],)).fetchall()
        bookings = conn.execute("SELECT * FROM bookings WHERE user_id=? ORDER BY created_at DESC", (session["user_id"],)).fetchall()
        conn.close()
        return render_template("dashboards/user_dashboard.html", cases=cases, bookings=bookings)

@app.route("/lawyer_dashboard")
def lawyer_dashboard():
    if "user" not in session or session.get("role") != "lawyer":
        return redirect("/login")
    conn = get_db()
    requests = conn.execute("SELECT * FROM bookings WHERE lawyer_name LIKE ? ORDER BY created_at DESC",
                            (f"%{session['user']}%",)).fetchall()
    conn.close()
    return render_template("dashboards/lawyer_dashboard.html", requests=requests)

@app.route("/student_dashboard")
def student_dashboard():
    if "user" not in session or session.get("role") != "student":
        return redirect("/login")
    return render_template("dashboards/student_dashboard.html",
                           famous_cases=FAMOUS_CASES, ipc_sections=IPC_SECTIONS)

@app.route("/logout")
def logout():
    name = session.get("first_name", "User")
    session.clear()
    flash(f"Goodbye, {name}! You have been logged out.", "success")
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)
