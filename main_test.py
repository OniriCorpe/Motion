#!/usr/bin/env python

"""
The test file to use with pytest.
'(motion-venv) $ python -m pytest main_test.py'
"""

import main


def test_check_notion_token():
    """
    Tests the check_notion_token(token) function with valid and invalids tokens.
    """

    assert (
        main.check_notion_token("secret_xxpZwWkuRip7eXipUC7D2fS2sCMBi3v9KFq7aT46HFQ")
        is True
    )
    assert (
        main.check_notion_token("ojmvCx5XjJUfZziJ9a3AHQKGHcLdy2zKNVfNQa5YtFZaAQSbPZ")
        is False
    )
    assert main.check_notion_token("secret_test") is False
    assert main.check_notion_token("") is False


def check_agenda_format_date():
    """
    Tests the date formatting in all conditions.
    """
    assert main.agenda_format_date("2022-12-13") is "13/12"
    assert main.agenda_format_date("2024-01-27T14:30:00") is "27/01 14:30"
    assert main.agenda_format_date(None) is None
