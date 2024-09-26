import requests

url = "https://college-football-cff.p.rapidapi.com/schedule"

querystring = {"year": "2020", "group": "50"}

headers = {
    "x-rapidapi-key": "YOUR_ACTUAL_API_KEY",
    "x-rapidapi-host": "college-football-cff.p.rapidapi.com"
}

response = requests.get(url, headers=headers, params=querystring)

if response.status_code == 200:
    data = response.json()
    print(data)
else:
    print(f"API request failed with status code {response.status_code}")
    print(response.text)
