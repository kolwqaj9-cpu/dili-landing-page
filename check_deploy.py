import json
import requests

config = json.load(open('.netlify_config.json'))
headers = {'Authorization': f'Bearer {config["api_token"]}'}

deploy_id = '6981f352ccad4d088890b21c'
r = requests.get(f'https://api.netlify.com/api/v1/deploys/{deploy_id}', headers=headers)
d = r.json()

print(f'Deploy ID: {deploy_id}')
print(f'State: {d.get("state")}')
print(f'Published: {d.get("published_at") is not None}')
print(f'\nTo publish:')
print(f'https://app.netlify.com/sites/{config["site_id"]}/deploys/{deploy_id}')
