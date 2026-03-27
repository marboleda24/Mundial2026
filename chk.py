import requests
import sys

headers = {'X-Auth-Token': '1f0345e601be416db95eabbf090149a2'}
print("Fetching teams...")
res = requests.get('https://api.football-data.org/v4/competitions/WC/teams', headers=headers)
print("Status:", res.status_code)
print(res.json())

print("Fetching matches...")
res2 = requests.get('https://api.football-data.org/v4/competitions/WC/matches', headers=headers)
print("Status:", res2.status_code)
print(res2.json())
