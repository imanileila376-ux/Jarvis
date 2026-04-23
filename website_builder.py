import os
import json
import zipfile
import io
import requests
from datetime import datetime

# ────────────────────────────────────────────────────────────────
# SETUP
# Replace with your actual Netlify token
# ────────────────────────────────────────────────────────────────

NETLIFY_TOKEN = os.environ.get(
    "NETLIFY_TOKEN",
    "nfp_G6RWTF39TyYmAdeQkhoX1LRpTjVJ4idBaf53"
)
NETLIFY_API = "https://api.netlify.com/api/v1"
WHATSAPP = "+254118240486"
EMAIL = "elizabethnzasi530@gmail.com"
COMPANY = "Digital Growth Agency"

# ────────────────────────────────────────────────────────────────
# COLOR SCHEMES
# ────────────────────────────────────────────────────────────────

COLORS = {
    "dental clinics": {
        "primary": "#1B4FD8",
        "accent": "#00B4D8",
        "bg": "#F8FAFF",
        "text": "#333333"
    },
    "law firms": {
        "primary": "#1A1A2E",
        "accent": "#C9A84C",
        "bg": "#F5F5F5",
        "text": "#333333"
    },
    "real estate agents": {
        "primary": "#2D6A4F",
        "accent": "#FFD700",
        "bg": "#F9F9F9",
        "text": "#333333"
    },
    "gyms": {
        "primary": "#CC0000",
        "accent": "#FF6B00",
        "bg": "#111111",
        "text": "#FFFFFF"
    },
    "restaurants": {
        "primary": "#8B0000",
        "accent": "#D4AF37",
        "bg": "#FFF8F0",
        "text": "#333333"
    },
    "medical clinics": {
        "primary": "#0077B6",
        "accent": "#00B4D8",
        "bg": "#F0F8FF",
        "text": "#333333"
    },
    "hvac companies": {
        "primary": "#FF6B00",
        "accent": "#1A1A2E",
        "bg": "#F5F5F5",
        "text": "#333333"
    },
    "solar installers": {
        "primary": "#F9A825",
        "accent": "#2E7D32",
        "bg": "#F1F8E9",
        "text": "#333333"
    },
}

# ────────────────────────────────────────────────────────────────
# SERVICES
# ────────────────────────────────────────────────────────────────

