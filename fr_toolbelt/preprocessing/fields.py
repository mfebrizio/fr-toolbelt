
from abc import ABC, abstractmethod


class FieldData(ABC):
    def __init__(self, 
                 documents: list[dict], 
                 field_key: str = None,
                 subfield_key: str = None, 
                 subfield_keys: tuple[str] = (),
                 value_key: str = None,
                 value_keys: tuple[str] = ()
                 ) -> None:
        self.documents = documents
        self.field_key = field_key
        self.subfield_key = subfield_key
        self.subfield_keys = subfield_keys
        self.value_key = value_key
        self.value_keys = value_keys
    
    @abstractmethod
    def _extract_field_info(self, document: dict):
        pass

    def _create_value_key(self, document: dict, values: str = None) -> dict:
        document_copy = document.copy()
            
        document_copy.update(
            {self.value_key: values, }
            )
        
        return document_copy
    
    def _create_value_keys(self, document: dict, values: tuple = None) -> dict:

        document_copy = document.copy()
        
        # values: rin_info tuples (RIN, Priority, UA issue)
        if values is None:
            document_copy.update(
                {k: None for k in self.value_keys}
                )
        else:
            document_copy.update(
                {k: v for k, v in zip(self.value_keys, values)}
                )
        
        return document_copy
    
    def process_data(self) -> list[dict]:
        if self.value_key is not None:
            return [self._create_value_key(doc, values=self._extract_field_info(doc)) for doc in self.documents]
        else:
            return [self._create_value_keys(doc, values=self._extract_field_info(doc)) for doc in self.documents]
