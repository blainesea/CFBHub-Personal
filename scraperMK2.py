import requests
from bs4 import BeautifulSoup
import csv

# URL of the page to scrape
url = "https://www.jhowell.net/cf/scores/Sked2024.htm"

# Request the webpage
response = requests.get(url)

if response.status_code == 200:
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find all tables (assuming there are multiple tables to scrape)
    tables = soup.find_all('table', {'border': '1'})

    # Prepare the CSV file
    csv_file = 'football_schedule.csv'
    with open(csv_file, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)

        # Loop over each table
        for table in tables:
            # Get the team name from the first row
            team_name_row = table.find('tr')
            team_name = team_name_row.get_text(strip=True)

            # Write the team name as a header in the CSV
            writer.writerow([team_name])

            # Get the subsequent rows (game details)
            game_rows = table.find_all('tr')[1:]  # Skip the team name row
            for game_row in game_rows:
                cells = game_row.find_all('td')
                # Extract text from each cell
                row_data = [cell.get_text(strip=True) for cell in cells]
                # Write the row data to the CSV file
                writer.writerow(row_data)

    print(f"Data has been successfully written to {csv_file}")
