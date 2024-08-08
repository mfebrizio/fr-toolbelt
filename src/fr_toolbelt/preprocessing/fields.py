
from abc import ABC, abstractmethod


class FieldData(ABC):
    """Base class for processing Federal Register fields."""    
    def __init__(self, 
                 documents: list[dict], 
                 field_key: str | None = None,
                 subfield_key: str | None = None, 
                 subfield_keys: tuple[str] = (),
                 value_key: str | None = None,
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

    def _create_value_key(self, document: dict, values: str | None = None) -> dict:
        document_copy = document.copy() 
        document_copy.update(
            {self.value_key: values, }
            )
        return document_copy
    
    def _create_value_keys(self, document: dict, values: tuple | None = None) -> dict:

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
    
    def _del_field_key(self, document: dict, add_keys: str | tuple | list | None = None):
        document_copy = document.copy()
        if add_keys is not None:
            if isinstance(add_keys, str):
                keys = [add_keys, self.field_key]
            elif isinstance(add_keys, tuple | list):
                keys = list(add_keys) + [self.field_key]
            else:
                raise TypeError(f"Parameter add_keys must be `str`, `list`, or `tuple`; received {type(add_keys)}.")
            for key in keys:
                document_copy.pop(key, None)
        else:
            document_copy.pop(self.field_key, None)
        return document_copy
        
    def process_data(self, del_keys: str | tuple | list | None = None) -> list[dict]:
        
        if self.value_key is not None:
            return [self._del_field_key(self._create_value_key(doc, values=self._extract_field_info(doc)), add_keys=del_keys) for doc in self.documents]
        else:
            return [self._del_field_key(self._create_value_keys(doc, values=self._extract_field_info(doc)), add_keys=del_keys) for doc in self.documents]
