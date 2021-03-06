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


def test_agenda_format_day():
    """
    Tests that the function agenda_format_day(
        number_of_days_before,
        date_start,
        cfg_today,
        cfg_tomorrow,
        cfg_in_days,)
    formats properly a the string.
    """

    assert (
        main.agenda_format_day(
            0,
            "2022-13-12",
            "ajd",
            "dem",
            " j",
        )
        == "ajd"
    )
    assert (
        main.agenda_format_day(
            0,
            "2021-05-10T13:12:00",
            "ajd",
            "dem",
            " j",
        )
        == "13:12"
    )
    assert (
        main.agenda_format_day(
            1,
            "2022-13-12",
            "ajd",
            "dem",
            " j",
        )
        == "dem"
    )
    assert (
        main.agenda_format_day(
            2,
            "2022-13-12",
            "ajd",
            "dem",
            " j",
        )
        == "2 j"
    )
    assert (
        main.agenda_format_day(
            3,
            "2022-13-12",
            "ajd",
            "dem",
            " j",
        )
        == "3 j"
    )


def test_agenda_results():
    """
    Tests that the function agenda_results(data) formats correctly under all conditions.
    """

    assert not main.agenda_results(
        {"results": []},
        "2022-01-15",
        "Date",
        "Nom",
    )
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
            "Date",
            "Nom",
        )
        == [("ajd", "test 1")],
    )
    assert (
        main.agenda_results(
            {
                "results": [
                    {
                        "properties": {
                            "Date": {
                                "date": {
                                    "start": "2022-12-13T13:12:00.000+01:00",
                                    "end": None,
                                },
                            },
                            "Nom": {
                                "title": [
                                    {
                                        "plain_text": "test heure",
                                    }
                                ],
                            },
                        },
                    }
                ],
            },
            "2022-12-13",
            "Date",
            "Nom",
        )
        == [("13:12", "test heure")],
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
                                "start": "2022-12-08T13:12:00.000+01:00",
                                "end": None,
                            },
                        },
                        "Nom": {
                            "title": [
                                {
                                    "plain_text": "test heure 2",
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
                                "start": "2022-12-11",
                                "end": "2022-12-12",
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
                                    "plain_text": "test 5",
                                }
                            ],
                        },
                    },
                },
            ],
        },
        "2022-12-08",
        "Date",
        "Nom",
    ) == [
        ("ajd", "test 1"),
        ("13:12", "test heure 2"),
        ("dem", "test 3"),
        ("3 j", "test 4"),
        ("4 j", "test 5"),
    ]


def test_meds_results():
    """
    Tests that the function meds_results(data) formats correctly under all conditions.
    """

    assert not main.meds_results({"results": []})
    assert main.meds_results(
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
    ) == ["test 1 : ???1"]
    assert main.meds_results(
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
    ) == ["test 1 : ???1", "test 2 : ???2"]


def test_int_to_tuple():
    """
    Tests that the function int_to_tuple() returns tuples.
    """

    assert main.int_to_tuple(1) == (1,)
    assert main.int_to_tuple((2,)) == (2,)
    assert main.int_to_tuple((3, )) == (3,)  # fmt: skip
    assert main.int_to_tuple((4, 5)) == (4, 5)
    assert main.int_to_tuple((6,7)) == (6, 7)  # fmt: skip


def test_generate_custom_text():
    """
    Tests that the function generate_custom_text() returns good data.
    """

    assert main.generate_custom_text([], 2, 14) == ""
    assert main.generate_custom_text([["test not today", 2]], 1, 14) == ""
    assert main.generate_custom_text([["test not today tuple", (2, 3)]], 1, 14) == ""
    assert main.generate_custom_text([["test today", 2]], 2, 14) == "test today"
    assert (
        main.generate_custom_text([["test today tuple", (0, 2)]], 2, 14)
        == "test today tuple"
    )
    assert main.generate_custom_text([["odd", "test odd", 2]], 2, 14) == "test odd"
    assert (
        main.generate_custom_text([["odd", "test odd tuple", (2, 5)]], 2, 14)
        == "test odd tuple"
    )
    assert main.generate_custom_text([["even", "test even", 2]], 2, 15) == "test even"
    assert (
        main.generate_custom_text([["even", "test even tuple", (2, 6)]], 2, 15)
        == "test even tuple"
    )
    assert main.generate_custom_text([["even", "test not even", 2]], 2, 14) == ""
    assert (
        main.generate_custom_text([["even", "test not even tuple", (2, 6)]], 2, 14)
        == ""
    )
    assert main.generate_custom_text([["odd", "test not odd", 2]], 2, 15) == ""
    assert (
        main.generate_custom_text([["odd", "test not odd tuple", (2, 6)]], 2, 15) == ""
    )
    assert (
        main.generate_custom_text(
            [["test multiple lists not today", 2], ["test multiple lists", 3]], 1, 14
        )
        == ""
    )
    assert (
        main.generate_custom_text(
            [
                ["test multiple lists not today tuple", (2, 4)],
                ["test multiple lists 2", 3],
            ],
            1,
            14,
        )
        == ""
    )
    assert (
        main.generate_custom_text(
            [["test multiple lists 1", 2], ["test multiple lists 2", 1]], 1, 14
        )
        == "test multiple lists 2"
    )
    assert (
        main.generate_custom_text(
            [["test multiple lists 1 tuple", (2, 5)], ["test multiple lists 2", 1]],
            1,
            14,
        )
        == "test multiple lists 2"
    )
