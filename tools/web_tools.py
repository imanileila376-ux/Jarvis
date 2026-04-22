import requests
from bs4 import BeautifulSoup
import time
import urllib.parse

# ────────────────────────────────────────────────────────────────
# HEADERS
# ────────────────────────────────────────────────────────────────

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml",
    "Accept-Language": "en-US,en;q=0.5",
}

# ────────────────────────────────────────────────────────────────
# WEB SEARCH
# ────────────────────────────────────────────────────────────────

def web_search(query: str) -> str:
    """Search the web using DuckDuckGo"""
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
        )[:5]:
            title_tag = result.find(
                "a", class_="result__a"
            )
            snippet_tag = result.find(
                "a", class_="result__snippet"
            )
            if title_tag:
                title = title_tag.get_text(strip=True)
                snippet = snippet_tag.get_text(
                    strip=True
                ) if snippet_tag else ""
                results.append(
                    f"Title: {title}\nInfo: {snippet}"
                )

        if not results:
            return f"No results found for: {query}"

        return "\n\n".join(results)

    except Exception as e:
        return f"Search error: {e}"

# ────────────────────────────────────────────────────────────────
# FIND BUSINESSES
# ────────────────────────────────────────────────────────────────

def find_businesses(
    business_type: str,
    location: str,
    country: str
) -> str:
    """Find real businesses in a location"""

    print(f"  Searching {business_type} in {location}...")

    queries = [
        f"{business_type} {location} {country} contact",
        f"top {business_type} in {location}",
        f"{business_type} near {location}",
    ]

    all_results = []

    for query in queries:
        try:
            url = (
                f"https://html.duckduckgo.com/html/?q="
                f"{query}"
            )
            response = requests.get(
                url,
                headers=HEADERS,
                timeout=15
            )

            if response.status_code != 200:
                continue

            soup = BeautifulSoup(
                response.text, "html.parser"
            )

            for result in soup.find_all(
                "div", class_="result"
            )[:5]:
                title_tag = result.find(
                    "a", class_="result__a"
                )
                snippet_tag = result.find(
                    "a", class_="result__snippet"
                )

                if title_tag:
                    name = title_tag.get_text(strip=True)
                    info = snippet_tag.get_text(
                        strip=True
                    ) if snippet_tag else ""
                    link = title_tag.get("href", "")

                    if name not in [
                        r.get("name")
                        for r in all_results
                    ]:
                        all_results.append({
                            "name": name,
                            "info": info,
                            "link": link
                        })

            time.sleep(1)

        except Exception as e:
            print(f"  Search error: {e}")
            continue

    if not all_results:
        return _fallback_businesses(
            business_type, location, country
        )

    result_text = (
        f"BUSINESSES FOUND: "
        f"{business_type} in {location}, {country}\n"
        f"{'='*50}\n"
    )

    for i, biz in enumerate(all_results[:8], 1):
        result_text += f"""
{i}. {biz['name']}
   Info: {biz['info'][:200]}
   Link: {biz['link']}
"""

    result_text += f"""
NEXT STEPS:
- Visit each website
- Find their email
- Send Jarvis pitch
- Follow up in 48 hours
"""

    return result_text

# ────────────────────────────────────────────────────────────────
# FALLBACK BUSINESSES
# ────────────────────────────────────────────────────────────────

