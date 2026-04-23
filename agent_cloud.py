import json
import os
import time
import schedule
import requests
import resend
from bs4 import BeautifulSoup
from datetime import datetime
from litellm import completion

# ────────────────────────────────────────────────────────────────
# SETUP
# ────────────────────────────────────────────────────────────────

GROQ_KEY = os.environ.get("GROQ_API_KEY", "")
EMAIL_USER = os.environ.get(
    "EMAIL_USER", "elizabethnzasi530@gmail.com"
)
RESEND_KEY = os.environ.get("RESEND_KEY", "")
WHATSAPP = os.environ.get(
    "WHATSAPP", "+254118240486"
)
USER_NAME = "Dan"
COMPANY = "Digital Growth Agency"
VERSION = "v6"

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
        },
        {
            "name": "Cellino Law",
            "email": "info@cellinolaw.com",
            "location": "New York",
        },
        {
            "name": "The Barnes Firm",
            "email": "info@thebarnesfirm.com",
            "location": "New York",
        },
        {
            "name": "Block O Toole and Murphy",
            "email": "info@blockotoole.com",
            "location": "New York",
        },
        {
            "name": "Sullivan and Cromwell",
            "email": "info@sullcrom.com",
            "location": "New York",
        },
        {
            "name": "Skadden Arps Slate",
            "email": "info@skadden.com",
            "location": "New York",
        },
        {
            "name": "Davis Polk and Wardwell",
            "email": "info@davispolk.com",
            "location": "New York",
        },
        {
            "name": "Cleary Gottlieb Steen",
            "email": "info@cgsh.com",
            "location": "New York",
        },
    ],
    "dental clinics": [
        {
            "name": "Aspen Dental Los Angeles",
            "email": "info@aspendental.com",
            "location": "Los Angeles",
        },
        {
            "name": "Pacific Dental Services",
            "email": "info@pacificdentalservices.com",
            "location": "Los Angeles",
        },
        {
            "name": "Western Dental",
            "email": "info@westerndental.com",
            "location": "Los Angeles",
        },
        {
            "name": "LA Dental Center",
            "email": "contact@ladentalcenter.com",
            "location": "Los Angeles",
        },
        {
            "name": "Brite Dental",
            "email": "info@britedental.com",
            "location": "Los Angeles",
        },
        {
            "name": "Smile Generation",
            "email": "info@smilegeneration.com",
            "location": "Los Angeles",
        },
        {
            "name": "Beverly Hills Dental",
            "email": "info@beverlyhillsdental.com",
            "location": "Los Angeles",
        },
        {
            "name": "Premier Dental LA",
            "email": "info@premierdentalla.com",
            "location": "Los Angeles",
        },
    ],
    "real estate agents": [
        {
            "name": "Keller Williams Chicago",
            "email": "info@kwchicago.com",
            "location": "Chicago",
        },
        {
            "name": "Century 21 Chicago",
            "email": "info@century21chicago.com",
            "location": "Chicago",
        },
        {
            "name": "Coldwell Banker Chicago",
            "email": "info@cbchicago.com",
            "location": "Chicago",
        },
        {
            "name": "Baird and Warner",
            "email": "info@bairdwarner.com",
            "location": "Chicago",
        },
        {
            "name": "RE MAX Chicago",
            "email": "info@remaxchicago.com",
            "location": "Chicago",
        },
        {
            "name": "Compass Chicago",
            "email": "chicago@compass.com",
            "location": "Chicago",
        },
        {
            "name": "Dream Town Realty",
            "email": "info@dreamtown.com",
            "location": "Chicago",
        },
        {
            "name": "Berkshire Hathaway Chicago",
            "email": "info@bhhschicago.com",
            "location": "Chicago",
        },
    ],
    "medical clinics": [
        {
            "name": "CareNow Houston",
            "email": "info@carenow.com",
            "location": "Houston",
        },
        {
            "name": "NextCare Urgent Care",
            "email": "info@nextcare.com",
            "location": "Houston",
        },
        {
            "name": "AFC Urgent Care Houston",
            "email": "info@afcurgentcare.com",
            "location": "Houston",
        },
        {
            "name": "Concentra Houston",
            "email": "info@concentra.com",
            "location": "Houston",
        },
        {
            "name": "Memorial Hermann",
            "email": "info@memorialhermann.org",
            "location": "Houston",
        },
        {
            "name": "Houston Methodist",
            "email": "info@houstonmethodist.org",
            "location": "Houston",
        },
        {
            "name": "Kelsey Seybold Clinic",
            "email": "info@kelsey-seybold.com",
            "location": "Houston",
        },
        {
            "name": "Texas Medical Center",
            "email": "info@tmc.edu",
            "location": "Houston",
        },
    ],
    "gyms": [
        {
            "name": "Equinox Miami",
            "email": "miami@equinox.com",
            "location": "Miami",
        },
        {
            "name": "LA Fitness Miami",
            "email": "info@lafitness.com",
            "location": "Miami",
        },
        {
            "name": "Planet Fitness Miami",
            "email": "info@planetfitness.com",
            "location": "Miami",
        },
        {
            "name": "Gold's Gym Miami",
            "email": "miami@goldsgym.com",
            "location": "Miami",
        },
        {
            "name": "Crunch Fitness Miami",
            "email": "info@crunch.com",
            "location": "Miami",
        },
        {
            "name": "Barry's Bootcamp Miami",
            "email": "miami@barrys.com",
            "location": "Miami",
        },
        {
            "name": "F45 Training Miami",
            "email": "info@f45training.com",
            "location": "Miami",
        },
        {
            "name": "SoulCycle Miami",
            "email": "info@soul-cycle.com",
            "location": "Miami",
        },
    ],
    "hvac companies": [
        {
            "name": "One Hour Air Dallas",
            "email": "info@onehourhvac.com",
            "location": "Dallas",
        },
        {
            "name": "Aire Serv Dallas",
            "email": "info@aireserv.com",
            "location": "Dallas",
        },
        {
            "name": "Service Experts Dallas",
            "email": "info@serviceexperts.com",
            "location": "Dallas",
        },
        {
            "name": "Comfort Systems Dallas",
            "email": "info@comfortsystems.com",
            "location": "Dallas",
        },
        {
            "name": "Lennox International",
            "email": "info@lennox.com",
            "location": "Dallas",
        },
        {
            "name": "Trane Dallas",
            "email": "info@trane.com",
            "location": "Dallas",
        },
        {
            "name": "Carrier Dallas",
            "email": "info@carrier.com",
            "location": "Dallas",
        },
        {
            "name": "ABC Home Commercial",
            "email": "info@abchomeandcommercial.com",
            "location": "Dallas",
        },
    ],
    "solar installers": [
        {
            "name": "Sunrun Seattle",
            "email": "info@sunrun.com",
            "location": "Seattle",
        },
        {
            "name": "SunPower Seattle",
            "email": "info@sunpower.com",
            "location": "Seattle",
        },
        {
            "name": "Tesla Solar Seattle",
            "email": "solarcity@tesla.com",
            "location": "Seattle",
        },
        {
            "name": "Vivint Solar Seattle",
            "email": "info@vivintsolar.com",
            "location": "Seattle",
        },
        {
            "name": "NW Wind and Solar",
            "email": "info@nwwindandsolar.com",
            "location": "Seattle",
        },
        {
            "name": "Puget Sound Solar",
            "email": "info@pugetsoundsolar.com",
            "location": "Seattle",
        },
        {
            "name": "Green Power Energy",
            "email": "info@greenpowerenergy.com",
            "location": "Seattle",
        },
        {
            "name": "Solar Universe Seattle",
            "email": "info@solaruniverse.com",
            "location": "Seattle",
        },
    ],
    "restaurants": [
        {
            "name": "Legal Sea Foods Boston",
            "email": "info@legalseafoods.com",
            "location": "Boston",
        },
        {
            "name": "The Capital Grille Boston",
            "email": "info@thecapitalgrille.com",
            "location": "Boston",
        },
        {
            "name": "Davios Boston",
            "email": "info@davios.com",
            "location": "Boston",
        },
        {
            "name": "Boston Chops",
            "email": "info@bostonchops.com",
            "location": "Boston",
        },
        {
            "name": "Row 34 Boston",
            "email": "info@row34.com",
            "location": "Boston",
        },
        {
            "name": "Sarma Boston",
            "email": "info@sarmarestaurant.com",
            "location": "Boston",
        },
        {
            "name": "Toro Boston",
            "email": "info@toro-restaurant.com",
            "location": "Boston",
        },
        {
            "name": "Waypoint Boston",
            "email": "info@waypointcambridge.com",
            "location": "Boston",
        },
    ],
}

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
        url = (
            f"https://html.duckduckgo.com/html/"
            f"?q={requests.utils.quote(query)}"
        )
        response = requests.get(
            url,
            headers=HEADERS,
            timeout=15
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
    queries = [
        f"{business_name} {location} email contact",
        f"{business_name} contact us email",
    ]

    config = load_config()

    for query in queries:
        try:
            results = search_web(query)
            if not results:
                continue

            messages = [
                {
                    "role": "system",
                    "content": (
                        "Find email address in this text. "
                        "Return ONLY the email. "
                        "Example: info@company.com "
                        "If none found return: none"
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
                " " not in found.strip()
            ):
                return found.strip()

            time.sleep(1)

        except Exception as e:
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

    # Strategy 1: Real database
    db_key = business_type.lower()
    if db_key in REAL_BUSINESSES:
        db_results = REAL_BUSINESSES[db_key]
        location_matches = [
            b for b in db_results
            if location.lower() in
            b.get("location", "").lower()
        ]
        if location_matches:
            businesses = location_matches
            print(
                f"  Database: "
                f"{len(businesses)} found"
            )
        else:
            businesses = db_results[:5]
            print(
                f"  Database: "
                f"{len(businesses)} found"
            )

    # Strategy 2: Web search for more
    try:
        query = (
            f"{business_type} {location} "
            f"email contact"
        )
        results = search_web(query)

        if results:
            messages = [
                {
                    "role": "system",
                    "content": (
                        "Extract business names and emails. "
                        "Return ONLY JSON: "
                        '[{"name":"...", "email":"..."}] '
                        "Only JSON."
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

                existing = [
                    b["name"] for b in businesses
                ]

                if isinstance(extra, list):
                    for item in extra:
                        name = item.get("name", "")
                        email = item.get("email", "")
                        if (
                            name and
                            len(name) > 3 and
                            name not in existing
                        ):
                            businesses.append({
                                "name": name,
                                "email": email,
                                "location": location
                            })

                print(f"  Total: {len(businesses)}")

            except Exception as e:
                print(f"  Parse error: {e}")

    except Exception as e:
        print(f"  Web error: {e}")

    # Strategy 3: Fallback
    if not businesses:
        print("  Using fallback...")
        fallback = [
            f"Premier {business_type.title()} {location}",
            f"Elite {business_type.title()} {location}",
            f"Advanced {business_type.title()} {location}",
            f"{location} {business_type.title()} Pro",
            f"Top {business_type.title()} {location}",
        ]
        businesses = [
            {
                "name": n,
                "email": "",
                "location": location
            }
            for n in fallback
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
        print(f"Save lead error: {e}")

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
        return (
            f"{len(leads)} total leads. "
            f"{sent} emails sent."
        )
    except:
        return "Error loading leads."

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
# EMAIL SENDER - RESEND
# ────────────────────────────────────────────────────────────────

def send_email(
    to_email: str,
    business_name: str,
    pitch: str
) -> bool:
    """
    Send email using Resend.
    Free: 3000 emails per month.
    Works perfectly on Railway.
    """
    if not RESEND_KEY:
        print(
            "RESEND_KEY not set. "
            "Add it to Railway Variables."
        )
        return False

    try:
        resend.api_key = RESEND_KEY

        html_content = f"""
<html>
<body style="font-family: Arial, sans-serif;
             max-width: 600px;
             margin: 0 auto;
             padding: 20px;">

    <div style="background: #1a1a2e;
                padding: 20px;
                border-radius: 8px;
                margin-bottom: 20px;">
        <h2 style="color: #ffffff; margin: 0;">
            {COMPANY}
        </h2>
        <p style="color: #cccccc;
                  margin: 5px 0 0 0;
                  font-size: 14px;">
            We build websites that make money
        </p>
    </div>

    <div style="padding: 20px;
                background: #f9f9f9;
                border-radius: 8px;
                line-height: 1.8;
                color: #333333;">
        {pitch.replace(chr(10), "<br>")}
    </div>

    <div style="margin-top: 20px;
                padding: 15px;
                border-top: 2px solid #1a1a2e;
                color: #333333;">
        <p style="margin: 0;">
            <strong>Dan</strong><br>
            Managing Partner<br>
            {COMPANY}<br>
            WhatsApp: {WHATSAPP}<br>
            Email: {EMAIL_USER}
        </p>
    </div>

    <div style="margin-top: 10px;
                padding: 8px;
                text-align: center;
                font-size: 11px;
                color: #999999;">
        To unsubscribe reply STOP.
    </div>

</body>
</html>
        """

        response = resend.Emails.send({
            "from": "onboarding@resend.dev",
            "to": to_email,
            "subject": (
                f"Website Growth Proposal "
                f"for {business_name}"
            ),
            "html": html_content
        })

        if response and response.get("id"):
            print(
                f"Email sent to {to_email} "
                f"ID: {response['id']}"
            )
            return True
        else:
            print(f"Resend failed: {response}")
            return False

    except Exception as e:
        print(f"Email error: {e}")
        return False

# ────────────────────────────────────────────────────────────────
# WRITE PITCH
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
                f"You are Jarvis an elite sales agent "
                f"for {COMPANY}. "
                f"Write a sharp professional email pitch. "
                f"Price is exactly $2000 for Growth package. "
                f"Show ROI numbers. "
                f"Strong call to action. "
                f"Under 120 words. "
                f"Professional USA business tone. "
                f"Use paragraphs not bullet points."
            )
        },
        {
            "role": "user",
            "content": (
                f"Write pitch for:\n"
                f"Business: {business_name}\n"
                f"Type: {business_type}\n"
                f"Location: {location}\n"
                f"Price: $2,000\n"
                f"Contact: WhatsApp {WHATSAPP} "
                f"or {EMAIL_USER}"
            )
        }
    ]

    pitch = ask_jarvis(messages, config)

    if not pitch:
        pitch = (
            f"Hi {business_name} team,\n\n"
            f"I help {business_type} in {location} "
            f"get more clients with a professional "
            f"website.\n\n"
            f"Our Growth Package at $2,000 includes "
            f"a professional website, WhatsApp "
            f"integration, lead capture, and SEO. "
            f"Most clients see ROI within 60 days.\n\n"
            f"Interested? "
            f"WhatsApp: {WHATSAPP}\n\n"
            f"Dan\n{COMPANY}"
        )

    return pitch

# ────────────────────────────────────────────────────────────────
# AUTO HUNT WITH EMAIL
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
    no_email_count = 0

    try:
        businesses = find_real_businesses(
            business_type,
            location,
            country
        )

        if not businesses:
            print("No businesses found.")
            return

        print(
            f"Processing {len(businesses)} "
            f"businesses..."
        )

        for biz in businesses:
            name = biz.get("name", "")
            email = biz.get("email", "")

            if not name:
                continue

            print(f"\nProcessing: {name}")

            # Search for email if missing
            if not email or "@" not in email:
                print(f"  Searching email...")
                email = search_email(name, location)
                if email:
                    print(f"  Found: {email}")
                else:
                    print(f"  No email found")

            # Write pitch
            pitch = write_pitch(
                name,
                business_type,
                location,
                config
            )

            # Send or save
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
                    log_email(
                        name, email, "Failed"
                    )
                    save_lead(
                        name, email,
                        location, country,
                        "Email Failed"
                    )
            else:
                no_email_count += 1
                save_lead(
                    name,
                    "No email found",
                    location, country,
                    "Need Email"
                )
                print(f"  Saved for manual")

            time.sleep(3)

        # Save report
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

# ────────────────────────────────────────────────────────────────
# EVENING REPORT
# ────────────────────────────────────────────────────────────────

def evening_report(config: dict):
    print("\nEVENING REPORT\n")

    leads = view_leads()
    files = [
        f for f in os.listdir(".")
        if f.endswith(".txt")
    ]

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
            "content": (
                "You are Jarvis. "
                "Give Dan a sharp evening report. "
                "Under 80 words. Motivating."
            )
        },
        {
            "role": "user",
            "content": (
                f"Stats for Dan:\n"
                f"Leads: {leads}\n"
                f"Emails sent today: {email_count}\n"
                f"Files: {len(files)}\n"
                f"Give summary and top 3 priorities."
            )
        }
    ]

    report = ask_jarvis(messages, config)
    print(f"\nEVENING REPORT:\n{report}\n")

    write_file(
        f"report_{datetime.now().strftime('%Y%m%d')}.txt",
        report
    )

# ────────────────────────────────────────────────────────────────
# MIDDAY FOLLOWUP
# ────────────────────────────────────────────────────────────────

def midday_followup(config: dict):
    print("\nMIDDAY FOLLOW-UP\n")

    leads = view_leads()

    messages = [
        {
            "role": "system",
            "content": (
                "You are Jarvis. "
                "Be sharp. Under 40 words."
            )
        },
        {
            "role": "user",
            "content": (
                f"Dan leads: {leads}\n"
                f"Quick follow up reminder."
            )
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
CLOUD SCHEDULER ACTIVE
====================================
Morning Hunt + Emails: 08:00 AM
Midday Follow-up:      12:00 PM
Evening Report:        07:00 PM
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
  Model: groq/llama-3.3-70b-versatile
  Market: USA PRIMARY
  Email: Resend
  Mode: 24/7 Hunt and Email
====================================
    """)

    if not GROQ_KEY:
        print("ERROR: GROQ_API_KEY not set!")
        return

    if not RESEND_KEY:
        print(
            "WARNING: RESEND_KEY not set.\n"
            "Jarvis will hunt but NOT send emails.\n"
            "Get free key at resend.com\n"
            "Add RESEND_KEY to Railway Variables."
        )

    config = load_config()

    # Run startup hunt
    print("Running startup hunt...")
    auto_hunt(
        "law firms",
        "New York",
        "USA",
        config
    )

    # Start daily scheduler
    start_scheduler(config)

if __name__ == "__main__":
    main()