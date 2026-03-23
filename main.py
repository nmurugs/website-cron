import os
import requests
from bs4 import BeautifulSoup
from groq import Groq

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# 1. Fetch the main index page
url = "https://www.whitehouse.gov/executive-orders/"
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')

# 2. Get the FIRST order's headline and the link to its full page
first_order = soup.find('h2')
title = first_order.text.strip()
full_url = first_order.find('a')['href'] # This finds the link inside the H2

# 3. Check Memory
if os.path.exists("history.txt"):
    with open("history.txt", "r") as f:
        history = f.read()
else:
    history = ""

if title not in history:
    print(f"New Order Detected: {title}")
    
    # 4. WALK INSIDE: Fetch the full document page
    page_content = requests.get(full_url).text
    page_soup = BeautifulSoup(page_content, 'html.parser')
    
    # 5. GRAB THE BODY: Most WH orders are in 'p' tags inside an article or section
    # We'll take the first 15 paragraphs to avoid hitting AI limits
    paragraphs = page_soup.find_all('p')
    body_text = "\n".join([p.text for p in paragraphs[:15]])

    # 6. ASK THE BRAIN: Use the full text for the summary
    chat_completion = client.chat.completions.create(
        messages=[
            {"role": "system", "content": "You are a policy analyst. Summarize the following executive order text into 3 bullet points: Main Goal, Key Requirement, and Impact."},
            {"role": "user", "content": f"Title: {title}\n\nContent:\n{body_text}"}
        ],
        model="llama-3.3-70b-versatile",
    )
    
    summary = chat_completion.choices[0].message.content
    print(f"--- AI ANALYSIS ---\n{summary}")

    # 7. Update Memory
    with open("history.txt", "a") as f:
        f.write(title + "\n")
else:
    print("Nothing new to report.")


# import os
# from groq import Groq
# import requests
# from bs4 import BeautifulSoup

# # 1. Setup Groq
# client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# # 2. Scrape (Same logic as before)
# url = "https://www.whitehouse.gov/executive-orders/"
# html = requests.get(url).text
# soup = BeautifulSoup(html, 'html.parser')
# latest_eo = soup.find('h2').text.strip()

# # 3. Memory Check
# if os.path.exists("history.txt"):
#     with open("history.txt", "r") as f:
#         history = f.read()
# else:
#     history = ""

# if latest_eo not in history:
#     # 4. Use Groq's Free Model
#     chat_completion = client.chat.completions.create(
#         messages=[{"role": "user", "content": f"Summarize this: {latest_eo}"}],
#         model="llama-3.3-70b-versatile",
#     )
#     print(f"Summary: {chat_completion.choices[0].message.content}")

#     # 5. Update Memory
#     with open("history.txt", "a") as f:
#         f.write(latest_eo + "\n")
