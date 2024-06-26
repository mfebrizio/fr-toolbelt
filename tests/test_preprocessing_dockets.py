import json
from pathlib import Path

from fr_toolbelt.preprocessing import (
    RegsDotGovData, 
    Dockets, 
    )


# TEST OBJECTS AND UTILS #


TESTS_PATH = Path(__file__).parent

with open(TESTS_PATH / "test_documents.json", "r", encoding="utf-8") as f:
    TEST_DATA = json.load(f).get("results", [])


# preprocessing.dockets #


def test_extract_regsdotgov_info(documents = TEST_DATA):
    dockets = RegsDotGovData(documents)
    data = (dockets._extract_field_info(doc) for doc in dockets.documents)
    assert all((isinstance(d, str) or d is None) for d in data)


def test_create_regsdotgov_key(documents = TEST_DATA):
    dockets = RegsDotGovData(documents)
    data = (dockets._create_value_key(doc, values="test") for doc in dockets.documents)
    assert all((isinstance(d, dict) and d.get(dockets.value_key) == "test") for d in data)


def test_process_regsdotgov_data(documents = TEST_DATA):
    dockets = RegsDotGovData(documents)
    data = dockets.process_data()
    assert isinstance(data, list) and (len(data) == len(documents))


def test_extract_docket_info(documents = TEST_DATA):
    dockets = Dockets(documents)
    data = (dockets._extract_field_info(doc) for doc in dockets.documents)
    assert all((isinstance(d, str) or d is None) for d in data)


def test_create_docket_key(documents = TEST_DATA):
    dockets = Dockets(documents)
    data = (dockets._create_value_key(doc, values="test") for doc in dockets.documents)
    assert all((isinstance(d, dict) and d.get(dockets.value_key) == "test") for d in data)


def test_process_docket_data(documents = TEST_DATA):
    dockets = Dockets(documents)
    data = dockets.process_data()
    assert isinstance(data, list)
    assert len(data) == len(documents)
