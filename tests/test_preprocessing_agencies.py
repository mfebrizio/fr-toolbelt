from itertools import product
import json
from pathlib import Path

from requests import get

from fr_toolbelt.preprocessing import (
    AgencyMetadata, 
    AgencyData, )


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


def test_agencies_data_process_defaults(
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


def test_agencies_data_process_return_format_str(
        documents = TEST_DATA, 
        metadata = TEST_METADATA, 
        schema = TEST_SCHEMA, 
        check_keys = ("agency_slugs", "independent_reg_agency", ), 
        check_prefixes = ("parent_", "subagency_", ), 
        return_format="short_name", 
):
    agency_data = AgencyData(documents=documents, metadata=metadata, schema=schema)
    processed = agency_data.process_data(return_format=return_format)
    assert isinstance(processed, list)
    assert len(processed) > 0
    processed_keys = set((k for d in processed for k in d))
    checks = list(check_keys) + [f"{p[0]}{p[1]}" for p in product(check_prefixes, (return_format, ))]
    for key in checks:
        assert key in processed_keys, f"Output missing {key=}"
    for key in agency_data.field_keys:
        assert key not in processed_keys, f"Failed to delete keys: {key=}"


def test_agencies_data_process_return_format_tuple(
        documents = TEST_DATA, 
        metadata = TEST_METADATA, 
        schema = TEST_SCHEMA, 
        check_keys = ("agency_slugs", "independent_reg_agency", ), 
        check_prefixes = ("parent_", "subagency_", ), 
        return_format=("short_name", "slug", ), 
):
    agency_data = AgencyData(documents=documents, metadata=metadata, schema=schema)
    processed = agency_data.process_data(return_format=return_format)
    assert isinstance(processed, list)
    assert len(processed) > 0
    processed_keys = set((k for d in processed for k in d))
    checks = list(check_keys) + [f"{p[0]}{p[1]}" for p in product(check_prefixes, return_format)]
    for key in checks:
        assert key in processed_keys, f"Output missing {key=}"
    for key in agency_data.field_keys:
        assert key not in processed_keys, f"Failed to delete keys: {key=}"
