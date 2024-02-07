try:
    from .fields import FieldData
except ImportError:
    from fields import FieldData


class RegInfoData(FieldData):
    
    def __init__(self, 
                 documents: list[dict], 
                 field_key: str = "regulation_id_number_info", 
                 subfield_keys: tuple[str] = ("priority_category", "issue"), 
                 value_keys: tuple[str] = ("rin", "rin_priority")
                 ) -> None:
        super().__init__(documents=documents, field_key=field_key, subfield_keys=subfield_keys, value_keys=value_keys)

    def _extract_field_info(self, document: dict) -> tuple:
        
        field_info = document.get(self.field_key, {})
        
        tuple_list = []
        if len(field_info)==0:
            tuple_list.append(None)
        else:
            for k, v in field_info.items():
                if v:
                    n_tuple = (k, v.get(self.subfield_keys[0]), v.get(self.subfield_keys[1]))
                else:
                    n_tuple = (k, "", "")
                    
            tuple_list.append(n_tuple)
            try:
                tuple_list.sort(reverse=True, key=lambda x: x[2])
            except IndexError:
                pass
        
        # only return RIN info from most recent Unified Agenda issue
        return tuple_list[0]


if __name__ == "__main__":
    
    test_documents = [{f"{n}": n} for n in range(10)]
    test_instance = RegInfoData(test_documents)
    print(type(test_instance))
    print(dir(test_instance))
    print(test_instance.field_key, 
          test_instance.subfield_keys, 
          test_instance.value_keys)
