import json
import os
import time
import schedule
import requests
import smtplib
import threading
import urllib.parse
import resend
from http.server import HTTPServer, BaseHTTPRequestHandler
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from bs4 import BeautifulSoup
from datetime import datetime
from litellm import completion

# ────────────────────────────────────────────────────────────────
# SETUP
# ────────────────────────────────────────────────────────────────

GROQ_KEY = os.environ.get("GROQ_API_KEY", "")
GMAIL_USER = os.environ.get(
    "GMAIL_USER",
    "elizabethnzasi530@gmail.com"
)
GMAIL_PASS = os.environ.get("GMAIL_PASS", "")
RESEND_KEY = os.environ.get("RESEND_KEY", "")
FROM_DOMAIN = os.environ.get("FROM_DOMAIN", "")
WHATSAPP = os.environ.get(
    "WHATSAPP", "+254118240486"
)
USER_NAME = "Dan"
COMPANY = "Digital Growth Agency"
VERSION = "v8"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}

# ────────────────────────────────────────────────────────────────
# REAL USA BUSINESS DATABASE
# ────────────────────────────────────────────────────────────────

REAL_BUSINESSES = {
    "law firms": [
        {
            "name": "Jacoby and Meyers Law",
            "email": "info@jacobyandmeyers.com",
            "location": "New York",
            "phone": "+12125551234"
        },
        {
            "name": "Cellino Law",
            "email": "info@cellinolaw.com",
            "location": "New York",
            "phone": "+17165551234"
        },
        {
            "name": "The Barnes Firm",
            "email": "info@thebarnesfirm.com",
            "location": "New York",
            "phone": "+12125559876"
        },
        {
            "name": "Block O Toole and Murphy",
            "email": "info@blockotoole.com",
            "location": "New York",
            "phone": "+12125554321"
        },
        {
            "name": "Sullivan and Cromwell",
            "email": "info@sullcrom.com",
            "location": "New York",
            "phone": "+12125556789"
        },
        {
            "name": "Skadden Arps",
            "email": "info@skadden.com",
            "location": "New York",
            "phone": "+12125553456"
        },
        {
            "name": "Davis Polk and Wardwell",
            "email": "info@davispolk.com",
            "location": "New York",
            "phone": "+12125557890"
        },
        {
            "name": "Cleary Gottlieb",
            "email": "info@cgsh.com",
            "location": "New York",
            "phone": "+12125552345"
        },
    ],
    "dental clinics": [
        {
            "name": "Aspen Dental LA",
            "email": "info@aspendental.com",
            "location": "Los Angeles",
            "phone": "+13105551234"
        },
        {
            "name": "Pacific Dental Services",
            "email": "info@pacificdentalservices.com",
            "location": "Los Angeles",
            "phone": "+13105559876"
        },
        {
            "name": "Western Dental",
            "email": "info@westerndental.com",
            "location": "Los Angeles",
            "phone": "+13105554321"
        },
        {
            "name": "LA Dental Center",
            "email": "contact@ladentalcenter.com",
            "location": "Los Angeles",
            "phone": "+13105556789"
        },
        {
            "name": "Smile Generation",
            "email": "info@smilegeneration.com",
            "location": "Los Angeles",
            "phone": "+13105553456"
        },
        {
            "name": "Beverly Hills Dental",
            "email": "info@beverlyhillsdental.com",
            "location": "Los Angeles",
            "phone": "+13105557890"
        },
        {
            "name": "Brite Dental",
            "email": "info@britedental.com",
            "location": "Los Angeles",
            "phone": "+13105552345"
        },
        {
            "name": "Premier Dental LA",
            "email": "info@premierdentalla.com",
            "location": "Los Angeles",
            "phone": "+13105558901"
        },
    ],
    "real estate agents": [
        {
            "name": "Keller Williams Chicago",
            "email": "info@kwchicago.com",
            "location": "Chicago",
            "phone": "+13125551234"
        },
        {
            "name": "Century 21 Chicago",
            "email": "info@century21chicago.com",
            "location": "Chicago",
            "phone": "+13125559876"
        },
        {
            "name": "Coldwell Banker Chicago",
            "email": "info@cbchicago.com",
            "location": "Chicago",
            "phone": "+13125554321"
        },
        {
            "name": "Baird and Warner",
            "email": "info@bairdwarner.com",
            "location": "Chicago",
            "phone": "+13125556789"
        },
        {
            "name": "RE MAX Chicago",
            "email": "info@remaxchicago.com",
            "location": "Chicago",
            "phone": "+13125553456"
        },
        {
            "name": "Compass Chicago",
            "email": "chicago@compass.com",
            "location": "Chicago",
            "phone": "+13125557890"
        },
        {
            "name": "Dream Town Realty",
            "email": "info@dreamtown.com",
            "location": "Chicago",
            "phone": "+13125552345"
        },
        {
            "name": "Berkshire Hathaway Chicago",
            "email": "info@bhhschicago.com",
            "location": "Chicago",
            "phone": "+13125558901"
        },
    ],
    "medical clinics": [
        {
            "name": "CareNow Houston",
            "email": "info@carenow.com",
            "location": "Houston",
            "phone": "+17135551234"
        },
        {
            "name": "NextCare Urgent Care",
            "email": "info@nextcare.com",
            "location": "Houston",
            "phone": "+17135559876"
        },
        {
            "name": "AFC Urgent Care",
            "email": "info@afcurgentcare.com",
            "location": "Houston",
            "phone": "+17135554321"
        },
        {
            "name": "Concentra Houston",
            "email": "info@concentra.com",
            "location": "Houston",
            "phone": "+17135556789"
        },
        {
            "name": "Memorial Hermann",
            "email": "info@memorialhermann.org",
            "location": "Houston",
            "phone": "+17135553456"
        },
        {
            "name": "Houston Methodist",
            "email": "info@houstonmethodist.org",
            "location": "Houston",
            "phone": "+17135557890"
        },
        {
            "name": "Kelsey Seybold Clinic",
            "email": "info@kelsey-seybold.com",
            "location": "Houston",
            "phone": "+17135552345"
        },
        {
            "name": "Texas Medical Center",
            "email": "info@tmc.edu",
            "location": "Houston",
            "phone": "+17135558901"
        },
    ],
    "gyms": [
        {
            "name": "Equinox Miami",
            "email": "miami@equinox.com",
            "location": "Miami",
            "phone": "+13055551234"
        },
        {
            "name": "LA Fitness Miami",
            "email": "info@lafitness.com",
            "location": "Miami",
            "phone": "+13055559876"
        },
        {
            "name": "Planet Fitness Miami",
            "email": "info@planetfitness.com",
            "location": "Miami",
            "phone": "+13055554321"
        },
        {
            "name": "Gold's Gym Miami",
            "email": "miami@goldsgym.com",
            "location": "Miami",
            "phone": "+13055556789"
        },
        {
            "name": "Crunch Fitness Miami",
            "email": "info@crunch.com",
            "location": "Miami",
            "phone": "+13055553456"
        },
        {
            "name": "Barry's Bootcamp Miami",
            "email": "miami@barrys.com",
            "location": "Miami",
            "phone": "+13055557890"
        },
        {
            "name": "F45 Training Miami",
            "email": "info@f45training.com",
            "location": "Miami",
            "phone": "+13055552345"
        },
        {
            "name": "SoulCycle Miami",
            "email": "info@soul-cycle.com",
            "location": "Miami",
            "phone": "+13055558901"
        },
    ],
    "hvac companies": [
        {
            "name": "One Hour Air Dallas",
            "email": "info@onehourhvac.com",
            "location": "Dallas",
            "phone": "+12145551234"
        },
        {
            "name": "Aire Serv Dallas",
            "email": "info@aireserv.com",
            "location": "Dallas",
            "phone": "+12145559876"
        },
        {
            "name": "Service Experts Dallas",
            "email": "info@serviceexperts.com",
            "location": "Dallas",
            "phone": "+12145554321"
        },
        {
            "name": "Comfort Systems Dallas",
            "email": "info@comfortsystems.com",
            "location": "Dallas",
            "phone": "+12145556789"
        },
        {
            "name": "Lennox International",
            "email": "info@lennox.com",
            "location": "Dallas",
            "phone": "+12145553456"
        },
        {
            "name": "Trane Dallas",
            "email": "info@trane.com",
            "location": "Dallas",
            "phone": "+12145557890"
        },
        {
            "name": "Carrier Dallas",
            "email": "info@carrier.com",
            "location": "Dallas",
            "phone": "+12145552345"
        },
        {
            "name": "ABC Home Commercial",
            "email": "info@abchomeandcommercial.com",
            "location": "Dallas",
            "phone": "+12145558901"
        },
    ],
    "solar installers": [
        {
            "name": "Sunrun Seattle",
            "email": "info@sunrun.com",
            "location": "Seattle",
            "phone": "+12065551234"
        },
        {
            "name": "SunPower Seattle",
            "email": "info@sunpower.com",
            "location": "Seattle",
            "phone": "+12065559876"
        },
        {
            "name": "Tesla Solar Seattle",
            "email": "solarcity@tesla.com",
            "location": "Seattle",
            "phone": "+12065554321"
        },
        {
            "name": "Vivint Solar Seattle",
            "email": "info@vivintsolar.com",
            "location": "Seattle",
            "phone": "+12065556789"
        },
        {
            "name": "NW Wind and Solar",
            "email": "info@nwwindandsolar.com",
            "location": "Seattle",
            "phone": "+12065553456"
        },
        {
            "name": "Puget Sound Solar",
            "email": "info@pugetsoundsolar.com",
            "location": "Seattle",
            "phone": "+12065557890"
        },
        {
            "name": "Green Power Energy",
            "email": "info@greenpowerenergy.com",
            "location": "Seattle",
            "phone": "+12065552345"
        },
        {
            "name": "Solar Universe Seattle",
            "email": "info@solaruniverse.com",
            "location": "Seattle",
            "phone": "+12065558901"
        },
    ],
    "restaurants": [
        {
            "name": "Legal Sea Foods Boston",
            "email": "info@legalseafoods.com",
            "location": "Boston",
            "phone": "+16175551234"
        },
        {
            "name": "The Capital Grille Boston",
            "email": "info@thecapitalgrille.com",
            "location": "Boston",
            "phone": "+16175559876"
        },
        {
            "name": "Davios Boston",
            "email": "info@davios.com",
            "location": "Boston",
            "phone": "+16175554321"
        },
        {
            "name": "Boston Chops",
            "email": "info@bostonchops.com",
            "location": "Boston",
            "phone": "+16175556789"
        },
        {
            "name": "Row 34 Boston",
            "email": "info@row34.com",
            "location": "Boston",
            "phone": "+16175553456"
        },
        {
            "name": "Sarma Boston",
            "email": "info@sarmarestaurant.com",
            "location": "Boston",
            "phone": "+16175557890"
        },
        {
            "name": "Toro Boston",
            "email": "info@toro-restaurant.com",
            "location": "Boston",
            "phone": "+16175552345"
        },
        {
            "name": "Waypoint Boston",
            "email": "info@waypointcambridge.com",
            "location": "Boston",
            "phone": "+16175558901"
        },
    ],
}

