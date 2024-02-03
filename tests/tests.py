from datetime import date
import json
from pathlib import Path
from pprint import pprint

from requests import get

from fr_toolbelt.api_requests import (
    DateFormatter, 
    retrieve_results_by_next_page, 
    )

from fr_toolbelt.preprocessing import (
    AgencyMetadata, 
    AgencyData, 
#    extract_year, 
#    convert_to_datetime_date, 
#    date_in_quarter, 
#    greater_than_date, 
    RegsDotGovData, 
    Dockets, 
    Presidents,
    RegInfoData, 
    process_documents, 
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
    

# api_requests.format_dates #


def test_extract_year(
        input_success: dict = {"string": "2023-01-01", "year": 2023}, 
        input_fail: str = "01/01/2023"
    ):
    
    fdate = DateFormatter(input_success.get("string"))
    year = fdate.get_year()
    assert isinstance(year, int)
    assert year == input_success.get("year")
    
    year_fail = DateFormatter(input_fail).get_year()
    assert year_fail is None

def test_convert_to_datetime_date(
        success = ("2024-01-01", "20240101", "2024-W01-1", date(2024, 1, 1))
    ):
    
    for attempt in success:
        fdate = DateFormatter()
        result = fdate.__convert_to_datetime_date(attempt) 
        assert isinstance(result, date)


def test_date_in_quarter():
    
    attempt1, attempt2, year, quarter = date(2023, 1, 1), date(2023, 4, 1), "2023", "Q1"
    
    fdate1 = DateFormatter(attempt1)
    result = fdate1.date_in_quarter(year, quarter)
    assert attempt1 == result
    
    fdate2 = DateFormatter(attempt2)
    result = fdate2.date_in_quarter(year, quarter)
    assert attempt2 != result
    assert result == fdate2.quarter_schema.get(quarter)[1], "should return end of Q1"
    
    result = fdate2.date_in_quarter(year, quarter, return_quarter_end=False)
    assert attempt2 != result
    assert result == fdate2.quarter_schema.get(quarter)[0], "should return beginning of Q1"


# add: greater_than_date, 


# api_requests.get_documents #


def test_retrieve_results_by_next_page_full(
    endpoint_url: str = ENDPOINT_URL, 
    dict_params: dict = TEST_PARAMS_FULL, 
    test_response = TEST_RESPONSE_FULL
    ):
    
    results = retrieve_results_by_next_page(endpoint_url, dict_params)
    assert len(results) == test_response.get("count")


def test_retrieve_results_by_next_page_partial(
    endpoint_url: str = ENDPOINT_URL, 
    dict_params: dict = TEST_PARAMS_PARTIAL
    ):
    
    results = retrieve_results_by_next_page(endpoint_url, dict_params)
    assert len(results) == 10000, f"Should return 10,000; compare to API call: {TEST_URL_PARTIAL}"


test_get_documents = (
    test_retrieve_results_by_next_page_full, 
    test_retrieve_results_by_next_page_partial, 
    )


# preprocessing.agencies #


def test_agencies_get_metadata():
    agency_metadata = AgencyMetadata()
    agency_metadata.get_metadata()
    assert isinstance(agency_metadata.data, list)


def test_agencies_transform():
    agency_metadata = AgencyMetadata()
    agency_metadata.get_metadata()
    agency_metadata.transform()
    assert len(agency_metadata.transformed_data) > 0
    assert isinstance(agency_metadata.transformed_data, dict)


# add: to_json, save_metadata, save_schema


test_agencies = (
    test_agencies_get_metadata, 
    test_agencies_transform, 
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
    #pprint(rin.value_keys)
    #pprint([d for d in data][0])
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


test_documents = (
    test_process_documents_all, 
)




# tuple of all tests #
ALL_TESTS = (
    test_get_documents 
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
