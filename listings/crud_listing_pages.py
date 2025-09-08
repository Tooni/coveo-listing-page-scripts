#!/usr/bin/env python3
import json
import os
import requests
import sys

ORG_ID = 'barcasportsmcy01fvu'
TRACKING_ID = 'commerce'
BASE_URL = 'https://platformdev.cloud.coveo.com/'
ACCESS_TOKEN = 'jjjjjjjjj-eeee-ffff-gggg-hhhhhhhhhhhh'
LISTINGS_ENDPOINT = 'rest/organizations/{org_id}/commerce/unstable/v2/listings/pages'
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
        print("No Content")
    elif response.ok:
        print(response.json())
    elif response.status_code == 412:
        print(response.text)
    else:
        print("Error in response:")
        print(response.json())
        response.raise_for_status()


def create_from_json():
    listing_pages = []
    for filename in os.listdir(f'{SCRIPT_DIRECTORY}/data'):
        listing_page = json.load(
            open(f'{SCRIPT_DIRECTORY}/data/{filename}'))
        listing_page['trackingId'] = TRACKING_ID
        listing_pages.append(listing_page)

    url = BASE_URL + f'{LISTINGS_ENDPOINT}/bulk-create'.format(org_id=ORG_ID)
    response = requests.post(
        url, headers={'Authorization': f'Bearer {ACCESS_TOKEN}'}, json=listing_pages)

    handle_response(response)


def delete_by_ids(*ids):
    url = BASE_URL + f'{LISTINGS_ENDPOINT}/bulk-delete'.format(org_id=ORG_ID)
    response = requests.post(
        url, headers={'Authorization': f'Bearer {ACCESS_TOKEN}'}, json=ids)

    handle_response(response)


def delete_all_for_tracking_id():
    url = BASE_URL + \
        f'{LISTINGS_ENDPOINT}?trackingId={TRACKING_ID}&page=0&perPage=100'.format(
            org_id=ORG_ID)
    response = requests.get(
        url, headers={'Authorization': f'Bearer {ACCESS_TOKEN}'})

    if response.ok:
        listing_pages = response.json().get('items', [])
        ids = [listing_page['id'] for listing_page in listing_pages]

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


# create_from_json()
# delete_all_for_tracking_id()
# update_all_with_same_page_rule()
# delete_by_ids("0b54d369-4078-4611-a185-eda1fb46fcdb", "3e78bb88-28d4-47a3-8e65-e15c69e13deb")
