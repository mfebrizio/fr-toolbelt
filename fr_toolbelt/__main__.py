if __name__ == "__main__":

    from pprint import pprint

    from fr_toolbelt.api_requests import (
        get_documents_by_date, 
    )

    from fr_toolbelt.preprocessing import (
        process_documents, 
        AgencyMetadata, 
        AgencyData, 
        Dockets, 
        Presidents, 
        RegInfoData, 
    )
    
    start = "2024-01-01"
    end = "2024-01-31"
    fields = [
        "document_number", 
        "publication_date", 
        "agency_names", 
        "agencies", 
        "title", 
        "type", 
        "regulation_id_number_info", 
        #"regulations_dot_gov_info", 
        "dockets", 
        "docket_ids", 
        "president", 
        ]
    results, count = get_documents_by_date(start, end, fields=fields)
    print("\n\n-- RAW --\n")
    pprint(results[0])
    
    metadata, schema = AgencyMetadata().get_agency_metadata()
    agency_data = AgencyData(results, metadata, schema)
    processed_agencies = agency_data.process_data(return_format="name")
    print("\n\n-- AGENCIES --\n")
    pprint(processed_agencies[0])
    
    dockets = Dockets(processed_agencies)
    processed_dockets = dockets.process_data(del_keys="docket_ids")
    print("\n\n-- DOCKETS --\n")
    pprint(processed_dockets[0])
    
    presidents = Presidents(processed_dockets)
    processed_presidents = presidents.process_data()
    print("\n\n-- PRESIDENTS --\n")
    pprint(processed_presidents[0])
    
    rin = RegInfoData(processed_presidents)
    processed_rin = rin.process_data()
    print("\n\n-- RIN --\n")
    pprint(processed_rin[0])
    
    processed_docs = process_documents(results)
    print("\n\n-- ALL --\n")
    pprint(processed_docs[0])

    processed_docs = process_documents(results, del_keys="type")
    print("\n\n-- ALL (del 1 key) --\n")
    pprint(processed_docs[0])

    processed_docs = process_documents(results, del_keys=("type", "docket_ids"), return_values_as_str=False, identify_ira=False)
    print("\n\n-- ALL (del 2 keys) --\n")
    pprint(processed_docs[0])
