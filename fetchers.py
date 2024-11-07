import requests
from database import db
from models import Team, Ranking

# Function to fetch teams from the API and populate the database
def fetch_and_store_teams():

    if Team.query.first():
        print("Teams already exist in the database. Skipping API request.")
        return
    
    url = 'https://api.collegefootballdata.com/teams'
    headers = {
        'Authorization': 'Bearer OaVFD68X/G/TZu4gHMxr/ApYaot/HP/quea1h2FSetWo2sUz/QpxIvafH5MZpqee'
    }
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        teams_data = response.json()
#        print(teams_data)
        
        for team in teams_data:
            team_name = team['school']
            abbreviation = team.get('abbreviation', None)
            conference = team.get('conference', None)

            existing_team = Team.query.filter_by(name=team_name).first()
            if not existing_team:
                new_team = Team(name=team_name, abbreviation=abbreviation, conference=conference)
                db.session.add(new_team)

        db.session.commit()
        print("Teams have been added to the database.")
    else:
        print(f"Failed to fetch teams. Status code: {response.status_code}")

# Fetch rankings data from the API and store in the database
def fetch_and_store_rankings():
    url = 'https://api.collegefootballdata.com/rankings?year=2024&week=9' # Hard coded the week -- need to fix, maybe
    headers = {
        'Authorization': 'Bearer OaVFD68X/G/TZu4gHMxr/ApYaot/HP/quea1h2FSetWo2sUz/QpxIvafH5MZpqee'
    }
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        rankings_data = response.json()
        
        ap_poll = rankings_data[0]['polls'][0]['ranks']

        for team in ap_poll:
            rank = team['rank']
            name = team['school']
            conference = team.get('conference', 'N/A')
            record = team.get('record', 'N/A')

            existing_team = Ranking.query.filter_by(name=name).first()

            if existing_team:
                existing_team.rank = rank
                existing_team.conference = conference
                existing_team.record = record
            else:
                new_team = Ranking(rank=rank, name=name, conference=conference, record=record)
                db.session.add(new_team)

        db.session.commit()
        print("Rankings updated in the database.")
    else:
        print(f"Failed to fetch rankings. Status code: {response.status_code}")

def fetch_team_schedule(team_name):
    url = f'https://api.collegefootballdata.com/games?year=2024&seasonType=regular&team={team_name}'
    headers = {
        'Authorization': 'Bearer OaVFD68X/G/TZu4gHMxr/ApYaot/HP/quea1h2FSetWo2sUz/QpxIvafH5MZpqee'
    }
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        schedule_data = response.json()
        schedule = [
            {
                "date": game['start_date'],
                "opponent": game['home_team'] if game['away_team'] == team_name else game['away_team'],
                "location": "Home" if game['home_team'] == team_name else "Away"
            }
            for game in schedule_data
        ]
        return schedule
    else:
        print(f"Failed to fetch schedule. Status code: {response.status_code}")
        return None