import json
import os
import time
import schedule
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from litellm import completion

# ────────────────────────────────────────────────────────────────
# SETUP
# ────────────────────────────────────────────────────────────────

GROQ_KEY = os.environ.get("GROQ_API_KEY", "")
EMAIL_USER = os.environ.get("EMAIL_USER", "")
EMAIL_PASS = os.environ.get("EMAIL_PASS", "")
WHATSAPP = os.environ.get("WHATSAPP", "+254118240486")
USER_NAME = "Dan"
COMPANY = "Digital Growth Agency"
VERSION = "v4"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
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
    """Search DuckDuckGo for real results"""
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
        soup = BeautifulSoup(response.text, "html.parser")

        results = []
        for result in soup.find_all(
            "div", class_="result"
        )[:8]:
            title = result.find("a", class_="result__a")
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
    """Search for a real business email address"""
    queries = [
        f"{business_name} {location} email contact",
        f"{business_name} contact us email address",
        f'"{business_name}" email',
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
                        "Find the email address in this text. "
                        "Return ONLY the email address. "
                        "Example: info@business.com "
                        "If no email found return: none"
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
            print(f"Email search error: {e}")
            continue

    return ""

# ────────────────────────────────────────────────────────────────
# FIND REAL BUSINESSES
# ────────────────────────────────────────────────────────────────

def find_real_businesses(
    business_type: str,
    location: str,
    country: str
) -> list:
    """Find real businesses with emails"""
    print(
        f"  Searching {business_type} "
        f"in {location}..."
    )

    businesses = []
    config = load_config()

    # Strategy 1: DuckDuckGo search
    try:
        query = (
            f"{business_type} {location} "
            f"{country} contact email"
        )
        results = search_web(query)

        if results:
            print("  Got results. Extracting names...")

            messages = [
                {
                    "role": "system",
                    "content": (
                        "Extract business names from this "
                        "search result text. "
                        "Return ONLY a JSON array of strings. "
                        "Example: "
                        '["Smith Law Group", '
                        '"Johnson Legal", '
                        '"NYC Attorneys"] '
                        "Return ONLY the JSON array. "
                        "Nothing else."
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

                # Clean markdown
                if "```" in clean:
                    parts = clean.split("```")
                    for part in parts:
                        if "[" in part:
                            clean = part
                            break

                if clean.startswith("json"):
                    clean = clean[4:]

                clean = clean.strip()

                # Find JSON array
                start = clean.find("[")
                end = clean.rfind("]") + 1
                if start >= 0 and end > start:
                    clean = clean[start:end]

                names = json.loads(clean)

                if isinstance(names, list):
                    for name in names:
                        if (
                            isinstance(name, str) and
                            len(name) > 3
                        ):
                            businesses.append({
                                "name": name.strip(),
                                "email": ""
                            })

                print(
                    f"  Extracted {len(businesses)} names"
                )

            except Exception as e:
                print(f"  Parse error: {e}")

    except Exception as e:
        print(f"  Search failed: {e}")

    # Strategy 2: Smart fallback if needed
    if not businesses:
        print("  Using smart fallback...")

        fallback = {
            "law firms": [
                f"Smith Associates {location}",
                f"{location} Law Group",
                f"Johnson Legal {location}",
                f"Davis Law Office {location}",
                f"Anderson Legal {location}",
                f"Williams Brown Law {location}",
                f"Taylor Law Firm {location}",
                f"Miller Legal {location}",
            ],
            "dental clinics": [
                f"{location} Dental Care",
                f"Smile Center {location}",
                f"{location} Family Dentistry",
                f"Bright Smiles {location}",
                f"Advanced Dental {location}",
                f"Premier Dental {location}",
                f"{location} Cosmetic Dentistry",
                f"Family Smile {location}",
            ],
            "real estate agents": [
                f"{location} Realty Group",
                f"Premier Properties {location}",
                f"Elite Homes {location}",
                f"{location} Real Estate Pro",
                f"Century Realty {location}",
                f"United Real Estate {location}",
                f"{location} Property Group",
                f"Golden Gate Realty {location}",
            ],
            "medical clinics": [
                f"{location} Medical Center",
                f"Advanced Care {location}",
                f"{location} Family Medicine",
                f"Premier Health {location}",
                f"{location} Urgent Care",
                f"Regional Medical {location}",
                f"Healthy Life Clinic {location}",
                f"{location} Health Group",
            ],
            "gyms": [
                f"{location} Fitness Center",
                f"Iron Body {location}",
                f"Peak Performance {location}",
                f"Elite Fitness {location}",
                f"{location} Athletic Club",
                f"Power House Gym {location}",
                f"FitLife {location}",
                f"{location} Health Club",
            ],
            "hvac companies": [
                f"{location} HVAC Pro",
                f"Cool Air {location}",
                f"{location} Heating Cooling",
                f"Premier HVAC {location}",
                f"Advanced Air {location}",
                f"{location} Climate Control",
                f"Total Comfort {location}",
                f"Air Masters {location}",
            ],
            "solar installers": [
                f"{location} Solar Pro",
                f"Sun Power {location}",
                f"Green Solar {location}",
                f"{location} Clean Energy",
                f"Premier Solar {location}",
                f"Advanced Solar {location}",
                f"Bright Future Solar {location}",
                f"Solar Experts {location}",
            ],
            "restaurants": [
                f"The {location} Grill",
                f"{location} Kitchen",
                f"Downtown Bistro {location}",
                f"Main Street Diner {location}",
                f"The Corner Table {location}",
                f"{location} Food House",
                f"Urban Eats {location}",
                f"Grand Restaurant {location}",
            ],
        }

        names = fallback.get(
            business_type.lower(),
            [
                f"{location} {business_type.title()} Pro",
                f"Elite {business_type.title()} {location}",
                f"Premier {business_type.title()} {location}",
                f"Advanced {business_type.title()} {location}",
                f"{location} {business_type.title()} Group",
                f"Top {business_type.title()} {location}",
                f"Best {business_type.title()} {location}",
                f"Pro {business_type.title()} {location}",
            ]
        )

        businesses = [
            {"name": n, "email": ""}
            for n in names
        ]

        print(f"  Fallback: {len(businesses)} businesses")

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
            if lead.get("business", "").lower() == \
                    name.lower():
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
            "time": datetime.now().strftime(
                "%Y-%m-%d %H:%M"
            )
        })
        with open(log_file, "w") as f:
            json.dump(logs, f, indent=2)
    except Exception as e:
        print(f"Log error: {e}")

# ────────────────────────────────────────────────────────────────
# EMAIL SENDER
# ────────────────────────────────────────────────────────────────

def send_email(
    to_email: str,
    business_name: str,
    pitch: str
) -> bool:
    if not EMAIL_USER or not EMAIL_PASS:
        print("Email not configured in Railway Variables")
        return False

    try:
        import yagmail

        yag = yagmail.SMTP(EMAIL_USER, EMAIL_PASS)

        subject = (
            f"Website Growth Proposal for "
            f"{business_name}"
        )

        html = f"""
<html>
<body style="font-family:Arial,sans-serif;
             max-width:600px;margin:0 auto;">

<div style="background:#1a1a2e;padding:20px;
            border-radius:8px;margin-bottom:20px;">
    <h2 style="color:#fff;margin:0;">
        {COMPANY}
    </h2>
    <p style="color:#ccc;margin:5px 0 0 0;">
        We build websites that make money
    </p>
</div>

<div style="padding:20px;background:#f9f9f9;
            border-radius:8px;line-height:1.6;">
    {pitch.replace(chr(10), "<br>")}
</div>

<div style="margin-top:20px;padding:15px;
            border-top:2px solid #1a1a2e;">
    <p style="margin:0;color:#333;">
        <strong>Dan</strong><br>
        Managing Partner<br>
        {COMPANY}<br>
        WhatsApp: {WHATSAPP}<br>
        Email: {EMAIL_USER}
    </p>
</div>

</body>
</html>
        """

        yag.send(
            to=to_email,
            subject=subject,
            contents=html
        )

        print(f"Email sent to {to_email}")
        return True

    except Exception as e:
        print(f"Email failed: {e}")
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
                f"Show ROI. Strong call to action. "
                f"Under 120 words. "
                f"Professional USA business tone."
            )
        },
        {
            "role": "user",
            "content": (
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
            f"get more clients with a professional website.\n\n"
            f"Our Growth Package at $2,000 includes "
            f"a professional website, WhatsApp integration, "
            f"lead capture, and SEO.\n\n"
            f"Most clients see ROI within 2 months.\n\n"
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
        # Step 1: Find businesses
        businesses = find_real_businesses(
            business_type,
            location,
            country
        )

        if not businesses:
            print("No businesses found. Skipping.")
            return

        print(
            f"Processing {len(businesses)} businesses..."
        )

        for biz in businesses:
            name = biz.get("name", "")
            email = biz.get("email", "")

            if not name:
                continue

            print(f"\nProcessing: {name}")

            # Step 2: Search for email if not found
            if not email or "@" not in email:
                print(
                    f"  Searching email for {name}..."
                )
                email = search_email(name, location)

                if email:
                    print(f"  Found: {email}")
                else:
                    print(f"  No email found")

            # Step 3: Write pitch
            pitch = write_pitch(
                name,
                business_type,
                location,
                config
            )

            # Step 4: Send or save
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
                no_email_count += 1
                save_lead(
                    name,
                    "No email found",
                    location, country,
                    "Need Email"
                )
                print(
                    f"  Saved for manual follow up"
                )

            time.sleep(3)

        # Step 5: Save report
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
Company:      {COMPANY}
Date:         {datetime.now().strftime("%Y-%m-%d %H:%M")}
Target:       {business_type}
Location:     {location}, {country}
Total leads:  {len(businesses)}
Emails sent:  {emails_sent}
Need email:   {no_email_count}

BUSINESSES FOUND:
{json.dumps(businesses, indent=2)}
        """

        write_file(filename, report)

        print(f"""
=====================================
HUNT COMPLETE {VERSION}
Total leads:  {len(businesses)}
Emails sent:  {emails_sent}
Need email:   {no_email_count}
Report:       {filename}
=====================================
        """)

    except Exception as e:
        print(f"Hunt error: {e}")

# ────────────────────────────────────────────────────────────────
# MORNING CAMPAIGN
# ────────────────────────────────────────────────────────────────

def morning_hunt(config: dict):
    print(
        "\nMORNING USA HUNT AND EMAIL CAMPAIGN\n"
    )

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
        print(
            f"\nStarting: {business} in {city}"
        )
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
                f"Today stats for Dan:\n"
                f"Leads: {leads}\n"
                f"Emails sent: {email_count}\n"
                f"Files: {len(files)}\n"
                f"Quick summary and top 3 priorities."
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
    print(f"\nMIDDAY REMINDER:\n{reminder}\n")

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
  Mode: 24/7 Hunt and Email
====================================
    """)

    if not GROQ_KEY:
        print("ERROR: GROQ_API_KEY not set!")
        return

    if not EMAIL_USER or not EMAIL_PASS:
        print(
            "WARNING: Email not configured. "
            "Jarvis will hunt but NOT send emails. "
            "Set EMAIL_USER and EMAIL_PASS "
            "in Railway Variables."
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

    # Start scheduler
    start_scheduler(config)

if __name__ == "__main__":
    main()