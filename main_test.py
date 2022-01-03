#!/usr/bin/env python

import main
from tests import config_test

def test_config_has_setting():
    assert main.config_has_setting(config_test, "AGENDA_DB_ID") == False
    assert main.config_has_setting(config_test, "NOTION_TOKEN") == True
