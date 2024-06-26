from pathlib import Path
import csv

import pytest

from fr_toolbelt.api_requests import parse_document_numbers, InputFileError


TEST_PATH = Path(__file__).parent


def _create_test_csv_to_parse(path: Path):
    
    with open(path / 'test_parse_document_numbers.csv', 'w', newline='') as csvfile:
        fieldnames = ['document_number', 'html_url']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        writer.writerow({'document_number': '2024-02204', 'html_url': 'https://federalregister.gov/d/2024-02204'})
        writer.writerow({'document_number': '2023-28203', 'html_url': 'https://federalregister.gov/d/2024-28203'})
        writer.writerow({'document_number': '2023-25797', 'html_url': 'https://federalregister.gov/d/2024-25797'})


@pytest.fixture(scope="session")
def get_csv_file(tmp_path_factory):
    fn = tmp_path_factory.mktemp("data")
    _create_test_csv_to_parse(path=fn)
    return fn


def test_parse_document_numbers_csv(get_csv_file):
    
    results = parse_document_numbers(get_csv_file)
    assert isinstance(results, list)
    assert len(results) == 3


def test_parse_document_numbers_error(path: Path = TEST_PATH):
    test_error = None
    results_out = None
    try:
        results_out = parse_document_numbers(path)
    except InputFileError as e:
        test_error = e
        assert isinstance(e, InputFileError)
    assert test_error is not None, f"{test_error=}"
    assert results_out is None
