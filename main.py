#!/usr/bin/env python

"""
A shitty 🦝 project to display the next events of my Notion calendar on a
mall e-ink screen (Pimoroni's Inky Phat) connected to a Raspberry Pi Zero W."
Related git repository: https://labo.emelyne.eu/oniricorpe/Motion
"""

import sys
from datetime import date, datetime, timedelta
from PIL import Image, ImageDraw, ImageFont
from inky.auto import auto
from notion_client import Client, APIErrorCode, APIResponseError
import config as cfg


def agenda_retrieve():
    """
    Retrieves data from the "AGENDA" database from the Notion API.
    """

    # query to the notion API
    try:
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
    except APIResponseError as error:
        if error.code == APIErrorCode.Unauthorized:
            sys.exit(
                "API Error: Unauthorized\n"
                "Please configure a proper Notion token in your configuration file.\n"
                "Get your token here: https://developers.notion.com/docs/getting-started"
            )
        elif error.code == APIErrorCode.ObjectNotFound:
            sys.exit(
                "API Error: ObjectNotFound\n"
                "Given the bearer token used, the resource does not exist.\n"
                "This error can also indicate that the resource has not been"
                "shared with owner of the bearer token."
            )
        elif error.code == APIErrorCode.RestrictedResource:
            sys.exit(
                "API Error: RestrictedResource\n"
                "Given the bearer token used, the client doesn't have"
                "permission to perform this operation."
            )
        else:
            sys.exit("API Error: Please check your agenda database token.")


def meds_retrieve():
    """
    Retrieves data from the "MEDS" database from the Notion API.
    """

    # query to the notion API
    try:
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
    except APIResponseError as error:
        if error.code == APIErrorCode.Unauthorized:
            sys.exit(
                "API Error: Unauthorized\n"
                "Please configure a proper Notion token in your configuration file.\n"
                "Get your token here: https://developers.notion.com/docs/getting-started"
            )
        elif error.code == APIErrorCode.ObjectNotFound:
            sys.exit(
                "API Error: ObjectNotFound\n"
                "Given the bearer token used, the resource does not exist.\n"
                "This error can also indicate that the resource has not been"
                "shared with owner of the bearer token."
            )
        elif error.code == APIErrorCode.RestrictedResource:
            sys.exit(
                "API Error: RestrictedResource\n"
                "Given the bearer token used, the client doesn't have"
                "permission to perform this operation."
            )
        else:
            return {"results": []}


def calculate_date_delta(date_start, date_now):
    """
    Calculates the number of days between two dates.

    Args:
        date_start (string) : The date of the event from which to subtract the other date.
        date_now (string): The current date to be subtracted to the other date.
        The two arguments must be formatted as follows: "%Y-%m-%d"

    Returns:
        int: The number of days between the two dates.
    """
    return abs(
        date(int(date_start[:4]), int(date_start[5:7]), int(date_start[8:10]))
        - date(int(date_now[:4]), int(date_now[5:7]), int(date_now[8:10]))
    ).days


def agenda_results(data, date_now):
    """
    Processes the outpout data of agenda_retrieve().

    Returns :
    A list of all events to come in a number of rolling days configured in the config file.
    """

    data_processed = []
    for item in data["results"]:
        # get the event starting date
        date_start = item["properties"][cfg.AGENDA["DATE"]]["date"]["start"]
        # calculate the remaining days before the event
        number_of_days_before = calculate_date_delta(date_start, date_now)
        # format the remaining days before the event
        if number_of_days_before == 0:
            number_of_days_before = cfg.AGENDA["TODAY"]
        elif number_of_days_before == 1:
            number_of_days_before = cfg.AGENDA["TOMORROW"]
        else:
            in_days = cfg.AGENDA["IN_DAYS"]
            number_of_days_before = f"{number_of_days_before}{in_days}"
        # get the event name
        name = item["properties"][cfg.AGENDA["NAME"]]["title"][0]["plain_text"]
        # add the data to the list
        data_processed.append((number_of_days_before, name))
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
    Generates an image with the information of the agenda, the current date, etc.

    Returns:
        image: Properly formatted image.
    """

    if cfg.OPTIONAL["FONT"]:
        fnt = ImageFont.truetype(cfg.OPTIONAL["FONT"], 13)
    else:
        fnt = ImageFont.load_default()
    # initiate a B&W image
    image = Image.new("P", (250, 122), "white")
    generate = ImageDraw.Draw(image)
    date_now = datetime.now().strftime("%Y-%m-%d")
    for iteration, item in enumerate(agenda_results(agenda_retrieve(), date_now)):
        if iteration < 6:
            # the time before the event
            generate.text(
                (35, 3 + iteration * 16), item[0], font=fnt, fill="black", anchor="ra"
            )
            # the name of the event
            generate.text(
                (40, 3 + iteration * 16), item[1], font=fnt, fill="black", anchor="la"
            )
            # if there is an event today, color the border of the screen in red
            if cfg.AGENDA["TODAY"] in item[0]:
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
        if meds_results(meds_retrieve()):
            generate.text((240, 100), "restock", font=fnt, fill="black", anchor="ra")
    # return generated image
    if cfg.OPTIONAL["FLIP"]:
        return image.transpose(Image.ROTATE_180)
    return image


display = auto()
display.set_image(generate_image())
display.show()
# generate_image().save("/mnt/c/Users/Emelyne/Downloads/test.png")

# please note that i'm gay
