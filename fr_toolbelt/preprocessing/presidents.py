# no imports; all native python


class Presidents:
    def __init__(
            self, 
            documents: list[dict], 
            key: str = "president", 
            schema: dict = {
                "transition_years": (1993, 2001, 2009, 2017, 2021), 
                "presidents": ("william-j-clinton", "george-w-bush", "barack-obama", "donald-trump", "joe-biden"), 
                }
        ) -> None:
        self.documents = documents
        self.key = key
        self.schema = schema

    def __extract_president_info(self, document: dict) -> str | None:
        
        president_info = document.get(self.key, {})
        
        if len(president_info) == 0:
            values = None
        else:
            values = president_info.get("identifier")

        return values

    def __create_president_key(self, document: dict, values: str = None) -> dict:
        
        document_copy = document.copy()
        
        document_copy.update({
            "president_id": values, 
            })
        
        return document_copy
    
    def process_data(self) -> list[dict]:
        return [self.__create_president_key(doc, values=self.__extract_president_info(doc)) for doc in self.documents]


if __name__ == "__main__":
    
    pass
