import json
import os
import time
import schedule
from datetime import datetime
from litellm import completion
from tools.basic_tools import TOOLS, TOOL_FUNCTIONS
from tools.web_tools import WEB_TOOLS, WEB_TOOL_FUNCTIONS

# ────────────────────────────────────────────────────────────────
# SETUP
# ────────────────────────────────────────────────────────────────

ALL_TOOLS = TOOLS + WEB_TOOLS
ALL_FUNCTIONS = {**TOOL_FUNCTIONS, **WEB_TOOL_FUNCTIONS}

# All secrets come from Railway Variables
# Never hardcode them in code
GROQ_KEY = os.environ.get("GROQ_API_KEY", "")
EMAIL_USER = os.environ.get("EMAIL_USER", "")
EMAIL_PASS = os.environ.get("EMAIL_PASS", "")
WHATSAPP = os.environ.get("WHATSAPP", "+254118240486")
USER_NAME = "Dan"
COMPANY = "Digital Growth Agency"

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
# CHAT
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
# EMAIL ENGINE
# ────────────────────────────────────────────────────────────────

def send_email(
    to_email: str,
    business_name: str,
    pitch: str
) -> bool:
    """
    Send a professional email to a lead.
    Returns True if successful.
    """
    if not EMAIL_USER or not EMAIL_PASS:
        print(
            "Email not configured. "
            "Set EMAIL_USER and EMAIL_PASS "
            "in Railway Variables."
        )
        return False

    try:
        import yagmail

        yag = yagmail.SMTP(EMAIL_USER, EMAIL_PASS)

        subject = (
            f"Website Proposal for {business_name} "
            f"- {COMPANY}"
        )

        html_body = f"""
<html>
<body style="font-family: Arial, sans-serif; 
             max-width: 600px; 
             margin: 0 auto;">

    <div style="background: #1a1a2e; 
                padding: 20px;
                border-radius: 8px;
                margin-bottom: 20px;">
        <h2 style="color: #ffffff; margin: 0;">
            {COMPANY}
        </h2>
        <p style="color: #cccccc; margin: 5px 0 0 0;">
            We build websites that make money
        </p>
    </div>

    <div style="padding: 20px;
                background: #f9f9f9;
                border-radius: 8px;
                line-height: 1.6;">
        {pitch.replace(chr(10), '<br>')}
    </div>

    <div style="margin-top: 20px;
                padding: 15px;
                border-top: 2px solid #1a1a2e;">
        <p style="margin: 0; color: #333;">
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
            contents=html_body
        )

        print(f"Email sent to: {to_email}")
        return True

    except Exception as e:
        print(f"Email error: {e}")
        return False

def log_email(
    business_name: str,
    to_email: str,
    status: str
):
    """Log all sent emails to a file"""
    try:
        log_file = "emails_log.json"
        logs = []

        if os.path.exists(log_file):
            with open(log_file, "r") as f:
                logs = json.load(f)

        logs.append({
            "business": business_name,
            "email": to_email,
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
    """Write a personalized $2000 sales pitch"""
    messages = [
        {
            "role": "system",
            "content": f"""You are Jarvis, an elite sales agent
for {COMPANY}.
Write a sharp professional email pitch.
Price is exactly $2,000 for the Growth package.
Include ROI numbers.
End with strong call to action.
Under 150 words.
Sound confident and professional."""
        },
        {
            "role": "user",
            "content": f"""Write a pitch for:
