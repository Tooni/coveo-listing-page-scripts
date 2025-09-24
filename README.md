Copied from the commerce-tools repo to make it publicly available: https://github.com/coveo-platform/commerce-tools/pull/156 

The `crud_listing_pages.py` will be used to create/read/update/delete listing pages using the new public endpoints

1) Please clone `config.sample.json` file into `config.json` and populate the following parameters: ORG_ID, TRACKING_ID, ACCESS_TOKEN, BASE_URL, and LOCALES.

    *LOCALES parameter is optional*

2) To run the script you have to provide the command name using the **--command** or **-c** parameter. 

    Example: `python3 crud_listing_pages.py --command create`

---------
Here is the list of supported commands:
- **list**: list existing listing pages for a specific Tracking ID
- **create**: creates listing pages from json files under create-data folder (bulk)
- **update**: updates listing pages from json files under update-data folder (bulk)
- **delete_all**: deletes all listing pages for a specific Tracking ID
- **delete_by_ids**: deletes listing pages using provided IDs in update-data/listings.json file