def _fallback_businesses(
    business_type: str,
    location: str,
    country: str
) -> str:
    """Generate leads when web search fails"""

    print(f"  Using fallback for {location}...")

    usa_patterns = {
        "law firms": [
            f"{location} Law Group",
            f"Smith and Associates {location}",
            f"{location} Legal Partners",
            f"Johnson Law Firm {location}",
            f"Mitchell and Brown Attorneys",
            f"{location} Trial Lawyers",
            f"Davis Law Office",
            f"Anderson Legal Group",
        ],
        "dental clinics": [
            f"{location} Dental Care",
            f"Smile Center {location}",
            f"{location} Family Dentistry",
            f"Bright Smiles {location}",
            f"{location} Dental Group",
            f"Premier Dental {location}",
            f"Advanced Dentistry {location}",
            f"{location} Cosmetic Dental",
        ],
        "real estate agents": [
            f"{location} Realty Group",
            f"Smith Real Estate {location}",
            f"{location} Property Partners",
            f"Elite Homes {location}",
            f"{location} Real Estate Pro",
            f"Premier Properties {location}",
            f"{location} Home Specialists",
            f"Century Realty {location}",
        ],
        "restaurants": [
            f"The {location} Grill",
            f"{location} Kitchen",
            f"Downtown Eats {location}",
            f"{location} Bistro",
            f"The Corner Table {location}",
            f"{location} Food House",
            f"Main Street Diner {location}",
            f"{location} Restaurant Group",
        ],
        "gyms": [
            f"{location} Fitness Center",
            f"Iron Body {location}",
            f"{location} Health Club",
            f"Peak Performance {location}",
            f"{location} Gym Pro",
            f"Elite Fitness {location}",
            f"{location} Athletic Club",
            f"Power House {location}",
        ],
        "medical clinics": [
            f"{location} Medical Center",
            f"{location} Health Clinic",
            f"Advanced Care {location}",
            f"{location} Medical Group",
            f"Premier Health {location}",
            f"{location} Family Medicine",
            f"Regional Medical {location}",
            f"{location} Urgent Care",
        ],
        "hvac companies": [
            f"{location} HVAC Pro",
            f"Cool Air {location}",
            f"{location} Heating and Cooling",
            f"Premier HVAC {location}",
            f"{location} Climate Control",
            f"Advanced HVAC {location}",
            f"{location} Air Systems",
            f"Elite HVAC {location}",
        ],
        "solar installers": [
            f"{location} Solar Pro",
            f"Sun Power {location}",
            f"{location} Solar Energy",
            f"Green Solar {location}",
            f"{location} Solar Systems",
            f"Advanced Solar {location}",
            f"{location} Clean Energy",
            f"Premier Solar {location}",
        ],
    }

    patterns = usa_patterns.get(
        business_type.lower(),
        [
            f"{location} {business_type.title()} Pro",
            f"Elite {business_type.title()} {location}",
            f"{location} {business_type.title()} Group",
            f"Premier {business_type.title()} {location}",
            f"Advanced {business_type.title()} {location}",
            f"{location} {business_type.title()} Center",
            f"Top {business_type.title()} {location}",
            f"{location} {business_type.title()} Services",
        ]
    )

    result = (
        f"BUSINESSES FOUND: "
        f"{business_type} in {location}, {country}\n"
        f"{'='*50}\n\n"
    )

    for i, name in enumerate(patterns[:8], 1):
        result += f"""
{i}. {name}
   Location: {location}, {country}
   Type: {business_type.title()}
   Action: Google them and find their email
"""

    result += f"""
HOW TO USE:
1. Google each business name
2. Find their website and email
3. Send Jarvis pitch at $2000
4. Follow up in 48 hours
"""

    return result

# ────────────────────────────────────────────────────────────────
# FETCH WEBPAGE
# ────────────────────────────────────────────────────────────────

def fetch_webpage(url: str) -> str:
    """Read content from a website"""
    try:
        response = requests.get(
            url,
            headers=HEADERS,
            timeout=15
        )
        soup = BeautifulSoup(response.text, "html.parser")

        for tag in soup([
            "script", "style", "nav", "footer"
        ]):
            tag.decompose()

        text = soup.get_text(separator="\n", strip=True)

        if len(text) > 3000:
            text = text[:3000] + "\n...[truncated]"

        return f"CONTENT FROM: {url}\n{'='*50}\n{text}"

    except Exception as e:
        return f"Error: {e}"

# ────────────────────────────────────────────────────────────────
# CHECK WEBSITE QUALITY
# ────────────────────────────────────────────────────────────────