# ────────────────────────────────────────────────────────────────
# WEB SERVER - Fixes Render port error
# ────────────────────────────────────────────────────────────────

class PingHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(
            b"Jarvis is alive and hunting"
        )

    def log_message(self, format, *args):
        pass

def start_web_server():
    """Start web server so Render detects port"""
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(
        ("0.0.0.0", port),
        PingHandler
    )
    thread = threading.Thread(
        target=server.serve_forever,
        daemon=True
    )
    thread.start()
    print(f"Web server running on port {port}")

# ────────────────────────────────────────────────────────────────
# CONFIG
# ────────────────────────────────────────────────────────────────

def load_config():
    return {
        "llm": {
            "model": os.environ.get(
                "MODEL",
                "groq/llama-3.3-70b-versatile"
            ),
            "api_key": GROQ_KEY,
            "temperature": 0.8,
            "max_tokens": 1000
        }
    }

# ────────────────────────────────────────────────────────────────
# AI CHAT
# ────────────────────────────────────────────────────────────────

def ask_jarvis(
    messages: list,
    config: dict
) -> str:
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
        url = (
            f"https://html.duckduckgo.com/html/"
            f"?q={requests.utils.quote(query)}"
        )
        response = requests.get(
            url, headers=HEADERS, timeout=15
        )
        soup = BeautifulSoup(
            response.text, "html.parser"
        )
        results = []
        for result in soup.find_all(
            "div", class_="result"
        )[:8]:
            title = result.find(
                "a", class_="result__a"
            )
            snippet = result.find(
                "a", class_="result__snippet"
            )
            if title:
                results.append(
                    f"Name: {title.get_text(strip=True)}\n"
                    f"Info: {snippet.get_text(strip=True) if snippet else ''}"
                )
        return "\n\n".join(results) if results else ""
    except Exception as e:
        print(f"Search error: {e}")
        return ""

def search_email(
    business_name: str,
    location: str
) -> str:
    config = load_config()
    for query in [
        f"{business_name} {location} email contact",
        f"{business_name} contact email",
    ]:
        try:
            results = search_web(query)
            if not results:
                continue
            messages = [
                {
                    "role": "system",
                    "content": (
                        "Find email in this text. "
                        "Return ONLY the email. "
                        "If none return: none"
                    )
                },
                {
                    "role": "user",
                    "content": results[:2000]
                }
            ]
            found = ask_jarvis(
                messages, config
            ).strip().lower()
            if (
                "@" in found and
                "." in found and
                len(found) < 100 and
                "none" not in found and
                " " not in found
            ):
                return found
            time.sleep(1)
        except:
            continue
    return ""

# ────────────────────────────────────────────────────────────────
# FIND BUSINESSES
# ────────────────────────────────────────────────────────────────

def find_real_businesses(
    business_type: str,
    location: str,
    country: str
) -> list:
    print(
        f"  Finding {business_type} "
        f"in {location}..."
    )
    businesses = []
    config = load_config()

    # Real database first
    db_key = business_type.lower()
    if db_key in REAL_BUSINESSES:
        db_results = REAL_BUSINESSES[db_key]
        matches = [
            b for b in db_results
            if location.lower() in
            b.get("location", "").lower()
        ]
        businesses = matches if matches else db_results[:5]
        print(f"  Database: {len(businesses)}")

    # Web search for more
    try:
        results = search_web(
            f"{business_type} {location} email"
        )
        if results:
            messages = [
                {
                    "role": "system",
                    "content": (
                        "Extract business names and emails. "
                        "Return ONLY JSON: "
                        '[{"name":"...", "email":"..."}]'
                    )
                },
                {
                    "role": "user",
                    "content": results[:3000]
                }
            ]
            response = ask_jarvis(messages, config)
            try:
                clean = response.strip()
                start = clean.find("[")
                end = clean.rfind("]") + 1
                if start >= 0 and end > start:
                    clean = clean[start:end]
                extra = json.loads(clean)
                existing = [b["name"] for b in businesses]
                if isinstance(extra, list):
                    for item in extra:
                        name = item.get("name", "")
                        email = item.get("email", "")
                        if name and name not in existing:
                            businesses.append({
                                "name": name,
                                "email": email,
                                "location": location,
                                "phone": ""
                            })
            except:
                pass
    except:
        pass

    # Fallback
    if not businesses:
        businesses = [
            {
                "name": f"Premier {business_type.title()} {location}",
                "email": "",
                "location": location,
                "phone": ""
            },
            {
                "name": f"Elite {business_type.title()} {location}",
                "email": "",
                "location": location,
                "phone": ""
            },
            {
                "name": f"Top {business_type.title()} {location}",
                "email": "",
                "location": location,
                "phone": ""
            },
        ]

    return businesses[:8]

# ────────────────────────────────────────────────────────────────
# FILE OPERATIONS
# ────────────────────────────────────────────────────────────────

def save_lead(
    name: str,
    email: str,
    location: str,
    country: str,
    status: str
):
    try:
        leads_file = "leads_database.json"
        leads = []
        if os.path.exists(leads_file):
            with open(leads_file, "r") as f:
                leads = json.load(f)
        for lead in leads:
            if lead.get(
                "business", ""
            ).lower() == name.lower():
                return
        leads.append({
            "id": len(leads) + 1,
            "business": name,
            "contact": email,
            "location": location,
            "country": country,
            "deal_value": "$2,000",
            "status": status,
            "date": datetime.now().strftime(
                "%Y-%m-%d %H:%M"
            )
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
        sent = len([
            l for l in leads
            if l.get("status") == "Email Sent"
        ])
        return f"{len(leads)} leads. {sent} sent."
    except:
        return "Error."

def write_file(filename: str, content: str):
    try:
        with open(
            filename, "w", encoding="utf-8"
        ) as f:
            f.write(content)
    except Exception as e:
        print(f"Write error: {e}")

def log_email(
    name: str,
    email: str,
    status: str
):
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
            "time": datetime.now().strftime(
                "%Y-%m-%d %H:%M"
            )
        })
        with open(log_file, "w") as f:
            json.dump(logs, f, indent=2)
    except Exception as e:
        print(f"Log error: {e}")

# ────────────────────────────────────────────────────────────────
# EMAIL HTML BUILDER
# ────────────────────────────────────────────────────────────────

def build_email_html(
    business_name: str,
    pitch: str
) -> str:
    return f"""
<html>
<body style="font-family:Arial,sans-serif;
             max-width:600px;
             margin:0 auto;
             padding:20px;">

    <div style="background:#1a1a2e;
                padding:20px;
                border-radius:8px;
                margin-bottom:20px;">
        <h2 style="color:#ffffff;margin:0;">
            {COMPANY}
        </h2>
        <p style="color:#cccccc;
                  margin:5px 0 0 0;
                  font-size:14px;">
            We build websites that make money
        </p>
    </div>

    <div style="padding:20px;
                background:#f9f9f9;
                border-radius:8px;
                line-height:1.8;
                color:#333333;">
        {pitch.replace(chr(10), "<br>")}
    </div>

    <div style="margin-top:20px;
                padding:15px;
                border-top:2px solid #1a1a2e;
                color:#333333;">
        <p style="margin:0;">
            <strong>Dan</strong><br>
            Managing Partner<br>
            {COMPANY}<br>
            WhatsApp: {WHATSAPP}<br>
            Email: {GMAIL_USER}
        </p>
    </div>

    <div style="margin-top:10px;
                padding:8px;
                text-align:center;
                font-size:11px;
                color:#999999;">
        To unsubscribe reply STOP.
    </div>

</body>
</html>
    """

