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
import config as cfg


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


def current_date_timedelta():
    """
    Calculates the current date to which a certain number of days defined
    in the configuration file (NUMBER_OF_DAYS) is added.
    """

    return date.today() + timedelta(days=cfg.AGENDA["NUMBER_OF_DAYS"])


def init_notion_token():
    """
    Return the Notion client initialized with the token
    or exit the program if there is no token.
    """

    # check that the Notion token is filled
    if "secret_" in cfg.NOTION_TOKEN and len(cfg.NOTION_TOKEN) == 50:
        # if there is string, trying to init the Notion token with it
        return Client(auth=cfg.NOTION_TOKEN)
    # if the Notion token isn't filled, print error and stop the program
    sys.exit(
        "Please configure your Notion token in your configuration file.\n"
        "Get your token here: https://developers.notion.com/docs/getting-started"
    )


def show_current_date():
    """
    If 'SHOW_DATE' is True in the configuration file, print the current date formated.
    """

    # get and print today's date (without year)
    # if 'show_date' is true in the configuration file, display the current date
    if cfg.SHOW_DATE:
        print(date.today().strftime("%d/%m"))


def agenda_retrieve():
    """
    Retrieves data from the "AGENDA" database from the Notion API.
    """

    return init_notion_token().databases.query(  # query to the notion API
        **{
            "database_id": cfg.AGENDA["DB_ID"],  # select the database to query
            "filter": {  # get only the items that come in this rolling week
                "and": [  # we want to satisfy the 2 conditions
                    {
                        "property": cfg.AGENDA["DATE"],
                        "date": {  # we want the current and future items
                            # Date filter condition:
                            # https://developers.notion.com/reference/post-database-query#date-filter-condition
                            "on_or_after": date.today().strftime("%Y-%m-%d"),
                        },
                    },
                    {
                        "property": cfg.AGENDA["DATE"],
                        "date": {  # we want the items in a week and before
                            # Date filter condition:
                            # https://developers.notion.com/reference/post-database-query#date-filter-condition
                            "on_or_before": current_date_timedelta().strftime(
                                "%Y-%m-%d"
                            ),
                        },
                    },
                ]
            },
            "sorts": [  # sort items from nearest to farthest
                {
                    "property": cfg.AGENDA["DATE"],
                    "direction": "ascending",
                },
            ],
        }
    )


def meds_retrieve():
    """
    Retrieves data from the "MEDS" database from the Notion API.
    """

    return init_notion_token().databases.query(  # query to the notion API
        **{
            "database_id": cfg.MEDS["DB_ID"],  # select the database to query
            "filter": {  # get only the elements that need to be restocked
                "property": cfg.MEDS["REFILL"],
                "checkbox": {
                    "equals": True,
                },
            },
            "sorts": [  # sort items in alphabetical order
                {
                    "property": cfg.MEDS["NAME"],
                    "direction": "ascending",
                },
            ],
        }
    )


def agenda_format_date(data):
    """
    Processes a date string to format it.

    e.g. of input: "2021-05-10" or "2021-05-10T12:00:00" or "None"
    e.g. of output: "10/05" or "10/05 12:00" or "None"
    """
    if data is None:
        return None
    # check if 'date' has hour data
    if "T" in data:
        # combine day, month and hour
        return f"{data[8:-19]}/{data[5:-22]} {data[11:-13]}"
    # combine day and month
    return f"{data[8:]}/{data[5:7]}"


def agenda_results():
    """
    Processes the outpout data of agenda_retrieve().

    Returns :
    A list of all events to come in a number of rolling days configured in the config file.
    Or a string that indicates to configure the token in the config file.
    """

    # check that the database ID is filled
    if len(cfg.AGENDA["DB_ID"]) != 32:  # if the database ID is not filled
        return "Please configure your database ID 'AGENDA: DB_ID' in your config file"
    data = agenda_retrieve()["results"]
    data_processed = []
    # print all items that come in this rolling week
    for item in data:
        # get item starting date
        date_start = agenda_format_date(
            item["properties"][cfg.AGENDA["DATE"]]["date"]["start"]
        )
        # get item ending date
        date_end = agenda_format_date(
            item["properties"][cfg.AGENDA["DATE"]]["date"]["end"]
        )
        number_of_days_before = item["properties"][cfg.AGENDA["REMAINING_DAYS"]][
            "formula"
        ]["string"]
        # if 'Aujourd’hui' is found in the 'number_of_days_before' variable
        if cfg.AGENDA["FILTER_TODAY"] in number_of_days_before:
            number_of_days_before = cfg.AGENDA["TODAY"]
        elif cfg.AGENDA["FILTER_TOMORROW"] in number_of_days_before:
            number_of_days_before = cfg.AGENDA["TOMORROW"]
        else:
            in_days = cfg.AGENDA["IN_DAYS"]
            number_of_days_before = f"{number_of_days_before[5:-6]}{in_days}"
        name = item["properties"][cfg.AGENDA["NAME"]]["title"][0]["plain_text"]
        if date_end is None:  # if there is not an end date
            data_processed.append((date_start, number_of_days_before, name))
        else:  # if there is an end date
            data_processed.append(
                (f"{date_start}-{date_end}", number_of_days_before, name)
            )
    return data_processed


def meds_results():
    """
    Processes the outpout data of meds_retrieve().

    Returns :
    A list of all items to be restocked properly formatted.
    Or a string that indicates that nothing is to be restocked.
    Or a string that indicates to configure the token in the config file.
    """

    # check that the database ID is filled
    if len(cfg.MEDS["DB_ID"]) == 32:
        # print all the elements that need to be restocked
        data = meds_retrieve()["results"]
        data_processed = []
        if data:
            for item in data:
                # get item name
                name_meds = item["properties"][cfg.MEDS["NAME"]]["title"][0][
                    "plain_text"
                ]
                # get the minimum number of units to be restocked
                nb_refill = item["properties"][cfg.MEDS["NUMBER"]]["formula"]["number"]
                data_processed.append(f"{name_meds} : ≥{nb_refill}")
            return data_processed
        # there is no item to restock
        return "rien à restock"
    return "Please configure your database ID 'MEDS: DB_ID' in your config file"


show_current_date()
pprint(agenda_results())
pprint(meds_results())

# please note that i'm gay
