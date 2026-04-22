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
VERSION = "v3"

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
        url = f"https://html.duckduckgo.com/html/?q={query}"
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

def search_email(business_name: str, location: str) -> str:
    """Search for a business email address"""
    queries = [
        f"{business_name} {location} email contact",
        f"{business_name} {location} contact us",
        f'"{business_name}" email site:linkedin.com OR site:yellowpages.com',
    ]

    for query in queries:
        try:
            results = search_web(query)
            if not results:
                continue

            # Ask AI to find email
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

            config = load_config()
            found = ask_jarvis(messages, config).strip()

            if (
                "@" in found and
                "." in found and
                len(found) < 100 and
                "none" not in found.lower()
            ):
                return found

            time.sleep(1)

        except Exception as e:
            print(f"Email search error: {e}")
            continue

    return ""

def find_real_businesses(
    business_type: str,
    location: str,
    country: str
) -> list:
    """
    Find REAL businesses with REAL emails.
    Returns list of dicts with name and email.
    """
    print(f"  Searching for real {business_type} in {location}...")

    businesses = []

    # Multiple search strategies
    queries = [
        f"{business_type} {location} {country} email contact",
        f"best {business_type} in {location} website",
        f"{business_type} {location} phone email address",
        f"top {business_type} {location} contact information",
    ]

    seen_names = set()

    for query in queries:
        try:
            results = search_web(query)
            if not results:
                continue

            # Extract business names from results
            messages = [
                {
                    "role": "system",
                    "content": (
                        "Extract business names and any "
                        "email addresses from this text. "
                        "Return ONLY valid JSON array: "
                        '[{"name": "Business Name", '
                        '"email": "email or empty string"}] '
                        "Return only JSON nothing else."
                    )
                },
                {
                    "role": "user",
                    "content": results[:3000]
                }
            ]

            config = load_config()
            response = ask_jarvis(messages, config)

            try:
                # Clean JSON response
                clean = response.strip()
                if "```" in clean:
                    clean = clean.split("```")[1]
                    if clean.startswith("json"):
                        clean = clean[4:]
                clean = clean.strip()

                extracted = json.loads(clean)

                if isinstance(extracted, list):
                    for item in extracted:
                        name = item.get("name", "").strip()
                        email = item.get("email", "").strip()

                        if (
                            name and
                            len(name) > 3 and
                            name not in seen_names
                        ):
                            seen_names.add(name)
                            businesses.append({
                                "name": name,
                                "email": email
                            })

            except Exception as e:
                print(f"  JSON parse error: {e}")
                continue

            time.sleep(2)

        except Exception as e:
            print(f"  Query error: {e}")
            continue

    print(f"  Found {len(businesses)} businesses")
    return businesses[:10]

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
# SAVE LEAD
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

        # Check if already exists
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
        return f"{len(leads)} leads in database."
    except:
        return "Error loading leads."

def write_file(filename: str, content: str):
    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(content)
    except Exception as e:
        print(f"Write file error: {e}")

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
            "content": f"""You are Jarvis an elite sales agent
for {COMPANY}.
Write a sharp professional email pitch.
Price is exactly $2000 for Growth package.
Show ROI. End with strong call to action.
Under 120 words.
Professional USA business tone."""
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
            f"I noticed {business_type} businesses "
            f"in {location} are leaving money on the table "
            f"without a proper website.\n\n"
            f"Our Growth Package at $2,000 includes "
            f"a professional website, WhatsApp integration, "
            f"lead capture, and SEO setup.\n\n"
            f"Most clients see ROI within 2 months.\n\n"
            f"Ready to grow? "
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
    no_email = 0

    try:
        # Step 1: Find REAL businesses
        businesses = find_real_businesses(
            business_type,
            location,
            country
        )

        if not businesses:
            print("No businesses found. Skipping.")
            return

        print(f"Processing {len(businesses)} businesses...")

        for biz in businesses:
            name = biz.get("name", "")
            email = biz.get("email", "")

            if not name:
                continue

            print(f"\nProcessing: {name}")

            # Step 2: Find email if not already found
            if not email or "@" not in email:
                print(f"  Searching email for {name}...")
                email = search_email(name, location)

                if email:
                    print(f"  Found: {email}")
                else:
                    print(f"  No email found")

            # Step 3: Write personalized pitch
            pitch = write_pitch(
                name,
                business_type,
                location,
                config
            )

            # Step 4: Send email or save for manual
            if email and "@" in email and "." in email:
                success = send_email(email, name, pitch)

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
                no_email += 1
                save_lead(
                    name,
                    "No email found",
                    location, country,
                    "Need Email"
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
Need email:   {no_email}

BUSINESSES:
{json.dumps(businesses, indent=2)}
        """

        write_file(filename, report)

        print(f"""
=====================================
HUNT COMPLETE {VERSION}
Total leads:  {len(businesses)}
Emails sent:  {emails_sent}
Need email:   {no_email}
Report:       {filename}
=====================================
        """)

    except Exception as e:
        print(f"Hunt error: {e}")

# ────────────────────────────────────────────────────────────────
# MORNING CAMPAIGN
# ────────────────────────────────────────────────────────────────

def morning_hunt(config: dict):
    print("\nMORNING USA HUNT AND EMAIL CAMPAIGN\n")

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
        print(f"\nStarting hunt: {business} in {city}")
        auto_hunt(business, city, country, config)
        time.sleep(10)

    print("\nMorning campaign complete.")

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
                "Give Dan a sharp evening business report. "
                "Be concise and motivating. "
                "Under 80 words."
            )
        },
        {
            "role": "user",
            "content": (
                f"Today's stats for Dan:\n"
                f"Leads: {leads}\n"
                f"Emails sent: {email_count}\n"
                f"Files: {len(files)}\n"
                f"Give quick summary and top 3 priorities."
            )
        }
    ]

    report = ask_jarvis(messages, config)
    print(f"\nEVENING REPORT:\n{report}\n")

    write_file(
        f"report_{datetime.now().strftime('%Y%m%d')}.txt",
        report
    )

def midday_followup(config: dict):
    print("\nMIDDAY FOLLOW-UP\n")

    leads = view_leads()

    messages = [
        {
            "role": "system",
            "content": "You are Jarvis. Be sharp. Under 40 words."
        },
        {
            "role": "user",
            "content": (
                f"Dan's leads: {leads}\n"
                f"Give a quick follow up reminder."
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
            "Set EMAIL_USER and EMAIL_PASS in Railway."
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