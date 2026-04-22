import yaml
import json
import os
import time
import threading
import schedule
from datetime import datetime
from litellm import completion
from tools.basic_tools import TOOLS, TOOL_FUNCTIONS
from tools.web_tools import WEB_TOOLS, WEB_TOOL_FUNCTIONS
from memory_store import remember_fact, get_memory_summary

# ────────────────────────────────────────────────────────────────
# SETUP
# ────────────────────────────────────────────────────────────────

ALL_TOOLS = TOOLS + WEB_TOOLS
ALL_FUNCTIONS = {**TOOL_FUNCTIONS, **WEB_TOOL_FUNCTIONS}

WHATSAPP = "+254118240486"
EMAIL = "elizabethnzasi530@gmail.com"
COMPANY = "Digital Growth Agency"
WEBSITE = "www.digitalgrowth.com"
USER_NAME = "Dan"

# ────────────────────────────────────────────────────────────────
# CONFIG
# ────────────────────────────────────────────────────────────────

def load_config():
    return {
        "llm": {
            "model": os.environ.get(
                "MODEL", "groq/llama-3.3-70b-versatile"
            ),
            "api_key": os.environ.get("GROQ_API_KEY", ""),
            "temperature": 0.85,
            "max_tokens": 1200,
        },
        "agent": {
            "name": "Jarvis",
            "system_prompt": os.environ.get(
                "SYSTEM_PROMPT",
                "You are Jarvis, an elite AI sales agent for Dan."
            )
        }
    }

# ────────────────────────────────────────────────────────────────
# CHAT
# ────────────────────────────────────────────────────────────────

def chat(messages: list, config: dict) -> str:
    try:
        response = completion(
            model=config["llm"]["model"],
            messages=messages,
            api_key=config["llm"]["api_key"],
            temperature=config["llm"]["temperature"],
            max_tokens=config["llm"]["max_tokens"],
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {e}"

# ────────────────────────────────────────────────────────────────
# AUTO HUNT
# ────────────────────────────────────────────────────────────────

def auto_hunt(
    business_type: str,
    location: str,
    country: str,
    config: dict
) -> str:
    print(f"""
=====================================
AUTO HUNT
Target:   {business_type}
Location: {location}, {country}
Time:     {datetime.now().strftime("%Y-%m-%d %H:%M")}
=====================================
    """)

    try:
        businesses = ALL_FUNCTIONS["find_businesses"](
            business_type=business_type,
            location=location,
            country=country
        )

        price_report = ALL_FUNCTIONS["calculate_price"](
            country=country,
            city=location,
            business_type=business_type,
            size="medium"
        )

        roi_report = ALL_FUNCTIONS["calculate_roi"](
            country=country,
            revenue_per_client=1000,
            expected_new_clients=5,
            website_cost=2000
        )

        pitch_messages = [
            {
                "role": "system",
                "content": f"""You are Jarvis an elite sales agent.
Write sharp professional USA sales pitches.
Use each business name specifically.
Price is exactly $2000 for Growth package.
Include WhatsApp {WHATSAPP} Email {EMAIL}.
Under 150 words per pitch.
Sound like a top closer."""
            },
            {
                "role": "user",
                "content": f"""Write pitches for:
{businesses}
Pricing: {price_report}
ROI: {roi_report}
One pitch per business.
Sharp professional USA style."""
            }
        ]

        pitches = chat(pitch_messages, config)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = (
            f"hunt_{business_type}_{location}_{timestamp}.txt"
            .replace(" ", "_")
        )

        report = f"""
AUTO HUNT REPORT
================
Company:  {COMPANY}
WhatsApp: {WHATSAPP}
Email:    {EMAIL}
Date:     {datetime.now().strftime("%Y-%m-%d %H:%M")}
Target:   {business_type}
Location: {location}, {country}

BUSINESSES FOUND:
{businesses}

PRICING:
{price_report}

ROI:
{roi_report}

PITCHES:
{pitches}
        """

        ALL_FUNCTIONS["write_file"](
            filename=filename,
            content=report
        )

        ALL_FUNCTIONS["save_lead"](
            business_name=f"{business_type} - {location}",
            contact=f"Email: {EMAIL}",
            location=location,
            country=country,
            deal_value="$2,000",
            status="New"
        )

        print(f"✅ Hunt complete. Saved to {filename}")
        return pitches

    except Exception as e:
        print(f"❌ Hunt error: {e}")
        return f"Error: {e}"

# ────────────────────────────────────────────────────────────────
# SCHEDULED TASKS
# ────────────────────────────────────────────────────────────────

def morning_hunt(config):
    print("\n⏰ MORNING USA HUNT STARTING...\n")

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

    for business, city, country in targets:
        print(f"\n🎯 Hunting {business} in {city}...")
        auto_hunt(business, city, country, config)
        time.sleep(5)

    print("\n✅ Morning hunt complete!")

def evening_report(config):
    print("\n⏰ EVENING REPORT...\n")

    leads = ALL_FUNCTIONS["view_leads"]()
    files = [
        f for f in os.listdir(".")
        if f.endswith(".txt")
    ]

    messages = [
        {
            "role": "system",
            "content": "You are Jarvis. Give Dan a sharp evening report."
        },
        {
            "role": "user",
            "content": f"""
Evening report for Dan.
Leads: {leads}
Files created: {len(files)}
Give:
1. What was accomplished
2. Top 3 priorities tomorrow
3. Motivating line
Under 100 words.
            """
        }
    ]

    report = chat(messages, config)
    print(f"\nEVENING REPORT:\n{report}\n")

    ALL_FUNCTIONS["write_file"](
        filename=f"report_{datetime.now().strftime('%Y%m%d')}.txt",
        content=report
    )

def midday_followup(config):
    print("\n⏰ MIDDAY FOLLOW-UP...\n")

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
Write a midday USA follow up reminder.
Under 50 words.
            """
        }
    ]

    reminder = chat(messages, config)
    print(f"\nMIDDAY REMINDER:\n{reminder}\n")

# ────────────────────────────────────────────────────────────────
# SCHEDULER
# ────────────────────────────────────────────────────────────────

def start_scheduler(config):
    print("""
====================================
JARVIS CLOUD SCHEDULER ACTIVE
====================================
Morning Hunt:    08:00 AM daily
Midday Followup: 12:00 PM daily
Evening Report:  07:00 PM daily
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
    config = load_config()

    print(f"""
====================================
  J.A.R.V.I.S CLOUD
  Elite Core Online for {USER_NAME}
  Model: {config['llm']['model']}
  Market: USA PRIMARY
  Mode: 24/7 Autonomous
====================================
    """)

    # Run morning hunt immediately on startup
    print("🚀 Running initial hunt on startup...")
    morning_hunt(config)

    # Start scheduler
    start_scheduler(config)

if __name__ == "__main__":
    main()