#!/usr/bin/env python

"""
The test file to use with pytest.
'(motion-venv) $ python -m pytest main_test.py'
"""

import main
from tests import config_test


def test_config_has_setting():
    """
    Test the function config_has_setting(config_file, config_item)
    for 1 case is valid and 1 is not.

    Using a specific config file for testing purpose, where:
    "NOTION_TOKEN" = "secret_xxx"
    "AGENDA_DB_ID" = ""
    """

    assert main.config_has_setting(config_test, "NOTION_TOKEN") is True
    assert main.config_has_setting(config_test, "AGENDA_DB_ID") is False
