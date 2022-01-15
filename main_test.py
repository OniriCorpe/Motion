#!/usr/bin/env python

"""
The test file to use with pytest.
'(motion-venv) $ python -m pytest main_test.py'
"""

import main


def test_calculate_date_delta():
    """
    Tests that the function calculate_date_delta(date_start, date_now)
    calculates correctly the number of days between two dates.
    """

    assert main.calculate_date_delta("2042-12-13", "2042-12-10") == 3
    assert main.calculate_date_delta("2014-02-13", "2014-02-14") == 1
    assert main.calculate_date_delta("1891-03-11", "1891-03-18") == 7
    assert main.calculate_date_delta("1871-03-18", "1995-02-14") == 45258


def test_agenda_results():
    """
    Tests that the function agenda_results(data) formats correctly under all conditions.
    """

    assert not main.agenda_results({"results": []}, "2022-01-15")
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
            },
            "2022-12-13",
        )
        == [("ajd", "test 1")],
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
        },
        "2022-12-08",
    ) == [
        ("ajd", "test 1"),
        ("dem", "test 2"),
        ("3 j", "test 3"),
        ("4 j", "test 4"),
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
