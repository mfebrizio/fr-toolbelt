from .fields import FieldData


class RegInfoData(FieldData):
    """Class for processing Regulation Identifier Number (RIN) data (sourced from [RegInfo](https://www.reginfo.gov/public/jsp/Utilities/faq.jsp#dashboard)).
    Inherits from `FieldData`.
    """
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
