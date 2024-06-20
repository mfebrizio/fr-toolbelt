from .agencies import AgencyMetadata, AgencyData
from .dockets import RegsDotGovData, Dockets
from .presidents import Presidents
from .rin import RegInfoData


class PreprocessingError:
    pass


def process_documents(
        documents: list[dict], 
        which: str | list | tuple = "all", 
        docket_data_source: str = "dockets", 
        del_keys: str | list | tuple = None, 
        **kwargs
    ) -> list[dict]:
    """Process one or more fields in each document.

    Args:
        documents (list[dict]): Documents to process.
        which (str | list | tuple, optional): Which fields to process per document. Defaults to "all". Valid inputs include "all" or some combination of "agencies", "dockets", "presidents", "rin".
        docket_data_source (str, optional): Select which field to use as a source for processing dockets data. Defaults to "dockets". Valid inputs include "regulations_dot_gov_info" and "dockets".
        del_keys (str | list | tuple, optional): Delete select keys from results. Defaults to None.

    Raises:
        PreprocessingError: Failed to preprocess input documents.

    Returns:
        list[dict]: Processed documents.
    """
    # dictionary of alternative sources
    source_dict = {
        "dockets": Dockets, 
        "regulations_dot_gov_info": RegsDotGovData
        }
    
    # maps keyword to class
    process_fields = {
        "agencies": AgencyData, 
        "dockets": source_dict.get(docket_data_source, Dockets), 
        "presidents": Presidents, 
        "rin": RegInfoData, 
        }
    
    # process documents
    if (which == "all") or ("all" in which and isinstance(which, (list, tuple))):
    
        for field, function in process_fields.items():
            if field == "agencies":
                metadata, schema = AgencyMetadata().get_agency_metadata()
                documents = function(documents, metadata, schema).process_data(**kwargs)
            else:
                documents = function(documents).process_data()
    
    elif isinstance(which, str) and (which in process_fields.keys()):
        if which == "agencies":
            metadata, schema = AgencyMetadata().get_agency_metadata()
            documents = process_fields[which](documents, metadata, schema).process_data(**kwargs)
        else:
            documents = process_fields[which](documents).process_data()
    
    elif isinstance(which, (list, tuple)):
        valid_fields = (w for w in which if w in process_fields.keys())
        for field in valid_fields:
            if field == "agencies":
                metadata, schema = AgencyMetadata().get_agency_metadata()
                documents = process_fields[field](documents, metadata, schema).process_data(**kwargs)
            else:
                documents = process_fields[field](documents).process_data()
    
    else:
        raise PreprocessingError("Failed to preprocess input documents.")
    
    # delete keys if passed
    if del_keys is not None:
        return [{k: v for k, v in doc.items() if ((k != del_keys) and (k not in del_keys))} for doc in documents]
    else:
        return documents
