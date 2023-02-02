import sys
import argparse
import json
import requests
#from python_on_whales import 

DOCKER_HUB_API_ENDPOINT = r'https://hub.docker.com/v2/'
#repo = r"liorf077/testrepo"

# Get all tags in the repository 
def get_tags(repo):
    headers = {'Content-type': 'application/json'}
    url = f'{DOCKER_HUB_API_ENDPOINT}repositories/{repo}/tags'
    request_method = getattr(requests, 'get')
    signature = [] 

    resp = request_method(url, headers)
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
        # Look for cosign signature - https://github.com/sigstore/cosign/blob/main/specs/SIGNATURE_SPEC.md
        if (".sig") in tag["name"]:
            signature.append(tag["name"])
    # Print the signature found
    if not signature:
       print("The image doesn't have cosign signature in the repository") 
    else:
        print("The image has cosign signature in the repository:\n {}".format(signature))

def get_arguments():
    # Get repository path from user
    parser = argparse.ArgumentParser(prog="Image Enumerator")
    parser.add_argument('-r', '--repo')
    args = parser.parse_args()
    # Print help if no arguments given
    if len(sys.argv) < 2:
        print("repository name is mandatory")
        sys.exit(1)
    return args.repo

def main():
    repo = get_arguments()
    get_tags(repo)

if __name__ == '__main__':
    main()