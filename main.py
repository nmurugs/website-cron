import os
from groq import Groq
import requests
from bs4 import BeautifulSoup

# 1. Setup Groq
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# 2. Scrape (Same logic as before)
url = "https://www.whitehouse.gov/executive-orders/"
html = requests.get(url).text
soup = BeautifulSoup(html, 'html.parser')
latest_eo = soup.find('h2').text.strip()

# 3. Memory Check
if os.path.exists("history.txt"):
    with open("history.txt", "r") as f:
        history = f.read()
else:
    history = ""

if latest_eo not in history:
    # 4. Use Groq's Free Model
    chat_completion = client.chat.completions.create(
        messages=[{"role": "user", "content": f"Summarize this: {latest_eo}"}],
        model="llama-3.3-70b-versatile",
    )
    print(f"Summary: {chat_completion.choices[0].message.content}")

    # 5. Update Memory
    with open("history.txt", "a") as f:
        f.write(latest_eo + "\n")
