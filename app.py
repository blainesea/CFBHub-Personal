from flask import Flask, render_template, request, redirect, url_for, session, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import requests
from database import db
from models import Team, Ranking, User 
from fetchers import fetch_and_store_ap_and_cfp_rankings, fetch_and_store_rankings, fetch_and_store_teams, fetch_team_schedule
import feedparser
# from stats_scraper import scrape_player_stats
from ncaa_scraper import scrape_ncaa_stats
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler

API_KEY = 'Bearer OaVFD68X/G/TZu4gHMxr/ApYaot/HP/quea1h2FSetWo2sUz/QpxIvafH5MZpqee'

def create_app():
    app = Flask(__name__)

    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///football_hub.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.secret_key = 'your_secret_key'

    scheduler = BackgroundScheduler()
    scheduler.add_job(fetch_and_store_rankings, 'cron', day_of_week='mon', hour=10)
    scheduler.add_job(fetch_and_store_ap_and_cfp_rankings, 'cron', day_of_week='mon', hour=11)
    #scheduler.start()

    db.init_app(app)

    @app.route('/')
    def home():
        user = None
        schedule = None
        if 'username' in session:
            user = User.query.filter_by(username=session['username']).first()
            if user and user.favorite_team:
                schedule = fetch_team_schedule(user.favorite_team)

        return render_template('home.html', user=user, schedule=schedule)

    @app.route('/scores')
    def scores():
        return render_template('scores.html')

    @app.route('/schedule', methods=['GET'])
    def schedule():
        team_id = request.args.get('team_id')
        week = request.args.get('week', get_current_week(), type=int)
        conference_filter = request.args.get('conference')

        team = Team.query.get(team_id) if team_id else None

        url = f'https://api.collegefootballdata.com/games?year=2024'
        if week:
            url += f'&week={week}'

        headers = {
            'Authorization': 'Bearer OaVFD68X/G/TZu4gHMxr/ApYaot/HP/quea1h2FSetWo2sUz/QpxIvafH5MZpqee'
        }
        response = requests.get(url, headers=headers)

        schedule = []
        conferences = set()

        if response.status_code == 200:
            games = response.json()

            for game in games:
                if game.get("home_conference"):
                    conferences.add(game["home_conference"])
                if game.get("away_conference"):
                    conferences.add(game["away_conference"])

                if (not team or game["home_team"] == team.name or game["away_team"] == team.name) and (
                    not conference_filter or 
                    game.get("home_conference") == conference_filter or 
                    game.get("away_conference") == conference_filter):

                    schedule.append({
                        "week": game.get("week"),
                        "home_team": game.get("home_team"),
                        "home_points": game.get("home_points"),
                        "away_team": game.get("away_team"),
                        "away_points": game.get("away_points"),
                        "conference_game": game.get("conference_game", False),
                        "over_under": game.get("over_under")  # Include betting odds if available
                    })

        conferences = sorted(conferences)

        return render_template('schedule.html', 
                            schedule=schedule, 
                            team=team, 
                            week=week, 
                            conferences=conferences, 
                            selected_conference=conference_filter,
                            teams=Team.query.all())

    def get_current_week():
        season_start = datetime(2024, 8, 26)  # Adjust based on the actual season start date
        today = datetime.today()
        weeks_since_start = (today - season_start).days // 7 + 1
        return max(1, min(weeks_since_start, 15))
    
    @app.route('/search', methods=['GET'])
    def search():
        search_query = request.args.get('search_query', '').strip()  # Retrieve and sanitize the search query
        schedule = []  # To store the schedule data
        record = {}  # To store the record data
        roster = []  # To store the roster data

        if search_query:  # Only proceed if there's a query
            # API URL for schedule
            schedule_url = f'https://api.collegefootballdata.com/games?year=2024'
            headers = {'Authorization': API_KEY}

            # Fetch schedule data
            schedule_response = requests.get(schedule_url, headers=headers)
            if schedule_response.status_code == 200:
                games = schedule_response.json()
                # Filter games for the searched team
                for game in games:
                    if game["home_team"] == search_query or game["away_team"] == search_query:
                        schedule.append({
                            "week": game.get("week"),
                            "home_team": game.get("home_team"),
                            "home_points": game.get("home_points"),
                            "away_team": game.get("away_team"),
                            "away_points": game.get("away_points"),
                            "date": game.get("start_date")
                        })
            else:
                print("Error fetching schedule data:", schedule_response.status_code)

            # API URL for records
            records_url = 'https://api.collegefootballdata.com/records'
            params = {'year': 2024, 'seasonType': 'regular'}

            # Fetch record data
            records_response = requests.get(records_url, headers=headers, params=params)
            if records_response.status_code == 200:
                records = records_response.json()
                for team_record in records:
                    if team_record["team"] == search_query:
                        record = {
                            "conference": team_record.get("conference", "N/A"),
                            "total": team_record.get("total", {}),
                            "homeGames": team_record.get("homeGames", {}),
                            "awayGames": team_record.get("awayGames", {}),
                            "conferenceGames": team_record.get("conferenceGames", {}),
                            "expectedWins": team_record.get("expectedWins", 0)
                        }
                        break
            else:
                print("Error fetching records data:", records_response.status_code)

            # API URL for roster
            roster_url = 'https://api.collegefootballdata.com/roster'
            params = {'team': search_query}  # Filter roster by team
            roster_response = requests.get(roster_url, headers=headers, params=params)
            if roster_response.status_code == 200:
                roster = roster_response.json()  # Get the full roster list
            else:
                print("Error fetching roster data:", roster_response.status_code)

        return render_template('search.html', search_query=search_query, schedule=schedule, record=record, roster=roster)

    
    
    @app.route('/news')
    def news():
        url = 'https://www.espn.com/espn/rss/ncf/news'
        feed = feedparser.parse(url)
        
        if feed.bozo:
            return "Failed to retrieve news."

        news_articles = []
        
        for entry in feed.entries:
            news_articles.append({
                'title': entry.title,
                'link': entry.link,
                'summary': entry.summary,
                'published': entry.published if 'published' in entry else 'N/A'
            })

        return render_template('news.html', news_articles=news_articles)

    @app.template_filter()
    def enumerate_filter(seq):
        return list(enumerate(seq))

    # @app.route('/stats', methods=['GET'])
    # def stats():
    #     stat_type = request.args.get('stat_type', 'passing') 
    #     player_stats = scrape_player_stats(stat_type)
    #     return render_template('stats.html', player_stats=player_stats, stat_type=stat_type)
    @app.route('/stats', methods=['GET'])
    def stats():
        stat_type = request.args.get('stat_type', 'passing')
        player_stats = scrape_ncaa_stats(stat_type)
        return render_template('stats.html', player_stats=player_stats, stat_type=stat_type)

    @app.route('/rankings', methods=['GET']) # need to clean up
    def rankings():
        selected_poll = request.args.get('poll', 'AFCA Coaches')  # Default to 'AFCA Coaches'

        print(f"Selected poll: {selected_poll}")

        rankings_data = (
            Ranking.query.filter_by(poll_type=selected_poll)
            .order_by(Ranking.rank)
            .all()
        )

        print(f"Fetched {len(rankings_data)} rows for poll type '{selected_poll}'")
        print(f"Data: {[{'rank': r.rank, 'name': r.name, 'poll_type': r.poll_type} for r in rankings_data]}")

        if not rankings_data:
            return f"No rankings available for {selected_poll}.", 404

        return render_template('top_25_rankings.html', rankings=rankings_data, selected_poll=selected_poll)

    @app.route('/gameProjections', methods=['GET'])
    def gameProjections():
        week = request.args.get('week', 1, type=int)
        url = f'https://api.collegefootballdata.com/games?year=2024&week={week}'
        headers = {
            'Authorization': 'Bearer OaVFD68X/G/TZu4gHMxr/ApYaot/HP/quea1h2FSetWo2sUz/QpxIvafH5MZpqee'
        }
        response = requests.get(url, headers=headers)

        games = []
        if response.status_code == 200:
            games = response.json()

            games = sorted(games, key=lambda game: (
                (game.get('home_pregame_elo') in [None, '-'] and game.get('home_postgame_elo') in [None, '-'] and 
                game.get('away_pregame_elo') in [None, '-'] and game.get('away_postgame_elo') in [None, '-'] and
                game.get('excitement_index') in [None, '-']),
                
                (game.get('home_pregame_elo') in [None, '-'] and game.get('home_postgame_elo') in [None, '-'] or
                game.get('away_pregame_elo') in [None, '-'] and game.get('away_postgame_elo') in [None, '-']) and
                game.get('excitement_index') not in [None, '-'],
                
                game.get('excitement_index') in [None, '-']
            ))
        return render_template('gameProjections.html', games=games, week=week)

    @app.route('/settings')
    def settings():
        if 'username' not in session:
            return redirect(url_for('login'))
        
        user = User.query.filter_by(username=session['username']).first()
        
        return render_template('settings.html', user=user)

    @app.route('/update_settings', methods=['POST'])
    def update_settings():
        if 'username' not in session:
            return redirect(url_for('login'))
        
        favorite_team = request.form['favorite_team']
        
        user = User.query.filter_by(username=session['username']).first()
        
        if favorite_team:
            user.favorite_team = favorite_team
        
        db.session.commit()
        
        return redirect(url_for('settings'))

    @app.route('/create_account', methods=['GET', 'POST'])
    def create_account():
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']

            existing_user = User.query.filter_by(username=username).first()
            if existing_user:
                return 'Username already exists. Please choose another.'

            hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

            new_user = User(username=username, password=hashed_password)
            db.session.add(new_user)
            db.session.commit()

            return redirect('/login')

        return render_template('create_account.html')

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        error = None
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']

            user = User.query.filter_by(username=username).first()

            if user and check_password_hash(user.password, password):
                session['username'] = user.username
                return redirect(url_for('home'))
            else:
                error = 'Invalid username or password.'

        return render_template('login.html', error=error)

    @app.route('/update_username', methods=['POST'])
    def update_username():
        if 'username' not in session:
            return redirect(url_for('login'))
        
        new_username = request.form['new_username']
        current_user = User.query.filter_by(username=session['username']).first()

        existing_user = User.query.filter_by(username=new_username).first()
        if existing_user:
            return 'Username is already taken. Please choose another.'

        current_user.username = new_username
        session['username'] = new_username
        db.session.commit()

        return redirect(url_for('settings'))

    @app.route('/update_password', methods=['POST'])
    def update_password():
        if 'username' not in session:
            return redirect(url_for('login'))
        
        current_password = request.form['current_password']
        new_password = request.form['new_password']

        current_user = User.query.filter_by(username=session['username']).first()

        if not check_password_hash(current_user.password, current_password):
            return 'Current password is incorrect.'

        hashed_new_password = generate_password_hash(new_password, method='pbkdf2:sha256')
        current_user.password = hashed_new_password
        db.session.commit()

        return redirect(url_for('settings'))

    @app.route('/search_teams', methods=['GET'])
    def search_teams():
        query = request.args.get('query', '')
        if query:
            teams = Team.query.filter(Team.name.ilike(f'%{query}%')).all()
            team_list = [{'id': team.id, 'name': team.name} for team in teams]
            return {'teams': team_list}
        return {'teams': []}

    @app.route('/update_favorite_team', methods=['POST'])
    def update_favorite_team():
        if 'username' not in session:
            return redirect(url_for('login'))

        favorite_team_id = request.form['favorite_team_id']
        user = User.query.filter_by(username=session['username']).first()
        favorite_team = Team.query.get(favorite_team_id)

        if favorite_team:
            user.favorite_team = favorite_team.name
            db.session.commit()

        return redirect(url_for('settings'))

    @app.route('/logout')
    def logout():
        session.pop('username', None)
        return redirect(url_for('home'))

    @app.route('/rankings/top25', methods=['GET'])
    def top_25_rankings():
        selected_poll = request.args.get('poll', 'AFCA Coaches')  # Default to 'AFCA Coaches'
       
