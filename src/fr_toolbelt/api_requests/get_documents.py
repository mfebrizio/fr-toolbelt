from copy import deepcopy
import csv
from datetime import datetime, date
from pathlib import Path
import re
import time
from zoneinfo import ZoneInfo

import requests

from ..utils.duplicates import process_duplicates
from ..utils.format_dates import DateFormatter

# get patched version of progress bar
from ..utils.patch_progress import getpatchedprogress
progress = getpatchedprogress()
from progress.bar import Bar

BASE_PARAMS = {
    "per_page": 1000, 
    "page": 0, 
    "order": "oldest"
    }
BASE_URL = r"https://www.federalregister.gov/api/v1/documents.json?"
DEFAULT_FIELDS = (
    "document_number", 
    "citation", 
    "publication_date", 
    "agency_names", 
    "agencies", 
    "title", 
    "type", 
    "action",
    "abstract", 
    "docket_ids", 
    "dockets",
    "president",
    "regulation_id_number_info", 
    "regulations_dot_gov_info",
    "correction_of",
    "json_url",
    "html_url", 
    )

ET = ZoneInfo("America/New_York")  #tz.gettz("EST")
TODAY_ET = datetime.now(tz=ET).date()


# -- functions for handling API requests -- #


class QueryError(Exception):
    pass


class InputFileError(Exception):
    pass


def sleep_retry(timeout: int, retry: int = 3):
    """Decorator to sleep and retry request when receiving an error 
    (source: [RealPython](https://realpython.com/python-sleep/#adding-a-python-sleep-call-with-decorators)).

    Args:
        timeout (int): Number of seconds to sleep after error.
        retry (int, optional): Number of times to retry. Defaults to 3.
    """    
    def retry_decorator(function):
        def wrapper(*args, **kwargs):
            retries = 0
            while retries < retry:
                try:
                    value = function(*args, **kwargs)
                    if value is not None:
                        return value
                    else:
                        raise QueryError
                except (requests.HTTPError, requests.JSONDecodeError, ):
                    #print(f'Sleeping for {timeout} seconds')
                    time.sleep(timeout)
                    retries += 1
        return wrapper
    return retry_decorator


def _ensure_json_response(response: requests.Response):
    """Ensure request response is valid JSON by checking for 200 status code. 
    Returns JSON response or empty dictionary.
    """
    if response.status_code == 200:
        res_json = response.json()
    else:
        res_json = {}
    return res_json


@sleep_retry(60)
def _retrieve_results_by_page_range(num_pages: int, endpoint_url: str, dict_params: dict) -> list:
    """Retrieve documents by looping over a given number of pages.

    Args:
        num_pages (int): Number of pages to retrieve documents from.
        endpoint_url (str): URL for API endpoint.
        dict_params (dict): Paramters to pass in GET request.

    Returns:
        list: Documents retrieved from the API.
    """
    results, tally = [], 0
    for page in range(1, num_pages + 1):  # grab results from each page
        dict_params.update({"page": page})
        response = requests.get(endpoint_url, params=dict_params)
        response = _ensure_json_response(response)
        results_this_page = response.get("results", [])
        results.extend(results_this_page)
        tally += len(results_this_page)
    count = response.json()["count"]
    print(count, tally)
    return results, count


@sleep_retry(60)
def _retrieve_results_by_next_page(endpoint_url: str, dict_params: dict) -> list:
    """Retrieve documents by accessing "next_page_url" returned by each request.

    Args:
        endpoint_url (str): url for documents.{format} endpoint.
        dict_params (dict): Paramters to pass in GET request.

    Raises:
        QueryError: Failed to retrieve documents from all pages.

    Returns:
        list: Documents retrieved from the API.
    """
    results = []
    response = requests.get(endpoint_url, params=dict_params)
    response = _ensure_json_response(response)
    pages = response.get("total_pages", 1)
    next_page_url = response.get("next_page_url")
    counter = 0
    while next_page_url is not None:
        counter += 1
        results_this_page = response.get("results", [])
        results.extend(results_this_page)
        response = requests.get(next_page_url).json()
        next_page_url = response.get("next_page_url")
    else:
        counter += 1
        results_this_page = response.get("results", [])
        results.extend(results_this_page)
    
    # raise exception if failed to access all pages
    if counter != pages:
        raise QueryError(f"Failed to retrieve documents from {pages} pages.")
    
    return results


