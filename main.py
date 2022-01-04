#!/usr/bin/env python

"""
A shitty 🦝 project to display the next events of my Notion calendar on a
mall  -ink screen (Pimoroni's Inky Phat) connected to a Raspberry Pi Zero W."
Related git repository: https://labo.emelyne.eu/oniricorpe/Motion
"""

import sys
from datetime import date, timedelta
from pprint import pprint  # debug
from notion_client import Client
import peewee
import config


#  about WAL: https://sqlite.org/pragma.html#pragma_journal_mode
db = peewee.SqliteDatabase(
    # name of the DB file
    "data.db",
    # 2MB page-cache & using WAL-mode
    pragmas=(("cache_size", -1024 * 2), ("journal_mode", "wal")),
)


class BaseModel(peewee.Model):
    """The base model for the other models, adds common parameters to them"""

    class Meta:  # pylint: disable=[R0903]
        """Declaration of which database is to be used"""

        database = db


class NextEvents(BaseModel):
    """Declaration of what the database contains for NextEvents"""

    name = peewee.CharField()
    date_start = peewee.DateField()
    date_end = peewee.DateField()
    id = peewee.CharField(unique=True)


class Meds(BaseModel):
    """Declaration of what the database contains for Meds"""

    name = peewee.CharField()
    nb_refill = peewee.DecimalField()
    refill = peewee.BooleanField()
    id = peewee.CharField(unique=True)


db.connect()
db.create_tables([NextEvents, Meds])


def get_current_date():
    """Return the current date."""
    return date.today()


def current_date_timedelta(number_of_days):
    """
    TODO
    """

    # edit the number of days if you want
    return get_current_date() + timedelta(days=number_of_days)


def config_has_setting(config_file, config_item):
    """
    Arguments:
    'config_file': The configuration file to check. Default: 'config'.
    'config_item': The name of the constant to check in the configuration file.
    eg: "NOTION_TOKEN" or "AGENDA_DB_ID".

    The fonction returns a boolean:
    'True' if the constant is filled.
    'False' if the constant is empty.
    """
    return getattr(config_file, config_item) != ""


def init_notion():
    """
    Return the Notion client initialized with the token
    or exit the program if there is no token.
    """

    # check that the Notion token is filled
    if config_has_setting(config, "NOTION_TOKEN"):
        # if there is string, trying to init the Notion token with it
        return Client(auth=config.NOTION_TOKEN)
    # if the Notion token isn't filled, print error and stop the program
    sys.exit(
        "Please configure your Notion token.\n"
        "Get your token here: https://developers.notion.com/docs/getting-started"
    )


def show_current_date():
    """
    If 'SHOW_DATE' is True in the configuration file, print the current date formated.
    """

    # get and print today's date (without year)
    # if 'show_date' is true in the configuration file, display the current date
    if config.SHOW_DATE:
        print(get_current_date().strftime("%d/%m"))


show_current_date()


# check that the database ID is filled
if config_has_setting(config, "AGENDA_DB_ID"):
    next_events = init_notion().databases.query(  # query to the notion API
        **{
            "database_id": config.AGENDA_DB_ID,  # select the database to query
            "filter": {  # get only the items that come in this rolling week
                "and": [  # we want to satisfy the 2 conditions
                    {
                        "property": "Date",  # edit with the name of the property to filter
                        "date": {  # we want the current and future items
                            # Date filter condition:
                            # https://developers.notion.com/reference/post-database-query#date-filter-condition
                            "on_or_after": get_current_date().strftime("%Y-%m-%d"),
                        },
                    },
                    {
                        "property": "Date",  # edit with the name of the property to filter
                        "date": {  # we want the items in a week and before
                            # Date filter condition:
                            # https://developers.notion.com/reference/post-database-query#date-filter-condition
                            "on_or_before": current_date_timedelta(
                                config.NUMBER_OF_DAYS).strftime("%Y-%m-%d"),
                        },
                    },
                ]
            },
            "sorts": [  # sort items from nearest to farthest
                {
                    "property": "Date",  # edit with the name of the property to sort against
                    "direction": "ascending",
                },
            ],
        }
    )
    # print all items that come in this rolling week
    for item in next_events["results"]:
        # edit 'Date' with the name of the property of your database
        # get item starting date
        date_start = item["properties"]["Date"]["date"]["start"]
        if "T" in date_start:  # check if 'date' has hour data
            date_day = date_start[8:-19]  # get day
            date_month = date_start[5:-22]  # get month
            date_hour = date_start[11:-13]  # get hour
            date_start = (
                # combine day, month and hour
                f"{date_day}/{date_month} {date_hour}"
            )
        elif "T" not in date_start:  # check if 'date' has no hour data
            date_day = date_start[8:]  # get day
            date_month = date_start[5:7]  # get month
            date_start = f"{date_day}/{date_month}"  # combine day and month
        # edit 'Date' with the name of the property of your database
        # get item ending date
        date_end = item["properties"]["Date"]["date"]["end"]
        if date_end is not None:  # if there is an end date
            if "T" in date_end:  # check if 'date' has hour data
                date_day = date_end[8:-19]  # get day
                date_month = date_end[5:-22]  # get month
                date_hour = date_end[11:-13]  # get hour
                date_end = (
                    # combine day, month and hour
                    f"{date_day}/{date_month} {date_hour}"
                )
            elif "T" not in date_end:  # check if 'date' has no hour data
                date_day = date_end[8:]  # get day
                date_month = date_end[5:7]  # get month
                date_end = f"{date_day}/{date_month}"  # combine day and month
        else:  # if there is not an end date
            date_end = False
        # edit 'Nb Jours' with the name in your database
        number_of_days_before = item["properties"]["Nb Jours"]["formula"]["string"]
        # if 'Dans' is found in the 'number_of_days_before' variable
        if "Dans" in number_of_days_before:
            number_of_days_before = number_of_days_before[5:-6] + " j"
        # if 'Aujourd’hui' is found in the 'number_of_days_before' variable
        elif "Aujourd’hui" in number_of_days_before:
            number_of_days_before = "ajd"
        elif "Demain" in number_of_days_before:
            number_of_days_before = "dem"
        # edit 'Nom' with the name of your database
        name = item["properties"]["Nom"]["title"][0]["plain_text"]
        if date_end is False:  # if there is not an end date
            print(f"{date_start} {number_of_days_before} {name}")
        else:  # if there is an end date
            print(f"{date_start}-{date_end} {number_of_days_before} {name}")
else:  # if the database ID is not filled
    print("Please configure your database ID 'AGENDA_DB_ID' in your config file")

# check that the database ID is filled
if config_has_setting(config, "MEDS_DB_ID"):
    meds = init_notion().databases.query(  # query to the notion API
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
    if meds["results"]:
        for item in meds["results"]:
            # edit 'Nom' and 'NbRefill' with the name of the property of your database
            # get item name
            name_meds = item["properties"]["Nom"]["title"][0]["plain_text"]
            # get the minimum number of units to be restocked
            nb_refill = item["properties"]["NbRefill"]["formula"]["number"]
            pprint(f"{name_meds} : ≥{nb_refill}")
    else:  # there is no item to restock
        print("rien à restock")

# please note that i'm gay
