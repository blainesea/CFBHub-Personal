import requests
import json

# API endpoint for schedules
url = 'https://api.collegefootballdata.com/roster'
params = {
    'year': 2024,  # Specify the year you're interested in
    'team': 'Alabama'  # Regular season games
}
headers = {
    'Authorization': 'Bearer OaVFD68X/G/TZu4gHMxr/ApYaot/HP/quea1h2FSetWo2sUz/QpxIvafH5MZpqee'
}

# Send GET request
response = requests.get(url, headers=headers, params=params)

# Check if the request was successful
if response.status_code == 200:
    # Parse and print the response in JSON format
    data = response.json()
    print(json.dumps(data, indent=4))  # pretty-print the data for easier reading
else:
    print(f"Error: Unable to fetch data (Status Code: {response.status_code})")