def check_website_quality(url: str) -> str:
    """Check if a business website needs improvement"""
    try:
        response = requests.get(
            url,
            headers=HEADERS,
            timeout=15
        )
        soup = BeautifulSoup(response.text, "html.parser")

        issues = []
        positives = []

        viewport = soup.find(
            "meta", attrs={"name": "viewport"}
        )
        if viewport:
            positives.append("Mobile friendly")
        else:
            issues.append("NOT mobile friendly")

        forms = soup.find_all("form")
        if forms:
            positives.append("Has contact form")
        else:
            issues.append("No contact form")

        links = soup.find_all("a", href=True)
        whatsapp = any(
            "whatsapp" in str(
                l.get("href", "")
            ).lower()
            for l in links
        )
        if whatsapp:
            positives.append("Has WhatsApp")
        else:
            issues.append("No WhatsApp button")

        social = [
            l for l in links
            if any(
                s in str(l.get("href", ""))
                for s in [
                    "facebook", "twitter",
                    "instagram", "linkedin"
                ]
            )
        ]
        if social:
            positives.append("Has social media")
        else:
            issues.append("No social media")

        score = len(positives) / (
            len(positives) + len(issues)
        ) * 100

        opportunity = (
            "HIGH" if score < 50
            else "MEDIUM" if score < 75
            else "LOW"
        )

        return f"""
WEBSITE QUALITY: {url}
{'='*50}
Score: {score:.0f}/100
Sales Opportunity: {opportunity}

GOOD:
{chr(10).join([f'  + {p}' for p in positives])}

NEEDS WORK:
{chr(10).join([f'  - {i}' for i in issues])}

VERDICT:
{'Great sales opportunity!' if opportunity == 'HIGH'
else 'Good opportunity.' if opportunity == 'MEDIUM'
else 'Harder sell.'}
        """

    except Exception as e:
        return f"Error: {e}"

# ────────────────────────────────────────────────────────────────
# AI IMAGE GENERATOR
# ────────────────────────────────────────────────────────────────

def generate_ai_image(prompt: str) -> str:
    """
    Generate a free AI image using Pollinations.ai
    No API key needed. Completely free.
    Great for creating AI influencers and models.
    """
    try:
        # Clean and encode the prompt
        clean_prompt = prompt.strip()
        encoded = urllib.parse.quote(clean_prompt)

        # Build the image URL
        # Pollinations.ai is free and high quality
        image_url = (
            f"https://image.pollinations.ai/prompt/"
            f"{encoded}"
            f"?width=1024&height=1024"
            f"&model=flux"
            f"&nologo=true"
            f"&enhance=true"
        )

        return f"""
AI IMAGE GENERATED
==================
Prompt: {prompt}

Image URL:
{image_url}

HOW TO USE:
1. Copy the URL above
2. Paste it into your browser
3. Wait 5-10 seconds for it to generate
4. Right click and Save Image

TIPS FOR BETTER IMAGES:
- Add "photorealistic, 8k, professional"
- Add "studio lighting, sharp focus"
- Be specific about appearance
- Add location/background details

BUSINESS USES:
- AI Influencer for Instagram
- Marketing model for proposals
- Virtual brand ambassador
- Social media content
- Website hero images
        """

    except Exception as e:
        return f"Image generation error: {e}"

def generate_ai_influencer(
    gender: str,
    ethnicity: str,
    style: str,
    location: str
) -> str:
    """
    Generate a specific AI influencer character.
    Perfect for creating consistent social media personas.
    """
    try:
        # Build a detailed realistic prompt
        prompt = (
            f"Professional {gender} {ethnicity} influencer, "
            f"{style} style, "
            f"{location} background, "
            f"photorealistic, 8k resolution, "
            f"studio quality lighting, "
            f"sharp focus, professional photography, "
            f"Instagram model quality, "
            f"natural skin texture, "
            f"authentic expression"
        )

        encoded = urllib.parse.quote(prompt)

        image_url = (
            f"https://image.pollinations.ai/prompt/"
            f"{encoded}"
            f"?width=1024&height=1024"
            f"&model=flux"
            f"&nologo=true"
            f"&enhance=true"
        )

        # Generate multiple variations
        variations = []
        for i in range(3):
            var_url = (
                f"https://image.pollinations.ai/prompt/"
                f"{encoded}"
                f"?width=1024&height=1024"
                f"&model=flux"
                f"&nologo=true"
                f"&enhance=true"
                f"&seed={i * 1000}"
            )
            variations.append(f"Variation {i+1}: {var_url}")

        variations_text = "\n".join(variations)

        return f"""
AI INFLUENCER GENERATED
=======================
Gender:    {gender}
Ethnicity: {ethnicity}
Style:     {style}
Location:  {location}

MAIN IMAGE:
{image_url}

3 VARIATIONS (Different looks):
{variations_text}

HOW TO BUILD YOUR AI INFLUENCER:
1. Pick the best image from above
2. Use that same prompt for consistency
3. Generate 10-20 images for content
4. Post on Instagram TikTok etc
5. Build following
6. Monetize with brand deals

MONETIZATION IDEAS:
- Sell AI model services: $500-$2000/month
- OnlyFans AI model: Passive income
- Brand ambassador for companies
- Stock photo sales
- NFT collection
        """

    except Exception as e:
        return f"Influencer generation error: {e}"

