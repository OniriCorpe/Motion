#!/usr/bin/env python

import os
import notion_client
from notion_client import Client
from datetime import date, timedelta
import config

# debug
from pprint import pprint


today = date.today()


# init the notion token
# get your token: https://developers.notion.com/docs/getting-started
if config.NOTION_TOKEN != "":  # check that the notion token is filled
    notion = Client(auth=config.NOTION_TOKEN)
else:  # if the notion token isn't filled
    print("Please configure your Notion Token")


# get and print today's date (without year)
if config.show_date:  # if 'show_date' is true in the configuration file, display the current date
    print(today.strftime("%d/%m"))


if config.agenda_db_id != "":  # check that the database ID is filled
    # edit the number of days if you want
    inaweek = today + timedelta(days = 7)
    next_events = notion.databases.query(  # query to the notion API
        **{
            "database_id": config.agenda_db_id,  # select the database to query
            "filter": {  # get only the items that come in this rolling week
                "and": [  # we want to satisfy the 2 conditions
                    {
                        "property": "Date",  # edit with the name of the property to filter
                        "date": {  # we want the current and future items
                            # Date filter condition: https://developers.notion.com/reference/post-database-query#date-filter-condition
                            "on_or_after": today.strftime("%Y-%m-%d"),
                        },
                    },
                    {
                        "property": "Date",  # edit with the name of the property to filter
                        "date":   {  # we want the items in a week and before
                            # Date filter condition: https://developers.notion.com/reference/post-database-query#date-filter-condition
                            "on_or_before": inaweek.strftime("%Y-%m-%d"),
                        },
                    },
                ]
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
        # get item starting
        date_start = item['properties']['Date']['date']['start']
        if "T" in date_start:  # check if 'date' has hour data
            date_day = date_start[8:len(date)-19]  # get day
            date_month = date_start[5:len(date)-22]  # get month
            date_hour = date_start[11:len(date)-13]  # get hour
            date_start = date_day + "/" + date_month + " " + \
                date_hour  # combine day, month and hour
        elif "T" not in date_start:  # check if 'date' has no hour data
            date_day = date_start[8:]  # get day
            date_month = date_start[5:7]  # get month
            date_start = date_day + "/" + date_month  # combine day and month
        # edit 'Date' with the name of the property of your database
        date_end = item['properties']['Date']['date']['end']  # get item ending
        if date_end is not None:  # if there is an end date
            if "T" in date_end:  # check if 'date' has hour data
                date_day = date_end[8:len(date)-19]  # get day
                date_month = date_end[5:len(date)-22]  # get month
                date_hour = date_end[11:len(date)-13]  # get hour
                date_end = date_day + "/" + date_month + " " + \
                    date_hour  # combine day, month and hour
            elif "T" not in date_end:  # check if 'date' has no hour data
                date_day = date_end[8:]  # get day
                date_month = date_end[5:7]  # get month
                date_end = date_day + "/" + date_month  # combine day and month
        else:  # if there is not an end date
            date_end = False
        # edit 'Nb Jours' with the name in your database
        nb = item['properties']['Nb Jours']['formula']['string']
        if "Dans" in nb:  # if 'Dans' is found in the 'nb' variable
            nb = nb[5:len(nb)-6] + " j"
        elif "Aujourd’hui" in nb:  # if 'Aujourd’hui' is found in the 'nb' variable
            nb = "ajd"
        elif "Demain" in nb:
            nb = "dem"
        # edit 'Nom' with the name of your database
        name = item['properties']['Nom']['title'][0]['plain_text']
        if date_end is False:  # if there is not an end date
            print(date_start + " " + nb + " " + name)
        else:  # if there is an end date
            print(date_start[:2] + "-" + date_end + " " + nb + " " + name)
else:  # if the database ID is not filled
    print("Please configure your database ID 'agenda_db_id' in your config file")


if config.meds_db_id != "":  # check that the database ID is filled
    meds_refill = notion.databases.query(  # query to the notion API
        **{
            "database_id": config.meds_db_id,  # select the database to query
            "filter": {  # get only the elements that need to be restocked
                "property": "Refill",
                "checkbox": {
                    "equals": True,
                },
            },
        }
    )
    pprint(meds_refill)