# ────────────────────────────────────────────────────────────────
# EMAIL SENDERS
# ────────────────────────────────────────────────────────────────

def send_via_gmail(
    to_email: str,
    subject: str,
    html: str
) -> bool:
    if not GMAIL_USER or not GMAIL_PASS:
        return False
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = (
            f"Dan - {COMPANY} <{GMAIL_USER}>"
        )
        msg["To"] = to_email
        msg.attach(MIMEText(html, "html"))

        with smtplib.SMTP_SSL(
            "smtp.gmail.com", 465
        ) as server:
            server.login(GMAIL_USER, GMAIL_PASS)
            server.sendmail(
                GMAIL_USER,
                to_email,
                msg.as_string()
            )
        print(f"Gmail sent to {to_email}")
        return True
    except Exception as e:
        print(f"Gmail error: {e}")
        return False

def send_via_resend(
    to_email: str,
    subject: str,
    html: str
) -> bool:
    if not RESEND_KEY:
        return False
    try:
        resend.api_key = RESEND_KEY
        if FROM_DOMAIN:
            from_email = f"Dan <dan@{FROM_DOMAIN}>"
        else:
            from_email = "onboarding@resend.dev"
            to_email = GMAIL_USER

        response = resend.Emails.send({
            "from": from_email,
            "to": to_email,
            "subject": subject,
            "html": html
        })
        if response and response.get("id"):
            print(f"Resend sent to {to_email}")
            return True
        return False
    except Exception as e:
        print(f"Resend error: {e}")
        return False

def send_email(
    to_email: str,
    business_name: str,
    pitch: str
) -> bool:
    """
    Smart email sender.
    Tries Gmail first then Resend.
    Gmail works on Render free tier.
    """
    subject = (
        f"Website Growth Proposal "
        f"for {business_name}"
    )
    html = build_email_html(business_name, pitch)

    # Try Gmail first
    if GMAIL_USER and GMAIL_PASS:
        success = send_via_gmail(
            to_email, subject, html
        )
        if success:
            return True
        print("Gmail failed. Trying Resend...")

    # Try Resend as backup
    if RESEND_KEY:
        return send_via_resend(
            to_email, subject, html
        )

    print("No email method configured.")
    return False

# ────────────────────────────────────────────────────────────────
# CONTENT WRITERS
# ────────────────────────────────────────────────────────────────

def write_pitch(
    business_name: str,
    business_type: str,
    location: str,
    config: dict
) -> str:
    messages = [
        {
            "role": "system",
            "content": (
                f"Elite sales agent for {COMPANY}. "
                f"Write sharp email pitch. "
                f"Price $2000. Show ROI. "
                f"Under 120 words. USA tone. "
                f"Paragraphs not bullet points."
            )
        },
        {
            "role": "user",
            "content": (
                f"Business: {business_name}\n"
                f"Type: {business_type}\n"
                f"Location: {location}\n"
                f"Price: $2,000\n"
                f"Contact: {WHATSAPP} or {GMAIL_USER}"
            )
        }
    ]
    pitch = ask_jarvis(messages, config)
    if not pitch:
        pitch = (
            f"Hi {business_name} team,\n\n"
            f"I help {business_type} in {location} "
            f"get more clients online.\n\n"
            f"Our Growth Package at $2,000 includes "
            f"a professional website, WhatsApp "
            f"integration, lead capture, and SEO. "
            f"Most clients see ROI within 60 days.\n\n"
            f"Interested? WhatsApp: {WHATSAPP}\n\n"
            f"Dan\n{COMPANY}"
        )
    return pitch

def write_call_script(
    business_name: str,
    business_type: str,
    location: str,
    config: dict
) -> str:
    messages = [
        {
            "role": "system",
            "content": (
                f"Sales coach for {COMPANY}. "
                f"Write short phone call script. "
                f"Natural conversational. "
                f"Under 100 words. "
                f"Include greeting value prop "
                f"and ask for meeting."
            )
        },
        {
            "role": "user",
            "content": (
                f"Call script for:\n"
                f"Business: {business_name}\n"
                f"Type: {business_type}\n"
                f"Location: {location}\n"
                f"Goal: Book 15 min demo"
            )
        }
    ]
    script = ask_jarvis(messages, config)
    if not script:
        script = (
            f"Hi may I speak with the owner please?\n\n"
            f"Hi my name is Dan from {COMPANY}.\n\n"
            f"I help {business_type} in {location} "
            f"get more clients with professional websites.\n\n"
            f"We build complete sites for just $2,000 "
            f"and most clients see results in 60 days.\n\n"
            f"Would you have 15 minutes this week "
            f"for a quick demo?\n\n"
            f"Objection response:\n"
            f"I understand. One new client from your "
            f"website pays for the whole thing."
        )
    return script

def write_whatsapp_message(
    business_name: str,
    business_type: str,
    location: str,
    config: dict
) -> str:
    messages = [
        {
            "role": "system",
            "content": (
                f"Sales agent for {COMPANY}. "
                f"Write short WhatsApp message. "
                f"Conversational and friendly. "
                f"Under 60 words. "
                f"Like a real person texting. "
                f"End with a question."
            )
        },
        {
            "role": "user",
            "content": (
                f"WhatsApp for:\n"
                f"Business: {business_name}\n"
                f"Type: {business_type}\n"
                f"Location: {location}\n"
                f"Price: $2,000"
            )
        }
    ]
    msg = ask_jarvis(messages, config)
    if not msg:
        msg = (
            f"Hi! I help {business_type} in "
            f"{location} get more clients online.\n\n"
            f"We build professional websites "
            f"for $2,000 that bring in real business.\n\n"
            f"Would you be open to a quick chat?"
        )
    return msg

def generate_whatsapp_link(
    phone: str,
    message: str
) -> str:
    if not phone:
        phone = WHATSAPP
    clean = "".join(filter(str.isdigit, phone))
    encoded = urllib.parse.quote(message)
    return f"https://wa.me/{clean}?text={encoded}"

# ────────────────────────────────────────────────────────────────
# DAILY SUMMARY EMAIL TO DAN
# ────────────────────────────────────────────────────────────────

