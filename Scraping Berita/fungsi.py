# modul
import requests
from bs4 import BeautifulSoup
import json
from tqdm import tqdm
import pandas as pd


def extract_json_ld(url): # function to extract JSON-LD data from a URL
    response = requests.get(url) # Send a GET request
    response.status_code # Check the status code
    soup = BeautifulSoup(response.content, 'html.parser') # Parse the HTML content

    # Find the JSON-LD script
    json_ld = soup.find('script', type='application/ld+json') # find the JSON-LD script tag and type
    if json_ld: # Check if the JSON-LD script is found
        data = json.loads(json_ld.string) # Load the JSON data
        if isinstance(data, list):  # accomodate if JSON-LD is an array 
            for item in data: # Loop through each item in the array
                if item.get('@type') == 'NewsArticle':  # Check if the item is a NewsArticle with the headline, datePublished, and articleBody  attributes
                    return {
                        "headline": item.get('headline'), # Get the headline
                        "datePublished": item.get('datePublished'), # Get the datePublished
                        "articleBody": item.get('articleBody'), # Get the article
                    }
        elif data.get('@type') == 'NewsArticle': # if JSON-LD is an object
            return {
                "headline": data.get('headline'), # Get the headline
                "datePublished": data.get('datePublished'), # Get the datePublished
                "articleBody": data.get('articleBody'), # Get the article
            }

    return None  # Return None if no JSON-LD is found

# Function to scrape the main page and extract news links
def scrape_main_page(main_url):     
    response = requests.get(main_url) # Send a GET request
    soup = BeautifulSoup(response.content, 'html.parser') # Parse the HTML content

    # Find all <li> tags with <a> containing links
    links = []  # Initialize an empty list to store the links
    for li in soup.find_all('li'): # Loop through all <li> tags
        a_tag = li.find('a', href=True) # Find the first <a> tag with an href attribute
        if a_tag: # Check if the <a> tag is found
            links.append(a_tag['href']) # Append the link to the list

    return links # Return the list of links

# Main function to scrape all articles with a progress bar
def scrape_all_articles(main_url): 
    links = scrape_main_page(main_url) # Scrape the main page to get the links
    articles = []   # Initialize an empty list to store the articles

    # Use tqdm to add a progress bar
    for link in tqdm(links, desc="Scraping Articles", unit="article"): # Loop through each link with a bar
        # Ensure full URL
        if not link.startswith('http'): # Check if the link is a full URL or not
            link = f"{main_url.rstrip('/')}/{link.lstrip('/')}" # Combine the base URL and the link
        article_data = extract_json_ld(link) # Extract JSON-LD data from the link
        if article_data:
            articles.append(article_data)

    return articles

# Define the function to drop rows based on a condition
def drop_rows_before_date(df, date_threshold):
    # Convert the threshold to datetime and localize it to match the DataFrame's timezone
    date_threshold = pd.to_datetime(date_threshold).tz_localize("Asia/Jakarta")
    # Filter rows where datePublished is greater than the threshold
    filtered_df = df[df['datePublished'] > date_threshold]
    return filtered_df

print("a")