SERVICES = {
    "dental clinics": [
        ("🦷", "Teeth Cleaning", "Professional cleaning for a brighter smile"),
        ("✨", "Teeth Whitening", "Get a dazzling white smile in one visit"),
        ("🔧", "Dental Implants", "Permanent solution for missing teeth"),
        ("😁", "Orthodontics", "Braces and aligners for perfect alignment"),
        ("🛡️", "Preventive Care", "Regular checkups to keep your smile healthy"),
        ("🚨", "Emergency Dental", "Available for urgent dental needs"),
    ],
    "law firms": [
        ("⚖️", "Personal Injury", "Fighting for maximum compensation"),
        ("🏛️", "Criminal Defense", "Protecting your rights and freedom"),
        ("👨‍👩‍👧", "Family Law", "Divorce custody and family matters"),
        ("🏢", "Business Law", "Legal protection for your business"),
        ("🏠", "Real Estate Law", "Property transactions and disputes"),
        ("💼", "Employment Law", "Workplace rights and discrimination"),
    ],
    "real estate agents": [
        ("🏠", "Buy a Home", "Find your perfect property"),
        ("💰", "Sell Your Property", "Get maximum value for your home"),
        ("📊", "Market Analysis", "Free property valuation and report"),
        ("🏢", "Commercial Real Estate", "Office retail and industrial"),
        ("🔑", "Property Management", "Hassle free rental management"),
        ("📈", "Investment Properties", "Build wealth through real estate"),
    ],
    "gyms": [
        ("💪", "Strength Training", "Build muscle with top equipment"),
        ("🏃", "Cardio Classes", "High energy classes to burn fat"),
        ("🧘", "Yoga and Pilates", "Flexibility balance and peace"),
        ("🥊", "Boxing and MMA", "Learn to fight and get in shape"),
        ("👤", "Personal Training", "One on one coaching for results"),
        ("🍎", "Nutrition Coaching", "Fuel your body for peak performance"),
    ],
    "restaurants": [
        ("🍽️", "Dine In", "Enjoy our warm welcoming atmosphere"),
        ("📦", "Takeout", "Order online for quick pickup"),
        ("🚗", "Delivery", "Fresh meals delivered to your door"),
        ("🎉", "Private Events", "Book us for special occasions"),
        ("🥂", "Catering", "Professional catering for any event"),
        ("👨‍🍳", "Chef Specials", "Seasonal dishes crafted with love"),
    ],
    "medical clinics": [
        ("🩺", "General Medicine", "Comprehensive healthcare for all ages"),
        ("🚨", "Urgent Care", "Walk in care without the ER wait"),
        ("💉", "Preventive Care", "Vaccinations and health screenings"),
        ("🧬", "Lab Testing", "Fast accurate diagnostic testing"),
        ("❤️", "Chronic Disease", "Management for diabetes hypertension"),
        ("🌿", "Telehealth", "See a doctor from home"),
    ],
    "hvac companies": [
        ("❄️", "AC Installation", "Stay cool with expert installation"),
        ("🔥", "Heating Systems", "Keep warm all winter long"),
        ("🔧", "Repairs", "Fast reliable repair service"),
        ("📋", "Maintenance", "Regular tune ups for peak performance"),
        ("💨", "Air Quality", "Breathe cleaner healthier air"),
        ("🏠", "Residential", "Complete home comfort solutions"),
    ],
    "solar installers": [
        ("☀️", "Solar Panels", "Harness the power of the sun"),
        ("🔋", "Battery Storage", "Store energy for any time use"),
        ("💡", "LED Lighting", "Energy efficient lighting solutions"),
        ("📊", "Energy Audit", "Find where you are wasting energy"),
        ("🏠", "Residential Solar", "Power your home with solar"),
        ("🏢", "Commercial Solar", "Reduce business energy costs"),
    ],
}

HEADLINES = {
    "dental clinics": "Your Perfect Smile Starts Here",
    "law firms": "Fighting For Justice. Fighting For You.",
    "real estate agents": "Find Your Dream Home Today",
    "gyms": "Transform Your Body. Transform Your Life.",
    "restaurants": "Experience Unforgettable Flavors",
    "medical clinics": "Your Health is Our Priority",
    "hvac companies": "Your Comfort is Our Business",
    "solar installers": "Power Your Future with Solar",
}

CTAS = {
    "dental clinics": "Book Appointment",
    "law firms": "Free Consultation",
    "real estate agents": "View Properties",
    "gyms": "Start Free Trial",
    "restaurants": "Reserve a Table",
    "medical clinics": "Book Appointment",
    "hvac companies": "Get Free Quote",
    "solar installers": "Get Free Quote",
}

# ────────────────────────────────────────────────────────────────
# GENERATE HTML
# ────────────────────────────────────────────────────────────────

