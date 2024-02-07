# fr-toolbelt

Toolbelt of classes and functions written in Python to use with the Federal Register (FR) API.

Name inspired by the [Requests Toolbelt](https://github.com/requests/toolbelt).

## Installation

ADD.

## Basic Usage

The FR toolbelt contains two modules:

- `api_requests` for requesting documents from the Federal Register API.
- `preprocessing` for processing Federal Register documents to further analyze.

### API requests module

The `api_requests` module makes it easy to retrieve FR documents from the API by specifying a date range or providing a list of document numbers (`document_number` is the unique identifier for each document).

A simple request for documents published in January 2024 requires a start and end date and returns a tuple of the list of results and the count of retrieved documents.

```{python}
from fr_toolbelt.api_requests import get_documents_by_date

start = "2024-01-01"
end = "2024-01-31"
results, count = get_documents_by_date(start, end)

```

Note that this function works around the maximum of 10,000 results per search by querying smaller subsets of documents and compiling them into a larger result set. So retrieving all [28,308 documents published in 2020](https://www.federalregister.gov/api/v1/documents.json?conditions[publication_date][year]=2020&per_page=1000) is now possible with a single function call.

To collect a particular set of documents, pass their document numbers as a parameter.

```{python}
from fr_toolbelt.api_requests import get_documents_by_number

document_numbers = ["2024-02204", "2023-28203", "2023-25797"]
results, count = get_documents_by_number(document_numbers)

```

These functions also handle date formatting under the hood and functionality for identifying and removing duplicate entries (not a current bug in the API if using the order=oldest or order=newest parameter).

The `api_requests` module may add support for endpoints other than the documents endpoint at a future point.

### Preprocessing module

```{json}
{'action': 'Proposed rule.',
 'agencies': [{'id': 54,
               'json_url': 'https://www.federalregister.gov/api/v1/agencies/54',
               'name': 'Commerce Department',
               'parent_id': None,
               'raw_name': 'DEPARTMENT OF COMMERCE',
               'slug': 'commerce-department',
               'url': 'https://www.federalregister.gov/agencies/commerce-department'},
              {'id': 241,
               'json_url': 'https://www.federalregister.gov/api/v1/agencies/241',
               'name': 'Industry and Security Bureau',
               'parent_id': 54,
               'raw_name': 'Bureau of Industry and Security',
               'slug': 'industry-and-security-bureau',
               'url': 'https://www.federalregister.gov/agencies/industry-and-security-bureau'}],
 'agency_names': ['Commerce Department', 'Industry and Security Bureau'],
 'citation': '89 FR 8363',
 'correction_of': None,
 'document_number': '2024-01930',
 'end_page': 8377,
 'html_url': 'https://www.federalregister.gov/documents/2024/02/07/2024-01930/clarifications-and-updates-to-defense-priorities-and-allocations-system-regulation',
 'pdf_url': 'https://www.govinfo.gov/content/pkg/FR-2024-02-07/pdf/2024-01930.pdf',
 'publication_date': '2024-02-07',
 'regulation_id_number_info': {'0694-AJ15': {'html_url': 'https://www.federalregister.gov/regulations/0694-AJ15/clarifications-and-updates-to-defense-priorities-and-allocations-system-regulation',
                                             'issue': '202310',
                                             'priority_category': 'Substantive, '
                                                                  'Nonsignificant',
                                             'title': 'Clarifications and '
                                                      'Updates to Defense '
                                                      'Priorities and '
                                                      'Allocations System '
                                                      'Regulation',
                                             'xml_url': 'http://www.reginfo.gov/public/do/eAgendaViewRule?pubId=202310&RIN=0694-AJ15&operation=OPERATION_EXPORT_XML'}},
 'start_page': 8363,
 'title': 'Clarifications and Updates to Defense Priorities and Allocations '
          'System Regulation',
 'type': 'Proposed Rule'}
```
