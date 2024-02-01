from pathlib import Path
import json
from pprint import pprint

from requests import get

from fr_toolbelt.api_requests import (
    retrieve_results_by_next_page, 
    )

from fr_toolbelt.preprocessing import (
    AgencyMetadata, 
    AgencyData, 
    RegsDotGovData, 
    Presidents,
    RegInfoData, 
    process_documents, 
    )


# TEST OBJECTS AND UTILS #

# url = "https://www.federalregister.gov/api/v1/documents.json?fields[]=abstract&fields[]=action&fields[]=agencies&fields[]=agency_names&fields[]=body_html_url&fields[]=cfr_references&fields[]=citation&fields[]=comment_url&fields[]=comments_close_on&fields[]=correction_of&fields[]=corrections&fields[]=dates&fields[]=disposition_notes&fields[]=docket_id&fields[]=docket_ids&fields[]=dockets&fields[]=document_number&fields[]=effective_on&fields[]=end_page&fields[]=excerpts&fields[]=executive_order_notes&fields[]=executive_order_number&fields[]=full_text_xml_url&fields[]=html_url&fields[]=images&fields[]=images_metadata&fields[]=json_url&fields[]=mods_url&fields[]=page_length&fields[]=page_views&fields[]=pdf_url&fields[]=president&fields[]=presidential_document_number&fields[]=proclamation_number&fields[]=public_inspection_pdf_url&fields[]=publication_date&fields[]=raw_text_url&fields[]=regulation_id_number_info&fields[]=regulation_id_numbers&fields[]=regulations_dot_gov_info&fields[]=regulations_dot_gov_url&fields[]=significant&fields[]=signing_date&fields[]=start_page&fields[]=subtype&fields[]=title&fields[]=toc_doc&fields[]=toc_subject&fields[]=topics&fields[]=type&fields[]=volume&per_page=20&order=oldest&conditions[publication_date][year]=2024"

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
    
    results = retrieve_results_by_next_page(endpoint_url, dict_params)
    assert len(results) == test_response.get("count")


def test_retrieve_results_by_next_page_partial(
    endpoint_url: str = ENDPOINT_URL, 
    dict_params: dict = TEST_PARAMS_PARTIAL
    ):
    
    results = retrieve_results_by_next_page(endpoint_url, dict_params)
    assert len(results) == 10000, f"Should return 10000; compare to API call: {TEST_URL_PARTIAL}"


test_get_documents = (
    test_retrieve_results_by_next_page_full, 
    test_retrieve_results_by_next_page_partial, 
    )


# preprocessing.dockets #


def test_extract_docket_info(documents = TEST_DATA):
    dockets = RegsDotGovData(documents)
    data = (dockets._extract_field_info(doc) for doc in dockets.documents)
    assert all((isinstance(d, str) or d is None) for d in data)


def test_create_docket_key(documents = TEST_DATA):
    dockets = RegsDotGovData(documents)
    data = (dockets._create_value_key(doc, values="test") for doc in dockets.documents)
    assert all((isinstance(d, dict) and d.get(dockets.value_key) == "test") for d in data)


def test_process_docket_data(documents = TEST_DATA):
    dockets = RegsDotGovData(documents)
    data = dockets.process_data()
    assert isinstance(data, list) and (len(data) == len(documents))


test_dockets = (
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
    #print([(isinstance(d, dict) and d.get("president_id")=="test") for d in data][0:20])
    assert all((isinstance(d, dict) and d.get(prez.value_key) == "test") for d in data)


def test_process_president_data(documents = TEST_DATA):
    prez = Presidents(documents)
    data = prez.process_data()
    assert isinstance(data, list) and (len(data) == len(documents))


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
    assert isinstance(data, list) and (len(data) == len(documents))


test_rin = (
    test_extract_rin_info, 
    test_create_rin_key, 
    test_process_rin_data, 
)


# preprocessing.documents #


def test_process_documents_all(documents = TEST_DATA):
    data = process_documents(documents)
    assert isinstance(data, list) and (len(data) == len(documents))


# preprocessing.agencies #


def test_agencies_get_metadata():
    agency_metadata = AgencyMetadata()
    agency_metadata.get_metadata()
    assert isinstance(agency_metadata.data, list)


def test_agencies_transform():
    agency_metadata = AgencyMetadata()
    agency_metadata.get_metadata()
    agency_metadata.transform()
    assert (
        len(agency_metadata.transformed_data) > 0
        ) and (
            isinstance(agency_metadata.transformed_data, dict)
            )


test_agencies = (
    test_agencies_get_metadata, 
    test_agencies_transform, 
)


# tuple of all tests #
all_tests = (
    test_get_documents 
    + test_dockets 
    + test_presidents 
    + test_rin
    + test_agencies
    + (test_process_documents_all, )
    )


if __name__ == "__main__":
    
    for func in all_tests:
        func()
    
    print("Tests complete.")
