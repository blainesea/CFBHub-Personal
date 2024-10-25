import requests
from bs4 import BeautifulSoup

def fetch_individual_stats():
    url = "https://www.ncaa.com/stats/football/fbs"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Initialize lists to store stats
    stats = {
        "passing": [],
        "rushing": [],
        "scoring_offense": [],
        "scoring_defense": []
    }

    # Scrape Passing Yards data
    passing_section = soup.find('h2', string="Passing Yards")
    if passing_section:
        passing_table = passing_section.find_next('table')
        rows = passing_table.find_all('tr')[1:]  # Skip header row
        for row in rows:
            columns = row.find_all('td')
            if columns:
                player = {
                    "rank": columns[0].text.strip(),
                    "player": columns[1].text.strip(),
                    "team": columns[2].text.strip(),
                    "yards": columns[3].text.strip()
                }
                stats['passing'].append(player)

    # Scrape Rushing Yards data
    rushing_section = soup.find('h2', string="Rushing Yards")
    if rushing_section:
        rushing_table = rushing_section.find_next('table')
        rows = rushing_table.find_all('tr')[1:]  # Skip header row
        for row in rows:
            columns = row.find_all('td')
            if columns:
                player = {
                    "rank": columns[0].text.strip(),
                    "player": columns[1].text.strip(),
                    "team": columns[2].text.strip(),
                    "yards": columns[3].text.strip()
                }
                stats['rushing'].append(player)

    # Scrape Scoring Offense data
    offense_section = soup.find('h2', string="Scoring Offense")
    if offense_section:
        offense_table = offense_section.find_next('table')
        rows = offense_table.find_all('tr')[1:]  # Skip header row
        for row in rows:
            columns = row.find_all('td')
            if columns:
                team = {
                    "rank": columns[0].text.strip(),
                    "team": columns[1].text.strip(),
                    "points": columns[2].text.strip()
                }
                stats['scoring_offense'].append(team)

    # Scrape Scoring Defense data
    defense_section = soup.find('h2', string="Scoring Defense")
    if defense_section:
        defense_table = defense_section.find_next('table')
        rows = defense_table.find_all('tr')[1:]  # Skip header row
        for row in rows:
            columns = row.find_all('td')
            if columns:
                team = {
                    "rank": columns[0].text.strip(),
                    "team": columns[1].text.strip(),
                    "points_allowed": columns[2].text.strip()
                }
                stats['scoring_defense'].append(team)

    return stats
