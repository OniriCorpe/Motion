#!/usr/bin/env python

"""
The test file to use with pytest.
'(motion-venv) $ python -m pytest main_test.py'
"""

import main


def test_check_notion_token():
    """
    [summary]
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
