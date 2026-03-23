import os
import requests
from bs4 import BeautifulSoup
from groq import Groq
from urllib.parse import urljoin  # The "Glue" for links

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# 1. Base URL
base_url = "https://www.moneycontrol.com/"
response = requests.get(base_url)
soup = BeautifulSoup(response.text, 'html.parser')

# 2. Find the FIRST order and its link
# We look for the first <h2> that contains an <a> tag
first_h2 = soup.find('h2')
link_tag = first_h2.find('a')

title = link_tag.text.strip()
relative_url = link_tag['href']
full_url = urljoin(base_url, relative_url) # Glues 'whitehouse.gov' to '/order-path'

print(f"DEBUG: Found Title: {title}")
print(f"DEBUG: Found Link: {full_url}")

# 3. Memory Check
if os.path.exists("history.txt"):
    with open("history.txt", "r") as f:
        history = f.read()
else:
    history = ""

if title not in history:
    print("ACTION: New order detected! Fetching full text...")
    
    # 4. Fetch the FULL page
    full_page_response = requests.get(full_url)
    full_soup = BeautifulSoup(full_page_response.text, 'html.parser')
    
    # 5. Extract Body Content
    # Most news/gov sites put the main text in 'p' tags
    # We grab the first 15 paragraphs
    paragraphs = full_soup.find_all('p')
    body_text = "\n".join([p.text for p in paragraphs[:15]])
    
    print(f"DEBUG: Extracted {len(body_text)} characters of text.")

    # 6. AI Analysis
    chat_completion = client.chat.completions.create(
        messages=[
            {"role": "system", "content": "You are a policy analyst. Summarize the provided text into: 1. Purpose, 2. Key Actions, 3. Impact."},
            {"role": "user", "content": f"Please analyze this order:\n\n{body_text}"}
        ],
        model="llama-3.3-70b-versatile",
    )
    
    print("\n--- AI ANALYSIS ---")
    print(chat_completion.choices[0].message.content)

    # 7. Update Memory
    with open("history.txt", "a") as f:
        f.write(title + "\n")
else:
    print("SKIP: Already processed this order.")
