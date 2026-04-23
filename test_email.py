import resend
import os

# Replace with your actual key
resend.api_key = "re_XstYXcTQ_AsuwkqudyGA9hhoJyksLHDAx"

response = resend.Emails.send({
    "from": "onboarding@resend.dev",
    "to": "elizabethnzasi530@gmail.com",
    "subject": "Jarvis Email Test",
    "html": "<h1>It works!</h1><p>Jarvis can now send emails.</p>"
})

print(f"Response: {response}")

if response.get("id"):
    print("SUCCESS! Email sent!")
else:
    print("FAILED. Check your API key.")