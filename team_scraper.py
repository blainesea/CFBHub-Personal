# from bs4 import BeautifulSoup
# import requests

# def fetch_teams():
#     url = 'https://www.espn.com/college-football/teams'
    
#     response = requests.get(url)
#     if response.status_code != 200:
#         return []  # Return empty if request failed
    
#     soup = BeautifulSoup(response.content, 'html.parser')
    
#     teams = []
#     # Adjust the selector to match the actual structure of the team listing
#     team_elements = soup.find_all('a', class_='AnchorLink')

#     for team in team_elements:
#         name = team.text.strip()
#         href = team['href']
#         # Extracting team abbreviation from the URL
#         if "/team/schedule/_/id/" in href:
#             team_id = href.split('/')[-2]  # Extract the team ID
#             teams.append({
#                 'name': name,
#                 'abbreviation': team_id  # Store ID for later use
#             })
    
#     return teams

# def fetch_team_schedule(team_id):
#     # URL to fetch the team's schedule
#     url = f'https://www.espn.com/college-football/team/schedule/_/id/{team_id}/season/2024'
    
#     response = requests.get(url)
#     if response.status_code != 200:
#         return []  # Return empty if request failed
    
#     soup = BeautifulSoup(response.content, 'html.parser')
    
#     schedule = []
    
#     # Scraping logic for ESPN team schedules
#     games = soup.find_all('tr', class_='Table__TR')
#     for game in games:
#         try:
#             date = game.find('td', class_='date').text.strip()
#             opponent = game.find('td', class_='opponent').text.strip()
#             venue = game.find('td', class_='venue').text.strip()
#             schedule.append({
#                 'date': date,
#                 'opponent': opponent,
#                 'venue': venue
#             })
#         except AttributeError:
#             # Handle games that don't have a full set of data
#             continue
    
#     return schedule
