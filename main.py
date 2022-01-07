#!/usr/bin/env python

"""
A shitty 🦝 project to display the next events of my Notion calendar on a
mall e-ink screen (Pimoroni's Inky Phat) connected to a Raspberry Pi Zero W."
Related git repository: https://labo.emelyne.eu/oniricorpe/Motion
"""

import sys
from datetime import date, timedelta
from pprint import pprint  # debug
from notion_client import Client
import config as cfg


def current_date_timedelta():
    """
    Calculates the current date to which a certain number of days defined
    in the configuration file (NUMBER_OF_DAYS) is added.
    """

    return date.today() + timedelta(days=cfg.AGENDA["NUMBER_OF_DAYS"])


def check_notion_token(token):
    """
    Checks that the Notion token in arg is correctly filled.

    Returns:
        True: The token contains "secret_" and is 50 characters long.
        False: The token is incorrect.
    """

    if "secret_" in token and len(token) == 50:
        return True
    return False


def check_db_id(db_id):
    """
    Checks if the DB ID in argument is 32 characters long.

    Args:
        db_id (string): The Notion's database ID you want to access to.

    Returns:
        True: The DB ID seems valid.
        False: The DB ID seems incorrect.
    """

    # check that the database ID is filled
    if len(db_id) == 32:  # if the database ID is not filled
        return True
    return False


def show_current_date():
    """
    If 'SHOW_DATE' is True in the configuration file, print the current date formated.
    """

    # get and print today's date (without year)
    # if 'show_date' is true in the configuration file, display the current date
    return date.today().strftime("%d/%m")


def agenda_retrieve():
    """
    Retrieves data from the "AGENDA" database from the Notion API.
    """

    if not check_notion_token(cfg.NOTION_TOKEN):
        sys.exit(
            "Please configure your Notion token in your configuration file.\n"
            "Get your token here: https://developers.notion.com/docs/getting-started"
        )
    if not check_db_id(cfg.AGENDA["DB_ID"]):
        sys.exit(
            "Please configure your database ID (AGENDA: DB_ID) in your config file."
        )
    # query to the notion API
    return Client(auth=cfg.NOTION_TOKEN).databases.query(
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

    if not check_notion_token(cfg.NOTION_TOKEN):
        sys.exit(
            "Please configure your Notion token in your configuration file.\n"
            "Get your token here: https://developers.notion.com/docs/getting-started"
        )
    if not check_db_id(cfg.MEDS["DB_ID"]):
        sys.exit("Please configure your database ID (MEDS: DB_ID) in your config file.")
    # query to the notion API
    return Client(auth=cfg.NOTION_TOKEN).databases.query(
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
    # e.g.: "2021-05-10T12:00:00" or "2021-05-10T12:00:00.000+01:00" returns "10/05 12:00"
    if "T" in data:
        return f"{data[8:10]}/{data[5:7]} {data[11:16]}"
    # e.g.: "2021-05-10" returns "10/05"
    return f"{data[8:]}/{data[5:7]}"


def agenda_results():
    """
    Processes the outpout data of agenda_retrieve().

    Returns :
    A list of all events to come in a number of rolling days configured in the config file.
    Or a string that indicates to configure the token in the config file.
    """

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

    # print all the elements that need to be restocked
    data = meds_retrieve()["results"]
    data_processed = []
    if data:
        for item in data:
            # get item name
            name_item = item["properties"][cfg.MEDS["NAME"]]["title"][0]["plain_text"]
            # get the minimum number of units to be restocked
            nb_refill = item["properties"][cfg.MEDS["NUMBER"]]["formula"]["number"]
            data_processed.append(f"{name_item} : ≥{nb_refill}")
        return data_processed
    # there is no item to restock
    return "rien à restock"


if cfg.SHOW_DATE:
    pprint(show_current_date())
pprint(agenda_results())
pprint(meds_results())

# please note that i'm gay
