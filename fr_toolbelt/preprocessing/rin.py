# no imports; all native python


class RegInfoData:
    
    def __init__(self, 
                 documents: list[dict], 
                 field_key: str = "regulation_id_number_info", 
                 subfield_keys: tuple[str] = ("priority_category", "issue"), 
                 
                 ) -> None:
        self.documents = documents
        self.field_key = field_key

    def __extract_rin_info(self, document: dict) -> tuple:
        
        rin_info = document.get(self.key, {})
        
        tuple_list = []
        if len(rin_info)==0:
            tuple_list.append(None)
        else:
            for k, v in rin_info.items():
                if v:
                    n_tuple = (k, v.get('priority_category'), v.get('issue'))
                else:
                    n_tuple = (k, '', '')
                    
            tuple_list.append(n_tuple)
            try:
                tuple_list.sort(reverse=True, key=lambda x: x[2])
            except IndexError:
                pass
        
        # only return RIN info from most recent Unified Agenda issue
        return tuple_list[0]

    def __create_rin_keys(self, document: dict, values: tuple = None) -> dict:

        document_copy = document.copy()
        
        # values: rin_info tuples (RIN, Priority, UA issue)
        if values is None:
            document_copy.update({
                "rin": None, 
                "rin_priority": None, 
                })
        else:
            document_copy.update({
                "rin": values[0], 
                "rin_priority": values[1], 
                })
        
        return document_copy
    
    def process_data(self) -> list[dict]:
        return [self.__create_rin_keys(doc, values=self.__extract_rin_info(doc)) for doc in self.documents]


if __name__ == "__main__":
    
    pass
