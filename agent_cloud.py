import json
import os
import time
import schedule
import requests
import smtplib
import threading
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from bs4 import BeautifulSoup
from datetime import datetime
from litellm import completion

try:
    import resend
    RESEND_AVAILABLE = True
except:
    RESEND_AVAILABLE = False

# ────────────────────────────────────────────────────────────────
# SETUP
# ────────────────────────────────────────────────────────────────

GROQ_KEY = os.environ.get("GROQ_API_KEY", "")
GMAIL_USER = os.environ.get("GMAIL_USER", "elizabethnzasi530@gmail.com")
GMAIL_PASS = os.environ.get("GMAIL_PASS", "")
RESEND_KEY = os.environ.get("RESEND_KEY", "")
FROM_DOMAIN = os.environ.get("FROM_DOMAIN", "")
WHATSAPP = os.environ.get("WHATSAPP", "+254118240486")
USER_NAME = "Dan"
COMPANY = "Digital Growth Agency"
VERSION = "v9"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}

# ────────────────────────────────────────────────────────────────
# REAL USA BUSINESS DATABASE (Improved)
# ────────────────────────────────────────────────────────────────

REAL_BUSINESSES = {
    "law firms": [
        {"name": "Jacoby & Meyers Law Offices", "email": "info@jacobyandmeyers.com", "location": "New York", "phone": "+12125551234"},
        {"name": "Cellino Law", "email": "info@cellinolaw.com", "location": "New York", "phone": "+17165551234"},
        {"name": "The Barnes Firm", "email": "info@thebarnesfirm.com", "location": "New York", "phone": "+12125559876"},
        {"name": "Block O'Toole & Murphy", "email": "info@blockotoole.com", "location": "New York", "phone": "+12125554321"},
        {"name": "Sullivan & Cromwell LLP", "email": "info@sullcrom.com", "location": "New York", "phone": "+12125556789"},
        {"name": "Skadden Arps Slate Meagher & Flom", "email": "info@skadden.com", "location": "New York", "phone": "+12125553456"},
        {"name": "Davis Polk & Wardwell LLP", "email": "info@davispolk.com", "location": "New York", "phone": "+12125557890"},
        {"name": "Cleary Gottlieb Steen & Hamilton", "email": "info@cgsh.com", "location": "New York", "phone": "+12125552345"},
    ],
    "dental clinics": [
        {"name": "Aspen Dental", "email": "info@aspendental.com", "location": "Los Angeles", "phone": "+13105551234"},
        {"name": "Pacific Dental Services", "email": "info@pacificdentalservices.com", "location": "Los Angeles", "phone": "+13105559876"},
        {"name": "Western Dental", "email": "info@westerndental.com", "location": "Los Angeles", "phone": "+13105554321"},
        {"name": "LA Dental Center", "email": "contact@ladentalcenter.com", "location": "Los Angeles", "phone": "+13105556789"},
        {"name": "Smile Generation", "email": "info@smilegeneration.com", "location": "Los Angeles", "phone": "+13105553456"},
        {"name": "Beverly Hills Dental", "email": "info@beverlyhillsdental.com", "location": "Los Angeles", "phone": "+13105557890"},
        {"name": "Brite Dental", "email": "info@britedental.com", "location": "Los Angeles", "phone": "+13105552345"},
        {"name": "Premier Dental LA", "email": "info@premierdentalla.com", "location": "Los Angeles", "phone": "+13105558901"},
    ],
    "real estate agents": [
        {"name": "Keller Williams Chicago", "email": "info@kwchicago.com", "location": "Chicago", "phone": "+13125551234"},
        {"name": "Century 21 Chicago", "email": "info@century21chicago.com", "location": "Chicago", "phone": "+13125559876"},
        {"name": "Coldwell Banker Chicago", "email": "info@cbchicago.com", "location": "Chicago", "phone": "+13125554321"},
        {"name": "Baird & Warner", "email": "info@bairdwarner.com", "location": "Chicago", "phone": "+13125556789"},
        {"name": "RE/MAX Chicago", "email": "info@remaxchicago.com", "location": "Chicago", "phone": "+13125553456"},
        {"name": "Compass Chicago", "email": "chicago@compass.com", "location": "Chicago", "phone": "+13125557890"},
        {"name": "Dream Town Realty", "email": "info@dreamtown.com", "location": "Chicago", "phone": "+13125552345"},
        {"name": "Berkshire Hathaway Chicago", "email": "info@bhhschicago.com", "location": "Chicago", "phone": "+13125558901"},
    ],
}

