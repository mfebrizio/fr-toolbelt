from fr_toolbelt.preprocessing import process_documents


if __name__ == "__main__":

    from pprint import pprint
    
    import requests
    url = r"https://www.federalregister.gov/api/v1/documents.json?fields[]=agencies&fields[]=agency_names&fields[]=document_number&fields[]=json_url&fields[]=type&per_page=1000&conditions[publication_date][is]=2024-02-05"
    res = requests.get(url).json()["results"]
    
    documents = process_documents(res)
    pprint(set((k for d in documents for k in d)))
    pprint(documents[0])
