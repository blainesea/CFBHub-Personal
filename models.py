from database import db

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
