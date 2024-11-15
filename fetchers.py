import requests
from datetime import datetime
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

def fetch_and_store_rankings():
    print(f"Running fetch_and_store_rankings at {datetime.now()}")
    # Helper function to get the current week
    def get_current_week():
        season_start = datetime(2024, 8, 26)  # Adjust based on the actual season start date
        today = datetime.today()
        weeks_since_start = (today - season_start).days // 7 + 1
        return max(1, min(weeks_since_start, 15))

    current_week = get_current_week()

    url = f'https://api.collegefootballdata.com/rankings?year=2024&week={current_week}'
    headers = {
        'Authorization': 'Bearer OaVFD68X/G/TZu4gHMxr/ApYaot/HP/quea1h2FSetWo2sUz/QpxIvafH5MZpqee'
    }
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        rankings_data = response.json()
        afca_poll = rankings_data[0]['polls'][0]['ranks']

        Ranking.query.filter_by(poll_type="AFCA Coaches").delete()
        db.session.commit()

        for team in afca_poll:
            rank = team['rank']
            name = team['school']
            conference = team.get('conference', 'N/A')
            record = team.get('record', 'N/A')

            new_team = Ranking(
                rank=rank,
                name=name,
                conference=conference,
                record=record,
                poll_type="AFCA Coaches"
            )
            db.session.add(new_team)

        db.session.commit()
        print("AFCA Coaches rankings updated in the database.")
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
    
def fetch_and_store_ap_and_cfp_rankings():
    print(f"Running fetch_and_store_ap_and_cfp_rankings at {datetime.now()}")
    # Helper function to get the current week
    def get_current_week():
        season_start = datetime(2024, 8, 26)  # Adjust based on the actual season start date
        today = datetime.today()
        weeks_since_start = (today - season_start).days // 7 + 1
        return max(1, min(weeks_since_start, 15))

    current_week = get_current_week()
    url = f'https://api.collegefootballdata.com/rankings?year=2024&week={current_week}'
    headers = {
        'Authorization': 'Bearer OaVFD68X/G/TZu4gHMxr/ApYaot/HP/quea1h2FSetWo2sUz/QpxIvafH5MZpqee'
    }
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        rankings_data = response.json()

        ap_poll = next((poll['ranks'] for poll in rankings_data[0]['polls'] if poll['poll'] == 'AP Top 25'), [])
        cfp_rankings = next((poll['ranks'] for poll in rankings_data[0]['polls'] if poll['poll'] == 'Playoff Committee Rankings'), [])

        store_rankings(ap_poll, 'AP')
        store_rankings(cfp_rankings, 'CFP')

        print("AP Poll and CFP rankings updated in the database.")
    else:
        print(f"Failed to fetch rankings. Status code: {response.status_code}")

def store_rankings(ranks, poll_type):
    for team in ranks:
        rank = team['rank']
        name = team['school']
        conference = team.get('conference', 'N/A')
        record = team.get('record', 'N/A')

        existing_team = Ranking.query.filter_by(name=name, poll_type=poll_type).first()

        if existing_team:
            existing_team.rank = rank
            existing_team.conference = conference
            existing_team.record = record
        else:
            new_ranking = Ranking(rank=rank, name=name, conference=conference, record=record, poll_type=poll_type)
            db.session.add(new_ranking)

    db.session.commit()
    