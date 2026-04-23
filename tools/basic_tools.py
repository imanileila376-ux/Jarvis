import os
import json
import urllib.parse
from datetime import datetime

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
2. Growth     : $ 2,000
3. Automation : $ 4,000

RECOMMENDED: Package 2 - Growth
TARGET DEAL: $ 2,000
"""

    symbols = {
        "uk": ("GBP", 2500),
        "united kingdom": ("GBP", 2500),
        "england": ("GBP", 2500),
        "australia": ("AUD", 3000),
        "aus": ("AUD", 3000),
        "canada": ("CAD", 2500),
        "ca": ("CAD", 2500),
        "germany": ("EUR", 3000),
        "deutschland": ("EUR", 3000),
        "south africa": ("ZAR", 25000),
        "sa": ("ZAR", 25000),
        "nigeria": ("NGN", 800000),
        "ng": ("NGN", 800000),
        "kenya": ("Ksh", 3000),
        "ke": ("Ksh", 3000),
        "ghana": ("GHS", 5000),
        "gh": ("GHS", 5000),
        "india": ("INR", 80000),
        "in": ("INR", 80000),
        "uae": ("AED", 5000),
        "dubai": ("AED", 5000),
        "singapore": ("SGD", 3000),
        "sg": ("SGD", 3000),
        "france": ("EUR", 2500),
        "fr": ("EUR", 2500),
        "brazil": ("BRL", 5000),
        "br": ("BRL", 5000),
        "mexico": ("MXN", 15000),
        "mx": ("MXN", 15000),
    }

    if country in symbols:
        symbol, base = symbols[country]
    else:
        symbol, base = "$", 2000

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
    }
    symbol = symbols.get(country, "$")
    monthly = revenue_per_client * expected_new_clients
    yearly = monthly * 12
    roi = ((yearly - website_cost) / website_cost) * 100
    payback = website_cost / monthly if monthly > 0 else 0

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
        contacted = [l for l in leads if l["status"] == "Contacted"]
        proposal = [l for l in leads if l["status"] == "Proposal Sent"]
        closed = [l for l in leads if l["status"] == "Closed"]
        lost = [l for l in leads if l["status"] == "Lost"]
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
                    datetime.now().strftime("%Y-%m-%d %H:%M")
                with open(leads_file, "w") as f:
                    json.dump(leads, f, indent=2)
                return f"Updated: {business_name}\n{old} to {new_status}"
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
                    datetime.now().strftime("%Y-%m-%d %H:%M")
                with open(leads_file, "w") as f:
                    json.dump(leads, f, indent=2)
                return f"Note added to {business_name}"
        return f"Not found: {business_name}"
    except Exception as e:
        return f"Error: {e}"

def generate_whatsapp_link(
    phone_number: str,
    message: str
) -> str:
    try:
        clean = "".join(filter(str.isdigit, phone_number))
        encoded = urllib.parse.quote(message)
        link = f"https://wa.me/{clean}?text={encoded}"
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

def build_website(
    business_name: str,
    business_type: str,
    location: str,
    client_email: str = "",
    client_phone: str = ""
) -> str:
    """Build and publish a website to Netlify"""
    try:
        from website_builder import build_website as _build
        return _build(
            business_name=business_name,
            business_type=business_type,
            location=location,
            client_email=client_email,
            client_phone=client_phone,
            whatsapp="+254118240486"
        )
    except Exception as e:
        return f"Website builder error: {e}"

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
            "description": "Calculate website price for a client based on location and business type",
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
            "description": "Calculate ROI to show client how website makes money",
            "parameters": {
                "type": "object",
                "properties": {
                    "country": {"type": "string"},
                    "revenue_per_client": {"type": "integer"},
                    "expected_new_clients": {"type": "integer"},
                    "website_cost": {"type": "integer"}
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
            "description": "Save a potential client to leads database",
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
            "description": "View all leads in sales pipeline",
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
            "description": "Update the status of a lead",
            "parameters": {
                "type": "object",
                "properties": {
                    "business_name": {"type": "string"},
                    "new_status": {"type": "string"}
                },
                "required": ["business_name", "new_status"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "add_note",
            "description": "Add a note to a lead in database",
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
    },
    {
        "type": "function",
        "function": {
            "name": "build_website",
            "description": "Build and publish a complete professional website for a client automatically. Use this when a client agrees to the deal or when asked to build a website.",
            "parameters": {
                "type": "object",
                "properties": {
                    "business_name": {
                        "type": "string",
                        "description": "Full name of the business"
                    },
                    "business_type": {
                        "type": "string",
                        "description": "Type of business like dental clinics law firms restaurants gyms"
                    },
                    "location": {
                        "type": "string",
                        "description": "City and state like Los Angeles or New York"
                    },
                    "client_email": {
                        "type": "string",
                        "description": "Client email address to send delivery"
                    },
                    "client_phone": {
                        "type": "string",
                        "description": "Client phone number"
                    }
                },
                "required": [
                    "business_name",
                    "business_type",
                    "location"
                ]
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
    "generate_whatsapp_link": generate_whatsapp_link,
    "build_website": build_website,
}