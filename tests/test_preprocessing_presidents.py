import json
from pathlib import Path

from fr_toolbelt.preprocessing import ( 
    Presidents, 
    )


# TEST OBJECTS AND UTILS #


TESTS_PATH = Path(__file__).parent

with open(TESTS_PATH / "test_documents.json", "r", encoding="utf-8") as f:
    TEST_DATA = json.load(f).get("results", [])


# preprocessing.presidents #


def test_extract_president_info(documents = TEST_DATA):
    prez = Presidents(documents)
    data = (prez._extract_field_info(doc) for doc in prez.documents)
    assert all((isinstance(d, str) or d is None) for d in data)


def test_create_president_key(documents = TEST_DATA):
    prez = Presidents(documents)
    data = (prez._create_value_key(doc, values="test") for doc in prez.documents)
    assert all((isinstance(d, dict) and d.get(prez.value_key) == "test") for d in data)


def test_process_president_data(documents = TEST_DATA):
    prez = Presidents(documents)
    data = prez.process_data()
    assert isinstance(data, list)
    assert len(data) == len(documents)
