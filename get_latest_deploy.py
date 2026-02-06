import json
import requests

with open('.netlify_config.json') as f:
    config = json.load(f)

headers = {'Authorization': f'Bearer {config["api_token"]}'}
r = requests.get(f'https://api.netlify.com/api/v1/sites/{config["site_id"]}/deploys?per_page=1', headers=headers)
d = r.json()[0] if r.json() else {}

print(f'Latest Deploy ID: {d.get("id", "N/A")}')
print(f'State: {d.get("state", "N/A")}')
print(f'Published: {d.get("published_at") is not None}')
print(f'\nTo publish manually:')
print(f'https://app.netlify.com/sites/{config["site_id"]}/deploys/{d.get("id", "")}')
