import sys
import argparse
import json
import requests

DOCKER_HUB_API_ENDPOINT = r'https://hub.docker.com/v2/'
repo = r"alpine/bundle"

# Get all tags in the repository 
def get_tags():
    headers = {'Content-type': 'application/json'}
    data = None
    url = f'{DOCKER_HUB_API_ENDPOINT}repositories/{repo}/tags'
    request_method = getattr(requests, 'get')
    if data and len(data) > 0:
        data = json.dumps(data, indent=2, sort_keys=True)
        resp = request_method(url, data, headers)
    else:
        resp = request_method(url, headers)
    content = {}
    if resp.status_code == 200:
        content = json.loads(resp.content.decode())

    # Print all tags
    print("Printing Tags in repo {}:".format(repo))
    for tag in content["results"]:
        print("-", tag["name"])    

def main():
    get_tags()

if __name__ == '__main__':
    main()