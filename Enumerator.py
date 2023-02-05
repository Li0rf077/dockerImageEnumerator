### IMPORTS ###
import sys
import argparse
import json
import requests

### GLOBALS ###
DOCKER_HUB_API_ENDPOINT = r'https://registry.hub.docker.com/v2/'
HEADERS = {'Content-type': 'application/json'}    

# Query tags to find the related digests in order to look for cosign signature format
def query_tag(repo, tag):
    diagests = []
    url = f'{DOCKER_HUB_API_ENDPOINT}repositories/{repo}/tags/{tag}'
    
    # Generate request
    resp = requests.get(url, headers=HEADERS)
    if resp.status_code == 200:
        tag_content = json.loads(resp.content.decode())
    else:
        print("There was a problem with the request.")
        sys.exit(1)
    
    # Extract diagest from tag, and add it to a list of diagests
    digest = tag_content['images'][0]['digest']
    digest = digest.replace(':','-')
    digest = digest+".sig"
    diagests.append(digest)
    return diagests

# extract manifest by tag
def get_manifest(repo, tag):
    auth_url = f"https://auth.docker.io/token?service=registry.docker.io&scope=repository:{repo}:pull"
    
    # Request token for REGISTRY_SERVICE and repo and extract token from the response
    token = requests.get(auth_url)
    if token.status_code == 200:
        token = json.loads(token.content.decode())
        token = token["token"]
    else:
        print("There was a problem with the request.")
        sys.exit(1)
    
    token_header = {"Authorization": f"bearer {token}"}
    url = f"https://index.docker.io/v2/{repo}/manifests/{tag}"

    # Request for manifest with the token 
    resp = requests.get(url, headers=token_header)
    if resp.status_code == 200:
        manifest = json.loads(resp.content.decode())
        return manifest
    elif resp.status_code == 404:
        return "manifest not found for image"
    else:
        print("There was a problem with the request.")
        sys.exit(1)

# Get all tags in the repository 
def get_tags(repo):
    url = f'{DOCKER_HUB_API_ENDPOINT}/repositories/{repo}/tags'
    
    # Generate request
    resp = requests.get(url, headers=HEADERS)
    if resp.status_code == 200:
        content = json.loads(resp.content.decode())
    else:
        print("There was a problem with the request. Check if the repository name is correct.")
        sys.exit(1)
    return content      

# Get repository path from user
def get_repository():
    parser = argparse.ArgumentParser(prog="Docker Image Enumerator")
    parser.add_argument('-r', '--repo')
    args = parser.parse_args()
    
    # Print help if arguments are missing
    if len(sys.argv) < 3:
        print("repository argument is mandatory")
        sys.exit(1)
    return args.repo

def main():
    suspected = []
    repo = get_repository()
    tags = get_tags(repo)
    
    # Print all tags
    print("Printing Tags in repo {}:".format(repo))
    for tag in tags["results"]:
        print("***", tag["name"], "***")
        
        # Fetch manifest for each tag
        manifest = get_manifest(repo, tag["name"])
        print("Printing manifest:")
        print(json.dumps(manifest, indent=2), "\n\n")
        
        # Look for cosign signature - https://github.com/sigstore/cosign/blob/main/specs/SIGNATURE_SPEC.md
        suspected.append(tag["name"])
        diagests = query_tag(repo, tag["name"])
    
    # Go over the lists of Diagests and tags, and find cosign signature
    for suspect in suspected:
        if suspect in diagests:
            print("found cosign signature {}".format(suspect))
    
if __name__ == '__main__':
    main()