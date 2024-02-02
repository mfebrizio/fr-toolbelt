try:
    from .fields import FieldData
except ImportError:
    from fields import FieldData


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
        
        field_info = document.get(self.field_key, {})
        
        if len(field_info) == 0:
            values = None
        elif isinstance(field_info, list):
            values = [docket.get(self.subfield_key) for docket in field_info]
        elif isinstance(field_info, dict):
            values = [field_info.get(self.subfield_key)]

        if values is not None:
            values = "; ".join(v for v in values if v is not None)
        
        return values


class Dockets(RegsDotGovData):
    def __init__(self, 
                 documents: list[dict], 
                 field_key: str = "dockets", 
                 subfield_key: str = "id", 
                 value_key: str = "docket_id"
                 ) -> None:
        super().__init__(documents=documents, field_key=field_key, subfield_key=subfield_key, value_key=value_key)


if __name__ == "__main__":
    
    #test_documents = [{f"{n}": n} for n in range(10)]
    #test_instance = RegsDotGovData(test_documents)
    #print(type(test_instance))
    #print(dir(test_instance))

    test_documents = [{f"{n}": n} for n in range(10)]
    test_instance = Dockets(test_documents)
    print(type(test_instance))
    print(dir(test_instance))
    print(test_instance.field_key, test_instance.subfield_key, test_instance.value_key)
