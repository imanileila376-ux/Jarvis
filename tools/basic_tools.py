import os
import json
import time
import urllib.parse
from datetime import datetime

try:
    import pywhatkit
    WHATSAPP_AVAILABLE = True
except:
    WHATSAPP_AVAILABLE = False

# ────────────────────────────────────────────────────────────────
# TOOL FUNCTIONS
# ────────────────────────────────────────────────────────────────

def calculate(expression: str) -> str:
    try:
        result = eval(expression)
        return str(result)
    except Exception as e:
        return f"Error: {e}"

def write_file(filename: str, content: str) -> str:
    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(content)
        return f"File saved: {filename}"
    except Exception as e:
        return f"Error: {e}"

def read_file(filename: str) -> str:
    try:
        with open(filename, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"Error: {e}"

def calculate_price(
    country: str,
    city: str,
    business_type: str,
    size: str
) -> str:
    country = country.lower().strip()
    city = city.lower().strip()
    business_type = business_type.lower().strip()
    size = size.lower().strip()

    # ── USA Fixed $2000 pricing ───────────────────────────────
    if country in [
        "usa", "united states",
        "america", "us"
    ]:
        return f"""
DYNAMIC PRICING REPORT
======================
Business : {business_type.title()}
Location : {city.title()}, USA
Size     : {size.title()}

PACKAGES:
---------
1. Starter    : $ 800
   5 page website, mobile friendly,
   contact form, Google Maps,
   social media links

2. Growth     : $ 2,000
   Everything in Starter plus
   WhatsApp button, lead capture,
   blog section, basic SEO

3. Automation : $ 4,000
   Everything in Growth plus
   online booking, payment integration,
   customer database, monthly reports,
   6 months support

RECOMMENDED: Package 2 - Growth
TARGET DEAL: $ 2,000
"""

    # ── Other countries ───────────────────────────────────────
    if country in ["uk", "united kingdom", "england"]:
        symbol = "GBP"
        base = 2500 if "london" in city else 1200

    elif country in ["australia", "aus"]:
        symbol = "AUD"
        base = 3000 if any(
            c in city for c in ["sydney", "melbourne"]
        ) else 1500

    elif country in ["canada", "ca"]:
        symbol = "CAD"
        base = 2500 if any(
            c in city for c in ["toronto", "vancouver"]
        ) else 1200

    elif country in ["germany", "deutschland"]:
        symbol = "EUR"
        base = 3000 if any(
            c in city for c in ["berlin", "munich"]
        ) else 1500

    elif country in ["south africa", "sa"]:
        symbol = "ZAR"
        base = 25000 if any(
            c in city for c in [
                "johannesburg", "cape town"
            ]
        ) else 12000

    elif country in ["nigeria", "ng"]:
        symbol = "NGN"
        base = 800000 if any(
            c in city for c in ["lagos", "abuja"]
        ) else 400000

    elif country in ["kenya", "ke"]:
        symbol = "Ksh"
        base = 3000 if any(
            c in city for c in ["nairobi", "mombasa"]
        ) else 2000

    elif country in ["ghana", "gh"]:
        symbol = "GHS"
        base = 5000

    elif country in ["tanzania", "tz"]:
        symbol = "TZS"
        base = 150000

    elif country in ["uganda", "ug"]:
        symbol = "UGX"
        base = 1500000

    elif country in ["rwanda", "rw"]:
        symbol = "RWF"
        base = 400000

    elif country in ["india", "in"]:
        symbol = "INR"
        base = 80000 if any(
            c in city for c in [
                "mumbai", "delhi", "bangalore"
            ]
        ) else 40000

    elif country in ["uae", "dubai", "emirates"]:
        symbol = "AED"
        base = 5000

    elif country in ["singapore", "sg"]:
        symbol = "SGD"
        base = 3000

    elif country in ["france", "fr"]:
        symbol = "EUR"
        base = 2500 if "paris" in city else 1500

    elif country in ["brazil", "br"]:
        symbol = "BRL"
        base = 5000 if "sao paulo" in city else 3000

    elif country in ["mexico", "mx"]:
        symbol = "MXN"
        base = 15000 if "mexico city" in city else 8000

    else:
        symbol = "$"
        base = 2000

    starter = int(base * 0.4)
    growth = base
    automation = int(base * 2)

    return f"""
DYNAMIC PRICING REPORT
======================
Business : {business_type.title()}
Location : {city.title()}, {country.title()}
Size     : {size.title()}

PACKAGES:
---------
1. Starter    : {symbol} {starter:,}
2. Growth     : {symbol} {growth:,}
3. Automation : {symbol} {automation:,}

RECOMMENDED: Package 2 - Growth
TARGET DEAL: {symbol} {growth:,}
"""

def calculate_roi(
    country: str,
    revenue_per_client: int,
    expected_new_clients: int,
    website_cost: int
) -> str:
    country = country.lower()
    symbols = {
        "kenya": "Ksh", "ke": "Ksh",
        "nigeria": "NGN", "ng": "NGN",
        "uk": "GBP", "united kingdom": "GBP",
        "australia": "AUD", "aus": "AUD",
        "canada": "CAD", "ca": "CAD",
        "south africa": "ZAR", "sa": "ZAR",
        "india": "INR", "in": "INR",
        "uae": "AED", "dubai": "AED",
        "ghana": "GHS", "gh": "GHS",
        "tanzania": "TZS", "tz": "TZS",
        "uganda": "UGX", "ug": "UGX",
        "rwanda": "RWF", "rw": "RWF",
    }
    symbol = symbols.get(country, "$")
    monthly = revenue_per_client * expected_new_clients
    yearly = monthly * 12
    roi = (
        (yearly - website_cost) / website_cost
    ) * 100
    payback = (
        website_cost / monthly if monthly > 0 else 0
    )
    return f"""
ROI CALCULATION
===============
Extra clients/month  : +{expected_new_clients}
Revenue per client   : {symbol} {revenue_per_client:,}
Extra monthly revenue: {symbol} {monthly:,}
Extra yearly revenue : {symbol} {yearly:,}
Website investment   : {symbol} {website_cost:,}
ROI                  : {roi:.0f}%
Payback period       : {payback:.1f} months

BOTTOM LINE:
Website pays for itself in {payback:.1f} months.
Then makes {symbol} {yearly:,} extra every year.
Over 5 years: {symbol} {yearly*5:,} extra!
"""

def save_lead(
    business_name: str,
    contact: str,
    location: str,
    country: str,
    deal_value: str,
    status: str = "New"
) -> str:
    try:
        leads_file = "leads_database.json"
        leads = []
        if os.path.exists(leads_file):
            with open(leads_file, "r") as f:
                leads = json.load(f)
        for lead in leads:
            if lead["business"].lower() == \
                    business_name.lower():
                return f"Lead exists: {business_name}"
        leads.append({
            "id": len(leads) + 1,
            "business": business_name,
            "contact": contact,
            "location": location,
            "country": country,
            "deal_value": deal_value,
            "status": status,
            "notes": "",
            "date_added": datetime.now().strftime(
                "%Y-%m-%d %H:%M"
            ),
            "last_updated": datetime.now().strftime(
                "%Y-%m-%d %H:%M"
            )
        })
        with open(leads_file, "w") as f:
            json.dump(leads, f, indent=2)
        return f"Lead saved: {business_name} | {deal_value}"
    except Exception as e:
        return f"Error: {e}"

def view_leads(country: str = "all") -> str:
    try:
        leads_file = "leads_database.json"
        if not os.path.exists(leads_file):
            return "No leads yet. Start hunting!"
        with open(leads_file, "r") as f:
            leads = json.load(f)
        if country != "all":
            leads = [
                l for l in leads
                if l["country"].lower() == country.lower()
            ]
        if not leads:
            return "No leads found."
        new = [l for l in leads if l["status"] == "New"]
        contacted = [
            l for l in leads
            if l["status"] == "Contacted"
        ]
        proposal = [
            l for l in leads
            if l["status"] == "Proposal Sent"
        ]
        closed = [
            l for l in leads
            if l["status"] == "Closed"
        ]
        lost = [
            l for l in leads
            if l["status"] == "Lost"
        ]
        result = f"""
LEADS PIPELINE ({len(leads)} total)
{'='*40}
New:           {len(new)}
Contacted:     {len(contacted)}
Proposal Sent: {len(proposal)}
Closed:        {len(closed)}
Lost:          {len(lost)}
{'='*40}
"""
        for i, lead in enumerate(leads, 1):
            result += f"""
{i}. {lead['business']}
   Location : {lead['location']}, {lead['country']}
   Value    : {lead['deal_value']}
   Status   : {lead['status']}
   Contact  : {lead['contact']}
   Added    : {lead['date_added']}
"""
        return result
    except Exception as e:
        return f"Error: {e}"

def update_lead_status(
    business_name: str,
    new_status: str
) -> str:
    try:
        leads_file = "leads_database.json"
        if not os.path.exists(leads_file):
            return "No leads database found."
        with open(leads_file, "r") as f:
            leads = json.load(f)
        for lead in leads:
            if lead["business"].lower() == \
                    business_name.lower():
                old = lead["status"]
                lead["status"] = new_status
                lead["last_updated"] = \
                    datetime.now().strftime(
                        "%Y-%m-%d %H:%M"
                    )
                with open(leads_file, "w") as f:
                    json.dump(leads, f, indent=2)
                return (
                    f"Updated: {business_name}\n"
                    f"{old} to {new_status}"
                )
        return f"Not found: {business_name}"
    except Exception as e:
        return f"Error: {e}"

def add_note(business_name: str, note: str) -> str:
    try:
        leads_file = "leads_database.json"
        if not os.path.exists(leads_file):
            return "No leads database found."
        with open(leads_file, "r") as f:
            leads = json.load(f)
        for lead in leads:
            if lead["business"].lower() == \
                    business_name.lower():
                lead["notes"] = note
                lead["last_updated"] = \
                    datetime.now().strftime(
                        "%Y-%m-%d %H:%M"
                    )
                with open(leads_file, "w") as f:
                    json.dump(leads, f, indent=2)
                return f"Note added to {business_name}"
        return f"Not found: {business_name}"
    except Exception as e:
        return f"Error: {e}"

def auto_send_whatsapp(
    phone_number: str,
    message: str
) -> str:
    """
    Auto send WhatsApp message using pywhatkit.
    Requires WhatsApp Web to be open in browser.
    """
    if not WHATSAPP_AVAILABLE:
        return (
            "pywhatkit not installed. "
            "Run: pip install pywhatkit"
        )

    try:
        if not phone_number.startswith("+"):
            return (
                "Error: Phone must start with + "
                "Example: +12125551234"
            )

        print(
            f"🚀 Opening WhatsApp for {phone_number}..."
        )
        print(
            "⚠️ DO NOT touch mouse or keyboard "
            "for 25 seconds!"
        )

        pywhatkit.sendwhatmsg_instantly(
            phone_no=phone_number,
            message=message,
            wait_time=20,
            tab_close=True,
            close_time=5
        )

        return f"Message sent to {phone_number}"

    except Exception as e:
        return f"WhatsApp error: {e}"

def generate_whatsapp_link(
    phone_number: str,
    message: str
) -> str:
    """Generate a click to chat WhatsApp link"""
    try:
        clean_phone = "".join(
            filter(str.isdigit, phone_number)
        )
        encoded = urllib.parse.quote(message)
        link = f"https://wa.me/{clean_phone}?text={encoded}"
        return f"""
WHATSAPP LINK READY
===================
Phone: {phone_number}

CLICK TO SEND:
{link}

HOW TO USE:
1. Copy link above
2. Paste in browser
3. WhatsApp opens with message ready
4. Press Send
        """
    except Exception as e:
        return f"Error: {e}"

# ────────────────────────────────────────────────────────────────
# TOOL DEFINITIONS
# ────────────────────────────────────────────────────────────────

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "calculate",
            "description": "Evaluate a math expression",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {"type": "string"}
                },
                "required": ["expression"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Save content to a file",
            "parameters": {
                "type": "object",
                "properties": {
                    "filename": {"type": "string"},
                    "content": {"type": "string"}
                },
                "required": ["filename", "content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read content from a file",
            "parameters": {
                "type": "object",
                "properties": {
                    "filename": {"type": "string"}
                },
                "required": ["filename"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculate_price",
            "description": "Calculate website price for a client",
            "parameters": {
                "type": "object",
                "properties": {
                    "country": {"type": "string"},
                    "city": {"type": "string"},
                    "business_type": {"type": "string"},
                    "size": {"type": "string"}
                },
                "required": [
                    "country", "city",
                    "business_type", "size"
                ]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculate_roi",
            "description": "Calculate ROI to show client value",
            "parameters": {
                "type": "object",
                "properties": {
                    "country": {"type": "string"},
                    "revenue_per_client": {
                        "type": "integer"
                    },
                    "expected_new_clients": {
                        "type": "integer"
                    },
                    "website_cost": {
                        "type": "integer"
                    }
                },
                "required": [
                    "country",
                    "revenue_per_client",
                    "expected_new_clients",
                    "website_cost"
                ]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "save_lead",
            "description": "Save a potential client to database",
            "parameters": {
                "type": "object",
                "properties": {
                    "business_name": {"type": "string"},
                    "contact": {"type": "string"},
                    "location": {"type": "string"},
                    "country": {"type": "string"},
                    "deal_value": {"type": "string"},
                    "status": {"type": "string"}
                },
                "required": [
                    "business_name", "contact",
                    "location", "country", "deal_value"
                ]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "view_leads",
            "description": "View all leads in pipeline",
            "parameters": {
                "type": "object",
                "properties": {
                    "country": {"type": "string"}
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "update_lead_status",
            "description": "Update status of a lead",
            "parameters": {
                "type": "object",
                "properties": {
                    "business_name": {"type": "string"},
                    "new_status": {"type": "string"}
                },
                "required": [
                    "business_name", "new_status"
                ]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "add_note",
            "description": "Add a note to a lead",
            "parameters": {
                "type": "object",
                "properties": {
                    "business_name": {"type": "string"},
                    "note": {"type": "string"}
                },
                "required": ["business_name", "note"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "auto_send_whatsapp",
            "description": "Automatically send a WhatsApp message to a phone number",
            "parameters": {
                "type": "object",
                "properties": {
                    "phone_number": {
                        "type": "string",
                        "description": "Phone with country code like +12125551234"
                    },
                    "message": {
                        "type": "string",
                        "description": "Message to send"
                    }
                },
                "required": ["phone_number", "message"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "generate_whatsapp_link",
            "description": "Generate a click to chat WhatsApp link with pre written message",
            "parameters": {
                "type": "object",
                "properties": {
                    "phone_number": {"type": "string"},
                    "message": {"type": "string"}
                },
                "required": ["phone_number", "message"]
            }
        }
    }
]

# ────────────────────────────────────────────────────────────────
# TOOL EXECUTOR
# ────────────────────────────────────────────────────────────────

TOOL_FUNCTIONS = {
    "calculate": calculate,
    "write_file": write_file,
    "read_file": read_file,
    "calculate_price": calculate_price,
    "calculate_roi": calculate_roi,
    "save_lead": save_lead,
    "view_leads": view_leads,
    "update_lead_status": update_lead_status,
    "add_note": add_note,
    "auto_send_whatsapp": auto_send_whatsapp,
    "generate_whatsapp_link": generate_whatsapp_link,
}