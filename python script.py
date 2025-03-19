from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from fake_useragent import UserAgent
import time
import json

# Set up proxy (example with Smartproxy, replace with your credentials)
proxy = "http://username:password@host:port"  # Replace with your proxy details

# Configure Selenium with headless browser and proxy
options = Options()
options.add_argument("--headless")  # Run without GUI
options.add_argument(f"user-agent={UserAgent().random}")  # Random user agent
options.add_argument(f"--proxy-server={proxy}")
driver = webdriver.Chrome(options=options)

# Target Facebook page (replace with your page URL)
page_url = "https://www.facebook.com/ProthomAlo"  # Example: Prothom Alo
driver.get(page_url)

# Scroll to load posts (real-time simulation)
def scroll_and_load_posts():
    posts_data = []
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)  # Wait for posts to load
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:  # No more posts to load
            break
        last_height = new_height

    # Extract posts
    posts = driver.find_elements(By.XPATH, "//div[@role='article']")
    for post in posts:
        try:
            # Extract text (if available)
            text = post.find_element(By.XPATH, ".//div[@data-ad-preview='message']").text
            # Extract reactions (likes, etc.)
            reactions = post.find_element(By.XPATH, ".//span[contains(@class, 'like')]").text
            # Extract comments
            comments = post.find_element(By.XPATH, ".//a[contains(@href, 'comment')]").text
            # Extract shares
            shares = post.find_element(By.XPATH, ".//span[contains(text(), 'Share')]").text.split()[0]
            
            post_data = {
                "text": text[:50],  # Limit text for brevity
                "reactions": reactions,
                "comments": comments,
                "shares": shares
            }
            posts_data.append(post_data)
        except Exception as e:
            continue  # Skip if elements not found
    
    return posts_data

# Run the crawler
print("Crawling posts from", page_url)
posts_data = scroll_and_load_posts()

# Calculate "reach" score (e.g., weighted sum of engagement)
for post in posts_data:
    try:
        reactions_num = int(post["reactions"].split()[0].replace(",", ""))
        comments_num = int(post["comments"].split()[0].replace(",", ""))
        shares_num = int(post["shares"].replace(",", ""))
        # Weighted score: shares > comments > reactions
        post["reach_score"] = (shares_num * 3) + (comments_num * 2) + reactions_num
    except ValueError:
        post["reach_score"] = 0  # Default if parsing fails

# Sort by reach score
top_posts = sorted(posts_data, key=lambda x: x["reach_score"], reverse=True)[:5]

# Output results
print(f"Top 5 posts by approximate reach (as of {time.ctime()}):")
for i, post in enumerate(top_posts, 1):
    print(f"{i}. Text: {post['text']} | Reach Score: {post['reach_score']} "
          f"(Reactions: {post['reactions']}, Comments: {post['comments']}, Shares: {post['shares']})")

# Save to JSON for later use
with open("facebook_posts.json", "w") as f:
    json.dump(top_posts, f, indent=4)

# Clean up
driver.quit()
