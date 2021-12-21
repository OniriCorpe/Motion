#!/usr/bin/env python

import os
import notion_client
from notion_client import Client
from datetime import date
import config

# debug
from pprint import pprint


# init the notion token
if config.NOTION_TOKEN != "": # check that the notion token id is filled in
    notion = Client(auth=config.NOTION_TOKEN)
else: # if the notion token isn't filled in
    print("Please configure your Notion Token")


# get and print today's date without year
if config.show_date: # if "show_date" is true in the config file, show the current date
    today = date.today()
    print (today.strftime("%d/%m"))


if config.agenda_db_id != "": # check that the db id is filled in
    next_events = notion.databases.query(
        **{
            "database_id": config.agenda_db_id,
            "filter": { # get only the items that come in this rolling week
                "property": "Date", # edit with the name of the property to filter
                "date": {
                    "next_week": {}, # Date filter condition: https://developers.notion.com/reference/post-database-query#date-filter-condition
                },
            },
            "sorts": [ # sort items from nearest to farthest
            {
            "property": "Date", # edit with the name of the property to sort against
            "direction": "ascending",
            },
            ]
        }
    )
    # print all items that come in this rolling week
    for item in next_events['results']:
        date = item['properties']['Date']['date']['start'] + " " # edit 'Date' with the name of the property of your database
        if date.find("T") != -1:
            date = date[5:len(date)-14] + " "
        elif date.find("T") == -1:
            date = date[5:]
        nb = item['properties']['Nb Jours']['formula']['string'] + " " # edit 'Nb Jours' with the name of your database
        if nb.find("Dans") == 0: # if 'Dans' is found in the 'nb' variable
            nb = nb[5:len(nb)-7] + " j "
        elif nb.find("🚨 Aujourd’hui") == 0: # if 'Aujourd’hui' is found in the 'nb' variable
            nb = "ajd "
        elif nb.find("⚠️ Demain") == 0:
            nb = "dem "
        name = item['properties']['Nom']['title'][0]['plain_text'] # edit 'Nom' with the name of your database
        print(date + nb + name)
else: # if the db id isn't filled in
    print("Please configure your database ID 'agenda_db_id' in your config file")


if config.meds_db_id != "": # check that the db id is filled in
    meds_refill = notion.databases.query(
        **{
            "database_id": config.meds_db_id,
            "filter": { # get only the elements that need to be restocked
                "property": "Refill",
                "checkbox": {
                    "equals": True,
                },
            },
        }
    )
    pprint(meds_refill)
