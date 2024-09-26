from flask import Flask, render_template
import requests

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/scores')
def scores():
    return render_template('scores.html')

@app.route('/teams')
def teams():
    return render_template('teams.html')

@app.route('/news')
def news():
    return render_template('news.html')

@app.route('/settings')
def settings():
    return render_template('settings.html')

if __name__ == '__main__':
    app.run(debug=True)
