import csv
from pathlib import Path
import random

import pytest

from fr_toolbelt.api_requests import parse_document_numbers, InputFileError


TEST_PATH = Path(__file__).parent
N_TEST_FILES = 5
N_TEST_FILE_ROWS = 100


def _create_test_csv_to_parse(path: Path, suffix: str = '.csv', **kwargs):
    with open(path / f'test_parse_document_numbers{suffix}', 'w', newline='') as csvfile:
        fieldnames = ['document_number', 'html_url']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, **kwargs)

        writer.writeheader()
        writer.writerow({'document_number': '2024-02204', 'html_url': 'https://federalregister.gov/d/2024-02204'})
        writer.writerow({'document_number': '2023-28203', 'html_url': 'https://federalregister.gov/d/2024-28203'})
        writer.writerow({'document_number': '2023-25797', 'html_url': 'https://federalregister.gov/d/2024-25797'})


def _create_test_csv_randomized(path: Path, n_files: int, n_rows: int = N_TEST_FILE_ROWS, **kwargs):
    with open(path / f'test_parse_document_numbers_{n_files}.csv', 'w', newline='') as csvfile:
        fieldnames = ['document_number', 'html_url']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, **kwargs)
        writer.writeheader()
        for _ in range(0, n_rows):
            rand_docnum = f'2024-{random.randrange(10000, 99999)}'
            writer.writerow({'document_number': rand_docnum, 'html_url': f'https://federalregister.gov/d/{rand_docnum}'})


@pytest.fixture(scope="session")
def get_csv_file(tmp_path_factory):
    fn = tmp_path_factory.mktemp("data_csv")
    _create_test_csv_to_parse(path=fn)
    return fn


@pytest.fixture(scope="session")
def get_txt_file(tmp_path_factory):
    fn = tmp_path_factory.mktemp("data_txt")
    _create_test_csv_to_parse(path=fn, suffix=".txt")
    return fn


@pytest.fixture(scope="session")
def get_non_csv_file(tmp_path_factory):
    fn = tmp_path_factory.mktemp("data_non_csv")
    _create_test_csv_to_parse(path=fn, suffix=".test")
    return fn


@pytest.fixture(scope="session")
def get_csv_file_mult(tmp_path_factory, n_files: int = N_TEST_FILES):
    fn = tmp_path_factory.mktemp("data_csv_mult")
    for n in range(0, n_files):
        _create_test_csv_randomized(path=fn, n_files=n)
    return fn


def test_parse_document_numbers_csv(get_csv_file):
    results = parse_document_numbers(get_csv_file)
    assert isinstance(results, list)
    assert len(results) == 3


def test_parse_document_numbers_txt(get_txt_file):
    results = parse_document_numbers(get_txt_file)
    assert isinstance(results, list)
    assert len(results) == 3


def test_parse_document_numbers_csv_mult(get_csv_file_mult):
    results = parse_document_numbers(get_csv_file_mult)
    assert isinstance(results, list)
    assert N_TEST_FILES * N_TEST_FILE_ROWS * 0.95 < len(results) <= N_TEST_FILES * N_TEST_FILE_ROWS, f"{len(results)} is not within 5% of test files * test rows"


def test_parse_document_numbers_error_empty(path: Path = TEST_PATH):
    test_error = None
    results_out = None
    try:
        results_out = parse_document_numbers(path)
    except InputFileError as e:
        test_error = e
        assert isinstance(e, InputFileError)
    assert test_error is not None, f"{test_error=}"
    assert results_out is None


def test_parse_document_numbers_error_non_csv(get_non_csv_file):
    test_error = None
    results_out = None
    try:
        results_out = parse_document_numbers(get_non_csv_file)
    except InputFileError as e:
        test_error = e
        assert isinstance(e, InputFileError)
    assert test_error is not None, f"{test_error=}"
    assert results_out is None
