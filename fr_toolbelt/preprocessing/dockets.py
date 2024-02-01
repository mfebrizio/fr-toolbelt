from .fields import FieldData


class RegsDotGovData(FieldData):

    def __init__(self, 
                 documents: list[dict], 
                 field_key: str = "regulations_dot_gov_info",
                 subfield_key: str = "docket_id", 
                 value_key: str = None
                 ) -> None:
        super().__init__(documents=documents, field_key=field_key, subfield_key=subfield_key)
        if value_key is None:
            self.value_key = subfield_key
        else:
            self.value_key = value_key

    def _extract_field_info(self, document: dict) -> str | None:
        
        docket_info = document.get(self.field_key, {})
        
        if len(docket_info) == 0:
            values = None
        elif isinstance(docket_info, list):
            values = [docket.get(self.subfield_key) for docket in docket_info]
        elif isinstance(docket_info, dict):
            values = [docket_info.get(self.subfield_key)]

        if values is not None:
            values = "; ".join(v for v in values if v is not None)
        
        return values


if __name__ == "__main__":
    
    test_documents = [{f"{n}": n} for n in range(10)]
    test_instance = RegsDotGovData(test_documents)
    print(type(test_instance))
    print(dir(test_instance))