def send_daily_summary(
    business_type: str,
    location: str,
    all_data: list,
    emails_sent: int
):
    """Send Dan a summary with all pitches scripts and links"""
    pitches_html = ""
    for i, p in enumerate(all_data, 1):
        pitches_html += f"""
<div style="background:white;
            padding:20px;
            margin-bottom:20px;
            border-radius:8px;
            border-left:4px solid #1a1a2e;">

    <h3 style="color:#1a1a2e;margin:0 0 8px 0;">
        {i}. {p['name']}
    </h3>
    <p style="margin:0 0 15px 0;
              font-size:13px;color:#666;">
        Email: {p['email'] or 'Find manually'} |
        Phone: {p.get('phone') or 'Find manually'}
    </p>

    <details style="margin-bottom:8px;">
        <summary style="cursor:pointer;
                        font-weight:bold;
                        color:#1a1a2e;
                        padding:8px;
                        background:#e8f0fe;
                        border-radius:5px;">
            Email Pitch (Sent Automatically)
        </summary>
        <div style="padding:12px;
                    background:#f9f9f9;
                    margin-top:5px;
                    border-radius:5px;
                    line-height:1.7;
                    font-size:14px;">
            {p['pitch'].replace(chr(10), '<br>')}
        </div>
    </details>

    <details style="margin-bottom:8px;">
        <summary style="cursor:pointer;
                        font-weight:bold;
                        color:#d4380d;
                        padding:8px;
                        background:#fff2e8;
                        border-radius:5px;">
            Call Script (Call Them Today)
        </summary>
        <div style="padding:12px;
                    background:#fff7f0;
                    margin-top:5px;
                    border-radius:5px;
                    line-height:1.7;
                    font-size:14px;">
            {p['call_script'].replace(chr(10), '<br>')}
        </div>
    </details>

    <details>
        <summary style="cursor:pointer;
                        font-weight:bold;
                        color:#389e0d;
                        padding:8px;
                        background:#f6ffed;
                        border-radius:5px;">
            WhatsApp Message (Click to Send)
        </summary>
        <div style="padding:12px;
                    background:#f0fff4;
                    margin-top:5px;
                    border-radius:5px;
                    line-height:1.7;
                    font-size:14px;">
            {p['wa_message'].replace(chr(10), '<br>')}
            <br><br>
            <a href="{p['wa_link']}"
               style="background:#25D366;
                      color:white;
                      padding:10px 20px;
                      border-radius:20px;
                      text-decoration:none;
                      font-weight:bold;
                      font-size:14px;">
                Open WhatsApp and Send
            </a>
        </div>
    </details>

</div>
        """

    html = f"""
<html>
<body style="font-family:Arial,sans-serif;
             max-width:700px;
             margin:0 auto;
             padding:20px;
             background:#f5f5f5;">

    <div style="background:#1a1a2e;
                padding:25px;
                border-radius:10px;
                margin-bottom:20px;
                text-align:center;">
        <h1 style="color:white;margin:0;
                   font-size:22px;">
            Jarvis Daily Hunt Report
        </h1>
        <p style="color:#ccc;margin:8px 0 0 0;">
            {business_type.title()} in {location}
            | {datetime.now().strftime("%Y-%m-%d %H:%M")}
        </p>
    </div>

    <div style="background:#e6f7ff;
                padding:15px;
                border-radius:8px;
                margin-bottom:15px;
                border:1px solid #91d5ff;">
        <strong>Today Stats:</strong><br>
        Businesses found: {len(all_data)}<br>
        Emails sent automatically: {emails_sent}<br>
        Need manual email: {len(all_data) - emails_sent}
    </div>

    <div style="background:#fff7e6;
                padding:15px;
                border-radius:8px;
                margin-bottom:20px;
                border:1px solid #ffd591;">
        <strong>Your Action Plan Dan:</strong><br>
        1. Emails already sent automatically<br>
        2. Call 3 businesses using scripts below<br>
        3. Click WhatsApp links to send messages<br>
        4. Follow up on previous replies<br>
        5. Close deals at $2,000 each
    </div>

    {pitches_html}

    <div style="background:#1a1a2e;
                padding:15px;
                border-radius:8px;
                text-align:center;
                color:#ccc;
                font-size:13px;">
        Jarvis Cloud {VERSION} | {COMPANY}<br>
        WhatsApp: {WHATSAPP}
    </div>

</body>
</html>
    """

    subject = (
        f"Jarvis: {len(all_data)} leads ready "
        f"| {emails_sent} emails sent "
        f"| {business_type} {location}"
    )

    # Send to Dan
    if GMAIL_USER and GMAIL_PASS:
        send_via_gmail(GMAIL_USER, subject, html)
    elif RESEND_KEY:
        try:
            resend.api_key = RESEND_KEY
            resend.Emails.send({
                "from": "onboarding@resend.dev",
                "to": GMAIL_USER,
                "subject": subject,
                "html": html
            })
        except Exception as e:
            print(f"Summary email error: {e}")

# ────────────────────────────────────────────────────────────────
# AUTO HUNT
# ────────────────────────────────────────────────────────────────

def auto_hunt(
    business_type: str,
    location: str,
    country: str,
    config: dict
):
    print(f"""
=====================================
AUTO HUNT + EMAIL {VERSION}
Target:   {business_type}
Location: {location}, {country}
Time:     {datetime.now().strftime("%Y-%m-%d %H:%M")}
=====================================
    """)

    emails_sent = 0
    all_data = []

    try:
        businesses = find_real_businesses(
            business_type, location, country
        )

        if not businesses:
            print("No businesses found.")
            return

        print(f"Processing {len(businesses)}...")

        for biz in businesses:
            name = biz.get("name", "")
            email = biz.get("email", "")
            phone = biz.get("phone", "")

            if not name:
                continue

            print(f"\nProcessing: {name}")

            # Find email if missing
            if not email or "@" not in email:
                print(f"  Searching email...")
                email = search_email(name, location)
                if email:
                    print(f"  Found: {email}")

            # Write all content
            pitch = write_pitch(
                name, business_type,
                location, config
            )
            call_script = write_call_script(
                name, business_type,
                location, config
            )
            wa_message = write_whatsapp_message(
                name, business_type,
                location, config
            )
            wa_link = generate_whatsapp_link(
                phone, wa_message
            )

            all_data.append({
                "name": name,
                "email": email,
                "phone": phone,
                "pitch": pitch,
                "call_script": call_script,
                "wa_message": wa_message,
                "wa_link": wa_link
            })

            # Send email to client
            if (
                email and
                "@" in email and
                "." in email and
                len(email) < 100
            ):
                success = send_email(
                    email, name, pitch
                )
                if success:
                    emails_sent += 1
                    log_email(name, email, "Sent")
                    save_lead(
                        name, email,
                        location, country,
                        "Email Sent"
                    )
                else:
                    log_email(name, email, "Failed")
                    save_lead(
                        name, email,
                        location, country,
                        "Email Failed"
                    )
            else:
                save_lead(
                    name, "No email",
                    location, country,
                    "Need Email"
                )
                print(f"  No email. Saved for manual.")

            time.sleep(3)

        # Send daily summary to Dan
        send_daily_summary(
            business_type, location,
            all_data, emails_sent
        )

        # Save report file
        timestamp = datetime.now().strftime(
            "%Y%m%d_%H%M%S"
        )
        filename = (
            f"hunt_{business_type}_"
            f"{location}_{timestamp}.txt"
            .replace(" ", "_")
        )

        report = f"""
HUNT REPORT {VERSION}
====================
Company:     {COMPANY}
Date:        {datetime.now().strftime("%Y-%m-%d %H:%M")}
Target:      {business_type}
Location:    {location}, {country}
Total:       {len(all_data)}
Emails sent: {emails_sent}

"""
        for p in all_data:
            report += f"""
{'='*60}
BUSINESS: {p['name']}
EMAIL:     {p['email'] or 'Not found'}
PHONE:     {p['phone'] or 'Not found'}

EMAIL PITCH:
{p['pitch']}

CALL SCRIPT:
{p['call_script']}

WHATSAPP:
{p['wa_message']}

WHATSAPP LINK:
{p['wa_link']}
"""

        write_file(filename, report)

        print(f"""
=====================================
HUNT COMPLETE {VERSION}
Total:       {len(all_data)}
Emails sent: {emails_sent}
Report:      {filename}
Summary:     Sent to {GMAIL_USER}
=====================================
        """)

    except Exception as e:
        print(f"Hunt error: {e}")

# ────────────────────────────────────────────────────────────────
# SCHEDULED TASKS
# ────────────────────────────────────────────────────────────────

def morning_hunt(config: dict):
    print("\nMORNING USA CAMPAIGN\n")

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
            email_count = len([
                l for l in logs
                if l.get("status") == "Sent"
            ])
    messages = [
        {
            "role": "system",
            "content": "Jarvis. Sharp report. 60 words."
        },
        {
            "role": "user",
            "content": (
                f"Leads: {leads}\n"
                f"Emails: {email_count}\n"
                f"Summary and top 3 priorities for Dan."
            )
        }
    ]
    report = ask_jarvis(messages, config)
    print(f"\nREPORT:\n{report}\n")
    write_file(
        f"report_{datetime.now().strftime('%Y%m%d')}.txt",
        report
    )

def midday_followup(config: dict):
    print("\nMIDDAY FOLLOWUP\n")
    leads = view_leads()
    messages = [
        {
            "role": "system",
            "content": "Jarvis. 30 words max."
        },
        {
            "role": "user",
            "content": f"Leads: {leads}. Dan reminder."
        }
    ]
    reminder = ask_jarvis(messages, config)
    print(f"\nREMINDER:\n{reminder}\n")

# ────────────────────────────────────────────────────────────────
# SCHEDULER
# ────────────────────────────────────────────────────────────────

def start_scheduler(config: dict):
    print("""
====================================
SCHEDULER ACTIVE
Morning Hunt:    08:00 AM
Midday Followup: 12:00 PM
Evening Report:  07:00 PM
====================================
    """)

    schedule.every().day.at("08:00").do(
        morning_hunt, config=config
    )
    schedule.every().day.at("12:00").do(
        midday_followup, config=config
    )
    schedule.every().day.at("19:00").do(
        evening_report, config=config
    )

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
  Model: Groq Llama 3.3 70B
  Market: USA PRIMARY
  Email: Gmail + Resend
  Calls: Scripts Generated
  WhatsApp: Links Generated
  Mode: 24/7 Autonomous
