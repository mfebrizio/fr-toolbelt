from datetime import datetime, date, timedelta
import json
from pathlib import Path

from dateutil import tz
from requests import get

from fr_toolbelt.api_requests import (
    _retrieve_results_by_next_page, 
    get_documents_by_date, 
    get_documents_by_number, 
    )


# TEST OBJECTS AND UTILS #


EST = tz.gettz("EST")
TODAY_EST = datetime.now(tz=EST).date()

TESTS_PATH = Path(__file__).parent

ENDPOINT_URL = r"https://www.federalregister.gov/api/v1/documents.json?"

TEST_PARAMS_FULL = {
    "per_page": 1000, 
    "page": 0, 
    "order": "oldest", 
    "conditions[publication_date][gte]": "2023-11-01", 
    "conditions[publication_date][lte]": "2023-11-30"
    }
TEST_RESPONSE_FULL = get(ENDPOINT_URL, TEST_PARAMS_FULL).json()

TEST_PARAMS_PARTIAL = {
    "per_page": 1000, 
    "page": 0, 
    "order": "oldest", 
    "conditions[publication_date][gte]": "2023-01-01", 
    "conditions[publication_date][lte]": "2023-06-30"
    }
TEST_URL_PARTIAL = get(ENDPOINT_URL, TEST_PARAMS_PARTIAL).url
TEST_RESPONSE_PARTIAL = get(ENDPOINT_URL, TEST_PARAMS_PARTIAL).json()
TEST_COUNT_PARTIAL = TEST_RESPONSE_PARTIAL["count"]

with open(TESTS_PATH / "test_documents.json", "r", encoding="utf-8") as f:
    TEST_DATA = json.load(f).get("results", [])


# api_requests.get_documents #


def test_retrieve_results_by_next_page_full(
    endpoint_url: str = ENDPOINT_URL, 
    dict_params: dict = TEST_PARAMS_FULL, 
    test_response = TEST_RESPONSE_FULL
    ):
    
    results = _retrieve_results_by_next_page(endpoint_url, dict_params)
    assert len(results) == test_response.get("count")


def test_retrieve_results_by_next_page_partial(
    endpoint_url: str = ENDPOINT_URL, 
    dict_params: dict = TEST_PARAMS_PARTIAL
    ):
    
    results = _retrieve_results_by_next_page(endpoint_url, dict_params)
    assert len(results) == 10000, f"Should return 10,000; compare to API call: {TEST_URL_PARTIAL}"


def test_get_documents_by_date(start = "2024-01-01", end = "2024-01-31"):
    results, count = get_documents_by_date(start, end)
    assert isinstance(results, list)
    assert count == len(results)


def test_get_documents_by_date_quarters(start = "2022-12-01", end = "2023-02-01"):
    results, count = get_documents_by_date(start, end)
    assert isinstance(results, list)
    assert count == len(results)
    

def test_get_documents_by_date_types(
        start = "2024-01-01", 
        end = "2024-01-31", 
        types = ["RULE", "PRORULE"], 
        type_schema = {
            "RULE": "Rule", 
            "PRORULE": "Proposed Rule", 
            "NOTICE": "Notice", 
            "PRESDOCU": "Presidential Document"
            }
    ):
    results, count = get_documents_by_date(start, end, document_types=types)
    assert isinstance(results, list)
    assert count == len(results)
    res_types = set(doc.get("type") for doc in results)
    assert len(res_types) <= len(types)
    assert all(1 if r in (type_schema.get(t) for t in types) else 0 for r in res_types)


def test_get_documents_by_date_above_max_threshold(start = "2020-01-01", end = "2022-12-31", max = 10000):
    results, count = get_documents_by_date(start, end)
    assert count > max
    assert isinstance(results, list)
    assert count == len(results)


def test_get_documents_by_date_no_end_date(delta = 365):
    start = (datetime.now(tz=EST) - timedelta(delta)).date()
    test_error = "will remain string if error is not handled in try/except block"
    try:
        results, count = get_documents_by_date(start)
    except TypeError as err:
        test_error = err
        results, count = get_documents_by_date(start, end_date=TODAY_EST)
    assert isinstance(test_error, str), "Error was handled in try/except block; bug remains in program"
    if TODAY_EST.isoweekday() not in (6, 7):
        max_date = max(date.fromisoformat(r.get("publication_date")) for r in results)
        assert max_date == TODAY_EST
    assert isinstance(results, list)
    assert count == len(results)


def test_get_documents_by_number(numbers = ["2024-02204", "2023-28203", "2023-25797"]):
    results, count = get_documents_by_number(numbers)
    assert isinstance(results, list)
    assert count == len(results)
