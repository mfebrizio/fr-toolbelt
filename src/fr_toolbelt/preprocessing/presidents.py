from .fields import FieldData


class Presidents(FieldData):
    """Class for processing president data.
    Inherits from `FieldData`.
    """    
    def __init__(
            self, 
            documents: list[dict], 
            field_key: str = "president", 
            subfield_key: str = "identifier", 
            value_key: str = "president_id", 
            schema: dict = {
                "transition_years": (1993, 2001, 2009, 2017, 2021, 2025), 
                "presidents": ("william-j-clinton", "george-w-bush", "barack-obama", "donald-trump", "joe-biden", "donald-trump"), 
                }
        ) -> None:
        super().__init__(documents=documents, field_key=field_key, subfield_key=subfield_key, value_key=value_key)
        self.schema = schema

    def _extract_field_info(self, document: dict) -> str | None:
        
        field_info = document.get(self.field_key, {})
        
        if len(field_info) == 0:
            values = None
        else:
            values = field_info.get(self.subfield_key)

        return values
