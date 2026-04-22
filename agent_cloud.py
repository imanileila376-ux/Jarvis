import yaml
import json
import os
import time
import threading
import schedule
import yagmail
from datetime import datetime
from litellm import completion
from tools.basic_tools import TOOLS, TOOL_FUNCTIONS
from tools.web_tools import WEB_TOOLS, WEB_TOOL_FUNCTIONS

# ────────────────────────────────────────────────────────────────
# SETUP & CONTACTS
# ────────────────────────────────────────────────────────────────
ALL_TOOLS = TOOLS + WEB_TOOLS
ALL_FUNCTIONS = {**TOOL_FUNCTIONS, **WEB_TOOL_FUNCTIONS}

WHATSAPP = "+254118240486"
EMAIL_USER = os.environ.get("EMAIL_USER", "elizabethnzasi530@gmail.com")
EMAIL_PASS = os.environ.get("EMAIL_PASS", "") # Set this in Railway Variables
USER_NAME = "Dan"

# ────────────────────────────────────────────────────────────────
# EMAIL ENGINE
# ────────────────────────────────────────────────────────────────
def send_auto_email(to_email, business_name, pitch):
    if not EMAIL_PASS:
        print("❌ Email failed: EMAIL_PASS variable not set in Railway.")
        return
    try:
        yag = yagmail.SMTP(EMAIL_USER, EMAIL_PASS)
        subject = f"Growth Strategy for {business_name} - Digital Growth Agency"
        
        # Professional HTML wrapper
        content = [
            f"<h2>Hello {business_name} team,</h2>",
            pitch.replace("\n", "<br>"),
            "<br><br>Best regards,<br>",
            "<strong>Dan</strong><br>Managing Partner<br>Digital Growth Agency",
            f"<br>WhatsApp: {WHATSAPP}"
        ]
        
        yag.send(to=to_email, subject=subject, contents=content)
        print(f"📧 EMAIL SENT TO: {to_email}")
    except Exception as e:
        print(f"❌ Email error: {e}")

# ────────────────────────────────────────────────────────────────
# CONFIG & CHAT
# ────────────────────────────────────────────────────────────────
def load_config():
    return {
        "llm": {
            "model": os.environ.get("MODEL", "groq/llama-3.3-70b-versatile"),
            "api_key": os.environ.get("GROQ_API_KEY", ""),
            "temperature": 0.8,
            "max_tokens": 1000
        }
    }

def ask_jarvis(messages, config):
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
        return str(e)

# ────────────────────────────────────────────────────────────────
# AUTO HUNT & EMAIL
# ────────────────────────────────────────────────────────────────
def auto_hunt(business_type, location, country, config):
    print(f"\n🎯 Hunting {business_type} in {location}...")
    
    # 1. Search for businesses
    raw_results = ALL_FUNCTIONS["find_businesses"](business_type, location, country)
    
    # 2. Extract Data using AI
    extraction_prompt = [
        {"role": "system", "content": "Extract business names and emails from this text. Return ONLY a JSON list of objects: [{'name': '...', 'email': '...'}]"},
        {"role": "user", "content": raw_results}
    ]
    
    extracted_json = ask_jarvis(extraction_prompt, config)
    
    try:
        leads = json.loads(extracted_json)
    except:
        print("⚠️ Could not extract clean email list. Skipping auto-email.")
        return

    # 3. Process each lead
    for lead in leads:
        name = lead.get('name', 'Business Owner')
        email = lead.get('email')
        
        if email and "@" in email:
            # Generate a killer $2,000 pitch
            pitch_prompt = [
                {"role": "system", "content": "You are JARVIS. Write a sharp, 3-sentence email pitch for a $2,000 website automation system. ROI focused."},
                {"role": "user", "content": f"Business Name: {name}"}
            ]
            pitch = ask_jarvis(pitch_prompt, config)
            
            # SEND IT!
            send_auto_email(email, name, pitch)
            
            # Save to Database
            ALL_FUNCTIONS["save_lead"](name, email, location, country, "$2,000", "Email Sent")
        else:
            # Just save as lead if no email found
            ALL_FUNCTIONS["save_lead"](name, "No Email Found", location, country, "$2,000", "Manual Check Needed")

# ────────────────────────────────────────────────────────────────
# SCHEDULER
# ────────────────────────────────────────────────────────────────
def start_scheduler(config):
    # Morning Hunt at 8 AM
    schedule.every().day.at("08:00").do(auto_hunt, "law firms", "New York", "USA", config)
    schedule.every().day.at("08:30").do(auto_hunt, "dental clinics", "Los Angeles", "USA", config)

    print("⏰ Cloud Scheduler Active. Standing by...")
    while True:
        schedule.run_pending()
        time.sleep(30)

def main():
    config = load_config()
    if not config["llm"]["api_key"]:
        print("❌ Error: GROQ_API_KEY not found.")
        return

    print("🚀 JARVIS CLOUD EMAILER ONLINE")
    
    # Run one hunt immediately on startup for testing
    auto_hunt("real estate agents", "Miami", "USA", config)
    
    start_scheduler(config)

if __name__ == "__main__":
    main()