====================================
    """)

    # Start web server first
    # This fixes the Render port error
    start_web_server()

    if not GROQ_KEY:
        print("ERROR: GROQ_API_KEY not set!")
        return

    # Show email status
    if GMAIL_USER and GMAIL_PASS:
        print(
            "Email: Gmail\n"
            "Sending directly to clients"
        )
    elif RESEND_KEY and FROM_DOMAIN:
        print(
            "Email: Resend with domain\n"
            "Sending directly to clients"
        )
    elif RESEND_KEY:
        print(
            "Email: Resend\n"
            "Sending to Dan only\n"
            "Get domain to send to clients"
        )
    else:
        print(
            "WARNING: No email configured\n"
            "Add GMAIL_USER and GMAIL_PASS"
        )

    config = load_config()

    # Run startup hunt
    print("\nRunning startup hunt...")
    auto_hunt(
        "law firms",
        "New York",
        "USA",
        config
    )

    # Start scheduler
    start_scheduler(config)

if __name__ == "__main__":
    main()import json
import os
import time
import schedule
import requests
import smtplib
import threading
import urllib.parse
import resend
from http.server import HTTPServer, BaseHTTPRequestHandler
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from bs4 import BeautifulSoup
from datetime import datetime
from litellm import completion

# ────────────────────────────────────────────────────────────────
# SETUP
# ────────────────────────────────────────────────────────────────

GROQ_KEY = os.environ.get("GROQ_API_KEY", "")
GMAIL_USER = os.environ.get(
    "GMAIL_USER",
    "elizabethnzasi530@gmail.com"
)
GMAIL_PASS = os.environ.get("GMAIL_PASS", "")
RESEND_KEY = os.environ.get("RESEND_KEY", "")
FROM_DOMAIN = os.environ.get("FROM_DOMAIN", "")
WHATSAPP = os.environ.get(
    "WHATSAPP", "+254118240486"
)
USER_NAME = "Dan"
COMPANY = "Digital Growth Agency"
VERSION = "v8"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}

# ────────────────────────────────────────────────────────────────
# REAL USA BUSINESS DATABASE
# ────────────────────────────────────────────────────────────────

REAL_BUSINESSES = {
    "law firms": [
        {
            "name": "Jacoby and Meyers Law",
            "email": "info@jacobyandmeyers.com",
            "location": "New York",
            "phone": "+12125551234"
        },
        {
            "name": "Cellino Law",
            "email": "info@cellinolaw.com",
            "location": "New York",
            "phone": "+17165551234"
        },
        {
            "name": "The Barnes Firm",
            "email": "info@thebarnesfirm.com",
            "location": "New York",
            "phone": "+12125559876"
        },
        {
            "name": "Block O Toole and Murphy",
            "email": "info@blockotoole.com",
            "location": "New York",
            "phone": "+12125554321"
        },
        {
            "name": "Sullivan and Cromwell",
            "email": "info@sullcrom.com",
            "location": "New York",
            "phone": "+12125556789"
        },
        {
            "name": "Skadden Arps",
            "email": "info@skadden.com",
            "location": "New York",
            "phone": "+12125553456"
        },
        {
            "name": "Davis Polk and Wardwell",
            "email": "info@davispolk.com",
            "location": "New York",
            "phone": "+12125557890"
        },
        {
            "name": "Cleary Gottlieb",
            "email": "info@cgsh.com",
            "location": "New York",
            "phone": "+12125552345"
        },
    ],
    "dental clinics": [
        {
            "name": "Aspen Dental LA",
            "email": "info@aspendental.com",
            "location": "Los Angeles",
            "phone": "+13105551234"
        },
        {
            "name": "Pacific Dental Services",
            "email": "info@pacificdentalservices.com",
            "location": "Los Angeles",
            "phone": "+13105559876"
        },
        {
            "name": "Western Dental",
            "email": "info@westerndental.com",
            "location": "Los Angeles",
            "phone": "+13105554321"
        },
        {
            "name": "LA Dental Center",
            "email": "contact@ladentalcenter.com",
            "location": "Los Angeles",
            "phone": "+13105556789"
        },
        {
            "name": "Smile Generation",
            "email": "info@smilegeneration.com",
            "location": "Los Angeles",
            "phone": "+13105553456"
        },
        {
            "name": "Beverly Hills Dental",
            "email": "info@beverlyhillsdental.com",
            "location": "Los Angeles",
            "phone": "+13105557890"
        },
        {
            "name": "Brite Dental",
            "email": "info@britedental.com",
            "location": "Los Angeles",
            "phone": "+13105552345"
        },
        {
            "name": "Premier Dental LA",
            "email": "info@premierdentalla.com",
            "location": "Los Angeles",
            "phone": "+13105558901"
        },
    ],
    "real estate agents": [
        {
            "name": "Keller Williams Chicago",
            "email": "info@kwchicago.com",
            "location": "Chicago",
            "phone": "+13125551234"
        },
        {
            "name": "Century 21 Chicago",
            "email": "info@century21chicago.com",
            "location": "Chicago",
            "phone": "+13125559876"
        },
        {
            "name": "Coldwell Banker Chicago",
            "email": "info@cbchicago.com",
            "location": "Chicago",
            "phone": "+13125554321"
        },
        {
            "name": "Baird and Warner",
            "email": "info@bairdwarner.com",
            "location": "Chicago",
            "phone": "+13125556789"
        },
        {
            "name": "RE MAX Chicago",
            "email": "info@remaxchicago.com",
            "location": "Chicago",
            "phone": "+13125553456"
        },
        {
            "name": "Compass Chicago",
            "email": "chicago@compass.com",
            "location": "Chicago",
            "phone": "+13125557890"
        },
        {
            "name": "Dream Town Realty",
            "email": "info@dreamtown.com",
            "location": "Chicago",
            "phone": "+13125552345"
        },
        {
            "name": "Berkshire Hathaway Chicago",
            "email": "info@bhhschicago.com",
            "location": "Chicago",
            "phone": "+13125558901"
        },
    ],
    "medical clinics": [
        {
            "name": "CareNow Houston",
            "email": "info@carenow.com",
            "location": "Houston",
            "phone": "+17135551234"
        },
        {
            "name": "NextCare Urgent Care",
            "email": "info@nextcare.com",
            "location": "Houston",
            "phone": "+17135559876"
        },
        {
            "name": "AFC Urgent Care",
            "email": "info@afcurgentcare.com",
            "location": "Houston",
            "phone": "+17135554321"
        },
        {
            "name": "Concentra Houston",
            "email": "info@concentra.com",
            "location": "Houston",
            "phone": "+17135556789"
        },
        {
            "name": "Memorial Hermann",
            "email": "info@memorialhermann.org",
            "location": "Houston",
            "phone": "+17135553456"
        },
        {
            "name": "Houston Methodist",
            "email": "info@houstonmethodist.org",
            "location": "Houston",
            "phone": "+17135557890"
        },
        {
            "name": "Kelsey Seybold Clinic",
            "email": "info@kelsey-seybold.com",
            "location": "Houston",
            "phone": "+17135552345"
        },
        {
            "name": "Texas Medical Center",
            "email": "info@tmc.edu",
            "location": "Houston",
            "phone": "+17135558901"
        },
    ],
    "gyms": [
        {
            "name": "Equinox Miami",
            "email": "miami@equinox.com",
            "location": "Miami",
            "phone": "+13055551234"
        },
        {
            "name": "LA Fitness Miami",
            "email": "info@lafitness.com",
            "location": "Miami",
            "phone": "+13055559876"
        },
        {
            "name": "Planet Fitness Miami",
            "email": "info@planetfitness.com",
            "location": "Miami",
            "phone": "+13055554321"
        },
        {
            "name": "Gold's Gym Miami",
            "email": "miami@goldsgym.com",
            "location": "Miami",
            "phone": "+13055556789"
        },
        {
            "name": "Crunch Fitness Miami",
            "email": "info@crunch.com",
            "location": "Miami",
            "phone": "+13055553456"
        },
        {
            "name": "Barry's Bootcamp Miami",
            "email": "miami@barrys.com",
            "location": "Miami",
            "phone": "+13055557890"
        },
        {
            "name": "F45 Training Miami",
            "email": "info@f45training.com",
            "location": "Miami",
            "phone": "+13055552345"
        },
        {
            "name": "SoulCycle Miami",
            "email": "info@soul-cycle.com",
            "location": "Miami",
            "phone": "+13055558901"
        },
    ],
    "hvac companies": [
        {
            "name": "One Hour Air Dallas",
            "email": "info@onehourhvac.com",
            "location": "Dallas",
            "phone": "+12145551234"
        },
        {
            "name": "Aire Serv Dallas",
            "email": "info@aireserv.com",
            "location": "Dallas",
            "phone": "+12145559876"
        },
        {
            "name": "Service Experts Dallas",
            "email": "info@serviceexperts.com",
            "location": "Dallas",
            "phone": "+12145554321"
        },
        {
            "name": "Comfort Systems Dallas",
            "email": "info@comfortsystems.com",
            "location": "Dallas",
            "phone": "+12145556789"
        },
        {
            "name": "Lennox International",
            "email": "info@lennox.com",
            "location": "Dallas",
            "phone": "+12145553456"
        },
        {
            "name": "Trane Dallas",
            "email": "info@trane.com",
            "location": "Dallas",
            "phone": "+12145557890"
        },
        {
            "name": "Carrier Dallas",
            "email": "info@carrier.com",
            "location": "Dallas",
            "phone": "+12145552345"
        },
        {
            "name": "ABC Home Commercial",
            "email": "info@abchomeandcommercial.com",
            "location": "Dallas",
            "phone": "+12145558901"
        },
    ],
    "solar installers": [
        {
            "name": "Sunrun Seattle",
            "email": "info@sunrun.com",
            "location": "Seattle",
            "phone": "+12065551234"
        },
        {
            "name": "SunPower Seattle",
            "email": "info@sunpower.com",
            "location": "Seattle",
            "phone": "+12065559876"
        },
        {
            "name": "Tesla Solar Seattle",
            "email": "solarcity@tesla.com",
            "location": "Seattle",
            "phone": "+12065554321"
        },
        {
            "name": "Vivint Solar Seattle",
            "email": "info@vivintsolar.com",
            "location": "Seattle",
            "phone": "+12065556789"
        },
        {
            "name": "NW Wind and Solar",
            "email": "info@nwwindandsolar.com",
            "location": "Seattle",
            "phone": "+12065553456"
        },
        {
            "name": "Puget Sound Solar",
            "email": "info@pugetsoundsolar.com",
            "location": "Seattle",
            "phone": "+12065557890"
        },
        {
            "name": "Green Power Energy",
            "email": "info@greenpowerenergy.com",
            "location": "Seattle",
            "phone": "+12065552345"
        },
        {
            "name": "Solar Universe Seattle",
            "email": "info@solaruniverse.com",
            "location": "Seattle",
            "phone": "+12065558901"
        },
    ],
    "restaurants": [
        {
            "name": "Legal Sea Foods Boston",
            "email": "info@legalseafoods.com",
            "location": "Boston",
            "phone": "+16175551234"
        },
        {
            "name": "The Capital Grille Boston",
            "email": "info@thecapitalgrille.com",
            "location": "Boston",
            "phone": "+16175559876"
        },
        {
            "name": "Davios Boston",
            "email": "info@davios.com",
            "location": "Boston",
            "phone": "+16175554321"
        },
        {
            "name": "Boston Chops",
            "email": "info@bostonchops.com",
            "location": "Boston",
            "phone": "+16175556789"
        },
        {
            "name": "Row 34 Boston",
            "email": "info@row34.com",
            "location": "Boston",
            "phone": "+16175553456"
        },
        {
            "name": "Sarma Boston",
            "email": "info@sarmarestaurant.com",
            "location": "Boston",
            "phone": "+16175557890"
        },
        {
            "name": "Toro Boston",
            "email": "info@toro-restaurant.com",
            "location": "Boston",
            "phone": "+16175552345"
        },
        {
            "name": "Waypoint Boston",
            "email": "info@waypointcambridge.com",
            "location": "Boston",
            "phone": "+16175558901"
        },
    ],
}

# ────────────────────────────────────────────────────────────────
# WEB SERVER - Fixes Render port error
# ────────────────────────────────────────────────────────────────

class PingHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(
            b"Jarvis is alive and hunting"
        )

    def log_message(self, format, *args):
        pass

def start_web_server():
    """Start web server so Render detects port"""
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(
        ("0.0.0.0", port),
        PingHandler
    )
    thread = threading.Thread(
        target=server.serve_forever,
        daemon=True
    )
    thread.start()
    print(f"Web server running on port {port}")

# ────────────────────────────────────────────────────────────────
# CONFIG
# ────────────────────────────────────────────────────────────────

def load_config():
    return {
        "llm": {
            "model": os.environ.get(
                "MODEL",
                "groq/llama-3.3-70b-versatile"
            ),
            "api_key": GROQ_KEY,
            "temperature": 0.8,
            "max_tokens": 1000
        }
    }

# ────────────────────────────────────────────────────────────────
# AI CHAT
# ────────────────────────────────────────────────────────────────

def ask_jarvis(
    messages: list,
    config: dict
) -> str:
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
        url = (
            f"https://html.duckduckgo.com/html/"
            f"?q={requests.utils.quote(query)}"
        )
        response = requests.get(
            url, headers=HEADERS, timeout=15
        )
        soup = BeautifulSoup(
            response.text, "html.parser"
        )
        results = []
        for result in soup.find_all(
            "div", class_="result"
        )[:8]:
            title = result.find(
                "a", class_="result__a"
            )
            snippet = result.find(
                "a", class_="result__snippet"
            )
            if title:
                results.append(
                    f"Name: {title.get_text(strip=True)}\n"
                    f"Info: {snippet.get_text(strip=True) if snippet else ''}"
                )
        return "\n\n".join(results) if results else ""
    except Exception as e:
        print(f"Search error: {e}")
        return ""

def search_email(
    business_name: str,
    location: str
) -> str:
    config = load_config()
    for query in [
        f"{business_name} {location} email contact",
        f"{business_name} contact email",
    ]:
        try:
            results = search_web(query)
            if not results:
                continue
            messages = [
                {
                    "role": "system",
                    "content": (
                        "Find email in this text. "
                        "Return ONLY the email. "
                        "If none return: none"
                    )
                },
                {
                    "role": "user",
                    "content": results[:2000]
                }
            ]
            found = ask_jarvis(
                messages, config
            ).strip().lower()
            if (
                "@" in found and
                "." in found and
                len(found) < 100 and
                "none" not in found and
                " " not in found
            ):
                return found
            time.sleep(1)
        except:
            continue
    return ""

# ────────────────────────────────────────────────────────────────
# FIND BUSINESSES
# ────────────────────────────────────────────────────────────────

def find_real_businesses(
    business_type: str,
    location: str,
    country: str
) -> list:
    print(
        f"  Finding {business_type} "
        f"in {location}..."
    )
    businesses = []
    config = load_config()

    # Real database first
    db_key = business_type.lower()
    if db_key in REAL_BUSINESSES:
        db_results = REAL_BUSINESSES[db_key]
        matches = [
            b for b in db_results
            if location.lower() in
            b.get("location", "").lower()
        ]
        businesses = matches if matches else db_results[:5]
        print(f"  Database: {len(businesses)}")

    # Web search for more
    try:
        results = search_web(
            f"{business_type} {location} email"
        )
        if results:
            messages = [
                {
                    "role": "system",
                    "content": (
                        "Extract business names and emails. "
                        "Return ONLY JSON: "
                        '[{"name":"...", "email":"..."}]'
                    )
                },
                {
                    "role": "user",
                    "content": results[:3000]
                }
            ]
            response = ask_jarvis(messages, config)
            try:
                clean = response.strip()
                start = clean.find("[")
                end = clean.rfind("]") + 1
                if start >= 0 and end > start:
                    clean = clean[start:end]
                extra = json.loads(clean)
                existing = [b["name"] for b in businesses]
                if isinstance(extra, list):
                    for item in extra:
                        name = item.get("name", "")
                        email = item.get("email", "")
                        if name and name not in existing:
                            businesses.append({
                                "name": name,
                                "email": email,
                                "location": location,
                                "phone": ""
                            })
            except:
                pass
    except:
        pass

    # Fallback
    if not businesses:
        businesses = [
            {
                "name": f"Premier {business_type.title()} {location}",
                "email": "",
                "location": location,
                "phone": ""
            },
            {
                "name": f"Elite {business_type.title()} {location}",
                "email": "",
                "location": location,
                "phone": ""
            },
            {
                "name": f"Top {business_type.title()} {location}",
                "email": "",
                "location": location,
                "phone": ""
            },
        ]

    return businesses[:8]

# ────────────────────────────────────────────────────────────────
# FILE OPERATIONS
# ────────────────────────────────────────────────────────────────

def save_lead(
    name: str,
    email: str,
    location: str,
    country: str,
    status: str
):
    try:
        leads_file = "leads_database.json"
        leads = []
        if os.path.exists(leads_file):
            with open(leads_file, "r") as f:
                leads = json.load(f)
        for lead in leads:
            if lead.get(
                "business", ""
            ).lower() == name.lower():
                return
        leads.append({
            "id": len(leads) + 1,
            "business": name,
            "contact": email,
            "location": location,
            "country": country,
            "deal_value": "$2,000",
            "status": status,
            "date": datetime.now().strftime(
                "%Y-%m-%d %H:%M"
            )
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
        sent = len([
            l for l in leads
            if l.get("status") == "Email Sent"
        ])
        return f"{len(leads)} leads. {sent} sent."
    except:
        return "Error."

def write_file(filename: str, content: str):
    try:
        with open(
            filename, "w", encoding="utf-8"
        ) as f:
            f.write(content)
    except Exception as e:
        print(f"Write error: {e}")

def log_email(
    name: str,
    email: str,
    status: str
):
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
            "time": datetime.now().strftime(
                "%Y-%m-%d %H:%M"
            )
        })
        with open(log_file, "w") as f:
            json.dump(logs, f, indent=2)
    except Exception as e:
        print(f"Log error: {e}")

# ────────────────────────────────────────────────────────────────
# EMAIL HTML BUILDER
# ────────────────────────────────────────────────────────────────

def build_email_html(
    business_name: str,
    pitch: str
) -> str:
    return f"""
