from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import requests

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///football_hub.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'your_secret_key'

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    favorite_team = db.Column(db.String(100))

    def __repr__(self):
        return f'<User {self.username}>'
    
class Team(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    abbreviation = db.Column(db.String(10))  # Optional
    conference = db.Column(db.String(100))  # Optional

    def __repr__(self):
        return f'<Team {self.name}>'
    
class Ranking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rank = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    conference = db.Column(db.String(100))
    record = db.Column(db.String(20))

    def __repr__(self):
        return f'<Ranking {self.name} - Rank {self.rank}>'

@app.route('/')
def home():
    user = None
    if 'username' in session:
        user = User.query.filter_by(username=session['username']).first()
    return render_template('home.html', user=user)

@app.route('/scores')
def scores():
    return render_template('scores.html')

@app.route('/teams')
def teams():
    return render_template('teams.html')

@app.route('/news')
def news():
    return render_template('news.html')

@app.route('/rankings')
def rankings():
    rankings_data = Ranking.query.order_by(Ranking.rank).all()
    return render_template('rankings.html', rankings=rankings_data)

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
    url = 'https://api.collegefootballdata.com/rankings?year=2024&week=9' # Hard coded the week -- need to fix
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


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        fetch_and_store_teams()
        fetch_and_store_rankings() 
    app.run(debug=True)

