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


# preprocessing.documents #

def test_process_documents_all(documents = TEST_DATA):
    data = process_documents(documents)
    assert (len(data) == len(documents)) and isinstance(data, list)


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







# tuple of all tests #


ALL_TESTS = (
    test_retrieve_results_by_next_page_full, 
    test_retrieve_results_by_next_page_partial, 
    test_process_documents_all, 
    test_agencies_get_metadata, 
    test_agencies_transform, 
    )


if __name__ == "__main__":
    
    for func in ALL_TESTS:
        func()
    
    print("Tests complete.")