Business: {business_name}
Type: {business_type}
Location: {location}
Price: $2,000 Growth Package
Contact: WhatsApp {WHATSAPP} or {EMAIL_USER}"""
        }
    ]

    pitch = ask_jarvis(messages, config)
    return pitch if pitch else (
        f"Hi {business_name} team,\n\n"
        f"I help {business_type} in {location} "
        f"get more clients with a professional website.\n\n"
        f"Our Growth Package is $2,000 and includes "
        f"everything you need to dominate online.\n\n"
        f"WhatsApp: {WHATSAPP}\n"
        f"Email: {EMAIL_USER}\n\n"
        f"Dan\n{COMPANY}"
    )

# ────────────────────────────────────────────────────────────────
# EXTRACT EMAILS FROM SEARCH RESULTS
# ────────────────────────────────────────────────────────────────

def extract_leads(
    raw_results: str,
    config: dict
) -> list:
    """
    Use AI to extract business names and emails
    from search results.
    """
    messages = [
        {
            "role": "system",
            "content": (
                "Extract business names and email addresses "
                "from this text. "
                "Return ONLY a valid JSON array like this: "
                '[{"name": "Business Name", '
                '"email": "email@example.com"}] '
                "If no email found use empty string. "
                "Return only the JSON nothing else."
            )
        },
        {
            "role": "user",
            "content": raw_results[:3000]
        }
    ]

    response = ask_jarvis(messages, config)

    try:
        # Clean the response
        clean = response.strip()
        if clean.startswith("```"):
            clean = clean.split("```")[1]
            if clean.startswith("json"):
                clean = clean[4:]
        clean = clean.strip()

        leads = json.loads(clean)
        return leads if isinstance(leads, list) else []

    except Exception as e:
        print(f"Extract error: {e}")
        return []

# ────────────────────────────────────────────────────────────────
# AUTO HUNT
# ────────────────────────────────────────────────────────────────

def auto_hunt(
    business_type: str,
    location: str,
    country: str,
    config: dict
):
    """
    Full automatic hunt:
    1. Find businesses
    2. Extract contacts
    3. Write pitch
    4. Send email
    5. Save lead
    """
    print(f"""
=====================================
AUTO HUNT + EMAIL
Target:   {business_type}
Location: {location}, {country}
Time:     {datetime.now().strftime("%Y-%m-%d %H:%M")}
=====================================
    """)

    try:
        # Step 1: Find businesses
        print("Searching for businesses...")
        raw_results = ALL_FUNCTIONS["find_businesses"](
            business_type=business_type,
            location=location,
            country=country
        )

        # Step 2: Extract leads
        print("Extracting contacts...")
        leads = extract_leads(raw_results, config)

        if not leads:
            print("No leads extracted. Saving raw results.")
            ALL_FUNCTIONS["save_lead"](
                business_name=f"{business_type} batch {location}",
                contact="No email found",
                location=location,
                country=country,
                deal_value="$2,000",
                status="Manual Check Needed"
            )
            return

        print(f"Found {len(leads)} leads!")

        # Step 3: Process each lead
        emails_sent = 0
        for lead in leads:
            name = lead.get("name", "Business")
            email = lead.get("email", "")

            print(f"\nProcessing: {name}")

            # Write personalized pitch
            pitch = write_pitch(
                name,
                business_type,
                location,
                config
            )

            # Send email if we have address
            if email and "@" in email and "." in email:
                success = send_email(email, name, pitch)

                if success:
                    emails_sent += 1
                    log_email(name, email, "Sent")
                    ALL_FUNCTIONS["save_lead"](
                        business_name=name,
                        contact=email,
                        location=location,
                        country=country,
                        deal_value="$2,000",
                        status="Email Sent"
                    )
                else:
                    log_email(name, email, "Failed")
                    ALL_FUNCTIONS["save_lead"](
                        business_name=name,
                        contact=email,
                        location=location,
                        country=country,
                        deal_value="$2,000",
                        status="Email Failed"
                    )
            else:
                # No email found save for manual follow up
                ALL_FUNCTIONS["save_lead"](
                    business_name=name,
                    contact="No email - manual search needed",
                    location=location,
                    country=country,
                    deal_value="$2,000",
                    status="Need Email"
                )
                print(f"No email for {name}. Saved for manual.")

            # Small delay between emails
            time.sleep(3)

        # Save hunt report
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = (
            f"hunt_{business_type}_{location}_{timestamp}.txt"
            .replace(" ", "_")
        )

        report = f"""
HUNT REPORT WITH EMAILS
=======================
Company:   {COMPANY}
Date:      {datetime.now().strftime("%Y-%m-%d %H:%M")}
Target:    {business_type}
Location:  {location}, {country}
Leads:     {len(leads)}
Emails sent: {emails_sent}

RAW RESULTS:
{raw_results}

