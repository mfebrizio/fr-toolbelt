from datetime import date
import json
from pathlib import Path
#from pprint import pprint

from requests import get

from fr_toolbelt.api_requests import (

    _retrieve_results_by_next_page, 
    get_documents_by_date, 
    get_documents_by_number, 

    )

from fr_toolbelt.preprocessing import (
    AgencyMetadata, 
    AgencyData, 
    RegsDotGovData, 
    Dockets, 
    Presidents,
    RegInfoData, 
    process_documents, 
    )

from fr_toolbelt.utils import (
    DateFormatter, 
    process_duplicates, 
    DuplicateError, 
)


# TEST OBJECTS AND UTILS #


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

TEST_METADATA, TEST_SCHEMA = AgencyMetadata().get_agency_metadata()


# api_requests.duplicates #


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
    assert len(flagged) == (len(TEST_DATA[0:2]) * 2)
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
        results_out = process_duplicates(results, "document_number", "test")
    except ValueError as e:
        test_error = e
        assert isinstance(e, ValueError)
    assert test_error is not None, f"{test_error=}"
    assert results_out is None


test_duplicates = (
    test_process_duplicates_raise, 
    test_process_duplicates_flag, 
    test_process_duplicates_drop_key,
    #test_process_duplicates_drop_dict, 
    test_process_duplicates_match_wildcard, 
)


# api_requests.format_dates #


def test__convert_to_datetime_date(
        success = ("2024-01-01", "20240101", "2024-W01-1", date(2024, 1, 1))
    ):
    
    for attempt in success:
        fdate = DateFormatter(attempt)
        result = fdate._DateFormatter__convert_to_datetime_date(attempt)
        assert isinstance(result, date)


def test_get_year_self(
        input_success: dict = {"string": "2023-01-01", "year": 2023}, 
        input_fail: str = "01/01/2023"
    ):
    
    fdate = DateFormatter(input_success.get("string"))
    year = fdate.get_year()
    assert isinstance(year, int)
    assert year == input_success.get("year")
    
    try:
        DateFormatter(input_fail).get_year()
    except ValueError as e:
        assert e.__class__ == ValueError


def test_get_year_alt(
        input_success: dict = {
            1: {"string": "2023-01-01", "year": 2023}, 
            2: {"string": "2024-01-01", "year": 2024}
            }
    ):
    
    fdate = DateFormatter(input_success.get(1).get("string"))
    year = fdate.get_year(input_success.get(2).get("string"))
    assert isinstance(year, int)
    assert year == input_success.get(2).get("year")


def test_get_formatted_date(
        success = ("2024-01-01", "20240101", "2024-W01-1", date(2024, 1, 1))
    ):
    for attempt in success:
        result = DateFormatter(attempt).get_formatted_date()
        assert isinstance(result, date)


def test_date_in_quarter():
    
    attempt1, attempt2, year, quarter = date(2023, 1, 1), date(2023, 4, 1), "2023", "Q1"
    
    fdate1 = DateFormatter(attempt1)
    result = fdate1.date_in_quarter(year, quarter)
    assert attempt1 == result
    
    fdate2 = DateFormatter(attempt2)
    result = fdate2.date_in_quarter(year, quarter)
    assert attempt2 != result
    assert f"{result}" == f"{year}-{fdate2.quarter_schema.get(quarter)[1]}", "should return end of Q1"
    
    result = fdate2.date_in_quarter(year, quarter, return_quarter_end=False)
    assert attempt2 != result
    assert f"{result}" == f"{year}-{fdate2.quarter_schema.get(quarter)[0]}", "should return beginning of Q1"


def test_gt_date_exclusive(inputs = {
        "earlier": date(2023, 1, 1), 
        "later": date(2023, 4, 1)}
    ):
    fdate = DateFormatter(inputs.get("later"))
    res = fdate.greater_than_date(inputs.get("earlier"))
    assert res, "later > earlier"
    res2 = fdate.greater_than_date(inputs.get("later"))
    assert not res2, "later !> later (exclusive)"
    
    fdate = DateFormatter(inputs.get("earlier"))
    res = fdate.greater_than_date(inputs.get("later"))
    assert not res, "earlier !> later"
    res2 = fdate.greater_than_date(inputs.get("earlier"))
    assert not res2, "earlier !> earlier (exclusive)"


def test_gt_date_inclusive(inputs = {
        "earlier": date(2023, 1, 1), 
        "later": date(2023, 4, 1)
        }
    ):
    fdate = DateFormatter(inputs.get("later"))
    res = fdate.greater_than_date(inputs.get("later"), inclusive=True)
    assert res, "later == later (inclusive)"
    
    fdate = DateFormatter(inputs.get("earlier"))
    res = fdate.greater_than_date(inputs.get("earlier"), inclusive=True)
    assert res, "earlier == earlier (inclusive)"


def test_lt_date_exclusive(inputs = {
        "earlier": date(2023, 1, 1), 
        "later": date(2023, 4, 1)
        }
    ):
    fdate = DateFormatter(inputs.get("later"))
    res = fdate.less_than_date(inputs.get("earlier"))
    assert not res, "later !< earlier"
    res2 = fdate.less_than_date(inputs.get("later"))
    assert not res2, "later !< later (exclusive)"
    
    fdate = DateFormatter(inputs.get("earlier"))
    res = fdate.less_than_date(inputs.get("later"))
    assert res, "earlier < later"
    res2 = fdate.less_than_date(inputs.get("earlier"))
    assert not res2, "earlier !< earlier (exclusive)"


