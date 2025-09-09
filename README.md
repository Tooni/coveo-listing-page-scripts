The `crud_listing_pages.py` will be used to create/update/delete listing pages using the new public endpoints

1) Please clone `config.sample.json` file into `config.json` and populate the following parameters: ORG_ID, TRACKING_ID, ACCESS_TOKEN, BASE_URL, LOCALES.

    *LOCALES paramter is optional*

2) To run the script you have to provide the command name using the **--command** or **-c** parameter. 

    Example: `python3 crud_listing_pages.py --command create`

---------
Here is the list of supported commands:
- **create**: creates listing pages (bulk)
- **update_all**: updates listing pages with 1 rule (bulk)
- **delete_all**: deletes all listing pages for a specific tracking id
- **delete_by_id**: deletes listing pages using provided IDs in temp/ids.json file