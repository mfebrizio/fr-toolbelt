from .fields import FieldData


class RegsDotGovData(FieldData):
    """Class for processing docket data sourced from Regulations.gov.
    Inherits from `FieldData`.
    """
    def __init__(self, 
                 documents: list[dict], 
                 field_key: str = "regulations_dot_gov_info",
                 subfield_key: str = "docket_id", 
                 value_key: str | None = None
                 ) -> None:
        super().__init__(documents=documents, field_key=field_key, subfield_key=subfield_key)
        if value_key is None:
            self.value_key = subfield_key
        else:
            self.value_key = value_key

    def _extract_field_info(self, document: dict) -> str | None:
        
        field_info = document.get(self.field_key, {})
        
        if len(field_info) == 0:
            values = None
        elif isinstance(field_info, list):
            values = [docket.get(self.subfield_key) for docket in field_info]
        elif isinstance(field_info, dict):
            values = [field_info.get(self.subfield_key)]

        if values is not None:
            #print(values)
            try_alt = all(("FRDOC" in v) for v in values if v is not None)
            if try_alt:
                values = self._try_alt_key(document)
            else:
                values = "; ".join(v for v in values if v is not None)
        
        return values
    
    def _try_alt_key(self, document: dict, alt_key: str = "docket_ids") -> str | None:
        
        field_info = document.get(alt_key, {})
        
        if len(field_info) == 0:
            values = None
        elif isinstance(field_info, list):
            values = field_info
        
        if values is not None:
            values = "; ".join(v for v in values if "FRDOC" not in v)
        
        return values


class Dockets(RegsDotGovData):
    """Class for processing docket data from "dockets" field.
    Inherits from `RegsDotGovData`.
    """
    def __init__(self, 
                 documents: list[dict], 
                 field_key: str = "dockets", 
                 subfield_key: str = "id", 
                 value_key: str = "docket_id"
                 ) -> None:
        super().__init__(documents=documents, field_key=field_key, subfield_key=subfield_key, value_key=value_key)