<html>
<body style="font-family:Arial,sans-serif;
             max-width:600px;
             margin:0 auto;
             padding:20px;">

    <div style="background:#1a1a2e;
                padding:20px;
                border-radius:8px;
                margin-bottom:20px;">
        <h2 style="color:#ffffff;margin:0;">
            {COMPANY}
        </h2>
        <p style="color:#cccccc;
                  margin:5px 0 0 0;
                  font-size:14px;">
            We build websites that make money
        </p>
    </div>

    <div style="padding:20px;
                background:#f9f9f9;
                border-radius:8px;
                line-height:1.8;
                color:#333333;">
        {pitch.replace(chr(10), "<br>")}
    </div>

    <div style="margin-top:20px;
                padding:15px;
                border-top:2px solid #1a1a2e;
                color:#333333;">
        <p style="margin:0;">
            <strong>Dan</strong><br>
            Managing Partner<br>
            {COMPANY}<br>
            WhatsApp: {WHATSAPP}<br>
            Email: {GMAIL_USER}
        </p>
    </div>

    <div style="margin-top:10px;
                padding:8px;
                text-align:center;
                font-size:11px;
                color:#999999;">
        To unsubscribe reply STOP.
    </div>

</body>
</html>
    """

# ────────────────────────────────────────────────────────────────
# EMAIL SENDERS
# ────────────────────────────────────────────────────────────────

def send_via_gmail(
    to_email: str,
    subject: str,
    html: str
) -> bool:
    if not GMAIL_USER or not GMAIL_PASS:
        return False
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = (
            f"Dan - {COMPANY} <{GMAIL_USER}>"
        )
        msg["To"] = to_email
        msg.attach(MIMEText(html, "html"))

        with smtplib.SMTP_SSL(
            "smtp.gmail.com", 465
        ) as server:
            server.login(GMAIL_USER, GMAIL_PASS)
            server.sendmail(
                GMAIL_USER,
                to_email,
                msg.as_string()
            )
        print(f"Gmail sent to {to_email}")
        return True
    except Exception as e:
        print(f"Gmail error: {e}")
        return False

def send_via_resend(
    to_email: str,
    subject: str,
    html: str
) -> bool:
    if not RESEND_KEY:
        return False
    try:
        resend.api_key = RESEND_KEY
        if FROM_DOMAIN:
            from_email = f"Dan <dan@{FROM_DOMAIN}>"
        else:
            from_email = "onboarding@resend.dev"
            to_email = GMAIL_USER

        response = resend.Emails.send({
            "from": from_email,
            "to": to_email,
            "subject": subject,
            "html": html
        })
        if response and response.get("id"):
            print(f"Resend sent to {to_email}")
            return True
        return False
    except Exception as e:
        print(f"Resend error: {e}")
        return False

def send_email(
    to_email: str,
    business_name: str,
    pitch: str
) -> bool:
    """
    Smart email sender.
    Tries Gmail first then Resend.
    Gmail works on Render free tier.
    """
    subject = (
        f"Website Growth Proposal "
        f"for {business_name}"
    )
    html = build_email_html(business_name, pitch)

    # Try Gmail first
    if GMAIL_USER and GMAIL_PASS:
        success = send_via_gmail(
            to_email, subject, html
        )
        if success:
            return True
        print("Gmail failed. Trying Resend...")

    # Try Resend as backup
    if RESEND_KEY:
        return send_via_resend(
            to_email, subject, html
        )

    print("No email method configured.")
    return False

# ────────────────────────────────────────────────────────────────
# CONTENT WRITERS
# ────────────────────────────────────────────────────────────────

def write_pitch(
    business_name: str,
    business_type: str,
    location: str,
    config: dict
) -> str:
    messages = [
        {
            "role": "system",
            "content": (
                f"Elite sales agent for {COMPANY}. "
                f"Write sharp email pitch. "
                f"Price $2000. Show ROI. "
                f"Under 120 words. USA tone. "
                f"Paragraphs not bullet points."
            )
        },
        {
            "role": "user",
            "content": (
                f"Business: {business_name}\n"
                f"Type: {business_type}\n"
                f"Location: {location}\n"
                f"Price: $2,000\n"
                f"Contact: {WHATSAPP} or {GMAIL_USER}"
            )
        }
    ]
    pitch = ask_jarvis(messages, config)
    if not pitch:
        pitch = (
            f"Hi {business_name} team,\n\n"
            f"I help {business_type} in {location} "
            f"get more clients online.\n\n"
            f"Our Growth Package at $2,000 includes "
            f"a professional website, WhatsApp "
            f"integration, lead capture, and SEO. "
            f"Most clients see ROI within 60 days.\n\n"
            f"Interested? WhatsApp: {WHATSAPP}\n\n"
            f"Dan\n{COMPANY}"
        )
    return pitch

def write_call_script(
    business_name: str,
    business_type: str,
    location: str,
    config: dict
) -> str:
    messages = [
        {
            "role": "system",
            "content": (
                f"Sales coach for {COMPANY}. "
                f"Write short phone call script. "
                f"Natural conversational. "
                f"Under 100 words. "
                f"Include greeting value prop "
                f"and ask for meeting."
            )
        },
        {
            "role": "user",
            "content": (
                f"Call script for:\n"
                f"Business: {business_name}\n"
                f"Type: {business_type}\n"
                f"Location: {location}\n"
                f"Goal: Book 15 min demo"
            )
        }
    ]
    script = ask_jarvis(messages, config)
    if not script:
        script = (
            f"Hi may I speak with the owner please?\n\n"
            f"Hi my name is Dan from {COMPANY}.\n\n"
            f"I help {business_type} in {location} "
            f"get more clients with professional websites.\n\n"
            f"We build complete sites for just $2,000 "
            f"and most clients see results in 60 days.\n\n"
            f"Would you have 15 minutes this week "
            f"for a quick demo?\n\n"
            f"Objection response:\n"
            f"I understand. One new client from your "
            f"website pays for the whole thing."
        )
    return script

def write_whatsapp_message(
    business_name: str,
    business_type: str,
    location: str,
    config: dict
) -> str:
    messages = [
        {
            "role": "system",
            "content": (
                f"Sales agent for {COMPANY}. "
                f"Write short WhatsApp message. "
                f"Conversational and friendly. "
                f"Under 60 words. "
                f"Like a real person texting. "
                f"End with a question."
            )
        },
        {
            "role": "user",
            "content": (
                f"WhatsApp for:\n"
                f"Business: {business_name}\n"
                f"Type: {business_type}\n"
                f"Location: {location}\n"
                f"Price: $2,000"
            )
        }
    ]
    msg = ask_jarvis(messages, config)
    if not msg:
        msg = (
            f"Hi! I help {business_type} in "
            f"{location} get more clients online.\n\n"
            f"We build professional websites "
            f"for $2,000 that bring in real business.\n\n"
            f"Would you be open to a quick chat?"
        )
    return msg

def generate_whatsapp_link(
    phone: str,
    message: str
) -> str:
    if not phone:
        phone = WHATSAPP
    clean = "".join(filter(str.isdigit, phone))
    encoded = urllib.parse.quote(message)
    return f"https://wa.me/{clean}?text={encoded}"

# ────────────────────────────────────────────────────────────────
# DAILY SUMMARY EMAIL TO DAN
# ────────────────────────────────────────────────────────────────

def send_daily_summary(
    business_type: str,
    location: str,
    all_data: list,
    emails_sent: int
):
    """Send Dan a summary with all pitches scripts and links"""
    pitches_html = ""
    for i, p in enumerate(all_data, 1):
        pitches_html += f"""
