import os
import requests
from bs4 import BeautifulSoup
from google import genai

# 1. Setup API
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

# 2. Scrape the White House (example)
url = "https://www.whitehouse.gov/executive-orders/"
html = requests.get(url).text
soup = BeautifulSoup(html, 'html.parser')
latest_eo = soup.find('h2').text.strip()

# 3. Check "Memory"
if os.path.exists("history.txt"):
    with open("history.txt", "r") as f:
        history = f.read()
else:
    history = ""

if latest_eo not in history:
    print(f"New Order Found: {latest_eo}")
    
    # 4. Analyze with AI
    response = client.models.generate_content(
        model="gemini-2.0-flash-lite-001", 
        contents=f"Summarize this executive order title: {latest_eo}"
    )
    print(f"AI Summary: {response.text}")

    # 5. Update Memory
    with open("history.txt", "a") as f:
        f.write(latest_eo + "\n")
else:
    print("No new orders found.")