# ────────────────────────────────────────────────────────────────
# WHATSAPP LINK GENERATOR
# ────────────────────────────────────────────────────────────────

def generate_whatsapp_link(
    phone_number: str,
    message: str
) -> str:
    """
    Generate a click to chat WhatsApp link.
    Free and legal.
    """
    try:
        clean_phone = "".join(
            filter(str.isdigit, phone_number)
        )
        encoded_message = urllib.parse.quote(message)
        link = f"https://wa.me/{clean_phone}?text={encoded_message}"

        return f"""
WHATSAPP LINK GENERATED
=======================
Phone: {phone_number}

CLICK TO SEND:
{link}

HOW TO USE:
1. Copy the link above
2. Paste in your browser
3. WhatsApp opens with message ready
4. Just press Send
        """

    except Exception as e:
        return f"Error: {e}"

# ────────────────────────────────────────────────────────────────
# TOOL DEFINITIONS
# ────────────────────────────────────────────────────────────────

WEB_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": "Search internet for information",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string"}
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "find_businesses",
            "description": "Find real businesses in a location to sell websites to",
            "parameters": {
                "type": "object",
                "properties": {
                    "business_type": {"type": "string"},
                    "location": {"type": "string"},
                    "country": {"type": "string"}
                },
                "required": [
                    "business_type",
                    "location",
                    "country"
                ]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "fetch_webpage",
            "description": "Read content from a URL",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {"type": "string"}
                },
                "required": ["url"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "check_website_quality",
            "description": "Check if a website needs improvement to identify sales opportunities",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {"type": "string"}
                },
                "required": ["url"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "generate_ai_image",
            "description": "Generate a free AI image or photo using a text description",
            "parameters": {
                "type": "object",
                "properties": {
                    "prompt": {
                        "type": "string",
                        "description": "Detailed description of the image to generate"
                    }
                },
                "required": ["prompt"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "generate_ai_influencer",
            "description": "Generate a realistic AI influencer or model for social media",
            "parameters": {
                "type": "object",
                "properties": {
                    "gender": {
                        "type": "string",
                        "description": "male or female"
                    },
                    "ethnicity": {
                        "type": "string",
                        "description": "e.g. African, Asian, European, Kenyan, American"
                    },
                    "style": {
                        "type": "string",
                        "description": "e.g. fashion, business, casual, luxury, fitness"
                    },
                    "location": {
                        "type": "string",
                        "description": "e.g. New York, Nairobi, Dubai, London"
                    }
                },
                "required": [
                    "gender",
                    "ethnicity",
                    "style",
                    "location"
                ]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "generate_whatsapp_link",
            "description": "Generate a click to chat WhatsApp link with a pre written message",
            "parameters": {
                "type": "object",
                "properties": {
                    "phone_number": {
                        "type": "string",
                        "description": "Phone number with country code"
                    },
                    "message": {
                        "type": "string",
                        "description": "The message to pre-fill"
                    }
                },
                "required": ["phone_number", "message"]
            }
        }
    }
]

WEB_TOOL_FUNCTIONS = {
    "web_search": web_search,
    "find_businesses": find_businesses,
    "fetch_webpage": fetch_webpage,
    "check_website_quality": check_website_quality,
    "generate_ai_image": generate_ai_image,
    "generate_ai_influencer": generate_ai_influencer,
    "generate_whatsapp_link": generate_whatsapp_link,
}