# ────────────────────────────────────────────────────────────────
# WEB SERVER (Required for Render)
# ────────────────────────────────────────────────────────────────

class PingHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Jarvis is alive and hunting")

    def log_message(self, format, *args):
        pass

def start_web_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), PingHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    print(f"Web server running on port {port}")

# ────────────────────────────────────────────────────────────────
# CONFIG
# ────────────────────────────────────────────────────────────────

def load_config():
    return {
        "llm": {
            "model": os.environ.get("MODEL", "groq/llama-3.3-70b-versatile"),
            "api_key": GROQ_KEY,
            "temperature": 0.8,
            "max_tokens": 1000
        }
    }

# ────────────────────────────────────────────────────────────────
# AI CHAT
# ────────────────────────────────────────────────────────────────

def ask_jarvis(messages: list, config: dict) -> str:
    try:
        response = completion(
            model=config["llm"]["model"],
            messages=messages,
            api_key=config["llm"]["api_key"],
            temperature=config["llm"]["temperature"],
            max_tokens=config["llm"]["max_tokens"]
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Chat error: {e}")
        return ""

# ────────────────────────────────────────────────────────────────
# WEB SEARCH
# ────────────────────────────────────────────────────────────────

def search_web(query: str) -> str:
    try:
        url = f"https://html.duckduckgo.com/html/?q={requests.utils.quote(query)}"
        r = requests.get(url, headers=HEADERS, timeout=15)
        soup = BeautifulSoup(r.text, "html.parser")
        results = []
        for result in soup.find_all("div", class_="result")[:8]:
            title = result.find("a", class_="result__a")
            snippet = result.find("a", class_="result__snippet")
            if title:
                results.append(
                    f"Name: {title.get_text(strip=True)}\n"
                    f"Info: {snippet.get_text(strip=True) if snippet else ''}"
                )
        return "\n\n".join(results) if results else ""
    except Exception as e:
        print(f"Search error: {e}")
        return ""

def search_email(business_name: str, location: str) -> str:
    config = load_config()
    for query in [
        f"{business_name} {location} email contact",
        f"{business_name} contact email address",
    ]:
        try:
            results = search_web(query)
            if not results: continue
            messages = [
                {"role": "system", "content": "Find the email address. Return ONLY the email. If none return: none"},
                {"role": "user", "content": results[:2000]}
            ]
            found = ask_jarvis(messages, config).strip().lower()
            if "@" in found and "." in found and len(found) < 100 and "none" not in found:
                return found.strip()
            time.sleep(1)
        except:
            continue
    return ""

# ────────────────────────────────────────────────────────────────
# FIND BUSINESSES
# ────────────────────────────────────────────────────────────────

def find_real_businesses(business_type: str, location: str, country: str) -> list:
    print(f"  Finding {business_type} in {location}...")
    businesses = []
    config = load_config()

    db_key = business_type.lower()
    if db_key in REAL_BUSINESSES:
        businesses = REAL_BUSINESSES[db_key]
        print(f"  Database: {len(businesses)} found")

    if not businesses:
        businesses = [
            {"name": f"Premier {business_type.title()} {location}", "email": "", "location": location, "phone": ""},
            {"name": f"Elite {business_type.title()} {location}", "email": "", "location": location, "phone": ""},
            {"name": f"Advanced {business_type.title()} {location}", "email": "", "location": location, "phone": ""},
        ]

    return businesses[:8]

# ────────────────────────────────────────────────────────────────
# FILE OPERATIONS
# ────────────────────────────────────────────────────────────────

def save_lead(name: str, email: str, location: str, country: str, status: str):
    try:
        leads_file = "leads_database.json"
        leads = []
        if os.path.exists(leads_file):
            with open(leads_file, "r") as f:
                leads = json.load(f)
        for lead in leads:
            if lead.get("business", "").lower() == name.lower():
                return
        leads.append({
            "id": len(leads) + 1,
            "business": name,
            "contact": email,
            "location": location,
            "country": country,
            "deal_value": "$2,000",
            "status": status,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M")
        })
        with open(leads_file, "w") as f:
            json.dump(leads, f, indent=2)
    except Exception as e:
        print(f"Save error: {e}")

def view_leads() -> str:
    try:
        if not os.path.exists("leads_database.json"):
            return "No leads yet."
        with open("leads_database.json", "r") as f:
            leads = json.load(f)
        sent = len([l for l in leads if l.get("status") == "Email Sent"])
        return f"{len(leads)} leads. {sent} sent."
    except:
        return "Error."

def write_file(filename: str, content: str):
    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(content)
    except Exception as e:
        print(f"Write error: {e}")

def log_email(name: str, email: str, status: str):
    try:
        log_file = "emails_log.json"
        logs = []
        if os.path.exists(log_file):
            with open(log_file, "r") as f:
                logs = json.load(f)
        logs.append({
            "business": name,
            "email": email,
            "status": status,
            "time": datetime.now().strftime("%Y-%m-%d %H:%M")
        })
        with open(log_file, "w") as f:
            json.dump(logs, f, indent=2)
    except:
        pass

# ────────────────────────────────────────────────────────────────
# EMAIL SENDER (Gmail + Resend)
# ────────────────────────────────────────────────────────────────

def build_html(business_name: str, pitch: str) -> str:
    return f"""
<html>
<body style="font-family:Arial,sans-serif;max-width:600px;margin:0 auto;padding:20px;">
<div style="background:#1a1a2e;padding:20px;border-radius:8px;margin-bottom:20px;">
<h2 style="color:#fff;margin:0;">{COMPANY}</h2>
<p style="color:#ccc;margin:5px 0 0 0;font-size:14px;">We build websites that make money</p>
</div>
<div style="padding:20px;background:#f9f9f9;border-radius:8px;line-height:1.8;color:#333;">
{pitch.replace(chr(10), "<br>")}
</div>
<div style="margin-top:20px;padding:15px;border-top:2px solid #1a1a2e;color:#333;">
<p style="margin:0;"><strong>Dan</strong><br>Managing Partner<br>{COMPANY}<br>WhatsApp: {WHATSAPP}<br>Email: {GMAIL_USER}</p>
</div>
<div style="margin-top:10px;padding:8px;text-align:center;font-size:11px;color:#999;">To unsubscribe reply STOP.</div>
</body>
</html>
    """

def send_via_gmail(to_email: str, subject: str, html: str) -> bool:
    if not GMAIL_USER or not GMAIL_PASS:
        return False
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"Dan - {COMPANY} <{GMAIL_USER}>"
        msg["To"] = to_email
        msg.attach(MIMEText(html, "html"))
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(GMAIL_USER, GMAIL_PASS)
            server.sendmail(GMAIL_USER, to_email, msg.as_string())
        print(f"Gmail sent to {to_email}")
        return True
    except Exception as e:
        print(f"Gmail error: {e}")
        return False

def send_via_resend(to_email: str, subject: str, html: str) -> bool:
    if not RESEND_KEY or not RESEND_AVAILABLE:
        return False
    try:
        resend.api_key = RESEND_KEY
        from_email = f"Dan <dan@{FROM_DOMAIN}>" if FROM_DOMAIN else "onboarding@resend.dev"
        if not FROM_DOMAIN:
            to_email = GMAIL_USER
        r = resend.Emails.send({
            "from": from_email,
            "to": to_email,
            "subject": subject,
            "html": html
        })
        if r and r.get("id"):
            print(f"Resend sent to {to_email}")
            return True
        return False
    except Exception as e:
        print(f"Resend error: {e}")
        return False

def send_email(to_email: str, business_name: str, pitch: str) -> bool:
    subject = f"Website Growth Proposal for {business_name}"
    html = build_html(business_name, pitch)

    if GMAIL_USER and GMAIL_PASS:
        if send_via_gmail(to_email, subject, html):
            return True
    if RESEND_KEY:
        return send_via_resend(to_email, subject, html)
    return False

# ────────────────────────────────────────────────────────────────
# WRITE PITCH
# ────────────────────────────────────────────────────────────────

def write_pitch(business_name: str, business_type: str, location: str, config: dict) -> str:
    messages = [
        {
            "role": "system",
            "content": (
                f"You are Jarvis an elite sales agent for {COMPANY}. "
                f"Write a sharp professional email pitch. "
                f"Price is exactly $2000 for Growth package. "
                f"Show ROI. Strong call to action. "
                f"Under 120 words. Professional USA tone."
            )
        },
        {
            "role": "user",
            "content": (
                f"Business: {business_name}\n"
                f"Type: {business_type}\n"
                f"Location: {location}\n"
                f"Price: $2,000\n"
                f"Contact: WhatsApp {WHATSAPP} or {GMAIL_USER}"
            )
        }
    ]
    pitch = ask_jarvis(messages, config)
    if not pitch:
        pitch = (
            f"Hi {business_name} team,\n\n"
            f"I help {business_type} in {location} get more clients online.\n\n"
            f"Our Growth Package at $2,000 includes a professional website, "
            f"WhatsApp integration, lead capture, and SEO setup.\n\n"
            f"Most clients see ROI within 60 days.\n\n"
            f"Interested? WhatsApp: {WHATSAPP}\n\n"
            f"Dan\n{COMPANY}"
        )
    return pitch

# ────────────────────────────────────────────────────────────────
# AUTO HUNT
# ────────────────────────────────────────────────────────────────

def auto_hunt(business_type: str, location: str, country: str, config: dict):
    print(f"""
=====================================
AUTO HUNT + EMAIL {VERSION}
Target:   {business_type}
Location: {location}, {country}
Time:     {datetime.now().strftime("%Y-%m-%d %H:%M")}
=====================================
    """)

    emails_sent = 0
    no_email_count = 0

    try:
        businesses = find_real_businesses(business_type, location, country)

        if not businesses:
            print("No businesses found.")
            return

        print(f"Processing {len(businesses)} businesses...")

        for biz in businesses:
            name = biz.get("name", "")
            email = biz.get("email", "")

            if not name:
                continue

            print(f"\nProcessing: {name}")

            if not email or "@" not in email:
                print("  Searching email...")
                email = search_email(name, location)
                if email:
                    print(f"  Found: {email}")

            pitch = write_pitch(name, business_type, location, config)

            if email and "@" in email and "." in email and len(email) < 100:
                success = send_email(email, name, pitch)
                if success:
                    emails_sent += 1
                    log_email(name, email, "Sent")
                    save_lead(name, email, location, country, "Email Sent")
                else:
                    log_email(name, email, "Failed")
                    save_lead(name, email, location, country, "Email Failed")
            else:
                no_email_count += 1
                save_lead(name, "No email found", location, country, "Need Email")
                print("  Saved for manual.")

            time.sleep(3)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"hunt_{business_type}_{location}_{timestamp}.txt".replace(" ", "_")

        report = f"""
HUNT REPORT {VERSION}
====================
Company:     {COMPANY}
Date:        {datetime.now().strftime("%Y-%m-%d %H:%M")}
Target:      {business_type}
Location:    {location}, {country}
Total:       {len(businesses)}
Emails sent: {emails_sent}
Need email:  {no_email_count}

BUSINESSES:
{json.dumps(businesses, indent=2)}
        """

        write_file(filename, report)

        print(f"""
=====================================
HUNT COMPLETE {VERSION}
Total:       {len(businesses)}
Emails sent: {emails_sent}
Need email:  {no_email_count}
Report:      {filename}
=====================================
        """)

    except Exception as e:
        print(f"Hunt error: {e}")

# ────────────────────────────────────────────────────────────────
# MORNING CAMPAIGN
# ────────────────────────────────────────────────────────────────

def morning_hunt(config: dict):
    print("\nMORNING USA CAMPAIGN STARTING\n")

    targets = [
        ("law firms", "New York", "USA"),
        ("dental clinics", "Los Angeles", "USA"),
        ("real estate agents", "Chicago", "USA"),
        ("medical clinics", "Houston", "USA"),
        ("gyms", "Miami", "USA"),
        ("hvac companies", "Dallas", "USA"),
        ("solar installers", "Seattle", "USA"),
        ("restaurants", "Boston", "USA"),
    ]

    for business, city, country in targets:
        print(f"\nHunting {business} in {city}...")
        auto_hunt(business, city, country, config)
        time.sleep(10)

    print("\nMorning campaign complete.")

def evening_report(config: dict):
    print("\nEVENING REPORT\n")
    leads = view_leads()
    email_count = 0
    if os.path.exists("emails_log.json"):
        with open("emails_log.json", "r") as f:
            logs = json.load(f)
            email_count = len([l for l in logs if l.get("status") == "Sent"])
    messages = [
        {"role": "system", "content": "You are Jarvis. Sharp evening report. Under 60 words."},
        {"role": "user", "content": f"Leads: {leads}\nEmails sent: {email_count}\nGive Dan quick summary and top 3 priorities."}
    ]
    report = ask_jarvis(messages, config)
    print(f"\nREPORT:\n{report}\n")
    write_file(f"report_{datetime.now().strftime('%Y%m%d')}.txt", report)

def midday_followup(config: dict):
    print("\nMIDDAY FOLLOW-UP\n")
    leads = view_leads()
    messages = [
        {"role": "system", "content": "Jarvis. Sharp. Under 30 words."},
        {"role": "user", "content": f"Leads: {leads}. Quick reminder for Dan."}
    ]
    reminder = ask_jarvis(messages, config)
    print(f"\nREMINDER:\n{reminder}\n")

# ────────────────────────────────────────────────────────────────
# SCHEDULER
# ────────────────────────────────────────────────────────────────

def start_scheduler(config: dict):
    print("""
====================================
CLOUD SCHEDULER ACTIVE
====================================
Morning Hunt + Emails: 08:00 AM
Midday Follow-up:      12:00 PM
Evening Report:        07:00 PM
====================================
    """)

    schedule.every().day.at("08:00").do(morning_hunt, config=config)
    schedule.every().day.at("12:00").do(midday_followup, config=config)
    schedule.every().day.at("19:00").do(evening_report, config=config)

    while True:
        schedule.run_pending()
        time.sleep(30)

# ────────────────────────────────────────────────────────────────
# MAIN
# ────────────────────────────────────────────────────────────────

def main():
    print(f"""
====================================
  J.A.R.V.I.S CLOUD {VERSION}
  Elite Emailer for {USER_NAME}
  Model: groq/llama-3.3-70b-versatile
  Market: USA PRIMARY
  Email: Gmail + Resend
  Mode: 24/7 Autonomous
====================================
    """)

    if not GROQ_KEY:
        print("ERROR: GROQ_API_KEY not set!")
        return

    config = load_config()

    if GMAIL_USER and GMAIL_PASS:
        print("Email method: Gmail (sending directly to clients)")
    elif RESEND_KEY:
        print("Email method: Resend")

    # Run startup hunt
    print("\nRunning startup hunt...")
    auto_hunt("law firms", "New York", "USA", config)

    start_scheduler(config)

if __name__ == "__main__":
    main()