from flask import Flask, render_template
import requests

app = Flask(__name__)

@app.route('/')
def home():
    # API request
    url = "https://college-football-cff.p.rapidapi.com/schedule"
    querystring = {"year": "2020", "group": "50"}
    
    headers = {
        "x-rapidapi-key": "your-rapidapi-key",
        "x-rapidapi-host": "college-football-cff.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers, params=querystring)

    # Handle the response
    if response.status_code == 200:
        data = response.json()  # Get the API response
    else:
        data = {"error": f"API request failed with status code {response.status_code}"}

    # Pass the data to the template
    return render_template('home.html', data=data)

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
