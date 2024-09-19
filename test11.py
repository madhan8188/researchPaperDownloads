import requests
import time

def fetch_papers(query, limit=5, retries=3):
    url = f"https://api.semanticscholar.org/graph/v1/paper/search"
    params = {
        'query': query,
    }
    
    for attempt in range(retries):
        response = requests.get(url, params=params)

        if response.status_code == 200:
            papers = response.json()['data']
            # for i, paper in enumerate(papers, 1):
            #     title = paper['title']
            #     authors = ", ".join(author['name'] for author in paper['authors'])
            #     year = paper.get('year', 'Unknown Year')
            #     paper_url = paper.get('url', 'No URL available')
            #     print(f"{i}. {title}\n   Authors: {authors}\n   Year: {year}\n   URL: {paper_url}\n")
            # break  # If successful, exit the loop
        elif response.status_code == 429:
            print(f"Rate limit exceeded, waiting before retrying... (Attempt {attempt+1}/{retries})")
            time.sleep(10)
        else:
            print(f"Failed to fetch papers. HTTP Status Code: {response.status_code}")
            break

if __name__ == "__main__":
    query = "polyphenols based color"
    fetch_papers(query)