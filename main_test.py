#!/usr/bin/env python

"""
The test file to use with pytest.
'(motion-venv) $ python -m pytest main_test.py'
"""

import main


def test_check_notion_token():
    """
    Tests the check_notion_token(token) function with valid and invalids tokens.

    A valid Notion token contains "secret_" and is 50 characters long.
    """

    assert (  # 50 chars with "secret_"
        main.check_notion_token("secret_xxpZwWkuRip7eXipUC7D2fS2sCMBi3v9KFq7aT46HFQ")
        is True
    )
    assert (  # 50 chars without "secret_"
        main.check_notion_token("ojmvCx5XjJUfZziJ9a3AHQKGHcLdy2zKNVfNQa5YtFZaAQSbPZ")
        is False
    )
    assert main.check_notion_token("secret_test") is False  # 11 chars with secret
    assert main.check_notion_token("") is False  # nothing


def test_db_id():
    """
    Tests the check_db_id(db_id) function with valid and invalids IDs.

    A valid ID is 32 characters long.
    """

    assert main.check_db_id("Uz79xghKTpgsnHNXdLJpbh98ey6rL6kx") is True  # 32
    assert main.check_db_id("Uz79xghKTpgsnHNXdLJpbh98ey6rL6kxx") is False  # 34
    assert main.check_db_id("Uz79xghKTpgsnHNXdLJpbh98ey6rL6") is False  # 30
    assert main.check_db_id("") is False  # 0


def test_agenda_format_date():
    """
    Tests the date formatting in all conditions.
    """

    assert main.agenda_format_date("2022-12-13") == "13/12"
    assert main.agenda_format_date("2024-01-27T14:30:00") == "27/01 14:30"
    assert main.agenda_format_date("2022-01-09T15:00:00.000") == "09/01 15:00"
    assert main.agenda_format_date("2021-10-15T12:00:00-07:00") == "15/10 12:00"
    assert main.agenda_format_date("2022-01-09T15:00:00.000+01:00") == "09/01 15:00"
    assert main.agenda_format_date(None) is None
