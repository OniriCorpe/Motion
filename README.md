# Motion

A shitty 🦝 project to display the next events of my [Notion](https://www.notion.so/) calendar on a small e-ink screen ([Pimoroni's Inky Phat](https://shop.pimoroni.com/products/inky-phat)) connected to a [Raspberry Pi Zero W](https://www.raspberrypi.com/products/raspberry-pi-zero-w/).

## Usage

Copy the configuration example file and rename it to 'config.py'.  
Configure your [Notion Token](https://developers.notion.com/docs/getting-started) and your [database ID](https://developers.notion.com/docs/getting-started#step-2-share-a-database-with-your-integration).  
Please note that this program is designed for [this agenda template](https://xaanaa.notion.site/Agenda-template-bc1b0b00787e44a18218cde30f71f524). You can freely adapt the code to your usage.

Optionally, you can activate the display of the current date and the display of an indicator that means that at least one of the elements of [this medical inventory template](https://xaanaa.notion.site/Inventaire-m-dical-template-4b72c6408bbd41878661705e2d9d5b37) is to be re-stocked.

## Installation

For good practices and safety, please use a [venv](https://docs.python.org/3/library/venv.html).
> $ python3 -m venv motion-venv  
> $ source activate motion-venv/bin/activate

Then install the dependencies:
> (motion-venv) $ pip install -r requirements-dev.txt  # For dev environment

or

> (motion-venv) $ pip install -r requirements-rpi.txt  # For prod environment

You can execute the program after having activated your venv:
> $ source activate motion-venv/bin/activate  
> (motion-venv) $ python main.py

The command to put in your crontab:
> cd /srv/Motion/ && motion-venv/bin/python3.9 main.py
