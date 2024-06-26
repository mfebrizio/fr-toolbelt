import json
from pathlib import Path

from fr_toolbelt.preprocessing import ( 
    process_documents, 
    )


# TEST OBJECTS AND UTILS #


TESTS_PATH = Path(__file__).parent

with open(TESTS_PATH / "test_documents.json", "r", encoding="utf-8") as f:
    TEST_DATA = json.load(f).get("results", [])


# preprocessing.documents #


def test_process_documents_all(documents = TEST_DATA):
    data = process_documents(documents)
    assert isinstance(data, list)
    assert len(data) == len(documents)


def test_process_documents_which_str1(documents = TEST_DATA, which="dockets"):
    data = process_documents(documents, which=which)
    assert isinstance(data, list)
    assert len(data) == len(documents)


def test_process_documents_which_str2(documents = TEST_DATA, which="agencies"):
    data = process_documents(documents, which=which)
    assert isinstance(data, list)
    assert len(data) == len(documents)


def test_process_documents_which_list(documents = TEST_DATA, which=["dockets", "agencies"]):
    data = process_documents(documents, which=which)
    assert isinstance(data, list)
    assert len(data) == len(documents)