def _query_documents_endpoint(
        endpoint_url: str, 
        dict_params: dict, 
        handle_duplicates: bool | str = False, 
        **kwargs
    ) -> tuple[list, int]:
    """GET request for documents endpoint.

    Args:
        endpoint_url (str): URL for API endpoint.
        dict_params (dict): Paramters to pass in GET request.

    Returns:
        tuple[list, int]: Tuple of API results, count of documents retrieved.
    """    
    results, running_count = [], 0
    response = requests.get(endpoint_url, params=dict_params)
    #print(response.url)
    res_json = response.json()
    max_documents_threshold = 10000
    response_count = res_json["count"]
    
    # handles queries returning no documents
    if response_count == 0:
        pass
    
    # handles queries that need multiple requests
    elif response_count > max_documents_threshold:
        
        # get range of dates
        start_date = DateFormatter(dict_params.get("conditions[publication_date][gte]"))
        end_date = DateFormatter(dict_params.get("conditions[publication_date][lte]", f"{TODAY_ET}"))
        
        # set range of years
        start_year = start_date.year
        end_year = end_date.year
        years = range(start_year, end_year + 1)
        
        # format: YYYY-MM-DD
        quarters = ("Q1", "Q2", "Q3", "Q4")
        
        # retrieve documents
        dict_params_qrt = deepcopy(dict_params)

        with Bar(kwargs.get("message", "Years retrieved"), max=len(years)) as bar:
            for year in years:
                for quarter in quarters:
                    
                    # set start and end dates based on input date
                    gte = start_date.date_in_quarter(year, quarter, return_quarter_end=False)
                    lte = end_date.date_in_quarter(year, quarter)
                    if start_date.greater_than_date(lte):
                        # skip quarters where start_date is later than last day of quarter
                        continue
                    elif end_date.less_than_date(gte):
                        # skip quarters where end_date is ealier than first day of quarter
                        break
                    
                    # update parameters by quarter
                    dict_params_qrt.update({
                        "conditions[publication_date][gte]": f"{gte}", 
                        "conditions[publication_date][lte]": f"{lte}"
                                            })
                    
                    # get documents
                    results_qrt = _retrieve_results_by_next_page(endpoint_url, dict_params_qrt)
                    results.extend(results_qrt)
                    running_count += len(results_qrt)
                bar.next()
                
    # handles normal queries
    elif response_count in range(max_documents_threshold + 1):
        running_count += response_count
        results.extend(_retrieve_results_by_next_page(endpoint_url, dict_params))
    
    # otherwise something went wrong
    else:
        raise QueryError(f"Query returned document count of {response_count}.")
    
    if running_count != response_count:
        #print(running_count)
        #print(results[-1])
        raise QueryError(f"Failed to retrieve all {response_count} documents.")
    
    if not handle_duplicates:
        pass
    else:
        results = process_duplicates(results, how=handle_duplicates, keys=("document_number", "citation"))
    return results, running_count


# -- retrieve documents using date range -- #