def test_lt_date_inclusive(inputs = {
        "earlier": date(2023, 1, 1), 
        "later": date(2023, 4, 1)
        }
    ):
    fdate = DateFormatter(inputs.get("later"))
    res = fdate.less_than_date(inputs.get("later"), inclusive=True)
    assert res, "later == later (inclusive)"
    
    fdate = DateFormatter(inputs.get("earlier"))
    res = fdate.less_than_date(inputs.get("earlier"), inclusive=True)
    assert res, "earlier == earlier (inclusive)"


test_dates = (
    test__convert_to_datetime_date, 
    test_get_year_self,
    test_get_year_alt, 
    test_get_formatted_date, 
    test_date_in_quarter, 
    test_gt_date_exclusive, 
    test_gt_date_inclusive, 
    test_lt_date_exclusive, 
    test_lt_date_inclusive, 
)


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
    #print(res_types)
    assert len(res_types) <= len(types)
    assert all(1 if r in (type_schema.get(t) for t in types) else 0 for r in res_types)


def test_get_documents_by_date_above_max_threshold(start = "2020-01-01", end = "2022-12-31"):
    results, count = get_documents_by_date(start, end)
    assert isinstance(results, list)
    assert count == len(results)


#def test_get_documents_by_date_duplicates(start = "2024-01-01", end = "2024-01-31"):
#    results, count = get_documents_by_date(start, end)
    #results + results
    #assert isinstance(results, list)
    #assert count == len(results)
    #res_types = set(doc.get("type") for doc in results)
    #assert len(res_types) <= len(types)
    #assert all(1 if t in types else 0 for t in res_types)
    


def test_get_documents_by_number(numbers = ["2024-02204", "2023-28203", "2023-25797"]):
    results, count = get_documents_by_number(numbers)
    assert isinstance(results, list)
    assert count == len(results)


test_get_documents = (
    test_retrieve_results_by_next_page_full, 
    test_retrieve_results_by_next_page_partial, 
    test_get_documents_by_date, 
    test_get_documents_by_date_quarters, 
    test_get_documents_by_date_types, 
    test_get_documents_by_date_above_max_threshold, 
    test_get_documents_by_number, 
    )


# preprocessing.agencies #


def test_agencies_metadata_init():
    agency_metadata = AgencyMetadata()
    assert isinstance(agency_metadata.data, list)
    assert len(agency_metadata.transformed_data) > 0
    assert isinstance(agency_metadata.transformed_data, dict)
    assert len(agency_metadata.schema) > 0
    assert isinstance(agency_metadata.schema, list)


def test_agencies_metadata_get():
    agency_metadata = AgencyMetadata()
    metadata, schema = agency_metadata.get_agency_metadata()
    assert isinstance(metadata, dict)
    assert isinstance(schema, list)


def test_agencies_metadata_save_metadata(path = TESTS_PATH, file_name: str = "test_metadata.json"):
    test_path = path / file_name
    assert not test_path.exists()
    agency_metadata = AgencyMetadata()
    agency_metadata.save_metadata(path, file_name=file_name)
    assert test_path.is_file()
    if test_path.is_file():
        test_path.unlink()


def test_agencies_metadata_save_schema(path = TESTS_PATH, file_name: str = "test_schema.json"):
    test_path = path / file_name
    assert not test_path.exists()
    agency_metadata = AgencyMetadata()
    agency_metadata.save_schema(path, file_name=file_name)
    assert test_path.is_file()
    if test_path.is_file():
        test_path.unlink()


def test_agencies_data_init(
        documents = TEST_DATA, 
        metadata = TEST_METADATA, 
        schema = TEST_SCHEMA
    ):
    agency_data = AgencyData(documents=documents, metadata=metadata, schema=schema)
    assert isinstance(agency_data.documents, list)
    assert len(agency_data.documents) > 0
    assert isinstance(agency_data.metadata, dict)
    assert len(agency_data.metadata) > 0
    assert isinstance(agency_data.schema, dict), f"schema should be type dict but it is type {type(agency_data.schema)}"
    assert len(agency_data.schema) == 3


def test_agencies_data_process(
        documents = TEST_DATA, 
        metadata = TEST_METADATA, 
        schema = TEST_SCHEMA, 
        check_keys = ("agency_slugs", "parent_slug", "subagency_slug", "independent_reg_agency")
):
    agency_data = AgencyData(documents=documents, metadata=metadata, schema=schema)
    processed = agency_data.process_data()
    assert isinstance(processed, list)
    assert len(processed) > 0
    processed_keys = set((k for d in processed for k in d))
    for key in check_keys:
        assert key in processed_keys, f"Output missing {key=}"
    for key in agency_data.field_keys:
        assert key not in processed_keys, f"Failed to delete keys: {key=}"



test_agencies = (
    test_agencies_metadata_init, 
    test_agencies_metadata_get, 
    test_agencies_metadata_save_metadata, 
    test_agencies_metadata_save_schema, 
    test_agencies_data_init, 
    test_agencies_data_process, 
)


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


test_dockets = (
    test_extract_regsdotgov_info, 
    test_create_regsdotgov_key, 
    test_process_regsdotgov_data, 
    test_extract_docket_info, 
    test_create_docket_key, 
    test_process_docket_data, 
)


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


test_presidents = (
    test_extract_president_info, 
    test_create_president_key, 
    test_process_president_data, 
)


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


test_rin = (
    test_extract_rin_info, 
    test_create_rin_key, 
    test_process_rin_data, 
)


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


test_documents = (
    test_process_documents_all, 
    test_process_documents_which_str1,
    test_process_documents_which_str2,
    test_process_documents_which_list, 
)


# tuple of all tests #
ALL_TESTS = (
    test_duplicates
    + test_dates
    + test_get_documents 
    + test_dockets 
    + test_presidents 
    + test_rin
    + test_agencies
    + test_documents
    )


if __name__ == "__main__":
    
    for func in ALL_TESTS:
        func()
    
    print("Tests complete.")
