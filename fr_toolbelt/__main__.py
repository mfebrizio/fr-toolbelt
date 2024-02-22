def main():
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
    results, count = get_documents_by_date(start, end)
    print(f"Retrieved {count} documents published from {start} to {end}.")
    print("\n\n-- PRINTING AN ILLUSTRATIVE DOCUMENT BEFORE PROCESSING --\n")
    pprint(results[0])
    
    metadata, schema = AgencyMetadata().get_agency_metadata()
    agency_data = AgencyData(results, metadata, schema)
    processed_agencies = agency_data.process_data(return_format="name")
    print("\n\n-- AFTER PROCESSING AGENCIES --\n")
    pprint(processed_agencies[0])
    
    dockets = Dockets(processed_agencies)
    processed_dockets = dockets.process_data(del_keys="docket_ids")
    print("\n\n-- AFTER PROCESSING DOCKETS (REGULATIONS.GOV INFO) --\n")
    pprint(processed_dockets[0])
    
    presidents = Presidents(processed_dockets)
    processed_presidents = presidents.process_data()
    print("\n\n-- AFTER PROCESSING PRESIDENTS --\n")
    pprint(processed_presidents[0])
    
    rin = RegInfoData(processed_presidents)
    processed_rin = rin.process_data()
    print("\n\n-- AFTER PROCESSING RIN (REGINFO.GOV INFO) --\n")
    pprint(processed_rin[0])
    
    processed_docs = process_documents(results)
    print("\n\n-- AFTER PROCESSING ALL FIELDS --\n")
    pprint(processed_docs[0])

    del_keys = "type"
    processed_docs = process_documents(results, del_keys=del_keys)
    print(f"\n\n-- AFTER PROCESSING ALL FIELDS AND DELETING 1 FIELD ({del_keys}) --\n")
    pprint(processed_docs[0])

    del_keys = ("type", "docket_ids")
    processed_docs = process_documents(results, del_keys=del_keys, return_values_as_str=False, identify_ira=False)
    print(f"\n\n-- AFTER PROCESSING ALL FIELDS, DELETING 2 FIELDS ({'; '.join(del_keys)}), RETURNING AGENCY INFO AS LISTS, AND NOT IDENTIFYING INDEPENDENT REG AGENCIES --\n")
    pprint(processed_docs[0])


if __name__ == "__main__":
    print("Executing this package as a module from the command line provides a quick way to test its functionality.")
    proceed = input("Would you like to proceed? [yes/no] >>> ").lower()
    while True:
        if proceed in ("yes", "y"):
            main()
            break
        elif proceed in ("no", "n"):
            break
        else:
            proceed = input("Invalid input.\nWould you like to proceed? [yes/no] >>> ").lower()
            continue
