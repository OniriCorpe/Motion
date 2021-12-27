#!/usr/bin/env python

"""
A shitty 🦝 project to display the next events of my Notion calendar on a
mall  -ink screen (Pimoroni's Inky Phat) connected to a Raspberry Pi Zero W."
Related git repository: https://labo.emelyne.eu/oniricorpe/Motion
"""

from datetime import date, timedelta
from pprint import pprint  # debug
from notion_client import Client
from peewee import *
import config


today = date.today()

#  about WAL: https://sqlite.org/pragma.html#pragma_journal_mode
db = SqliteDatabase('data.db', pragmas=(
    ('cache_size', -1024 * 2),  # 2MB page-cache.
    ('journal_mode', 'wal')))  # Use WAL-mode


class BaseModel(Model):
    class Meta:
        database = db


class next_events(BaseModel):
    name = CharField()
    date_start = DateField()
    date_end = DateField()
    id = CharField(unique=True)


class meds(BaseModel):
    name = CharField()
    nb_refill = DecimalField()
    refill = BooleanField()
    id = CharField(unique=True)


db.connect()
db.create_tables([next_events, meds])


# init the notion token
# get your token: https://developers.notion.com/docs/getting-started
if config.NOTION_TOKEN != "":  # check that the notion token is filled
    notion = Client(auth=config.NOTION_TOKEN)
else:  # if the notion token isn't filled
    print("Please configure your Notion Token")


# get and print today's date (without year)
if config.SHOW_DATE:  # if 'show_date' is true in the configuration file, display the current date
    print(today.strftime("%d/%m"))


if config.AGENDA_DB_ID != "":  # check that the database ID is filled
    # edit the number of days if you want
    inaweek = today + timedelta(days = 7)
    next_events = notion.databases.query(  # query to the notion API
        **{
            "database_id": config.AGENDA_DB_ID,  # select the database to query
            "filter": {  # get only the items that come in this rolling week
                "and": [  # we want to satisfy the 2 conditions
                    {
                        "property": "Date",  # edit with the name of the property to filter
                        "date": {  # we want the current and future items
                            # Date filter condition:
                            # https://developers.notion.com/reference/post-database-query#date-filter-condition
                            "on_or_after": today.strftime("%Y-%m-%d"),
                        },
                    },
                    {
                        "property": "Date",  # edit with the name of the property to filter
                        "date":   {  # we want the items in a week and before
                            # Date filter condition:
                            # https://developers.notion.com/reference/post-database-query#date-filter-condition
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
        # get item starting date
        date_start = item['properties']['Date']['date']['start']
        if "T" in date_start:  # check if 'date' has hour data
            date_day = date_start[8:-19]  # get day
            date_month = date_start[5:-22]  # get month
            date_hour = date_start[11:-13]  # get hour
            date_start = date_day + "/" + date_month + " " + \
                date_hour  # combine day, month and hour
        elif "T" not in date_start:  # check if 'date' has no hour data
            date_day = date_start[8:]  # get day
            date_month = date_start[5:7]  # get month
            date_start = date_day + "/" + date_month  # combine day and month
        # edit 'Date' with the name of the property of your database
        # get item ending date
        date_end = item['properties']['Date']['date']['end']
        if date_end is not None:  # if there is an end date
            if "T" in date_end:  # check if 'date' has hour data
                date_day = date_end[8:-19]  # get day
                date_month = date_end[5:-22]  # get month
                date_hour = date_end[11:-13]  # get hour
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
            nb = nb[5:-6] + " j"
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


if config.MEDS_DB_ID != "":  # check that the database ID is filled
    meds = notion.databases.query(  # query to the notion API
        **{
            "database_id": config.MEDS_DB_ID,  # select the database to query
            "filter": {  # get only the elements that need to be restocked
                "property": "Refill",
                "checkbox": {
                    "equals": True,
                },
            },
        }
    )
    # print all the elements that need to be restocked
    if meds['results']:
        for item in meds['results']:
            # edit 'Nom' and 'NbRefill' with the name of the property of your database
            # get item name
            name_meds = item['properties']['Nom']['title'][0]['plain_text']
            # get the minimum number of units to be restocked
            nb_refill = item['properties']['NbRefill']['formula']['number']
            refill = True
            pprint(name_meds + " : ≥" + str(nb_refill))
    else:  # there is no item to restock
        refill = False
        print("rien à restock")

# please note that i'm gay
