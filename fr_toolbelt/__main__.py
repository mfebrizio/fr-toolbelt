if __name__ == "__main__":

    from pprint import pprint

    from fr_toolbelt.api_requests import (
        get_documents_by_date, get_documents_by_number,     
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
    pprint(results[0])
    
    metadata, schema = AgencyMetadata().get_agency_metadata()
    agency_data = AgencyData(results, metadata, schema)
    processed_agencies = agency_data.process_data()
    print("\n\n-- AGENCIES --\n")
    pprint(processed_agencies[0])
    
    dockets = Dockets(processed_agencies)
    processed_dockets = dockets.process_data()
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
    
    #documents = process_documents(res)
    #pprint(set((k for d in documents for k in d)))
    #pprint(documents[0])
