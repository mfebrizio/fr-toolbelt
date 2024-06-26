import json
from pathlib import Path

from fr_toolbelt.utils import (
    process_duplicates, 
    DuplicateError, 
    )


TESTS_PATH = Path(__file__).parent
with open(TESTS_PATH / "test_documents.json", "r", encoding="utf-8") as f:
    TEST_DATA = json.load(f).get("results", [])


def test_process_duplicates_raise(results = TEST_DATA + TEST_DATA[0:2]):
    test_error = None
    results_out = None
    try:
        results_out = process_duplicates(results, "raise", key="document_number")
    except DuplicateError as e:
        test_error = e
        assert isinstance(e, DuplicateError)
    assert test_error is not None, f"{test_error=}"
    assert results_out is None
    

def test_process_duplicates_flag(results = TEST_DATA + TEST_DATA[0:2]):
    results_out = process_duplicates(results, "flag", key="document_number")
    flagged = [r for r in results_out if r.get("duplicate", False) == True]
    not_flagged = [r for r in results_out if r.get("duplicate", True) == False]
    #print(flagged)
    assert len(flagged) == (len(TEST_DATA[0:2]) * 2), f"No. flagged documents, {len(flagged)}, does not match duplicates."
    assert len(not_flagged) == (len(TEST_DATA) - len(TEST_DATA[0:2])), f"No. unflagged documents, {len(not_flagged)}, does not match uniques."
    assert all(1 if num in set(doc.get("document_number") for doc in flagged) else 0 for num in (doc.get("document_number") for doc in TEST_DATA[0:2]))


def test_process_duplicates_drop_key(results = TEST_DATA + TEST_DATA[0:2]):
    results_out = process_duplicates(results, "drop", key="document_number")
    assert len(results_out) == len(TEST_DATA)


def test_process_duplicates_drop_keys(results = TEST_DATA + TEST_DATA[0:2]):
    results_out = process_duplicates(results, "drop", keys=("document_number", "citation"))
    assert len(results_out) == len(TEST_DATA), f"{len(results_out)}, {len(TEST_DATA)}"


def test_process_duplicates_match_wildcard(results = TEST_DATA + TEST_DATA[0:2]):
    test_error = None
    results_out = None
    try:
        results_out = process_duplicates(results, "test", key="document_number")
    except ValueError as e:
        test_error = e
        assert isinstance(e, ValueError)
    assert test_error is not None, f"{test_error=}"
    assert results_out is None