def generate_html(
    business_name: str,
    business_type: str,
    location: str,
    phone: str = "",
    email: str = "",
    whatsapp: str = "+254118240486"
) -> str:

    btype = business_type.lower()
    scheme = COLORS.get(btype, COLORS["medical clinics"])
    services = SERVICES.get(btype, SERVICES["medical clinics"])
    headline = HEADLINES.get(btype, f"Welcome to {business_name}")
    cta = CTAS.get(btype, "Contact Us")

    primary = scheme["primary"]
    accent = scheme["accent"]
    bg = scheme["bg"]
    text = scheme["text"]

    wa_clean = "".join(filter(str.isdigit, whatsapp))

    services_html = ""
    for icon, name, desc in services:
        services_html += f"""
        <div class="card">
            <div class="card-icon">{icon}</div>
            <h3>{name}</h3>
            <p>{desc}</p>
        </div>"""

    select_options = "".join([
        f'<option>{s[1]}</option>'
        for s in services
    ])

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{business_name} - {location}</title>
<meta name="description" content="{business_name} is a leading {business_type} in {location}. Contact us today.">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Playfair+Display:wght@700&display=swap" rel="stylesheet">
<style>
*{{margin:0;padding:0;box-sizing:border-box;}}
body{{font-family:'Inter',sans-serif;color:{text};background:{bg};overflow-x:hidden;}}
nav{{position:fixed;top:0;width:100%;background:rgba(255,255,255,0.95);backdrop-filter:blur(10px);padding:15px 5%;display:flex;justify-content:space-between;align-items:center;z-index:1000;box-shadow:0 2px 20px rgba(0,0,0,0.1);}}
.logo{{font-family:'Playfair Display',serif;font-size:22px;font-weight:700;color:{primary};}}
.nav-links{{display:flex;gap:25px;list-style:none;}}
.nav-links a{{text-decoration:none;color:{text};font-weight:500;transition:color 0.3s;}}
.nav-links a:hover{{color:{primary};}}
.nav-cta{{background:{primary};color:white!important;padding:10px 20px;border-radius:25px;font-weight:600!important;}}
.hero{{min-height:100vh;background:linear-gradient(135deg,{primary} 0%,{accent} 100%);display:flex;align-items:center;padding:100px 5% 60px;position:relative;overflow:hidden;}}
.hero::before{{content:'';position:absolute;top:-50%;right:-20%;width:600px;height:600px;background:rgba(255,255,255,0.05);border-radius:50%;}}
.hero-content{{max-width:650px;position:relative;z-index:1;}}
.hero-badge{{display:inline-block;background:rgba(255,255,255,0.2);color:white;padding:8px 16px;border-radius:20px;font-size:14px;font-weight:500;margin-bottom:20px;border:1px solid rgba(255,255,255,0.3);}}
.hero h1{{font-family:'Playfair Display',serif;font-size:clamp(32px,5vw,60px);color:white;line-height:1.2;margin-bottom:20px;}}
.hero p{{font-size:17px;color:rgba(255,255,255,0.85);line-height:1.7;margin-bottom:35px;}}
.hero-buttons{{display:flex;gap:15px;flex-wrap:wrap;}}
.btn-primary{{background:white;color:{primary};padding:14px 28px;border-radius:30px;font-size:15px;font-weight:700;text-decoration:none;transition:transform 0.3s,box-shadow 0.3s;box-shadow:0 4px 15px rgba(0,0,0,0.2);}}
.btn-primary:hover{{transform:translateY(-2px);box-shadow:0 8px 25px rgba(0,0,0,0.3);}}
.btn-secondary{{background:transparent;color:white;padding:14px 28px;border-radius:30px;font-size:15px;font-weight:600;text-decoration:none;border:2px solid rgba(255,255,255,0.6);transition:all 0.3s;}}
.btn-secondary:hover{{background:rgba(255,255,255,0.1);}}
.stats{{background:white;padding:35px 5%;display:flex;justify-content:center;gap:60px;flex-wrap:wrap;box-shadow:0 4px 30px rgba(0,0,0,0.08);}}
.stat-item{{text-align:center;}}
.stat-number{{font-size:34px;font-weight:800;color:{primary};}}
.stat-label{{font-size:13px;color:#666;margin-top:4px;}}
section{{padding:80px 5%;}}
.section-header{{text-align:center;margin-bottom:50px;}}
.section-badge{{display:inline-block;background:{accent}25;color:{primary};padding:6px 14px;border-radius:20px;font-size:12px;font-weight:600;margin-bottom:12px;text-transform:uppercase;letter-spacing:1px;}}
.section-header h2{{font-family:'Playfair Display',serif;font-size:clamp(26px,4vw,40px);color:#1a1a1a;margin-bottom:12px;}}
.section-header p{{font-size:16px;color:#666;max-width:600px;margin:0 auto;line-height:1.7;}}
.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:25px;max-width:1200px;margin:0 auto;}}
.card{{background:white;padding:28px;border-radius:16px;box-shadow:0 4px 20px rgba(0,0,0,0.06);transition:transform 0.3s,box-shadow 0.3s;border:1px solid #f0f0f0;}}
.card:hover{{transform:translateY(-5px);box-shadow:0 12px 40px rgba(0,0,0,0.12);}}
.card-icon{{font-size:36px;margin-bottom:14px;}}
.card h3{{font-size:18px;font-weight:700;color:#1a1a1a;margin-bottom:8px;}}
.card p{{color:#666;line-height:1.6;font-size:14px;}}
.why-us{{background:linear-gradient(135deg,{primary}08,{accent}12);}}
.benefits{{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:20px;max-width:1000px;margin:0 auto;}}
.benefit{{text-align:center;padding:22px;background:white;border-radius:12px;box-shadow:0 2px 15px rgba(0,0,0,0.05);}}
.benefit-icon{{font-size:32px;margin-bottom:10px;}}
.benefit h3{{font-size:16px;font-weight:700;color:#1a1a1a;margin-bottom:6px;}}
.benefit p{{font-size:13px;color:#666;line-height:1.5;}}
.testimonials{{background:{primary};}}
.testimonials .section-header h2{{color:white;}}
.testimonials .section-header p{{color:rgba(255,255,255,0.7);}}
.tgrid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:20px;max-width:1000px;margin:0 auto;}}
.tcard{{background:rgba(255,255,255,0.1);padding:22px;border-radius:14px;border:1px solid rgba(255,255,255,0.2);}}
.stars{{color:#FFD700;font-size:18px;margin-bottom:10px;}}
.ttext{{color:rgba(255,255,255,0.9);font-style:italic;line-height:1.7;margin-bottom:12px;font-size:14px;}}
.tauthor{{color:rgba(255,255,255,0.7);font-size:13px;font-weight:600;}}
.contact-wrapper{{display:grid;grid-template-columns:1fr 1fr;gap:50px;max-width:1000px;margin:0 auto;align-items:start;}}
.contact-info h3{{font-size:26px;font-weight:700;color:#1a1a1a;margin-bottom:18px;}}
.contact-item{{display:flex;align-items:center;gap:12px;margin-bottom:14px;}}
.contact-icon{{font-size:20px;width:42px;height:42px;background:{primary}15;border-radius:50%;display:flex;align-items:center;justify-content:center;}}
.contact-text{{color:#333;font-size:14px;}}
.contact-form{{background:white;padding:32px;border-radius:20px;box-shadow:0 8px 40px rgba(0,0,0,0.1);}}
.form-group{{margin-bottom:16px;}}
.form-group label{{display:block;font-weight:600;margin-bottom:5px;color:#333;font-size:13px;}}
.form-group input,.form-group textarea,.form-group select{{width:100%;padding:11px 15px;border:2px solid #e0e0e0;border-radius:10px;font-size:14px;font-family:'Inter',sans-serif;transition:border-color 0.3s;outline:none;background:#fafafa;}}
.form-group input:focus,.form-group textarea:focus,.form-group select:focus{{border-color:{primary};background:white;}}
.form-group textarea{{height:100px;resize:vertical;}}
.btn-submit{{width:100%;background:{primary};color:white;padding:13px;border:none;border-radius:10px;font-size:15px;font-weight:700;cursor:pointer;transition:all 0.3s;}}
.btn-submit:hover{{background:{accent};transform:translateY(-1px);}}
footer{{background:#1a1a1a;color:white;padding:40px 5%;text-align:center;}}
.footer-logo{{font-family:'Playfair Display',serif;font-size:24px;font-weight:700;color:{accent};margin-bottom:8px;}}
.footer-links{{display:flex;justify-content:center;gap:20px;flex-wrap:wrap;margin:15px 0;}}
.footer-links a{{color:#aaa;text-decoration:none;transition:color 0.3s;font-size:13px;}}
.footer-links a:hover{{color:{accent};}}
.footer-bottom{{color:#555;font-size:12px;margin-top:15px;padding-top:15px;border-top:1px solid #333;}}
.wa-btn{{position:fixed;bottom:25px;right:25px;background:#25D366;color:white;width:58px;height:58px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:26px;text-decoration:none;box-shadow:0 4px 20px rgba(37,211,102,0.4);z-index:999;animation:pulse 2s infinite;}}
@keyframes pulse{{0%{{box-shadow:0 0 0 0 rgba(37,211,102,0.4);}}70%{{box-shadow:0 0 0 15px rgba(37,211,102,0);}}100%{{box-shadow:0 0 0 0 rgba(37,211,102,0);}}}}
.wa-btn:hover{{transform:scale(1.1);}}
@media(max-width:768px){{.nav-links{{display:none;}}.stats{{gap:25px;}}.contact-wrapper{{grid-template-columns:1fr;}}.hero-buttons{{flex-direction:column;}}}}
</style>
</head>
<body>

<nav>
<div class="logo">{business_name}</div>
<ul class="nav-links">
<li><a href="#services">Services</a></li>
<li><a href="#about">About</a></li>
<li><a href="#reviews">Reviews</a></li>
<li><a href="#contact" class="nav-cta">{cta}</a></li>
</ul>
</nav>

<section class="hero">
<div class="hero-content">
<div class="hero-badge">
⭐ Top Rated {business_type.title()} in {location}
</div>
<h1>{headline}</h1>
<p>
{business_name} delivers exceptional service
to clients across {location}.
Trusted by hundreds of satisfied customers.
</p>
<div class="hero-buttons">
<a href="#contact" class="btn-primary">{cta} →</a>
<a href="tel:{phone}" class="btn-secondary">
📞 Call Us Now
</a>
</div>
</div>
</section>

<div class="stats">
<div class="stat-item">
<div class="stat-number">500+</div>
<div class="stat-label">Happy Clients</div>
</div>
<div class="stat-item">
<div class="stat-number">15+</div>
<div class="stat-label">Years Experience</div>
</div>
<div class="stat-item">
<div class="stat-number">4.9⭐</div>
<div class="stat-label">Average Rating</div>
</div>
<div class="stat-item">
<div class="stat-number">100%</div>
<div class="stat-label">Satisfaction</div>
</div>
</div>

<section id="services">
<div class="section-header">
<div class="section-badge">What We Offer</div>
<h2>Our Services</h2>
<p>
Comprehensive solutions tailored
to your specific needs
</p>
</div>
<div class="grid">{services_html}</div>
</section>

<section id="about" class="why-us">
<div class="section-header">
<div class="section-badge">Why Us</div>
<h2>Why Choose {business_name}</h2>
<p>
We are committed to providing
the highest quality service
</p>
</div>
<div class="benefits">
<div class="benefit">
<div class="benefit-icon">🏆</div>
<h3>Award Winning</h3>
<p>Recognized as the best in {location}</p>
</div>
<div class="benefit">
<div class="benefit-icon">⚡</div>
<h3>Fast Service</h3>
<p>Quick turnaround without compromising quality</p>
</div>
<div class="benefit">
<div class="benefit-icon">🛡️</div>
<h3>Guaranteed</h3>
<p>100% satisfaction guarantee on all services</p>
</div>
<div class="benefit">
<div class="benefit-icon">💎</div>
<h3>Premium Quality</h3>
<p>Only the best for our valued clients</p>
</div>
</div>
</section>

<section id="reviews" class="testimonials">
<div class="section-header">
<div class="section-badge"
     style="background:rgba(255,255,255,0.2);
            color:white;">
Client Reviews
</div>
<h2>What Our Clients Say</h2>
<p>Real reviews from real satisfied clients</p>
</div>
<div class="tgrid">
<div class="tcard">
<div class="stars">⭐⭐⭐⭐⭐</div>
<p class="ttext">
"Absolutely exceptional service!
The team at {business_name} exceeded
all my expectations. Highly recommend
to anyone in {location}!"
</p>
<div class="tauthor">— Sarah M., {location}</div>
</div>
<div class="tcard">
<div class="stars">⭐⭐⭐⭐⭐</div>
<p class="ttext">
"Professional efficient and truly
outstanding. I have been a client
for 3 years and will never go
anywhere else. The best!"
</p>
<div class="tauthor">— James K., {location}</div>
</div>
<div class="tcard">
<div class="stars">⭐⭐⭐⭐⭐</div>
<p class="ttext">
"I cannot recommend {business_name}
enough. From the moment I walked in
I felt valued and well taken care of.
Simply the best!"
</p>
<div class="tauthor">— Maria L., {location}</div>
</div>
</div>
</section>

<section id="contact">
<div class="section-header">
<div class="section-badge">Get In Touch</div>
<h2>Contact {business_name}</h2>
<p>We are here to help. Reach out today.</p>
</div>
<div class="contact-wrapper">
<div class="contact-info">
<h3>Let's Talk</h3>
<div class="contact-item">
<div class="contact-icon">📍</div>
<div class="contact-text">
{location}, United States
</div>
</div>
<div class="contact-item">
<div class="contact-icon">📞</div>
<div class="contact-text">
{phone if phone else "Contact us for phone"}
</div>
</div>
<div class="contact-item">
<div class="contact-icon">📧</div>
<div class="contact-text">
{email if email else "Contact us for email"}
</div>
</div>
<div class="contact-item">
<div class="contact-icon">🕐</div>
<div class="contact-text">
Mon-Fri: 9AM-6PM<br>
Sat: 9AM-4PM<br>
Sun: Closed
</div>
</div>
<br>
<a href="https://wa.me/{wa_clean}"
   style="display:inline-block;
          background:#25D366;
          color:white;
          padding:12px 22px;
          border-radius:25px;
          text-decoration:none;
          font-weight:600;
          font-size:14px;">
💬 WhatsApp Us Now
</a>
</div>
<div class="contact-form">
<form onsubmit="handleSubmit(event)">
<div class="form-group">
<label>Your Name *</label>
<input type="text"
       placeholder="John Smith"
       required>
</div>
<div class="form-group">
<label>Email Address *</label>
<input type="email"
       placeholder="john@example.com"
       required>
</div>
<div class="form-group">
<label>Phone Number</label>
<input type="tel"
       placeholder="+1 (555) 000-0000">
</div>
<div class="form-group">
<label>Service Needed</label>
<select>
<option>Select a service</option>
{select_options}
</select>
</div>
<div class="form-group">
<label>Message</label>
<textarea
  placeholder="Tell us how we can help...">
</textarea>
</div>
<button type="submit" class="btn-submit">
{cta} →
</button>
</form>
</div>
</div>
</section>

<footer>
<div class="footer-logo">{business_name}</div>
<div style="color:#aaa;margin-bottom:15px;">
Serving {location} with Excellence
</div>
<div class="footer-links">
<a href="#services">Services</a>
<a href="#about">About</a>
<a href="#reviews">Reviews</a>
<a href="#contact">Contact</a>
<a href="https://wa.me/{wa_clean}">WhatsApp</a>
</div>
<div class="footer-bottom">
© {datetime.now().year} {business_name}.
All rights reserved.
Built by Digital Growth Agency.
</div>
</footer>

<a href="https://wa.me/{wa_clean}"
   class="wa-btn"
   target="_blank">💬</a>

<script>
document.querySelectorAll('a[href^="#"]').forEach(a=>{{
a.addEventListener('click',function(e){{
e.preventDefault();
const t=document.querySelector(
    this.getAttribute('href')
);
if(t)t.scrollIntoView({{
    behavior:'smooth',
    block:'start'
}});
}});
}});

function handleSubmit(e){{
e.preventDefault();
const btn=e.target.querySelector('.btn-submit');
btn.textContent='✅ Message Sent!';
btn.style.background='#28a745';
setTimeout(()=>{{
    btn.textContent='{cta} →';
    btn.style.background='{primary}';
    e.target.reset();
}},3000);
}}

window.addEventListener('scroll',()=>{{
const nav=document.querySelector('nav');
nav.style.boxShadow=window.scrollY>50
    ?'0 4px 30px rgba(0,0,0,0.15)'
    :'0 2px 20px rgba(0,0,0,0.1)';
}});
</script>
</body>
</html>"""

# ────────────────────────────────────────────────────────────────
# PUBLISH TO NETLIFY
# ────────────────────────────────────────────────────────────────

def publish_to_netlify(
    html: str,
    business_name: str
) -> str:
    """
    Publish website to Netlify automatically.
    Returns the live URL.
    """
    if not NETLIFY_TOKEN:
        print("No Netlify token. Saving locally.")
        return ""

    try:
        headers = {
            "Authorization": f"Bearer {NETLIFY_TOKEN}",
            "Content-Type": "application/json"
        }

        # Generate site name
        site_name = (
            business_name.lower()
            .replace(" ", "-")
            .replace("'", "")
            .replace("&", "and")
            + f"-{datetime.now().strftime('%H%M%S')}"
        )

        # Create new site
        print(f"Creating Netlify site: {site_name}...")
        create_response = requests.post(
            f"{NETLIFY_API}/sites",
            headers=headers,
            json={"name": site_name},
            timeout=30
        )

        if create_response.status_code not in [200, 201]:
            print(f"Site creation failed: {create_response.text}")
            return ""

        site_id = create_response.json().get("id")
        print(f"Site created: {site_id}")

        # Create zip with HTML
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(
            zip_buffer, "w",
            zipfile.ZIP_DEFLATED
        ) as zf:
            zf.writestr("index.html", html)
        zip_buffer.seek(0)

        # Deploy zip
        print("Deploying website...")
        deploy_headers = {
            "Authorization": f"Bearer {NETLIFY_TOKEN}",
            "Content-Type": "application/zip"
        }

        deploy_response = requests.post(
            f"{NETLIFY_API}/sites/{site_id}/deploys",
            headers=deploy_headers,
            data=zip_buffer.read(),
            timeout=60
        )

        if deploy_response.status_code not in [200, 201]:
            print(f"Deploy failed: {deploy_response.text}")
            return ""

        deploy_data = deploy_response.json()
        live_url = deploy_data.get(
            "ssl_url",
            deploy_data.get(
                "url",
                f"https://{site_id}.netlify.app"
            )
        )

        print(f"Website published: {live_url}")
        return live_url

    except Exception as e:
        print(f"Netlify error: {e}")
        return ""

# ────────────────────────────────────────────────────────────────
# SAVE LOCALLY
# ────────────────────────────────────────────────────────────────

def save_locally(
    html: str,
    business_name: str
) -> str:
    """Save website as local HTML file"""
    filename = (
        f"website_"
        f"{business_name.replace(' ', '_')}_"
        f"{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        f".html"
    )
    with open(filename, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Saved locally: {filename}")
    return filename

# ────────────────────────────────────────────────────────────────
# SEND DELIVERY EMAIL
# ────────────────────────────────────────────────────────────────

def send_delivery_email(
    to_email: str,
    business_name: str,
    website_url: str
) -> bool:
    """Send website delivery email to client"""
    try:
        import smtplib
        from email.mime.multipart import MIMEMultipart
        from email.mime.text import MIMEText

        gmail_user = os.environ.get(
            "GMAIL_USER", EMAIL
        )
        gmail_pass = os.environ.get("GMAIL_PASS", "")

        if not gmail_pass:
            print("No Gmail password set.")
            return False

        html = f"""
<html>
<body style="font-family:Arial,sans-serif;
             max-width:600px;
             margin:0 auto;
             padding:20px;">

<div style="background:#1a1a2e;
            padding:25px;
            border-radius:10px;
            margin-bottom:20px;
            text-align:center;">
    <h1 style="color:#ffffff;margin:0;">
        Your Website is LIVE!
    </h1>
    <p style="color:#cccccc;
              margin:10px 0 0 0;">
        {COMPANY}
    </p>
</div>

<div style="padding:20px;
            background:#f9f9f9;
            border-radius:8px;
            margin-bottom:20px;">
    <p style="font-size:18px;color:#333;">
        Hi <strong>{business_name}</strong> team,
    </p>
    <p style="color:#333;line-height:1.8;">
        Great news! Your professional website
        is now live and ready for the world.
    </p>

    <div style="text-align:center;margin:25px 0;">
        <a href="{website_url}"
           style="background:#1a1a2e;
                  color:white;
                  padding:15px 30px;
                  border-radius:8px;
                  text-decoration:none;
                  font-size:18px;
                  font-weight:bold;">
            View Your Website
        </a>
    </div>

    <p style="color:#333;line-height:1.8;">
        Your website URL:<br>
        <a href="{website_url}"
           style="color:#1a1a2e;
                  font-weight:bold;">
            {website_url}
        </a>
    </p>

    <p style="color:#333;line-height:1.8;">
        Your website includes:<br>
        ✅ Professional design<br>
        ✅ Mobile friendly<br>
        ✅ Contact form<br>
        ✅ WhatsApp button<br>
        ✅ SEO optimized<br>
        ✅ Fast loading
    </p>

    <p style="color:#333;line-height:1.8;">
        Next steps:<br>
        1. Share the link on social media<br>
        2. Add it to your Google Business profile<br>
        3. Put it on your business cards<br>
        4. Start getting more customers online!
    </p>
</div>

<div style="padding:15px;
            border-top:2px solid #1a1a2e;
            color:#333;">
    <p style="margin:0;">
        <strong>Dan</strong><br>
        Managing Partner<br>
        {COMPANY}<br>
        WhatsApp: {WHATSAPP}<br>
        Email: {gmail_user}
    </p>
</div>

</body>
</html>
        """

        msg = MIMEMultipart("alternative")
        msg["Subject"] = (
            f"Your Website is LIVE! - {business_name}"
        )
        msg["From"] = (
            f"Dan - {COMPANY} <{gmail_user}>"
        )
        msg["To"] = to_email
        msg.attach(MIMEText(html, "html"))

        with smtplib.SMTP_SSL(
            "smtp.gmail.com", 465
        ) as server:
            server.login(gmail_user, gmail_pass)
            server.sendmail(
                gmail_user,
                to_email,
                msg.as_string()
            )

        print(f"Delivery email sent to {to_email}")
        return True

    except Exception as e:
        print(f"Delivery email error: {e}")
        return False

# ────────────────────────────────────────────────────────────────
# MAIN BUILD FUNCTION
# ────────────────────────────────────────────────────────────────

def build_website(
    business_name: str,
    business_type: str,
    location: str,
    client_email: str = "",
    client_phone: str = "",
    whatsapp: str = "+254118240486"
) -> str:
    """
    Build and publish a complete website.

    Steps:
    1. Generate professional HTML
    2. Publish to Netlify (if token set)
    3. Save locally as backup
    4. Send delivery email to client
    5. Return live URL
    """

    print(f"""
=====================================
BUILDING WEBSITE
Business: {business_name}
Type:     {business_type}
Location: {location}
=====================================
    """)

    # Step 1: Generate HTML
    print("Generating HTML...")
    html = generate_html(
        business_name=business_name,
        business_type=business_type,
        location=location,
        phone=client_phone,
        email=client_email,
        whatsapp=whatsapp
    )
    print("HTML generated successfully.")

    # Step 2: Try Netlify
    live_url = ""
    if NETLIFY_TOKEN and NETLIFY_TOKEN != "YOUR_NETLIFY_TOKEN_HERE":
        live_url = publish_to_netlify(html, business_name)

    # Step 3: Save locally as backup
    local_file = save_locally(html, business_name)

    # Step 4: Send delivery email
    if live_url and client_email:
        send_delivery_email(
            client_email,
            business_name,
            live_url
        )

    # Step 5: Return result
    if live_url:
        return f"""
WEBSITE BUILT AND PUBLISHED!
=============================
Business:  {business_name}
Type:      {business_type}
Location:  {location}

LIVE URL:
{live_url}

The website is now LIVE on the internet.
Share this link with your client.

Local backup saved as:
{local_file}

Delivery email sent to:
{client_email if client_email else "No email provided"}
        """
    else:
        return f"""
WEBSITE BUILT SUCCESSFULLY!
============================
Business:  {business_name}
Type:      {business_type}
Location:  {location}

Saved locally as:
{local_file}

TO PUBLISH FOR FREE:
1. Go to https://netlify.com
2. Sign up free
3. Drag and drop {local_file}
4. Get instant live URL
5. Send URL to client

OR add your Netlify token to get
automatic publishing next time.
        """