<div style="background:white;
            padding:20px;
            margin-bottom:20px;
            border-radius:8px;
            border-left:4px solid #1a1a2e;">

    <h3 style="color:#1a1a2e;margin:0 0 8px 0;">
        {i}. {p['name']}
    </h3>
    <p style="margin:0 0 15px 0;
              font-size:13px;color:#666;">
        Email: {p['email'] or 'Find manually'} |
        Phone: {p.get('phone') or 'Find manually'}
    </p>

    <details style="margin-bottom:8px;">
        <summary style="cursor:pointer;
                        font-weight:bold;
                        color:#1a1a2e;
                        padding:8px;
                        background:#e8f0fe;
                        border-radius:5px;">
            Email Pitch (Sent Automatically)
        </summary>
        <div style="padding:12px;
                    background:#f9f9f9;
                    margin-top:5px;
                    border-radius:5px;
                    line-height:1.7;
                    font-size:14px;">
            {p['pitch'].replace(chr(10), '<br>')}
        </div>
    </details>

    <details style="margin-bottom:8px;">
        <summary style="cursor:pointer;
                        font-weight:bold;
                        color:#d4380d;
                        padding:8px;
                        background:#fff2e8;
                        border-radius:5px;">
            Call Script (Call Them Today)
        </summary>
        <div style="padding:12px;
                    background:#fff7f0;
                    margin-top:5px;
                    border-radius:5px;
                    line-height:1.7;
                    font-size:14px;">
            {p['call_script'].replace(chr(10), '<br>')}
        </div>
    </details>

    <details>
        <summary style="cursor:pointer;
                        font-weight:bold;
                        color:#389e0d;
                        padding:8px;
                        background:#f6ffed;
                        border-radius:5px;">
            WhatsApp Message (Click to Send)
        </summary>
        <div style="padding:12px;
                    background:#f0fff4;
                    margin-top:5px;
                    border-radius:5px;
                    line-height:1.7;
                    font-size:14px;">
            {p['wa_message'].replace(chr(10), '<br>')}
            <br><br>
            <a href="{p['wa_link']}"
               style="background:#25D366;
                      color:white;
                      padding:10px 20px;
                      border-radius:20px;
                      text-decoration:none;
                      font-weight:bold;
                      font-size:14px;">
                Open WhatsApp and Send
            </a>
        </div>
    </details>

