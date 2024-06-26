import json
from pathlib import Path

from fr_toolbelt.preprocessing import ( 
    RegInfoData, 
    )


# TEST OBJECTS AND UTILS #


TESTS_PATH = Path(__file__).parent

with open(TESTS_PATH / "test_documents.json", "r", encoding="utf-8") as f:
    TEST_DATA = json.load(f).get("results", [])


# preprocessing.rin #


def test_extract_rin_info(documents = TEST_DATA):
    rin = RegInfoData(documents)
    data = (rin._extract_field_info(doc) for doc in rin.documents)
    assert all((isinstance(d, tuple) or d is None) for d in data)


def test_create_rin_key(documents = TEST_DATA):
    rin = RegInfoData(documents)
    data = (rin._create_value_keys(doc, values=("test1", "test2")) for doc in rin.documents)
    assert all(
        isinstance(d, dict) 
        and (d.get(rin.value_keys[0]) == "test1") 
        and (d.get(rin.value_keys[1]) == "test2") 
        for d in data)


def test_process_rin_data(documents = TEST_DATA):
    rin = RegInfoData(documents)
    data = rin.process_data()
    assert isinstance(data, list)
    assert len(data) == len(documents)
