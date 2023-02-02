### IMPORTS ###
import sys
import argparse
import json
import requests

### GLOBALS ###
DOCKER_HUB_API_ENDPOINT = r'https://hub.docker.com/v2/'
HEADERS = {'Content-type': 'application/json'}
DIGESTS = []
SUSPECTED = []

# Query tags to find the related digests in order to look for cosign signature format
def query_tag(repo, tag):
    request_method = getattr(requests, 'get')
    url = f'{DOCKER_HUB_API_ENDPOINT}repositories/{repo}/tags/{tag}'
    resp = request_method(url, HEADERS)
    tag_content = {}
    if resp.status_code == 200:
        tag_content = json.loads(resp.content.decode())
    else:
        print("There was a problem with the request.")
        sys.exit(1)
    digest = tag_content['images'][0]['digest']
    digest = digest.replace(':','-')
    digest = digest+".sig"
    DIGESTS.append(digest)

# Get all tags in the repository 
def get_tags(repo):
    url = f'{DOCKER_HUB_API_ENDPOINT}repositories/{repo}/tags'
    request_method = getattr(requests, 'get')
    signature = []  
    resp = request_method(url, HEADERS)
    content = {}
    if resp.status_code == 200:
        content = json.loads(resp.content.decode())
    else:
        print("There was a problem with the request. Check if the repository name is correct.")
        sys.exit(1)
    # Print all tags
    print("Printing Tags in repo {}:".format(repo))
    for tag in content["results"]:
        print("-", tag["name"])
        SUSPECTED.append(tag["name"])
        # Look for cosign signature - https://github.com/sigstore/cosign/blob/main/specs/SIGNATURE_SPEC.md
        query_tag(repo, tag["name"])

# Get repository path from user
def get_argument():
    parser = argparse.ArgumentParser(prog="Image Enumerator")
    parser.add_argument('-r', '--repo')
    args = parser.parse_args()
    # Print help if no arguments given
    if len(sys.argv) < 2:
        print("repository name is mandatory")
        sys.exit(1)
    return args.repo

def main():
    repo = get_argument()
    get_tags(repo)

    # Go over the lists of Diagests and tags, and find cosign signature
    for suspect in SUSPECTED:
        if suspect in DIGESTS:
            print("found cosign signature {}".format(suspect))

if __name__ == '__main__':
    main()