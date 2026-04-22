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
from voice import speak, list_voices, set_voice
from listen import listen, listen_continuous, wait_for_clap
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

is_speaking = [False]

# ────────────────────────────────────────────────────────────────
# CONFIG
# ────────────────────────────────────────────────────────────────

def load_config():
    with open("config.yaml", "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

# ────────────────────────────────────────────────────────────────
# MEMORY
# ────────────────────────────────────────────────────────────────

class Memory:
    def __init__(self, system_prompt: str):
        persistent = get_memory_summary()
        full_prompt = system_prompt
        if persistent:
            full_prompt = (
                system_prompt +
                "\n\n" +
                persistent
            )
        self.messages = [
            {
                "role": "system",
                "content": full_prompt
            }
        ]
        self.max_messages = 40

    def add_user(self, text: str):
        self.messages.append({
            "role": "user",
            "content": text
        })

    def add_jarvis(self, text: str):
        self.messages.append({
            "role": "assistant",
            "content": text
        })

    def add_tool_call(self, tc_id, name, arguments):
        self.messages.append({
            "role": "assistant",
            "content": "",
            "tool_calls": [{
                "id": tc_id,
                "type": "function",
                "function": {
                    "name": name,
                    "arguments": arguments
                }
            }]
        })

    def add_tool_result(self, tc_id, name, result):
        self.messages.append({
            "role": "tool",
            "tool_call_id": tc_id,
            "name": name,
            "content": str(result)
        })

    def get(self):
        return self.messages

    def clear(self):
        system = self.messages[0]
        self.messages = [system]

    def trim(self):
        if len(self.messages) > self.max_messages:
            system = self.messages[0]
            recent = self.messages[
                -(self.max_messages - 1):
            ]
            self.messages = [system] + recent

# ────────────────────────────────────────────────────────────────
# AUTO SAVE FACTS
# ────────────────────────────────────────────────────────────────

def auto_save_facts(user_input: str):
    text = user_input.lower()
    triggers = [
        "my name is",
        "my goal is",
        "i want to",
        "i am trying to",
        "my business is",
        "i live in",
        "i am based in",
        "my target is",
        "my budget is",
        "remember that",
        "remember this",
        "dont forget",
        "my company is",
        "i sell",
        "my product is",
        "my service is",
        "my target market is",
        "my revenue is",
    ]
    for trigger in triggers:
        if trigger in text:
            fact = user_input.strip()
            remember_fact(fact)
            print(f"🧠 Remembered: {fact}\n")
            break

# ────────────────────────────────────────────────────────────────
# SPEAK
# ────────────────────────────────────────────────────────────────

def jarvis_speak(text: str):
    is_speaking[0] = True
    speak(text)
    time.sleep(0.3)
    is_speaking[0] = False

# ────────────────────────────────────────────────────────────────
# CHAT
# ────────────────────────────────────────────────────────────────

def chat(memory: Memory, config: dict) -> str:
    try:
        response = completion(
            model=config["llm"]["model"],
            messages=memory.get(),
            api_key=config["llm"]["api_key"],
            temperature=config["llm"]["temperature"],
            max_tokens=config["llm"]["max_tokens"],
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"System error Dan: {e}"

def chat_with_tool(
    memory: Memory,
    config: dict,
    tool_name: str
) -> str:
    print(f"\n🔧 Running {tool_name}...")
    try:
        response = completion(
            model=config["llm"]["model"],
            messages=memory.get(),
            api_key=config["llm"]["api_key"],
            temperature=0.1,
            max_tokens=500,
            tools=ALL_TOOLS,
            tool_choice={
                "type": "function",
                "function": {"name": tool_name}
            }
        )
        message = response.choices[0].message
        if not message.tool_calls:
            return chat(memory, config)
        tc = message.tool_calls[0]
        try:
            args = json.loads(tc.function.arguments)
            result = ALL_FUNCTIONS[tool_name](**args)
            print(f"✅ Done!\n")
        except Exception as e:
            return f"Tool error: {e}"
        memory.add_tool_call(
            tc.id,
            tc.function.name,
            tc.function.arguments
        )
        memory.add_tool_result(
            tc.id,
            tool_name,
            result
        )
        final = completion(
            model=config["llm"]["model"],
            messages=memory.get(),
            api_key=config["llm"]["api_key"],
            temperature=config["llm"]["temperature"],
            max_tokens=config["llm"]["max_tokens"],
        )
        return final.choices[0].message.content
    except Exception as e:
        return f"Error: {e}"

# ────────────────────────────────────────────────────────────────
# AUTO HUNT
# ────────────────────────────────────────────────────────────────

def auto_hunt(
    business_type: str,
    location: str,
    country: str,
    config: dict,
    memory: Memory
) -> str:
    print(f"""
=====================================
AUTO HUNT INITIATED
Target:   {business_type}
Location: {location}, {country}
=====================================
    """)

    jarvis_speak(
        f"Copy that {USER_NAME}. "
        f"Hunting {business_type} in {location}. "
        f"Stand by."
    )

    print("Scanning for targets...")
    businesses = ALL_FUNCTIONS["find_businesses"](
        business_type=business_type,
        location=location,
        country=country
    )
    jarvis_speak(
        "Targets acquired. Calculating pricing."
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
        website_cost=3000
    )

    jarvis_speak("Pricing locked. Writing pitches.")

    pitch_messages = [
        {
            "role": "system",
            "content": f"""You are Jarvis an elite sales agent.
Write sharp professional USA sales pitches.
Use each business name specifically.
Include USD pricing. Show ROI numbers.
Strong call to action.
Include WhatsApp {WHATSAPP} Email {EMAIL}.
Under 150 words per pitch.
Sound like a top closer.
Target is high value USA businesses."""
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

    try:
        pitch_response = completion(
            model=config["llm"]["model"],
            messages=pitch_messages,
            api_key=config["llm"]["api_key"],
            temperature=0.7,
            max_tokens=2000,
        )
        pitches = pitch_response.choices[0].message.content
    except Exception as e:
        pitches = f"Error: {e}"

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
Website:  {WEBSITE}
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

NEXT STEPS:
1. Google each business name
2. Find their email or contact form
3. Copy and send their pitch
4. Follow up after 2 days
5. Close the deal
6. Collect payment via PayPal or Stripe
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
        deal_value="See report",
        status="New"
    )

    jarvis_speak(
        f"Mission complete {USER_NAME}. "
        f"USA targets found. "
        f"Pitches ready. "
        f"Report saved. "
        f"Check your screen."
    )

    print(f"\nSaved to: {filename}\n")

    memory.add_jarvis(
        f"Auto hunt complete for {business_type} "
        f"in {location} {country}. "
        f"Saved to {filename}."
    )

    return pitches

# ────────────────────────────────────────────────────────────────
# SCHEDULER
# ────────────────────────────────────────────────────────────────

def run_morning_hunt(config: dict, memory: Memory):
    """Runs every morning. Hunts USA businesses."""
    print("\n⏰ MORNING USA HUNT STARTING...\n")
    jarvis_speak(
        f"Good morning {USER_NAME}. "
        f"Running your daily USA lead hunt. "
        f"Stand by."
    )

    # USA targets hunted every morning
    targets = [
        ("law firms", "New York", "USA"),
        ("dental clinics", "Los Angeles", "USA"),
        ("real estate agents", "Chicago", "USA"),
        ("restaurants", "Miami", "USA"),
        ("gyms", "Houston", "USA"),
    ]

    for business, city, country in targets:
        print(f"\n🎯 Hunting {business} in {city}...")
        auto_hunt(
            business, city, country, config, memory
        )
        time.sleep(3)

    jarvis_speak(
        f"Morning USA hunt complete {USER_NAME}. "
        f"New leads ready. "
        f"Check your files."
    )
    print("\n✅ Morning USA hunt complete!\n")

def run_evening_report(config: dict, memory: Memory):
    """Runs every evening. Day summary."""
    print("\n⏰ EVENING REPORT...\n")

    leads = ALL_FUNCTIONS["view_leads"]()
    files = [
        f for f in os.listdir(".")
        if f.endswith(".txt")
    ]

    report_messages = [
        {
            "role": "system",
            "content": f"""You are Jarvis.
Give Dan a sharp evening business report.
Focus on USA market progress.
Be concise and motivating.
Sound like Iron Man Jarvis."""
        },
        {
            "role": "user",
            "content": f"""
Create evening report for Dan.
Leads today: {leads}
Files created: {len(files)}
Give:
1. What was accomplished today
2. Top 3 USA priorities for tomorrow
3. Motivating closing line
Under 100 words.
            """
        }
    ]

    try:
        response = completion(
            model=config["llm"]["model"],
            messages=report_messages,
            api_key=config["llm"]["api_key"],
            temperature=0.7,
            max_tokens=200,
        )
        report = response.choices[0].message.content
        print(f"\nJarvis Evening Report:\n{report}\n")
        jarvis_speak(report)
    except Exception as e:
        print(f"Report error: {e}")

def run_midday_followup(config: dict, memory: Memory):
    """Runs every noon. Follow up reminders."""
    print("\n⏰ MIDDAY FOLLOW-UP...\n")

    leads = ALL_FUNCTIONS["view_leads"]()

    msg_messages = [
        {
            "role": "system",
            "content": "You are Jarvis. Be sharp and brief."
        },
        {
            "role": "user",
            "content": f"""
Dan has these leads: {leads}
Write a midday USA follow up reminder.
Tell him which leads to contact today.
Under 50 words. Sharp and direct.
            """
        }
    ]

    try:
        response = completion(
            model=config["llm"]["model"],
            messages=msg_messages,
            api_key=config["llm"]["api_key"],
            temperature=0.5,
            max_tokens=100,
        )
        reminder = response.choices[0].message.content
        print(f"\nJarvis: {reminder}\n")
        jarvis_speak(reminder)
    except Exception as e:
        print(f"Reminder error: {e}")

def start_scheduler(config: dict, memory: Memory):
    """Start background scheduler."""
    print("""
⏰ SCHEDULER ACTIVE:
   Morning USA hunt:  08:00 AM daily
   Midday followup:   12:00 PM daily
   Evening report:    07:00 PM daily
    """)

    schedule.every().day.at("08:00").do(
        run_morning_hunt, config=config, memory=memory
    )
    schedule.every().day.at("12:00").do(
        run_midday_followup, config=config, memory=memory
    )
    schedule.every().day.at("19:00").do(
        run_evening_report, config=config, memory=memory
    )

    def run_schedule():
        while True:
            schedule.run_pending()
            time.sleep(30)

    t = threading.Thread(target=run_schedule, daemon=True)
    t.start()
    print("✅ Scheduler running in background\n")

# ────────────────────────────────────────────────────────────────
# DETECT INTENT
# ────────────────────────────────────────────────────────────────

def detect_intent(text: str) -> str:
    t = text.lower()

    if any(w in t for w in [
        "auto hunt", "hunt for",
        "find and pitch", "do everything",
        "full auto", "auto find"
    ]):
        return "auto"

    elif any(w in t for w in [
        "find businesses", "find restaurants",
        "find law firms", "find salons",
        "find pharmacies", "find hospitals",
        "find hotels", "find schools",
        "find shops", "find companies",
        "find dentists", "find gyms",
        "find real estate"
    ]):
        return "find_businesses"

    elif any(w in t for w in [
        "check website", "website quality",
        "analyze website", "review website"
    ]):
        return "check_website_quality"

    elif any(w in t for w in [
        "price for a", "cost for a",
        "how much for a", "charge for a",
        "pricing for"
    ]):
        return "calculate_price"

    elif any(w in t for w in [
        "roi for", "return on investment",
        "calculate roi", "show roi"
    ]):
        return "calculate_roi"

    elif any(w in t for w in [
        "save lead", "add lead",
        "save client", "add client"
    ]):
        return "save_lead"

    elif any(w in t for w in [
        "show my leads", "view leads",
        "my leads", "my pipeline"
    ]):
        return "view_leads"

    elif any(w in t for w in [
        "update lead", "change status",
        "mark lead as"
    ]):
        return "update_lead_status"

    elif any(w in t for w in [
        "write proposal", "save proposal",
        "save to file", "write to file"
    ]):
        return "write_file"

    elif any(w in t for w in [
        "read file", "open file",
        "show file"
    ]):
        return "read_file"

    else:
        return "none"

# ────────────────────────────────────────────────────────────────
# PARSE AUTO COMMAND
# ────────────────────────────────────────────────────────────────

def parse_auto_command(text: str) -> tuple:
    t = text.lower()

    business_types = [
        "law firms", "lawyers",
        "dental clinics", "dentists",
        "real estate agents", "realtors",
        "restaurants", "restaurant",
        "gyms", "fitness centers",
        "hospitals", "clinics",
        "pharmacies", "pharmacy",
        "hotels", "lodges",
        "salons", "barbershops",
        "schools", "colleges",
        "car dealers", "garages",
        "supermarkets", "shops",
        "hvac companies", "roofing companies",
        "solar installers",
        "banks", "insurance companies",
    ]

    countries = [
        "usa", "united states", "america",
        "kenya", "nigeria", "ghana",
        "tanzania", "uganda", "rwanda",
        "south africa", "ethiopia",
        "uk", "australia", "canada",
        "india", "uae", "dubai",
        "germany", "france",
    ]

    cities = [
        # USA cities
        "new york", "manhattan", "brooklyn",
        "los angeles", "chicago", "miami",
        "houston", "dallas", "seattle",
        "boston", "atlanta", "san francisco",
        "phoenix", "denver", "las vegas",
        "austin", "nashville", "portland",
        # Kenya cities
        "nairobi", "mombasa", "kisumu",
        "eldoret", "nakuru", "westlands",
        "karen", "kilimani", "eastleigh",
        # Other cities
        "lagos", "abuja", "accra",
        "johannesburg", "cape town",
        "london", "dubai", "sydney",
        "toronto", "berlin", "paris",
    ]

    found_business = "law firms"
    found_city = "New York"
    found_country = "USA"

    for b in business_types:
        if b in t:
            found_business = b
            break

    for city in cities:
        if city in t:
            found_city = city.title()
            break

    for country in countries:
        if country in t:
            found_country = country.title()
            break

    return found_business, found_city, found_country

# ────────────────────────────────────────────────────────────────
# HANDLE MESSAGE
# ────────────────────────────────────────────────────────────────

def handle_message(
    user_input: str,
    memory: Memory,
    config: dict,
    voice_muted: bool = False
) -> bool:
    if not user_input:
        return True

    cmd = user_input.lower().strip()

    # ── Quit ──────────────────────────────────────────────────
    if any(w in cmd for w in [
        "quit", "exit", "bye",
        "goodbye", "shut down",
        "power off", "offline"
    ]):
        bye = (
            f"Going offline {USER_NAME}. "
            f"Scheduler keeps running. "
            f"USA hunt continues. "
            f"Stay sharp."
        )
        print(f"\nJarvis: {bye}\n")
        jarvis_speak(bye)
        return False

    # ── Clear session ──────────────────────────────────────────
    elif any(w in cmd for w in [
        "clear", "reset", "fresh start"
    ]):
        memory.clear()
        msg = (
            f"Session cleared {USER_NAME}. "
            f"Memory kept. "
            f"What is the mission?"
        )
        print(f"Jarvis: {msg}\n")
        jarvis_speak(msg)
        return True

    # ── Wipe all memory ────────────────────────────────────────
    elif any(w in cmd for w in [
        "forget everything",
        "wipe all memory",
        "delete memory",
        "clear all memory"
    ]):
        memory.clear()
        if os.path.exists("jarvis_memory.json"):
            os.remove("jarvis_memory.json")
        msg = (
            f"All memory wiped {USER_NAME}. "
            f"Starting fresh."
        )
        print(f"Jarvis: {msg}\n")
        jarvis_speak(msg)
        return True

    # ── Show memory ────────────────────────────────────────────
    elif any(w in cmd for w in [
        "what do you remember",
        "show memory",
        "what do you know about me",
        "my memory"
    ]):
        summary = get_memory_summary()
        if summary:
            print(f"\n{summary}\n")
            jarvis_speak(
                f"Memory loaded {USER_NAME}. "
                f"Check your screen."
            )
        else:
            msg = (
                f"No persistent memory yet {USER_NAME}. "
                f"Tell me something important."
            )
            print(f"Jarvis: {msg}\n")
            jarvis_speak(msg)
        return True

    # ── Manual schedule triggers ───────────────────────────────
    elif any(w in cmd for w in [
        "run morning hunt",
        "start morning hunt",
        "run daily hunt",
        "hunt now"
    ]):
        jarvis_speak(
            f"Running USA morning hunt now {USER_NAME}."
        )
        run_morning_hunt(config, memory)
        return True

    elif any(w in cmd for w in [
        "run evening report",
        "give me report",
        "daily report",
        "evening report"
    ]):
        jarvis_speak(
            f"Generating report {USER_NAME}."
        )
        run_evening_report(config, memory)
        return True

    elif any(w in cmd for w in [
        "follow up reminder",
        "show reminders",
        "what to follow up",
        "midday report"
    ]):
        run_midday_followup(config, memory)
        return True

    elif any(w in cmd for w in [
        "scheduler status",
        "what is scheduled",
        "show schedule",
        "schedule"
    ]):
        print(f"""
====================================
SCHEDULER STATUS - USA FOCUS
====================================
Morning Hunt:     08:00 AM daily
  Law firms       New York
  Dental clinics  Los Angeles
  Real estate     Chicago
  Restaurants     Miami
  Gyms            Houston

Midday Followup:  12:00 PM daily
  Follow up on existing leads

Evening Report:   07:00 PM daily
  Full day summary
  Tomorrow priorities
====================================
        """)
        jarvis_speak(
            f"Scheduler active {USER_NAME}. "
            f"Hunting USA leads daily. "
            f"Check screen for details."
        )
        return True

    # ── Leads ─────────────────────────────────────────────────
    elif any(w in cmd for w in [
        "leads", "pipeline", "my leads"
    ]):
        result = ALL_FUNCTIONS["view_leads"]()
        print(result)
        jarvis_speak(
            f"USA pipeline on screen {USER_NAME}."
        )
        return True

    # ── Files ─────────────────────────────────────────────────
    elif any(w in cmd for w in [
        "my files", "saved files",
        "show files", "list files"
    ]):
        files = [
            f for f in os.listdir(".")
            if f.endswith(".txt") or f.endswith(".json")
        ]
        if files:
            print(f"\nFiles ({len(files)} total):")
            for f in files:
                size = os.path.getsize(f)
                print(f"  {f} ({size} bytes)")
            print()
            jarvis_speak(
                f"{len(files)} files on record {USER_NAME}."
            )
        else:
            msg = f"No files yet {USER_NAME}."
            print(f"{msg}\n")
            jarvis_speak(msg)
        return True

    # ── Voices ────────────────────────────────────────────────
    elif cmd == "voices":
        list_voices()
        return True

    # ── Set voice ─────────────────────────────────────────────
    elif cmd.startswith("setvoice "):
        voice_name = user_input.split(" ", 1)[1].strip()
        set_voice(voice_name)
        jarvis_speak(
            f"Voice updated {USER_NAME}."
        )
        return True

    # ── Help ──────────────────────────────────────────────────
    elif cmd == "help":
        print(f"""
====================================
J.A.R.V.I.S - {USER_NAME}
PRIMARY MARKET: USA
====================================
VOICE:
  ENTER           Continuous voice
  C               Clap mode
  mute            Silence Jarvis
  unmute          Restore voice
  voices          List voices
  setvoice NAME   Change voice

COMMANDS:
  quit                   Shutdown
  clear                  Reset session
  forget everything      Wipe memory
  what do you remember   Show memory
  leads                  View pipeline
  my files               Saved files
  schedule               Show schedule
  help                   This menu

SCHEDULER:
  run morning hunt    Hunt USA now
  run evening report  Day summary
  follow up reminder  Who to call

USA BUSINESS HUNT:
  "Auto hunt law firms in New York USA"
  "Auto hunt dentists in Los Angeles USA"
  "Auto hunt real estate in Chicago USA"
  "Hunt restaurants in Miami USA"
  "Hunt gyms in Houston USA"

MANUAL TOOLS:
  "Price for a law firm in New York"
  "Find dental clinics in Boston USA"
  "Show my leads"
  "Check website of smithlaw.com"
  "Write proposal for Smith Law Firm"

MEMORY:
  "My goal is..."
  "Remember that..."
  "What do you remember about me?"
====================================
        """)
        jarvis_speak(
            f"Systems guide on screen {USER_NAME}."
        )
        return True

    # ── Auto save facts ────────────────────────────────────────
    auto_save_facts(user_input)

    # ── Auto hunt ─────────────────────────────────────────────
    intent = detect_intent(user_input)

    if intent == "auto":
        business, city, country = parse_auto_command(
            user_input
        )
        print(
            f"\nJarvis: Initiating USA hunt. "
            f"Target: {business} in {city}...\n"
        )
        result = auto_hunt(
            business, city, country, config, memory
        )
        print(f"\n{result}\n")
        return True

    # ── Normal conversation ───────────────────────────────────
    memory.add_user(user_input)
    memory.trim()

    print("Jarvis: ", end="", flush=True)

    if intent == "none":
        response = chat(memory, config)
    else:
        response = chat_with_tool(
            memory, config, intent
        )

    print(f"{response}\n")

    if not voice_muted:
        jarvis_speak(response)

    memory.add_jarvis(response)
    return True

# ────────────────────────────────────────────────────────────────
# MAIN
# ────────────────────────────────────────────────────────────────

def main():
    config = load_config()
    memory = Memory(config["agent"]["system_prompt"])
    voice_muted = False

    existing_memory = get_memory_summary()
    if existing_memory:
        intro = (
            f"Systems online {USER_NAME}. "
            f"Memory loaded. "
            f"USA hunt scheduler active. "
            f"Ready to close deals."
        )
    else:
        intro = (
            f"Elite systems online {USER_NAME}. "
            f"Groq 70B core active. "
            f"USA market locked in. "
            f"Scheduler hunting leads daily. "
            f"What is the mission?"
        )

    print(f"""
====================================
  J.A.R.V.I.S
  Elite Core Online for {USER_NAME}
  Model: Groq Llama 3.3 70B
  Market: USA PRIMARY
  Memory: Persistent
  Scheduler: Active
====================================
  ENTER    = Continuous voice
  C        = Clap mode
  Type     = Text mode
  help     = All commands
====================================
    """)

    start_scheduler(config, memory)

    print(f"Jarvis: {intro}\n")
    jarvis_speak(intro)

    while True:
        try:
            choice = input(
                f"{USER_NAME} "
                f"(ENTER=voice | C=clap | type): "
            ).strip()

            # ── Continuous voice ──────────────────────────────
            if choice == "":
                msg = (
                    f"Listening {USER_NAME}. "
                    f"Say stop to return to text."
                )
                print(f"\nJarvis: {msg}\n")
                jarvis_speak(msg)

                def on_voice(text):
                    if any(w in text.lower() for w in [
                        "stop", "stop listening",
                        "back to text", "text mode"
                    ]):
                        back = (
                            f"Switching to text "
                            f"{USER_NAME}."
                        )
                        print(f"Jarvis: {back}\n")
                        jarvis_speak(back)
                        return False
                    return handle_message(
                        text, memory,
                        config, voice_muted
                    )

                listen_continuous(
                    on_voice,
                    stop_words=[
                        "stop", "stop listening",
                        "quit", "exit", "bye",
                        "offline", "shutdown"
                    ],
                    is_speaking_flag=is_speaking
                )
                continue

            # ── Clap mode ─────────────────────────────────────
            elif choice.lower() == "c":
                msg = (
                    f"Clap mode active {USER_NAME}. "
                    f"Double clap to activate."
                )
                print(f"Jarvis: {msg}\n")
                jarvis_speak(msg)

                try:
                    while True:
                        print("👏 Waiting for clap...")
                        clapped = wait_for_clap()

                        if clapped:
                            wake = (
                                f"Yes {USER_NAME}. "
                                f"Listening."
                            )
                            print(f"Jarvis: {wake}")
                            jarvis_speak(wake)

                            def on_clap(text):
                                if any(
                                    w in text.lower()
                                    for w in [
                                        "stop clap",
                                        "exit clap",
                                        "quit"
                                    ]
                                ):
                                    return False
                                return handle_message(
                                    text, memory,
                                    config, voice_muted
                                )

                            listen_continuous(
                                on_clap,
                                stop_words=[
                                    "stop clap",
                                    "exit clap",
                                    "quit", "exit"
                                ],
                                is_speaking_flag=is_speaking
                            )
                            break

                except KeyboardInterrupt:
                    pass

                msg = f"Clap mode off {USER_NAME}."
                print(f"Jarvis: {msg}\n")
                jarvis_speak(msg)
                continue

            # ── Mute ──────────────────────────────────────────
            elif choice.lower() == "mute":
                voice_muted = True
                print(
                    f"Jarvis: Audio muted {USER_NAME}.\n"
                )
                continue

            # ── Unmute ────────────────────────────────────────
            elif choice.lower() == "unmute":
                voice_muted = False
                jarvis_speak(
                    f"Audio restored {USER_NAME}."
                )
                continue

            # ── Text input ────────────────────────────────────
            else:
                keep_going = handle_message(
                    choice, memory,
                    config, voice_muted
                )
                if not keep_going:
                    break

        except KeyboardInterrupt:
            bye = (
                f"Emergency shutdown {USER_NAME}. "
                f"USA scheduler keeps running. "
                f"Stay sharp."
            )
            print(f"\nJarvis: {bye}")
            jarvis_speak(bye)
            break

if __name__ == "__main__":
    main()