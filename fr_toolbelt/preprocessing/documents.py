
from .dockets import RegsDotGovData
from .presidents import Presidents
from .rin import RegInfoData


class PreprocessingError:
    pass


def process_documents(documents: list[dict], which: str = "all"):

    clean_fields = {
        "dockets": RegsDotGovData, 
        "presidents": Presidents, 
        "rin": RegInfoData, 
        }
    
    if which == "all":
    
        for v in clean_fields.values():
            documents = v(documents).process_data()
    
    elif which in (clean_fields.keys()):
        documents = clean_fields[which](documents).process_data()
    
    else:
        raise PreprocessingError
    
    return documents
    
    


#class FedRegData(RegsDotGovData, ):
    
