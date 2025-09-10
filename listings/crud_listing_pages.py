#!/usr/bin/env python3
import json
import os
import requests
import sys
import argparse

# Load configuration from config.json
# Expects ORG_ID, TRACKING_ID, BASE_URL, and ACCESS_TOKEN to be defined in the JSON file
try:
    with open('config.json') as f:
        config = json.load(f)
except Exception as e:
    print(f"Error loading config.json, please ensure the file exists and is valid JSON. Check config.sample.json for reference.")
    sys.exit(1)

ORG_ID = config['ORG_ID']
TRACKING_ID = config['TRACKING_ID']
BASE_URL = config['BASE_URL']
ACCESS_TOKEN = config['ACCESS_TOKEN']
LOCALES = config['LOCALES'] if 'LOCALES' in config else None

if (not ORG_ID or not TRACKING_ID or not BASE_URL or not ACCESS_TOKEN):
    print("Please set ORG_ID, TRACKING_ID, BASE_URL, and ACCESS_TOKEN in config.json")
    sys.exit(1)

# Command-line argument parsing, --command or -c is required to specify the command
# example usage: python crud_listing_pages.py --command create
parser = argparse.ArgumentParser()
parser.add_argument('--command', '-c', required=True, help='Command to perform')
args = parser.parse_args()

LISTINGS_ENDPOINT = f'rest/organizations/{ORG_ID}/commerce/unstable/v2/listings/pages'
SCRIPT_DIRECTORY = os.path.dirname(os.path.abspath(sys.argv[0]))

BASIC_PAGE_RULE = {
    "name": "Include product cat_slug contains games-toys/trampolines-floats/trampolines",
    "filters": [
        {
            "fieldName": "cat_slug",
            "operator": "contains",
            "value": {
                "type": "array",
                "values": [
                    "games-toys/trampolines-floats/trampolines"
                ]
            }
        }
    ]
}

def handle_response(response):
    if response.status_code == 204:
        print("Delete Succeeded")
    elif response.ok:
        print(response.json())
    elif response.status_code == 412:
        print(response.text)
    else:
        print("Error in response:")
        print(response.json())
        response.raise_for_status()

def write_ids_to_file(ids):
    try:
        with open(f'{SCRIPT_DIRECTORY}/temp/ids.json', "w") as f:
            json.dump(ids, f)
    except Exception as e:
        print(f"Error writing IDs to file: {e}")

def get_all_for_tracking_id():
    items = []
    page = 0
    
    while True:
        url = BASE_URL + \
            f'{LISTINGS_ENDPOINT}?trackingId={TRACKING_ID}&page={page}&perPage=100'.format(
                org_id=ORG_ID)
        response = requests.get(
            url, headers={'Authorization': f'Bearer {ACCESS_TOKEN}'})

        if response.ok:
            data = response.json()
            items.extend(data.get('items', []))
            if page >= data.get('totalPages', 0) - 1:
                break
            page += 1
        else:
            handle_response(response)
            break
    return items

def create_from_json():
    listing_pages = []
    try:
        for filename in os.listdir(f'{SCRIPT_DIRECTORY}/data'):
            listing_page = json.load(
                open(f'{SCRIPT_DIRECTORY}/data/{filename}'))
            listing_page['trackingId'] = TRACKING_ID
            if LOCALES and len(LOCALES) > 0:
                for page in listing_page['pageRules']:
                    page['locales'] = LOCALES
            listing_pages.append(listing_page)
        url = BASE_URL + f'{LISTINGS_ENDPOINT}/bulk-create'.format(org_id=ORG_ID)

        response = requests.post(
            url, headers={'Authorization': f'Bearer {ACCESS_TOKEN}'}, json=listing_pages)

        if response.ok:
            data = response.json()
            ids = [item['id'] for item in data]
            write_ids_to_file(ids)
        handle_response(response)
    except Exception as e:
        print(f"Error while creating listing pages from JSON files: {e}")

def delete_by_ids(*ids):
    try:
        url = BASE_URL + f'{LISTINGS_ENDPOINT}/bulk-delete'.format(org_id=ORG_ID)
        response = requests.post(
            url, headers={'Authorization': f'Bearer {ACCESS_TOKEN}'}, json=ids)

        handle_response(response)
    except Exception as e:
        print(f"Error while deleting listing pages by IDs: {e}")


def delete_all_for_tracking_id():
    items = get_all_for_tracking_id()
    if items:
        ids = [item['id'] for item in items]
        delete_by_ids(*ids)

def update_all_with_same_page_rule():
    url = BASE_URL + \
        f'{LISTINGS_ENDPOINT}?trackingId={TRACKING_ID}&page=0&perPage=100'.format(
            org_id=ORG_ID)
    response = requests.get(
        url, headers={'Authorization': f'Bearer {ACCESS_TOKEN}'})

    if response.ok:
        listing_pages = response.json().get('items', [])
        for listing_page in listing_pages:
            listing_page['pageRules'] = [BASIC_PAGE_RULE]

        update_url = BASE_URL + \
            f'{LISTINGS_ENDPOINT}/bulk-update'.format(org_id=ORG_ID)
        update_response = requests.put(
            update_url, headers={'Authorization': f'Bearer {ACCESS_TOKEN}'}, json=listing_pages)
        handle_response(update_response)

    handle_response(response)

if args.command == "create":
    create_from_json()
elif args.command == "list":
    names = get_all_for_tracking_id()
    print(json.dumps(names, indent=2))
# elif args.command == "delete_all":
#     delete_all_for_tracking_id()
elif args.command == "update_all":
    update_all_with_same_page_rule()
elif args.command == "delete_by_ids":
    with open(os.path.join(SCRIPT_DIRECTORY, 'temp', 'ids.json')) as f:
        ids = json.load(f)
    delete_by_ids(*ids)
    write_ids_to_file([])
else:
    print("Unknown command")