</div>
        """

    html = f"""
<html>
<body style="font-family:Arial,sans-serif;
             max-width:700px;
             margin:0 auto;
             padding:20px;
             background:#f5f5f5;">

    <div style="background:#1a1a2e;
                padding:25px;
                border-radius:10px;
                margin-bottom:20px;
                text-align:center;">
        <h1 style="color:white;margin:0;
                   font-size:22px;">
            Jarvis Daily Hunt Report
        </h1>
        <p style="color:#ccc;margin:8px 0 0 0;">
            {business_type.title()} in {location}
            | {datetime.now().strftime("%Y-%m-%d %H:%M")}
        </p>
    </div>

    <div style="background:#e6f7ff;
                padding:15px;
                border-radius:8px;
                margin-bottom:15px;
                border:1px solid #91d5ff;">
        <strong>Today Stats:</strong><br>
        Businesses found: {len(all_data)}<br>
        Emails sent automatically: {emails_sent}<br>
        Need manual email: {len(all_data) - emails_sent}
    </div>

    <div style="background:#fff7e6;
                padding:15px;
                border-radius:8px;
                margin-bottom:20px;
                border:1px solid #ffd591;">
        <strong>Your Action Plan Dan:</strong><br>
        1. Emails already sent automatically<br>
        2. Call 3 businesses using scripts below<br>
        3. Click WhatsApp links to send messages<br>
        4. Follow up on previous replies<br>
        5. Close deals at $2,000 each
    </div>

    {pitches_html}

    <div style="background:#1a1a2e;
                padding:15px;
                border-radius:8px;
                text-align:center;
                color:#ccc;
                font-size:13px;">
        Jarvis Cloud {VERSION} | {COMPANY}<br>
        WhatsApp: {WHATSAPP}
    </div>

</body>
</html>
    """

    subject = (
        f"Jarvis: {len(all_data)} leads ready "
        f"| {emails_sent} emails sent "
        f"| {business_type} {location}"
    )

    # Send to Dan
    if GMAIL_USER and GMAIL_PASS:
        send_via_gmail(GMAIL_USER, subject, html)
    elif RESEND_KEY:
        try:
            resend.api_key = RESEND_KEY
            resend.Emails.send({
                "from": "onboarding@resend.dev",
                "to": GMAIL_USER,
                "subject": subject,
                "html": html
            })
        except Exception as e:
            print(f"Summary email error: {e}")

# ────────────────────────────────────────────────────────────────
# AUTO HUNT
# ────────────────────────────────────────────────────────────────

def auto_hunt(
    business_type: str,
    location: str,
    country: str,
    config: dict
):
    print(f"""
=====================================
AUTO HUNT + EMAIL {VERSION}
Target:   {business_type}
Location: {location}, {country}
Time:     {datetime.now().strftime("%Y-%m-%d %H:%M")}
=====================================
    """)

    emails_sent = 0
    all_data = []

    try:
        businesses = find_real_businesses(
            business_type, location, country
        )

        if not businesses:
            print("No businesses found.")
            return

        print(f"Processing {len(businesses)}...")

        for biz in businesses:
            name = biz.get("name", "")
            email = biz.get("email", "")
            phone = biz.get("phone", "")

            if not name:
                continue

            print(f"\nProcessing: {name}")

            # Find email if missing
            if not email or "@" not in email:
                print(f"  Searching email...")
                email = search_email(name, location)
                if email:
                    print(f"  Found: {email}")

            # Write all content
            pitch = write_pitch(
                name, business_type,
                location, config
            )
            call_script = write_call_script(
                name, business_type,
                location, config
            )
            wa_message = write_whatsapp_message(
                name, business_type,
                location, config
            )
            wa_link = generate_whatsapp_link(
                phone, wa_message
            )

            all_data.append({
                "name": name,
                "email": email,
                "phone": phone,
                "pitch": pitch,
                "call_script": call_script,
                "wa_message": wa_message,
                "wa_link": wa_link
            })

            # Send email to client
            if (
                email and
                "@" in email and
                "." in email and
                len(email) < 100
            ):
                success = send_email(
                    email, name, pitch
                )
                if success:
                    emails_sent += 1
                    log_email(name, email, "Sent")
                    save_lead(
                        name, email,
                        location, country,
                        "Email Sent"
                    )
                else:
                    log_email(name, email, "Failed")
                    save_lead(
                        name, email,
                        location, country,
                        "Email Failed"
                    )
            else:
                save_lead(
                    name, "No email",
                    location, country,
                    "Need Email"
                )
                print(f"  No email. Saved for manual.")

            time.sleep(3)

        # Send daily summary to Dan
        send_daily_summary(
            business_type, location,
            all_data, emails_sent
        )

        # Save report file
        timestamp = datetime.now().strftime(
            "%Y%m%d_%H%M%S"
        )
        filename = (
            f"hunt_{business_type}_"
            f"{location}_{timestamp}.txt"
            .replace(" ", "_")
        )

        report = f"""
HUNT REPORT {VERSION}
====================
Company:     {COMPANY}
Date:        {datetime.now().strftime("%Y-%m-%d %H:%M")}
Target:      {business_type}
Location:    {location}, {country}
Total:       {len(all_data)}
Emails sent: {emails_sent}

"""
        for p in all_data:
            report += f"""
{'='*60}
BUSINESS: {p['name']}
EMAIL:     {p['email'] or 'Not found'}
PHONE:     {p['phone'] or 'Not found'}

EMAIL PITCH:
{p['pitch']}

CALL SCRIPT:
{p['call_script']}

WHATSAPP:
{p['wa_message']}

WHATSAPP LINK:
{p['wa_link']}
"""

        write_file(filename, report)

        print(f"""
=====================================
HUNT COMPLETE {VERSION}
Total:       {len(all_data)}
Emails sent: {emails_sent}
Report:      {filename}
Summary:     Sent to {GMAIL_USER}
=====================================
        """)

    except Exception as e:
        print(f"Hunt error: {e}")

# ────────────────────────────────────────────────────────────────
# SCHEDULED TASKS
# ────────────────────────────────────────────────────────────────

def morning_hunt(config: dict):
    print("\nMORNING USA CAMPAIGN\n")

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
            email_count = len([
                l for l in logs
                if l.get("status") == "Sent"
            ])
    messages = [
        {
            "role": "system",
            "content": "Jarvis. Sharp report. 60 words."
        },
        {
            "role": "user",
            "content": (
                f"Leads: {leads}\n"
                f"Emails: {email_count}\n"
                f"Summary and top 3 priorities for Dan."
            )
        }
    ]
    report = ask_jarvis(messages, config)
    print(f"\nREPORT:\n{report}\n")
    write_file(
        f"report_{datetime.now().strftime('%Y%m%d')}.txt",
        report
    )

def midday_followup(config: dict):
    print("\nMIDDAY FOLLOWUP\n")
    leads = view_leads()
    messages = [
        {
            "role": "system",
            "content": "Jarvis. 30 words max."
        },
        {
            "role": "user",
            "content": f"Leads: {leads}. Dan reminder."
        }
    ]
    reminder = ask_jarvis(messages, config)
    print(f"\nREMINDER:\n{reminder}\n")

# ────────────────────────────────────────────────────────────────
# SCHEDULER
# ────────────────────────────────────────────────────────────────

def start_scheduler(config: dict):
    print("""
====================================
SCHEDULER ACTIVE
Morning Hunt:    08:00 AM
Midday Followup: 12:00 PM
Evening Report:  07:00 PM
====================================
    """)

    schedule.every().day.at("08:00").do(
        morning_hunt, config=config
    )
    schedule.every().day.at("12:00").do(
        midday_followup, config=config
    )
    schedule.every().day.at("19:00").do(
        evening_report, config=config
    )

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
  Model: Groq Llama 3.3 70B
  Market: USA PRIMARY
  Email: Gmail + Resend
  Calls: Scripts Generated
  WhatsApp: Links Generated
  Mode: 24/7 Autonomous
====================================
    """)

    # Start web server first
    # This fixes the Render port error
    start_web_server()

    if not GROQ_KEY:
        print("ERROR: GROQ_API_KEY not set!")
        return

    # Show email status
    if GMAIL_USER and GMAIL_PASS:
        print(
            "Email: Gmail\n"
            "Sending directly to clients"
        )
    elif RESEND_KEY and FROM_DOMAIN:
        print(
            "Email: Resend with domain\n"
            "Sending directly to clients"
        )
    elif RESEND_KEY:
        print(
            "Email: Resend\n"
            "Sending to Dan only\n"
            "Get domain to send to clients"
        )
    else:
        print(
            "WARNING: No email configured\n"
            "Add GMAIL_USER and GMAIL_PASS"
        )

    config = load_config()

    # Run startup hunt
    print("\nRunning startup hunt...")
    auto_hunt(
        "law firms",
        "New York",
        "USA",
        config
    )

    # Start scheduler
    start_scheduler(config)

if __name__ == "__main__":
    main()