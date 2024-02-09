from copy import deepcopy
from datetime import date
from pathlib import Path
import re

from pandas import DataFrame, read_csv, read_excel
import requests

from .duplicates import identify_duplicates
from .format_dates import DateFormatter


BASE_PARAMS = {
    'per_page': 1000, 
    "page": 0, 
    'order': "oldest"
    }
BASE_URL = r'https://www.federalregister.gov/api/v1/documents.json?'


# -- functions for handling API requests -- #


class QueryError(Exception):
    pass


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
        results_this_page = response.json()["results"]
        results.extend(results_this_page)
        tally += len(results_this_page)
    count = response.json()["count"]
    print(count, tally)
    return results, count


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
    response = requests.get(endpoint_url, params=dict_params).json()
    pages = response.get("total_pages", 1)
    next_page_url = response.get("next_page_url")
    counter = 0
    while next_page_url is not None:
        counter += 1
        results_this_page = response["results"]
        results.extend(results_this_page)
        response = requests.get(next_page_url).json()
        next_page_url = response.get("next_page_url")
    else:
        counter += 1
        results_this_page = response["results"]
        results.extend(results_this_page)
    
    # raise exception if failed to access all pages
    if counter != pages:
        raise QueryError(f"Failed to retrieve documents from {pages} pages.")
    
    return results


def _query_documents_endpoint(endpoint_url: str, dict_params: dict):
    """GET request for documents endpoint.

    Args:
        endpoint_url (str): URL for API endpoint.
        dict_params (dict): Paramters to pass in GET request.

    Returns:
        tuple[list, int]: Tuple of API results, count of documents retrieved.
    """    
    results, count = [], 0
    response = requests.get(endpoint_url, params=dict_params).json()
    max_documents_threshold = 10000
    
    # handles queries returning no documents
    if response["count"] == 0:
        pass
    
    # handles queries that need multiple requests
    elif response["count"] > max_documents_threshold:
        
        # get range of dates
        start_date = DateFormatter(dict_params.get("conditions[publication_date][gte]"))
        end_date = DateFormatter(dict_params.get("conditions[publication_date][lte]"))
        
        # set range of years
        start_year = start_date.get_year()  #extract_year(start_date)
        if end_date is None:
            end_date = date.today()
            end_year = end_date.year
        else:
            end_year = end_date.get_year()
        years = range(start_year, end_year + 1)
        
        # format: YYYY-MM-DD
        quarter_tuples = (
            ("01-01", "03-31"), ("04-01", "06-30"), 
            ("07-01", "09-30"), ("10-01", "12-31")
            )
        
        # retrieve documents
        dict_params_qrt = deepcopy(dict_params)
        for year in years:
            for quarter in quarter_tuples:            
                results_qrt = []
                
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
                count += response["count"]
    
    # handles normal queries
    elif response["count"] in range(max_documents_threshold + 1):
        count += response["count"]
        results.extend(_retrieve_results_by_next_page(endpoint_url, dict_params))
    
    # otherwise something went wrong
    else:
        raise QueryError(f"Query returned document count of {response['count']}.")

    duplicates = identify_duplicates(results, key="document_number")
    count_dups = len(duplicates)
    if count_dups > 0:
        raise QueryError(f"API request returned {count_dups} duplicate values.")
    
    return results, count


# -- retrieve documents using date range -- #


