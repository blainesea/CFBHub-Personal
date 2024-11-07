import requests
from bs4 import BeautifulSoup

def scrape_player_stats(stat_type):
    if stat_type == 'passing':
        url = 'https://www.espn.com/college-football/stats/player/_/table/passing/sort/passingYards/dir/desc'
    elif stat_type == 'rushing':
        url = 'https://www.espn.com/college-football/stats/player/_/view/offense/stat/rushing/table/rushing/sort/rushingYards/dir/desc'
    elif stat_type == 'receiving':
        url = 'https://www.espn.com/college-football/stats/player/_/view/offense/stat/receiving/table/receiving/sort/receivingYards/dir/desc'
    elif stat_type == 'tackles':
        url = 'https://www.espn.com/college-football/stats/player/_/view/defense/table/defensive/sort/totalTackles/dir/desc'
    elif stat_type == 'sacks':
        url = 'https://www.espn.com/college-football/stats/player/_/view/defense/table/defensive/sort/sacks/dir/desc'
    elif stat_type == 'interceptions':
        url = 'https://www.espn.com/college-football/stats/player/_/view/defense/table/defensiveInterceptions/sort/interceptions/dir/desc'

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    ranks = []

    table = soup.find('table')
    if not table:
        return []

    rows = table.find_all('tr')[1:]
    for row in rows:
        cols = row.find_all('td')
        if len(cols) < 2:
            continue
        
        rank = cols[0].text.strip()  
        name = cols[1].find("a").text.strip() if cols[1].find("a") else cols[1].text.strip()
        team = cols[1].find("span", class_="athleteCell__teamAbbrev").text.strip() if cols[1].find("span", class_="athleteCell__teamAbbrev") else ""  

        ranks.append({
            "rank": rank,
            "name": name,
            "team": team
        })

    return ranks

# if __name__ == '__main__':
#     stat_types = ['passing', 'rushing', 'receiving']
    
#     for stat_type in stat_types:
#         player_stats = scrape_player_stats(stat_type)

#         print(f"Scraped {stat_type.capitalize()} Stats:")
#         for player in player_stats:
#             print(f"Rank: {player['rank']}, Name: {player['name']}, Team: {player['team']}")
#         print()