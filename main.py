#!/usr/bin/env python

import os
import notion_client
from notion_client import Client
from datetime import date
import config

# debug
from pprint import pprint


# init the notion token
if config.NOTION_TOKEN != "":  # check that the notion token id is filled in
    notion = Client(auth=config.NOTION_TOKEN)
else:  # if the notion token isn't filled in
    print("Please configure your Notion Token")


# get and print today's date without year
if config.show_date:  # if "show_date" is true in the config file, show the current date
    today = date.today()
    print(today.strftime("%d/%m"))


if config.agenda_db_id != "":  # check that the db id is filled in
    next_events = notion.databases.query(
        **{
            "database_id": config.agenda_db_id,
            "filter": {  # get only the items that come in this rolling week
                "property": "Date",  # edit with the name of the property to filter
                "date": {
                    "next_week": {},  # Date filter condition: https://developers.notion.com/reference/post-database-query#date-filter-condition
                },
            },
            "sorts": [  # sort items from nearest to farthest
                {
                    "property": "Date",  # edit with the name of the property to sort against
                    "direction": "ascending",
                    },
            ]
        }
    )
    # print all items that come in this rolling week
    for item in next_events['results']:
        # edit 'Date' with the name of the property of your database
        date = item['properties']['Date']['date']['start']
        if "T" in date:  # if hour data
            date_day = date[8:len(date)-19]  # get day
            date_month = date[5:len(date)-22]  # get month
            date_day_month = date_day + "/" + date_month + " "  # combine day and month
            date_hour = date[11:len(date)-13] + " "  # get hour
            date = date_day_month + date_hour  # combine day & month and hour
        elif "T" not in date:  # if not hour data
            date_day = date[8:]  # get day
            date_month = date[5:7]  # get month
            date = date_day + "/" + date_month + " "  # combine day and month
        nb = item['properties']['Nb Jours']['formula']['string'] + \
            " "  # edit 'Nb Jours' with the name of your database
        if "Dans" in nb:  # if 'Dans' is found in the 'nb' variable
            nb = nb[5:len(nb)-7] + " j "
        elif "Aujourd’hui" in nb:  # if 'Aujourd’hui' is found in the 'nb' variable
            nb = "ajd "
        elif "Demain" in nb:
            nb = "dem "
        # edit 'Nom' with the name of your database
        name = item['properties']['Nom']['title'][0]['plain_text']
        print(date + nb + name)
else:  # if the database ID isn't filled in
    print("Please configure your database ID 'agenda_db_id' in your config file")


if config.meds_db_id != "":  # check that the db id is filled in
    meds_refill = notion.databases.query(
        **{
            "database_id": config.meds_db_id,
            "filter": {  # get only the elements that need to be restocked
                "property": "Refill",
                "checkbox": {
                    "equals": True,
                },
            },
        }
    )
    pprint(meds_refill)
