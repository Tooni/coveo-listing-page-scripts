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

LISTINGS_ENDPOINT = f'rest/organizations/{ORG_ID}/commerce/v2/listings/pages'
SCRIPT_DIRECTORY = os.path.dirname(os.path.abspath(sys.argv[0]))
UPDATE_PATH = 'update-data/listings.json'

def handle_response(response):
    """
    Handle HTTP response and print appropriate messages based on status code.
    
    Args:
        response: HTTP response object from requests
    """
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

def write_to_file(content, filepath):
    """
    Write JSON content to a file with proper formatting.
    
    Args:
        content: Data to write to file (will be JSON serialized)
        filepath: Relative path from script directory where to write the file
    """
    try:
        with open(f'{SCRIPT_DIRECTORY}/{filepath}', "w") as f:
            json.dump(content, f, indent=4)
    except Exception as e:
        print(f"Error writing to file {filepath}: {e}")

def get_all_for_tracking_id():
    """
    Retrieve all listing pages for the configured tracking ID.
    Handles pagination to get all results across multiple pages.
    
    Returns:
        list: All listing page items found for the tracking ID
    """
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
    """
    Create listing pages from JSON files in the create-data directory.
    Reads all JSON files, adds tracking ID and locales, then bulk creates them.
    Saves the created listings to update-data/listings.json for future reference.
    """
    listing_pages = []
    try:
        for filename in os.listdir(f'{SCRIPT_DIRECTORY}/create-data'):
            listing_page = json.load(
                open(f'{SCRIPT_DIRECTORY}/create-data/{filename}'))
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
            write_to_file(data, UPDATE_PATH)
        handle_response(response)
    except Exception as e:
        print(f"Error while creating listing pages from JSON files: {e}")

def delete_by_ids(*ids):
    """
    Delete listing pages by their IDs using bulk delete endpoint.
    
    Args:
        *ids: Variable number of listing page IDs to delete
    """
    try:
        if (ids is None or len(ids) == 0):
            print("No IDs provided for deletion.")
            return
        url = BASE_URL + f'{LISTINGS_ENDPOINT}/bulk-delete'.format(org_id=ORG_ID)
        response = requests.post(
            url, headers={'Authorization': f'Bearer {ACCESS_TOKEN}'}, json=ids)

        handle_response(response)
    except Exception as e:
        print(f"Error while deleting listing pages by IDs: {e}")


def delete_all_for_tracking_id():
    """
    Delete all listing pages associated with the configured tracking ID.
    First retrieves all pages, then deletes them by their IDs.
    """
    items = get_all_for_tracking_id()
    if items and len(items) > 0:
        ids = [item['id'] for item in items]
        delete_by_ids(*ids)
    else:
        print("No listings found for deletion.")

def update_from_json():
    """
    Update listing pages using data from update-data/listings.json.
    Reads the saved listings file and performs bulk update operation.
    """
    listing_pages = json.load(
                open(f'{SCRIPT_DIRECTORY}/{UPDATE_PATH}'))

    if not listing_pages or len(listing_pages) == 0:
        print(f"No listings found in {UPDATE_PATH} for update.")
        return
    update_url = BASE_URL + \
        f'{LISTINGS_ENDPOINT}/bulk-update'.format(org_id=ORG_ID)
    update_response = requests.put(
        update_url, headers={'Authorization': f'Bearer {ACCESS_TOKEN}'}, json=listing_pages)
    handle_response(update_response)

if args.command == "list":
    names = get_all_for_tracking_id()
    print(json.dumps(names, indent=2))
elif args.command == "create":
    create_from_json()
elif args.command == "update":
    update_from_json()
elif args.command == "delete_all":
    delete_all_for_tracking_id()
    write_to_file([], UPDATE_PATH)
elif args.command == "delete_by_ids":
    with open(os.path.join(SCRIPT_DIRECTORY, UPDATE_PATH)) as f:
        items = json.load(f)
    ids = [item['id'] for item in items]
    delete_by_ids(*ids)
    write_to_file([], UPDATE_PATH)
else:
    print("Unknown command\n")
    print("Available commands are: create, list, update_all, delete_all, delete_by_ids")