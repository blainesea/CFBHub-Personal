# stats_scraper.py
import requests
from bs4 import BeautifulSoup

def scrape_ncaa_stats(stat_type):
    try:
        if stat_type == 'passing':
            url = 'https://www.ncaa.com/stats/football/fbs/current/individual/453'
            columns = [0, 1, 2, 3, 10]
        elif stat_type == 'rushing':
            url = 'https://www.ncaa.com/stats/football/fbs/current/individual/469'
            columns = [0, 1, 2, 3, 8]
        elif stat_type == 'interceptions':
            url = 'https://www.ncaa.com/stats/football/fbs/current/individual/14'
            columns = [0, 1, 2, 3, 6]
        elif stat_type == 'tackles':
            url = 'https://www.ncaa.com/stats/football/fbs/current/individual/34'
            columns = [0, 1, 2, 3, 8]
        else:
            raise ValueError("Invalid stat_type provided")

        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        table = soup.find('table')
        rows = table.find_all('tr')[1:]  # Skip the header row

        player_stats = []
        for row in rows:
            cols = row.find_all('td')
            if len(cols) > max(columns):
                data = [cols[i].text.strip() for i in columns]
                player_stats.append({
                    "rank": data[0],
                    "name": data[1],
                    "team": data[2],
                    "year": data[3],
                    "stat": data[4]
                })

        return player_stats

    except Exception as e:
        print(f"An error occurred: {e}")
        return []

