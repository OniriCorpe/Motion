#!/usr/bin/env python

"""
The test file to use with pytest.
'(motion-venv) $ python -m pytest main_test.py'
"""

import main


def test_check_notion_token():
    """
    Tests the check_notion_token(token) function with valid and invalids tokens.

    A valid Notion token contains "secret_" at the beginning and is 50 characters long.
    """

    assert (  # 50 chars with "secret_" at the beginning
        main.check_notion_token("secret_xxpZwWkuRip7eXipUC7D2fS2sCMBi3v9KFq7aT46HFQ")
        is True
    )
    assert (  # 50 chars with "secret_" in the middle
        main.check_notion_token("xxpZwWkuRip7eXipUsecret_C7D2fS2sCMBi3v9KFq7aT46HFQ")
        is False
    )
    assert (  # 50 chars without "secret_"
        main.check_notion_token("ojmvCx5XjJUfZziJ9a3AHQKGHcLdy2zKNVfNQa5YtFZaAQSbPZ")
        is False
    )
    assert main.check_notion_token("secret_test") is False  # 11 chars with secret
    assert main.check_notion_token("") is False  # nothing


def test_check_db_id():
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
    Tests that the function agenda_format_date(data) formats correctly under all conditions.
    """

    assert main.agenda_format_date("2022-12-13") == "13/12"
    assert main.agenda_format_date("2024-01-27T14:30:00") == "27/01 14:30"
    assert main.agenda_format_date("2022-01-09T15:00:00.000") == "09/01 15:00"
    assert main.agenda_format_date("2021-10-15T12:00:00-07:00") == "15/10 12:00"
    assert main.agenda_format_date("2022-01-09T15:00:00.000+01:00") == "09/01 15:00"
    assert main.agenda_format_date(None) is None


def test_agenda_results():
    """
    Tests that the function agenda_results(data) formats correctly under all conditions.
    """

    assert not main.agenda_results({"results": []})
    assert (
        main.agenda_results(
            {
                "results": [
                    {
                        "properties": {
                            "Date": {
                                "date": {
                                    "start": "2022-12-13",
                                    "end": None,
                                },
                            },
                            "Nb Jours": {
                                "formula": {
                                    "string": "🚨 Aujourd’hui",
                                },
                            },
                            "Nom": {
                                "title": [
                                    {
                                        "plain_text": "test 1",
                                    }
                                ],
                            },
                        },
                    }
                ],
            }
        )
        == [("13/12", "ajd", "test 1")]
    )
    assert main.agenda_results(
        {
            "results": [
                {
                    "properties": {
                        "Date": {
                            "date": {
                                "start": "2022-12-08",
                                "end": None,
                            },
                        },
                        "Nb Jours": {
                            "formula": {
                                "string": "🚨 Aujourd’hui",
                            },
                        },
                        "Nom": {
                            "title": [
                                {
                                    "plain_text": "test 1",
                                }
                            ],
                        },
                    },
                },
                {
                    "properties": {
                        "Date": {
                            "date": {
                                "start": "2022-12-09T13:12:00.000+01:00",
                                "end": None,
                            },
                        },
                        "Nb Jours": {
                            "formula": {"string": "Dans 2 jours"},
                        },
                        "Nom": {
                            "title": [
                                {
                                    "plain_text": "test 2",
                                }
                            ],
                        },
                    },
                },
                {
                    "properties": {
                        "Date": {
                            "date": {
                                "start": "2022-12-11",
                                "end": "2022-12-12",
                            },
                        },
                        "Nb Jours": {
                            "formula": {"string": "Dans 3 jours"},
                        },
                        "Nom": {
                            "title": [
                                {
                                    "plain_text": "test 3",
                                }
                            ],
                        },
                    },
                },
                {
                    "properties": {
                        "Date": {
                            "date": {
                                "start": "2022-12-12T13:00:00.000+01:00",
                                "end": "2022-12-14T12:00:00.000+01:00",
                            },
                        },
                        "Nb Jours": {
                            "formula": {"string": "Dans 5 jours"},
                        },
                        "Nom": {
                            "title": [
                                {
                                    "plain_text": "test 4",
                                }
                            ],
                        },
                    },
                },
            ],
        }
    ) == [
        ("08/12", "ajd", "test 1"),
        ("09/12 13:12", "2j", "test 2"),
        ("11/12-12/12", "3j", "test 3"),
        ("12/12 13:00-14/12 12:00", "5j", "test 4"),
    ]


def test_meds_results():
    """
    Tests that the function meds_results(data) formats correctly under all conditions.
    """

    assert not main.meds_results({"results": []})
    assert (
        main.meds_results(
            {
                "results": [
                    {
                        "properties": {
                            "NbRefill": {
                                "formula": {"number": 1},
                            },
                            "Nom": {
                                "title": [
                                    {
                                        "plain_text": "test 1",
                                    }
                                ],
                            },
                        },
                    }
                ],
            }
        )
        == ["test 1 : ≥1"]
    )
    assert (
        main.meds_results(
            {
                "results": [
                    {
                        "properties": {
                            "NbRefill": {
                                "formula": {"number": 1},
                            },
                            "Nom": {
                                "title": [
                                    {
                                        "plain_text": "test 1",
                                    }
                                ],
                            },
                        },
                    },
                    {
                        "properties": {
                            "NbRefill": {
                                "formula": {"number": 2},
                            },
                            "Nom": {
                                "title": [
                                    {
                                        "plain_text": "test 2",
                                    }
                                ],
                            },
                        },
                    },
                ]
            }
        )
        == ["test 1 : ≥1", "test 2 : ≥2"]
    )