def get_documents_by_date(start_date: str, 
                          end_date: str | None = None, 
                          fields: tuple = ('document_number', 
                                           'publication_date', 
                                           'agency_names', 
                                           'agencies', 
                                           'citation', 
                                           'start_page', 
                                           'end_page', 
                                           'html_url', 
                                           'pdf_url', 
                                           'title', 
                                           'type', 
                                           'action', 
                                           'regulation_id_number_info', 
                                           'correction_of'),
                          endpoint_url: str = BASE_URL, 
                          dict_params: dict = BASE_PARAMS):
    """Retrieve Federal Register documents using a date range.

    Args:
        start_date (str): Start date when documents were published (inclusive; format must be 'yyyy-mm-dd').
        end_date (str | None, optional): End date (inclusive; format must be 'yyyy-mm-dd'). Defaults to None (implies end date is `datetime.date.today()`).
        fields (tuple, optional): Fields/columns to retrieve. Defaults to ('document_number', 'publication_date', 'agency_names', 'agencies', 'citation', 'start_page', 'end_page', 'html_url', 'pdf_url', 'title', 'type', 'action', 'regulation_id_number_info', 'correction_of').
        endpoint_url (_type_, optional): Endpoint url. Defaults to r'https://www.federalregister.gov/api/v1/documents.json?'.

    Returns:
        tuple[list, int]: Tuple of API results, count of documents retrieved.
    """
    # update dictionary of parameters
    dict_params.update({
        'conditions[publication_date][gte]': f'{start_date}', 
        'fields[]': fields
        })
    
    # empty strings '' are falsey in Python: https://docs.python.org/3/library/stdtypes.html#truth-value-testing
    if end_date:
        dict_params.update({'conditions[publication_date][lte]': f"{end_date}"})
    
    results, count = _query_documents_endpoint(endpoint_url, dict_params)
    return results, count


# -- retrieve documents using input file -- #


def get_documents_by_number(document_numbers: list, 
                            fields: tuple = ('document_number', 
                                             'publication_date', 
                                             'agency_names', 
                                             'agencies', 
                                             'citation', 
                                             'start_page', 
                                             'end_page', 
                                             'html_url', 
                                             'pdf_url', 
                                             'title', 
                                             'type', 
                                             'action', 
                                             'regulation_id_number_info', 
                                             'correction_of'), 
                            sort_data: bool = True
                            ):
    """Retrieve Federal Register documents using a list of document numbers.

    Args:
        document_numbers (list): Documents to retrieve based on 'document_number' field.
        fields (tuple, optional): Fields/columns to retrieve. Defaults to ('document_number', 'publication_date', 'agency_names', 'agencies', 'citation', 'start_page', 'end_page', 'html_url', 'pdf_url', 'title', 'type', 'action', 'regulation_id_number_info', 'correction_of').
        sort_data (bool, optional): Sort documents by 'document_number'. Defaults to True.

    Returns:
        tuple[list, int]: Tuple of API results, count of documents retrieved.
    """    
    if sort_data:
        document_numbers_str = ",".join(sorted(document_numbers))
    else:
        document_numbers_str = ",".join(document_numbers)
    
    endpoint_url = fr'https://www.federalregister.gov/api/v1/documents/{document_numbers_str}.json?'
    dict_params = {'fields[]': fields}
    results, count = _query_documents_endpoint(endpoint_url, dict_params)
    return results, count


def _extract_document_numbers(
        df: DataFrame, 
        pattern: str = r"(?:[a-z]\d-)?[\w|\d]{2,4}-[\d]{5,}", 
        alt_column: str = "html_url"
    ) -> list[str]:
    r"""Extract list of Federal Register document numbers from a DataFrame.

    Args:
        df (DataFrame): Input data.
        pattern (str, optional): Regex pattern for identifying document numbers from url. 
        Defaults to r"(?:[a-z]\d-)?[\w|\d]{2,4}-[\d]{5,}".

    Returns:
        list[str]: List of document numbers.
    """
    if 'document_number' in df.columns:
        document_numbers = [f"{doc}".strip() for doc in df.loc[:, 'document_number'].to_numpy()]
    else:
        url_list = df.loc[:, alt_column].to_numpy()
        document_numbers = [re.search(pattern, url).group(0) for url in url_list]
    
    return document_numbers


def parse_document_numbers(path: Path):
    """Parse Federal Register document numbers from input data file.

    Args:
        path (Path): Path to input file.

    Raises:
        ValueError: Raises error when input file is not CSV or Excel spreadsheet.

    Returns:
        list: List of document numbers.
    """    
    file = next(p for p in path.iterdir() if (p.is_file() and p.name != ".gitignore"))
    if file.suffix in (".csv", ".txt", ".tsv"):
        with open(file, "r") as f:
            df = read_csv(f)
    elif file.suffix in (".xlsx", ".xls", ".xlsm"):
        with open(file, "rb") as f:
            df = read_excel(f)
    else:
        raise ValueError("Input file must be CSV or Excel spreadsheet.")
    
    return _extract_document_numbers(df)


if __name__ == "__main__":
    
    pass
