#!/usr/bin/env python

"""
A shitty 🦝 project to display the next events of my Notion calendar on a
mall e-ink screen (Pimoroni's Inky Phat) connected to a Raspberry Pi Zero W."
Related git repository: https://labo.emelyne.eu/oniricorpe/Motion
"""

import sys
from datetime import date, timedelta
from PIL import Image, ImageDraw, ImageFont
from inky.auto import auto
from notion_client import Client
import config as cfg


def check_notion_token(token):
    """
    Checks that the Notion token in argument is valid.

    Returns:
        True: The token starts with "secret_" and is 50 characters long.
        False: The token does not start with "secret_" or isn't 50 characters long.
    """

    if token.startswith("secret_") and len(token) == 50:
        return True
    return False


def check_db_id(db_id):
    """
    Checks if the database ID in argument is valid.

    Returns:
        True: The DB ID is 32 characters long.
        False: The DB ID isn't 32 characters long.
    """

    if len(db_id) == 32:
        return True
    return False


def agenda_retrieve():
    """
    Retrieves data from the "AGENDA" database from the Notion API.
    """

    # query to the notion API
    return Client(auth=cfg.NOTION_TOKEN).databases.query(
        **{
            # select the database to query
            "database_id": cfg.AGENDA["DB_ID"],
            # get only the items that come in this rolling week
            "filter": {
                # we want to satisfy the 2 conditions ("on_or_after" & "on_or_before")
                "and": [
                    {
                        "property": cfg.AGENDA["DATE"],
                        # we want the current and future items
                        "date": {
                            # Date filter condition:
                            # https://developers.notion.com/reference/post-database-query#date-filter-condition
                            # get today's date then format it correctly
                            "on_or_after": date.today().strftime("%Y-%m-%d"),
                        },
                    },
                    {
                        "property": cfg.AGENDA["DATE"],
                        # we want the items in a week and before
                        "date": {
                            # Date filter condition:
                            # https://developers.notion.com/reference/post-database-query#date-filter-condition
                            "on_or_before": (
                                # add the number of days defined in the
                                # configuration file to the today's date
                                date.today()
                                + timedelta(days=cfg.AGENDA["NUMBER_OF_DAYS"])
                                # then format it correctly
                            ).strftime("%Y-%m-%d"),
                        },
                    },
                ]
            },
            # sort items from nearest to farthest
            "sorts": [
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

    # query to the notion API
    return Client(auth=cfg.NOTION_TOKEN).databases.query(
        **{
            # select the database to query
            "database_id": cfg.MEDS["DB_ID"],
            # get only the elements that need to be restocked (for which the box is ticked)
            "filter": {
                "property": cfg.MEDS["REFILL"],
                "checkbox": {
                    "equals": True,
                },
            },
            # sort items in alphabetical order
            "sorts": [
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


def agenda_results(data):
    """
    Processes the outpout data of agenda_retrieve().

    Returns :
    A list of all events to come in a number of rolling days configured in the config file.
    """

    data_processed = []
    for item in data["results"]:
        # get the event starting date
        date_start = agenda_format_date(
            item["properties"][cfg.AGENDA["DATE"]]["date"]["start"]
        )
        # get the event ending date
        date_end = agenda_format_date(
            item["properties"][cfg.AGENDA["DATE"]]["date"]["end"]
        )
        # get the remaining time before the event
        number_of_days_before = item["properties"][cfg.AGENDA["REMAINING_DAYS"]][
            "formula"
        ]["string"]
        if cfg.AGENDA["FILTER_TODAY"] in number_of_days_before:
            number_of_days_before = cfg.AGENDA["TODAY"]
        elif cfg.AGENDA["FILTER_TOMORROW"] in number_of_days_before:
            number_of_days_before = cfg.AGENDA["TOMORROW"]
        else:
            in_days = cfg.AGENDA["IN_DAYS"]
            number_of_days_before = f"{number_of_days_before[5:-6]}{in_days}"
        # get the event name
        name = item["properties"][cfg.AGENDA["NAME"]]["title"][0]["plain_text"]
        # if there is no end date
        if date_end is None:
            data_processed.append((date_start, number_of_days_before, name))
        # if there is an end date
        else:
            data_processed.append(
                (f"{date_start}-{date_end}", number_of_days_before, name)
            )
    return data_processed


def meds_results(data):
    """
    Processes the outpout data of meds_retrieve().

    Returns :
    A list of all items to be restocked properly formatted.
    """

    data_processed = []
    for item in data["results"]:
        # get the item name
        name_item = item["properties"][cfg.MEDS["NAME"]]["title"][0]["plain_text"]
        # get the minimum number of units to be restocked
        nb_refill = item["properties"][cfg.MEDS["NUMBER"]]["formula"]["number"]
        # format a string and add it to the list
        data_processed.append(f"{name_item} : ≥{nb_refill}")
    return data_processed


def generate_image():
    """
    [summary]

    Args:
        data_img ([type]): [description]

    Returns:
        [type]: [description]
    """

    if cfg.OPTIONAL["FONT"]:
        fnt = ImageFont.truetype(cfg.OPTIONAL["FONT"], 13)
    else:
        fnt = ImageFont.load_default()
    # initiate a B&W image
    image = Image.new("P", (250, 122), "white")
    generate = ImageDraw.Draw(image)
    for iteration, item in enumerate(agenda_results(agenda_retrieve())):
        if iteration < 6:
            # the time before the event
            generate.text(
                (35, 3 + iteration * 16), item[1], font=fnt, fill="black", anchor="ra"
            )
            # the name of the event
            generate.text(
                (40, 3 + iteration * 16), item[2], font=fnt, fill="black", anchor="la"
            )
            # if there is an event today, color the border of the screen in red
            if cfg.AGENDA["TODAY"] in item[1]:
                display.set_border(display.RED)
        # show the current date
        if cfg.OPTIONAL["SHOW_DATE"]:
            generate.text(
                (10, 100),
                date.today().strftime("%d/%m"),
                font=fnt,
                fill="black",
                anchor="la",
            )
        # show a custom text on a (or multiple) custom day of the week
        for day in cfg.OPTIONAL["DAY"]:
            if date.today().weekday() == day:
                generate.text(
                    (125, 100),
                    cfg.OPTIONAL["CUSTOM_TEXT"],
                    font=fnt,
                    fill="black",
                    anchor="ma",
                )
        # show if something need to be restocked
        if check_db_id(cfg.MEDS["DB_ID"]) and meds_results(meds_retrieve()):
            generate.text((240, 100), "restock", font=fnt, fill="black", anchor="ra")
    # return generated image
    if cfg.OPTIONAL["FLIP"]:
        return image.transpose(Image.ROTATE_180)
    return image


if not check_notion_token(cfg.NOTION_TOKEN):
    sys.exit(
        "Please configure your Notion token in your configuration file.\n"
        "Get your token here: https://developers.notion.com/docs/getting-started"
    )
else:
    if check_db_id(cfg.AGENDA["DB_ID"]):
        display = auto()
        display.set_image(generate_image())
        display.show()
    else:
        sys.exit(
            "Please configure your database ID (AGENDA: DB_ID) in your config file."
        )

# please note that i'm gay