LEADS PROCESSED:
{json.dumps(leads, indent=2)}
        """

        ALL_FUNCTIONS["write_file"](
            filename=filename,
            content=report
        )

        print(f"""
=====================================
HUNT COMPLETE
Leads found:   {len(leads)}
Emails sent:   {emails_sent}
Report saved:  {filename}
=====================================
        """)

    except Exception as e:
        print(f"Hunt error: {e}")

# ────────────────────────────────────────────────────────────────
# DAILY REPORTS
# ────────────────────────────────────────────────────────────────

def morning_hunt(config: dict):
    """Runs every morning. Hunts and emails USA businesses."""
    print("\n MORNING USA HUNT AND EMAIL CAMPAIGN STARTING\n")

    targets = [
        ("law firms", "New York", "USA"),
        ("dental clinics", "Los Angeles", "USA"),
        ("real estate agents", "Chicago", "USA"),
        ("restaurants", "Miami", "USA"),
        ("gyms", "Houston", "USA"),
        ("medical clinics", "Boston", "USA"),
        ("hvac companies", "Dallas", "USA"),
        ("solar installers", "Seattle", "USA"),
    ]

    total_sent = 0

    for business, city, country in targets:
        print(f"\nHunting {business} in {city}...")
        auto_hunt(business, city, country, config)
        total_sent += 1
        time.sleep(5)

    print(f"\nMorning campaign complete. {total_sent} hunts done.")

def evening_report(config: dict):
    """Runs every evening. Summary of the day."""
    print("\nEVENING REPORT\n")

    leads = ALL_FUNCTIONS["view_leads"]()
    files = [
        f for f in os.listdir(".")
        if f.endswith(".txt")
    ]

    messages = [
        {
            "role": "system",
            "content": (
                "You are Jarvis. "
                "Give Dan a sharp evening business report. "
                "Be concise and motivating."
            )
        },
        {
            "role": "user",
            "content": f"""
Evening report for Dan.
Leads in database: {leads}
Files created today: {len(files)}
Give:
1. What was accomplished today
2. Top 3 priorities for tomorrow
3. One motivating line
Under 100 words.
            """
        }
    ]

    report = ask_jarvis(messages, config)
    print(f"\nEVENING REPORT:\n{report}\n")

    timestamp = datetime.now().strftime("%Y%m%d")
    ALL_FUNCTIONS["write_file"](
        filename=f"report_{timestamp}.txt",
        content=report
    )

def midday_followup(config: dict):
    """Runs every noon. Follow up reminders."""
    print("\nMIDDAY FOLLOW-UP\n")

    leads = ALL_FUNCTIONS["view_leads"]()

    messages = [
        {
            "role": "system",
            "content": "You are Jarvis. Be sharp and brief."
        },
        {
            "role": "user",
            "content": f"""
Dan's leads: {leads}
Which leads should Dan follow up with today?
Under 50 words. Sharp and direct.
            """
        }
    ]

    reminder = ask_jarvis(messages, config)
    print(f"\nMIDDAY REMINDER:\n{reminder}\n")

# ────────────────────────────────────────────────────────────────
# SCHEDULER
# ────────────────────────────────────────────────────────────────

def start_scheduler(config: dict):
    """Start the background scheduler."""
    print("""
====================================
CLOUD SCHEDULER ACTIVE
====================================
Morning Hunt + Emails: 08:00 AM daily
Midday Follow-up:      12:00 PM daily
Evening Report:        07:00 PM daily
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
  J.A.R.V.I.S CLOUD
  Elite Emailer for {USER_NAME}
  Model: groq/llama-3.3-70b-versatile
  Market: USA PRIMARY
  Mode: 24/7 Hunt and Email
====================================
    """)

    # Check for required variables
    if not GROQ_KEY:
        print("ERROR: GROQ_API_KEY not set in Railway Variables!")
        return

    if not EMAIL_USER or not EMAIL_PASS:
        print(
            "WARNING: Email not configured. "
            "Set EMAIL_USER and EMAIL_PASS "
            "in Railway Variables. "
            "Jarvis will hunt but not send emails."
        )

    config = load_config()

    # Run one hunt immediately on startup
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