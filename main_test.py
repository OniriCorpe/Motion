#!/usr/bin/env python

"""
The test file to use with pytest.
'(motion-venv) $ python -m pytest main_test.py'
"""

import main


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
        == [("ajd", "test 1")]
    )
    assert main.agenda_results(
        {
            "results": [
                {
                    "properties": {
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
        ("ajd", "test 1"),
        ("2 j", "test 2"),
        ("3 j", "test 3"),
        ("5 j", "test 4"),
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
