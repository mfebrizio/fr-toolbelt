# fr-toolbelt

Toolbelt of classes and functions written in Python to use with the [Federal Register (FR) API](https://www.federalregister.gov/developers/documentation/api/v1).

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

```python
from fr_toolbelt.api_requests import get_documents_by_date

start = "2024-01-01"
end = "2024-01-31"
results, count = get_documents_by_date(start, end)

```

To deviate from the default set of fields, pass the fields parameter to the function call.

```python

start = "2024-01-01"
end = "2024-01-31"
fields = ["document_number", "publication_date", "raw_text_url"]
results, count = get_documents_by_date(start, end, fields=fields)

```

More customization is possible by examining the parameters and docstrings. Note that this function works around the maximum of 10,000 results per search by querying smaller subsets of documents and compiling them into a larger result set. So retrieving all [28,308 documents published in 2020](https://www.federalregister.gov/api/v1/documents.json?conditions[publication_date][year]=2020&per_page=1000) is now possible with a single function call.

To collect a particular set of documents, pass their document numbers as a parameter.

```python
from fr_toolbelt.api_requests import get_documents_by_number

document_numbers = ["2024-02204", "2023-28203", "2023-25797"]
results, count = get_documents_by_number(document_numbers)

```

These functions also handle date formatting under the hood and functionality for identifying and removing duplicate entries (not a current bug in the API if using the order=oldest or order=newest parameter).

The `api_requests` module may add support for endpoints other than the documents endpoint at a future point.

### Preprocessing module

The `preprocessing` module handles common tasks to process the API data in a usable format. Below is an example of what the raw API data look like for a single illustrative document. Notice how fields like "agencies" and "regulation_id_number_info" are nested data structures that are difficult to use in their raw form.

```JSON5
{'agencies': [{'id': 12,
               'json_url': 'https://www.federalregister.gov/api/v1/agencies/12',
               'name': 'Agriculture Department',
               'parent_id': None,
               'raw_name': 'DEPARTMENT OF AGRICULTURE',
               'slug': 'agriculture-department',
               'url': 'https://www.federalregister.gov/agencies/agriculture-department'},
              {'id': 456,
               'json_url': 'https://www.federalregister.gov/api/v1/agencies/456',
               'name': 'Rural Business-Cooperative Service',
               'parent_id': 12,
               'raw_name': 'Rural Business-Cooperative Service',
               'slug': 'rural-business-cooperative-service',
               'url': 'https://www.federalregister.gov/agencies/rural-business-cooperative-service'}],
 'agency_names': ['Agriculture Department',
                  'Rural Business-Cooperative Service'],
 'docket_ids': ['DOCKET #: RBS-23-BUSINESS-0024'],
 'dockets': [{'agency_name': 'RBS',
              'documents': [{'allow_late_comments': None,
                             'comment_count': 1,
                             'comment_end_date': '2024-04-02',
                             'comment_start_date': '2024-01-02',
                             'comment_url': 'https://www.regulations.gov/commenton/RBS-23-BUSINESS-0024-0001',
                             'id': 'RBS-23-BUSINESS-0024-0001',
                             'regulations_dot_gov_open_for_comment': True,
                             'updated_at': '2024-01-22T00:04:26.978-05:00'}],
              'id': 'RBS-23-BUSINESS-0024',
              'supporting_documents': [],
              'supporting_documents_count': 0,
              'title': 'Notice of Funding Opportunity for the Rural Innovation '
                       'Stronger Economy (RISE) Grant Program for Fiscal Year '
                       '2024'}],
 'document_number': '2023-26792',
 'president': {'identifier': 'joe-biden', 'name': 'Joseph R. Biden Jr.'},
 'publication_date': '2024-01-02',
 'regulation_id_number_info': {},
 'title': 'Notice of Solicitation of Applications for the Rural Innovation '
          'Stronger Economy (RISE) Grant Program for Fiscal Year 2024',
 'type': 'Notice'}
```

To preprocess the agency information in a set of documents, we would use the `AgencyMetadata` class to retrieve agency metadata from the API and then process the documents with the `AgencyData` class.

```python
from fr_toolbelt.preprocessing import AgencyMetadata, AgencyData

# first we collect metadata for processing the agency information
agency_metadata = AgencyMetadata()
metadata, schema = agency_metadata.get_agency_metadata()

# then we process the documents using the AgencyData class
agency_data = AgencyData(results, metadata, schema)
processed_agencies = agency_data.process_data(return_format="name")
```

Below, see how the illustrative document shown previously now contains new key: value pairs ("agency_slugs", "independent_reg_agency", "parent_name", "subagency_name") and removes the old ones ("agencies", "agency_names").

```jsonl
{'agency_slugs': ['rural-business-cooperative-service',
                  'agriculture-department'],
 'docket_ids': ['DOCKET #: RBS-23-BUSINESS-0024'],
 'dockets': [{'agency_name': 'RBS',
              'documents': [{'allow_late_comments': None,
                             'comment_count': 1,
                             'comment_end_date': '2024-04-02',
                             'comment_start_date': '2024-01-02',
                             'comment_url': 'https://www.regulations.gov/commenton/RBS-23-BUSINESS-0024-0001',
                             'id': 'RBS-23-BUSINESS-0024-0001',
                             'regulations_dot_gov_open_for_comment': True,
                             'updated_at': '2024-01-22T00:04:26.978-05:00'}],
              'id': 'RBS-23-BUSINESS-0024',
              'supporting_documents': [],
              'supporting_documents_count': 0,
              'title': 'Notice of Funding Opportunity for the Rural Innovation '
                       'Stronger Economy (RISE) Grant Program for Fiscal Year '
                       '2024'}],
 'document_number': '2023-26792',
 'independent_reg_agency': False,
 'parent_name': 'Agriculture Department',
 'president': {'identifier': 'joe-biden', 'name': 'Joseph R. Biden Jr.'},
 'publication_date': '2024-01-02',
 'regulation_id_number_info': {},
 'subagency_name': 'Rural Business-Cooperative Service',
 'title': 'Notice of Solicitation of Applications for the Rural Innovation '
          'Stronger Economy (RISE) Grant Program for Fiscal Year 2024',
 'type': 'Notice'}
```

A similar series of commands accomplishes data processing for other fields. Classes are available for preprocessing "president" (`Presidents`), "regulation_id_number_info" (`RegInfoData`), and fields related to public commenting dockets (`Dockets` and `RegDotGovData`).

Alternatively, the `process_documents` function provides a simpler interface for combining these functionalities together.

```python
from fr_toolbelt.preprocessing import process_documents

# passing the del_keys parameter deletes those keys from the resulting dict
processed_docs = process_documents(results, del_keys=("type", "docket_ids"))
```

```python
{'agency_slugs': ['rural-business-cooperative-service',
                  'agriculture-department'],
 'docket_id': 'RBS-23-BUSINESS-0024',
 'document_number': '2023-26792',
 'independent_reg_agency': False,
 'parent_slug': 'agriculture-department',
 'president_id': 'joe-biden',
 'publication_date': '2024-01-02',
 'rin': None,
 'rin_priority': None,
 'subagency_slug': 'rural-business-cooperative-service',
 'title': 'Notice of Solicitation of Applications for the Rural Innovation '
          'Stronger Economy (RISE) Grant Program for Fiscal Year 2024'}
```
