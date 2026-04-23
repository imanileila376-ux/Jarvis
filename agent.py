import yaml
import json
import os
import time
import threading
from datetime import datetime
from litellm import completion
from tools.basic_tools import TOOLS, TOOL_FUNCTIONS
from tools.web_tools import WEB_TOOLS, WEB_TOOL_FUNCTIONS
from voice import speak, list_voices, set_voice
from listen import listen, listen_continuous, wait_for_clap
from memory_store import remember_fact, get_memory_summary

# ────────────────────────────────────────────────────────────────
# DETAILS
# ────────────────────────────────────────────────────────────────

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
            full_prompt = system_prompt + "\n\n" + persistent
        self.messages = [
            {"role": "system", "content": full_prompt}
        ]
        self.max_messages = 40

    def add_user(self, text: str):
        self.messages.append({
            "role": "user", "content": text
        })

    def add_jarvis(self, text: str):
        self.messages.append({
            "role": "assistant", "content": text
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
    tool_name: str,
    all_tools: list,
    all_functions: dict
) -> str:
    print(f"\n🔧 Using tool: {tool_name}...")

    try:
        response = completion(
            model=config["llm"]["model"],
            messages=memory.get(),
            api_key=config["llm"]["api_key"],
            temperature=0.1,
            max_tokens=1000,
            tools=all_tools,
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
            result = all_functions[tool_name](**args)
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
    memory: Memory,
    all_functions: dict
) -> str:
    print(f"""
=====================================
AUTO HUNT
Target:   {business_type}
Location: {location}, {country}
=====================================
    """)

    jarvis_speak(
        f"Copy that {USER_NAME}. "
        f"Hunting {business_type} in {location}."
    )

    businesses = all_functions["find_businesses"](
        business_type=business_type,
        location=location,
        country=country
    )
    jarvis_speak("Targets acquired. Calculating pricing.")

    price_report = all_functions["calculate_price"](
        country=country,
        city=location,
        business_type=business_type,
        size="medium"
    )

    roi_report = all_functions["calculate_roi"](
        country=country,
        revenue_per_client=1000,
        expected_new_clients=5,
        website_cost=2000
    )

    jarvis_speak("Writing pitches.")

    pitch_messages = [
        {
            "role": "system",
            "content": (
                f"Elite sales agent for {COMPANY}. "
                f"Write sharp USA pitches. "
                f"Price exactly $2000. Show ROI. "
                f"Include WhatsApp {WHATSAPP} "
                f"and Email {EMAIL}. "
                f"Under 150 words each."
            )
        },
        {
            "role": "user",
            "content": (
                f"Pitches for:\n{businesses}\n"
                f"Pricing: {price_report}\n"
                f"ROI: {roi_report}"
            )
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
Date:     {datetime.now().strftime("%Y-%m-%d %H:%M")}
Target:   {business_type}
Location: {location}, {country}

BUSINESSES:
{businesses}

PRICING:
{price_report}

ROI:
{roi_report}

PITCHES:
{pitches}
    """

    all_functions["write_file"](
        filename=filename,
        content=report
    )

    all_functions["save_lead"](
        business_name=f"{business_type} - {location}",
        contact=f"Email: {EMAIL}",
        location=location,
        country=country,
        deal_value="$2,000",
        status="New"
    )

    jarvis_speak(
        f"Mission complete {USER_NAME}. "
        f"Check your screen."
    )

    print(f"Saved to: {filename}\n")
    memory.add_jarvis(
        f"Hunt complete for {business_type} "
        f"in {location}. Saved to {filename}."
    )

    return pitches

# ────────────────────────────────────────────────────────────────
# AUTO SAVE FACTS
# ────────────────────────────────────────────────────────────────

def auto_save_facts(user_input: str):
    text = user_input.lower()
    triggers = [
        "my name is", "my goal is",
        "i want to", "my business is",
        "i live in", "remember that",
        "remember this", "dont forget",
        "my company is", "my target market is",
    ]
    for trigger in triggers:
        if trigger in text:
            remember_fact(user_input.strip())
            print(f"🧠 Remembered: {user_input.strip()}\n")
            break

# ────────────────────────────────────────────────────────────────
# DETECT INTENT
# ────────────────────────────────────────────────────────────────

def detect_intent(text: str) -> str:
    t = text.lower()

    # Website building - check FIRST
    if any(w in t for w in [
        "build website", "create website",
        "make website", "build their site",
        "publish website", "build and publish",
        "build site for", "make site for",
        "build a website", "create a website",
        "build the website", "build_website",
        "website tool", "launch website",
        "deploy website", "generate website",
        "client agreed", "client said yes",
        "client paid", "build their website",
        "create their website",
        "make their website",
    ]):
        return "build_website"

    # Auto hunt
    elif any(w in t for w in [
        "auto hunt", "hunt for",
        "find and pitch", "do everything",
        "full auto", "auto find"
    ]):
        return "auto"

    # Find businesses
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

    # Check website quality
    elif any(w in t for w in [
        "check website", "website quality",
        "analyze website", "review website"
    ]):
        return "check_website_quality"

    # AI Image generation
    elif any(w in t for w in [
        "generate image", "create image",
        "ai image", "generate photo",
        "ai influencer", "generate influencer",
        "create model", "ai model",
        "virtual influencer"
    ]):
        return "generate_ai_image"

    # Price
    elif any(w in t for w in [
        "price for", "cost for",
        "how much for", "charge for",
        "pricing for", "quote for"
    ]):
        return "calculate_price"

    # ROI
    elif any(w in t for w in [
        "roi for", "return on investment",
        "calculate roi", "show roi"
    ]):
        return "calculate_roi"

    # Save lead
    elif any(w in t for w in [
        "save lead", "add lead",
        "save client", "add client",
        "save this lead"
    ]):
        return "save_lead"

    # View leads
    elif any(w in t for w in [
        "show my leads", "view leads",
        "my leads", "my pipeline",
        "all leads"
    ]):
        return "view_leads"

    # Update lead
    elif any(w in t for w in [
        "update lead", "change status",
        "mark lead as"
    ]):
        return "update_lead_status"

    # Write file
    elif any(w in t for w in [
        "write proposal", "save proposal",
        "save to file", "write to file"
    ]):
        return "write_file"

    # Read file
    elif any(w in t for w in [
        "read file", "open file", "show file"
    ]):
        return "read_file"

    # WhatsApp link
    elif any(w in t for w in [
        "whatsapp link", "wa.me",
        "generate whatsapp"
    ]):
        return "generate_whatsapp_link"

    else:
        return "none"

# ────────────────────────────────────────────────────────────────
# PARSE AUTO COMMAND
# ────────────────────────────────────────────────────────────────

def parse_auto_command(text: str) -> tuple:
    t = text.lower()

    business_types = [
        "restaurants", "restaurant",
        "law firms", "lawyers",
        "dental clinics", "dentists",
        "hospitals", "clinics",
        "pharmacies", "pharmacy",
        "hotels", "lodges",
        "salons", "barbershops",
        "gyms", "fitness centers",
        "schools", "colleges",
        "real estate agents",
        "car dealers", "garages",
        "supermarkets", "shops",
        "hvac companies",
        "solar installers",
        "medical clinics",
    ]

    countries = [
        "usa", "united states", "america",
        "kenya", "nigeria", "ghana",
        "south africa", "ethiopia",
        "uk", "australia", "canada",
        "india", "uae", "dubai",
        "germany", "france",
    ]

    cities = [
        "new york", "manhattan",
        "los angeles", "chicago", "miami",
        "houston", "dallas", "seattle",
        "boston", "atlanta", "san francisco",
        "nairobi", "mombasa", "westlands",
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
    all_tools: list,
    all_functions: dict,
    voice_muted: bool = False
) -> bool:
    if not user_input:
        return True

    cmd = user_input.lower().strip()

    # Quit
    if any(w in cmd for w in [
        "quit", "exit", "bye",
        "goodbye", "shut down", "offline"
    ]):
        bye = f"Going offline {USER_NAME}. Stay sharp."
        print(f"\nJarvis: {bye}\n")
        jarvis_speak(bye)
        return False

    # Clear
    elif any(w in cmd for w in [
        "clear", "reset", "fresh start"
    ]):
        memory.clear()
        msg = f"Cleared {USER_NAME}. What is the mission?"
        print(f"Jarvis: {msg}\n")
        jarvis_speak(msg)
        return True

    # Wipe all memory
    elif any(w in cmd for w in [
        "forget everything", "wipe all memory",
        "delete memory"
    ]):
        memory.clear()
        if os.path.exists("jarvis_memory.json"):
            os.remove("jarvis_memory.json")
        msg = f"All memory wiped {USER_NAME}."
        print(f"Jarvis: {msg}\n")
        jarvis_speak(msg)
        return True

    # Show memory
    elif any(w in cmd for w in [
        "what do you remember",
        "show memory",
        "what do you know about me"
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
                f"No memory yet {USER_NAME}. "
                f"Tell me something important."
            )
            print(f"Jarvis: {msg}\n")
            jarvis_speak(msg)
        return True

    # Leads
    elif any(w in cmd for w in [
        "leads", "pipeline", "my leads"
    ]):
        result = all_functions["view_leads"]()
        print(result)
        jarvis_speak(f"Pipeline on screen {USER_NAME}.")
        return True

    # Files
    elif any(w in cmd for w in [
        "my files", "saved files",
        "show files", "list files"
    ]):
        files = [
            f for f in os.listdir(".")
            if f.endswith(".txt") or
            f.endswith(".json") or
            f.endswith(".html")
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

    # Voices
    elif cmd == "voices":
        list_voices()
        jarvis_speak("Check screen for voices.")
        return True

    # Set voice
    elif cmd.startswith("setvoice "):
        voice_name = user_input.split(" ", 1)[1].strip()
        set_voice(voice_name)
        jarvis_speak(f"Voice updated {USER_NAME}.")
        return True

    # Mute
    elif cmd == "mute":
        print(f"Jarvis: Voice muted {USER_NAME}.\n")
        return True

    # Help
    elif cmd == "help":
        print(f"""
====================================
J.A.R.V.I.S - {USER_NAME}
====================================
VOICE:
  ENTER           Continuous voice
  C               Clap mode
  mute            Silence voice
  voices          List voices
  setvoice NAME   Change voice

COMMANDS:
  quit                   Shutdown
  clear                  Reset session
  forget everything      Wipe all memory
  what do you remember   Show memory
  leads                  View pipeline
  my files               Saved files
  help                   This menu

WEBSITE BUILDER:
  "Build a website for [Business Name]
   [business type] in [City]"

  Examples:
  "Build a website for Bright Smiles
   dental clinic in Los Angeles"

  "Build a website for Smith Law Group
   law firm in New York"

  "Build a website for The Capital Grille
   restaurant in Boston"

BUSINESS HUNTING:
  "Auto hunt law firms in New York USA"
  "Hunt dental clinics in LA USA"
  "Find restaurants in Miami USA"

PRICING:
  "Price for a law firm in New York"

AI IMAGES:
  "Generate AI influencer female
   American fashion New York"

LEADS:
  "Show my leads"
  "Save lead: Name City Contact Value"

JUST TALK:
  Ask Jarvis anything
====================================
        """)
        jarvis_speak(f"Help on screen {USER_NAME}.")
        return True

    # Auto save facts
    auto_save_facts(user_input)

    # Detect intent
    intent = detect_intent(user_input)

    # Auto hunt
    if intent == "auto":
        business, city, country = parse_auto_command(
            user_input
        )
        print(
            f"\nJarvis: Hunting {business} "
            f"in {city}...\n"
        )
        jarvis_speak(
            f"Initiating hunt {USER_NAME}. "
            f"Target {business} in {city}."
        )
        result = auto_hunt(
            business, city, country,
            config, memory, all_functions
        )
        print(f"\n{result}\n")
        return True

    # Tool call
    elif intent != "none":
        memory.add_user(user_input)
        memory.trim()

        print("Jarvis: ", end="", flush=True)
        response = chat_with_tool(
            memory, config, intent,
            all_tools, all_functions
        )
        print(f"{response}\n")

        if not voice_muted:
            jarvis_speak(response)

        memory.add_jarvis(response)
        return True

    # Normal chat
    else:
        memory.add_user(user_input)
        memory.trim()

        print("Jarvis: ", end="", flush=True)
        response = chat(memory, config)
        print(f"{response}\n")

        if not voice_muted:
            jarvis_speak(response)

        memory.add_jarvis(response)
        return True

# ────────────────────────────────────────────────────────────────
# MAIN
# ────────────────────────────────────────────────────────────────

def main():
    # Build combined tools INSIDE main
    # so all tools are loaded first
    ALL_TOOLS = TOOLS + WEB_TOOLS
    ALL_FUNCTIONS = {
        **TOOL_FUNCTIONS,
        **WEB_TOOL_FUNCTIONS
    }

    config = load_config()
    memory = Memory(config["agent"]["system_prompt"])
    voice_muted = False

    existing_memory = get_memory_summary()
    if existing_memory:
        intro = (
            f"Systems online {USER_NAME}. "
            f"Memory loaded. Ready for the mission."
        )
    else:
        intro = (
            f"Elite systems online {USER_NAME}. "
            f"Groq 70B core active. "
            f"Website builder ready. "
            f"What is the mission today?"
        )

    print(f"""
====================================
  J.A.R.V.I.S
  Elite AI for {USER_NAME}
  Model: Groq Llama 3.3 70B
  Website Builder: Active
  Memory: Persistent
====================================
  ENTER    = Continuous voice
  C        = Clap mode
  Type     = Text mode
  help     = All commands
====================================
    """)

    print(f"Jarvis: {intro}\n")
    jarvis_speak(intro)

    while True:
        try:
            choice = input(
                f"{USER_NAME} "
                f"(ENTER=voice | C=clap | type): "
            ).strip()

            # Continuous voice
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
                        "back to text"
                    ]):
                        back = f"Back to text {USER_NAME}."
                        print(f"Jarvis: {back}\n")
                        jarvis_speak(back)
                        return False
                    return handle_message(
                        text, memory, config,
                        ALL_TOOLS, ALL_FUNCTIONS,
                        voice_muted
                    )

                listen_continuous(
                    on_voice,
                    stop_words=[
                        "stop", "quit", "exit"
                    ],
                    is_speaking_flag=is_speaking
                )
                continue

            # Clap mode
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
                                f"Yes {USER_NAME}. Listening."
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
                                    text, memory, config,
                                    ALL_TOOLS, ALL_FUNCTIONS,
                                    voice_muted
                                )

                            listen_continuous(
                                on_clap,
                                stop_words=[
                                    "stop clap",
                                    "exit clap",
                                    "quit"
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

            # Mute
            elif choice.lower() == "mute":
                voice_muted = True
                print(
                    f"Jarvis: Voice muted {USER_NAME}.\n"
                )
                continue

            # Unmute
            elif choice.lower() == "unmute":
                voice_muted = False
                jarvis_speak(
                    f"Audio restored {USER_NAME}."
                )
                continue

            # Text input
            else:
                keep_going = handle_message(
                    choice, memory, config,
                    ALL_TOOLS, ALL_FUNCTIONS,
                    voice_muted
                )
                if not keep_going:
                    break

        except KeyboardInterrupt:
            bye = f"Goodbye {USER_NAME}. Stay sharp."
            print(f"\nJarvis: {bye}")
            jarvis_speak(bye)
            break

if __name__ == "__main__":
    main()