#        print("Top 25 Rankings route accessed!")
#        print(f"Selected poll: {selected_poll}")

        rankings_data = Ranking.query.filter_by(poll_type=selected_poll).order_by(Ranking.rank).all()

#        print(f"Fetched {len(rankings_data)} rows for poll type '{selected_poll}'")
#        print(f"Data: {[{'rank': r.rank, 'name': r.name, 'poll_type': r.poll_type} for r in rankings_data]}")

        if not rankings_data:
            return f"No rankings available for {selected_poll}.", 404

        return render_template('top_25_rankings.html', rankings=rankings_data, selected_poll=selected_poll)

    @app.route('/conference_rankings')
    def conference_rankings():
        url = 'https://api.collegefootballdata.com/games?year=2024'
        headers = {
            'Authorization': 'Bearer OaVFD68X/G/TZu4gHMxr/ApYaot/HP/quea1h2FSetWo2sUz/QpxIvafH5MZpqee'
        }
        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            return "Failed to retrieve conference standings."

        games = response.json()
        standings = {}

        allowed_conferences = [
            "ACC",
            "American Athletic",
            "Big 12",
            "Big Ten",
            "Conference USA",
            "FBS Independents",
            "Mid-American",
            "Mountain West",
            "Pac-12",
            "SEC",
            "Sun Belt"
        ]

        for game in games:
            if game.get("conference_game"):
                home_team = game["home_team"]
                away_team = game["away_team"]
                home_points = game["home_points"] or 0
                away_points = game["away_points"] or 0
                home_conference = game["home_conference"]
                away_conference = game["away_conference"]

                for team, points, opponent_points, conference in [
                    (home_team, home_points, away_points, home_conference),
                    (away_team, away_points, home_points, away_conference),
                ]:
                    if conference not in allowed_conferences:
                        continue

                    if conference not in standings:
                        standings[conference] = {}

                    if team not in standings[conference]:
                        standings[conference][team] = {
                            "wins": 0,
                            "losses": 0,
                            "points_for": 0,
                            "points_against": 0
                        }

                    standings[conference][team]["points_for"] += points
                    standings[conference][team]["points_against"] += opponent_points

                    if points > opponent_points:
                        standings[conference][team]["wins"] += 1
                    elif points < opponent_points:
                        standings[conference][team]["losses"] += 1

        standings = {
            conf: dict(sorted(teams.items(), key=lambda x: x[1]["wins"], reverse=True))
            for conf, teams in standings.items()
        }

        selected_conference = request.args.get('conference', allowed_conferences[0])

        return render_template(
            'conference_rankings.html',
            standings=standings,
            allowed_conferences=allowed_conferences,
            selected_conference=selected_conference
        )
    
    return app

app = create_app()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        fetch_and_store_teams()
        fetch_and_store_rankings()
        fetch_and_store_ap_and_cfp_rankings()
    #scheduler.start()  
    app.run(debug=True)