def get_documents_by_date(start_date: str | date, 
                          end_date: str | date | None = None, 
                          document_types: tuple | list = None,
                          fields: tuple[str] | list[str] = DEFAULT_FIELDS,
                          endpoint_url: str = BASE_URL, 
                          dict_params: dict = BASE_PARAMS, 
                          handle_duplicates: bool | str = False, 
                          **kwargs
                          ):
    """Retrieve Federal Register documents using a date range.

    Args:
        start_date (str): Start date when documents were published (inclusive; format must be "yyyy-mm-dd").
        end_date (str, optional): End date (inclusive; format must be "yyyy-mm-dd"). Defaults to None (implies end date is today for EST timezone).
        document_types (tuple[str] | list[str], optional): If passed, only return specific document types. 
        Valid types are "RULE" (final rules), "PRORULE" (proposed rules), "NOTICE" (notices), and "PRESDOCU" (presidential documents). Defaults to None.
        fields (tuple | list, optional): Fields/columns to retrieve. Defaults to constant DEFAULT_FIELDS.
        endpoint_url (str, optional): Endpoint url. Defaults to r"https://www.federalregister.gov/api/v1/documents.json?".

    Returns:
        tuple[list, int]: Tuple of API results, count of documents retrieved.
    """
    # Not passing end_date implies end date of today EST
    if end_date is None:
        end_date = TODAY_ET

    # update dictionary of parameters
    params = dict_params.copy()
    params.update({
        "conditions[publication_date][gte]": f"{start_date}", 
        "conditions[publication_date][lte]": f"{end_date}", 
        "fields[]": fields, 
        })
    
    if document_types is not None:
        params.update({"conditions[type][]": list(document_types)})
    
    results, count = _query_documents_endpoint(
        endpoint_url, 
        params, 
        handle_duplicates=handle_duplicates, 
        **kwargs
        )
    return results, count


# -- retrieve documents using input file -- #


def get_documents_by_number(document_numbers: list, 
                            fields: tuple | list = DEFAULT_FIELDS, 
                            sort_data: bool = True
                            ):
    """Retrieve Federal Register documents using a list of document numbers.

    Args:
        document_numbers (list): Documents to retrieve based on "document_number" field.
        fields (tuple, optional): Fields/columns to retrieve. Defaults to constant DEFAULT_FIELDS.
        sort_data (bool, optional): Sort documents by "document_number". Defaults to True.

    Returns:
        tuple[list, int]: Tuple of API results, count of documents retrieved.
    """    
    if sort_data:
        document_numbers_str = ",".join(sorted(document_numbers))
    else:
        document_numbers_str = ",".join(document_numbers)
    
    endpoint_url = fr"https://www.federalregister.gov/api/v1/documents/{document_numbers_str}.json?"
    dict_params = {"fields[]": fields}
    results, count = _query_documents_endpoint(endpoint_url, dict_params)
    return results, count


def _read_csv(path_to_file, pattern: str = r"(?:[a-z]\d-)?[\w|\d]{2,4}-[\d]{5,}", alt_column: str = "html_url", **kwargs):
    """Read document numbers from a CSV file, based on document_numbers column or alternative column with a regex pattern.
    """
    with open(path_to_file, "r", newline="") as csvfile:
        reader = csv.DictReader(csvfile, **kwargs)
        if 'document_number' in reader.fieldnames:
            document_numbers = [f"{row.get('document_number', '')}".strip() for row in reader]
        elif alt_column in reader.fieldnames:
            alt_list = [f"{row.get(alt_column, '')}".strip() for row in reader]
            document_numbers = [re.search(pattern, alt).group(0) for alt in alt_list]
        else:
            raise InputFileError(f"document_number column or alternative id column , {alt_column}, missing from csv.")
        return document_numbers


def parse_document_numbers(path: Path, alt_column: str = "html_url", **kwargs):
    """Parse Federal Register document numbers from input CSV within a directory.

    Args:
        path (Path): Path to directory containing data file.
        alt_column (str, optional): Alternate column to search for document numbers. Defaults to "html_url".

    Raises:
        InputFileError: Raises error when no .csv files found in directory.

    Returns:
        list: List of document numbers.
    """    
    document_numbers = []
    files = (p for p in path.iterdir() if (p.is_file() and p.suffix in (".csv", ".txt", )))
    for file in files:
        document_numbers.extend(_read_csv(file, alt_column=alt_column, **kwargs))
    if len(document_numbers) == 0:
        raise InputFileError("No .csv files found in directory.")
    return list(set(document_numbers))
