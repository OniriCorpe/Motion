#!/usr/bin/env python

import main
from tests import config

def test_config_has_setting():
    assert main.config_has_setting(config, "AGENDA_DB_ID") == False
    assert main.config_has_setting(config, "NOTION_TOKEN") == True
