import requests
from bs4 import BeautifulSoup

def scrape_si_headlines():
    url = "https://www.si.com/college/college-football"
    response = requests.get(url)
    
    # Check if the request was successful
    if response.status_code != 200:
        print(f"Failed to retrieve the page. Status code: {response.status_code}")
        return []

    # Print part of the HTML content to inspect it
    print("HTML content preview:")
    print(response.text[:1000])  # Print the first 1000 characters for inspection

    soup = BeautifulSoup(response.text, "html.parser")

    # Placeholder for headlines extraction
    headlines = []
    article_elements = soup.find_all("a", class_="type-article")

    if not article_elements:
        print("No elements found with class 'type-article'. Trying a different approach.")
        
        # Print all the anchor tags with any class attribute for debugging
        for anchor in soup.find_all("a"):
            print("Anchor tag with class:", anchor.get("class"), "| Text:", anchor.get_text(strip=True))

    for article in article_elements:
        title = article.get_text(strip=True)
        link = article.get("href")
        if title and link:
            full_link = f"https://www.si.com{link}" if link.startswith("/") else link
            headlines.append({"title": title, "link": full_link})

    return headlines

if __name__ == "__main__":
    top_headlines = scrape_si_headlines()
    print("\nTop Headlines from Sports Illustrated:")
    for headline in top_headlines:
        print(f"{headline['title']}\n{headline['link']}\n")
