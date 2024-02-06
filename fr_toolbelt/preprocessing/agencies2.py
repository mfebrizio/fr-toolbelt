from types import GeneratorType


# source: https://www.law.cornell.edu/uscode/text/44/3502
INDEPENDENT_REG_AGENCIES: tuple[str] = (
    'federal-reserve-system',
    'commodity-futures-trading-commission',
    'consumer-product-safety-commission',
    'federal-communications-commission',
    'federal-deposit-insurance-corporation',
    'federal-energy-regulatory-commission',
    'federal-housing-finance-agency',
    'federal-maritime-commission',
    'federal-trade-commission',
    'interstate-commerce-commission',    
    'federal-mine-safety-and-health-review-commission',
    'national-labor-relations-board',
    'nuclear-regulatory-commission',
    'occupational-safety-and-health-review-commission',
    'postal-regulatory-commission',
    'securities-and-exchange-commission',
    'consumer-financial-protection-bureau',
    'financial-research-office',
    'comptroller-of-the-currency',
    )


class AgencyData2:
    def __init__(
        self, 
        metadata: dict[dict], 
        schema: list[str], 
        documents: list[dict], 
        field_keys: tuple[str] = ("agencies", "agency_names")
        ) -> None:
            self.documents = documents
            self.field_keys = field_keys
            metadata_results = metadata.get("results", None)
            if metadata_results is not None:
                self.metadata = metadata_results
            else:
                self.metadata = metadata
            self.schema = {
                "agencies": schema, 
                "parents": self._get_parents(), 
                "subagencies": self._get_subagencies(), 
                }

    def _get_parents(self) -> list[str]:
        """Get top-level parent agency slugs from Agency metadata.
        Only includes agencies that have no parent themselves.
        
        Returns:
            list[str]: List of agency slugs for top-level parent agencies.
        """
        return [k for k, v in self.metadata.items() if (v.get("parent_id") is None)]
    
    def _get_subagencies(self) -> list[str]:
        """Get subagency slugs from Agency metadata.
        Includes agencies that have a parent agency, even if they are a parent themselves.
        
        Returns:
            list[str]: List of agency slugs for subagencies.
        """
        return [k for k, v in self.metadata.items() if (v.get("parent_id") is not None)]

    def _return_values_as_str(self, input_values: list | tuple | set | int | float, sep: str = "; "):
        """Return values as a string (e.g., ["a", "b", "c"] -> "a; b; c", 1.23 -> "1.23").
        Converts `list`, `tuple`, `set`, `int`, or `float` to `str`; otherwise returns value unaltered.

        Args:
            input_values (list | tuple | set | int | float): Values to convert to `str`.
            sep (str, optional): Separator for joining values. Defaults to "; ".

        Returns:
            list[str]: List of converted values for assigning to DataFrame series.
        """
        return [
            sep.join(document) 
                if isinstance(document, (list, tuple, set, GeneratorType)) else 
                    (f"{document}" if isinstance(document, (int, float)) else document) 
                        for document in input_values
            ]
    
    def _get_agency_info(self, agency_slug: str, return_value_key: str) -> str | int | list | None:
        """Retrieve value of "return_value_key" from metadata `dict` associated with "agency_slug".

        Args:
            agency_slug (str): Agency slug identifier.
            return_value_key (str): Agency attributes associated with agency metadata (e.g., "name", "slug", "id", etc.).

        Returns:
            str | int | list | None: Value associated with "return_value_key" for given agency, else None.
        """
        return self.metadata.get(agency_slug, {}).get(return_value_key, None)
    
    def _extract_agency_slugs(self, document: dict):
        
        # clean slug list to only include agencies in the schema
        # there are some bad metadata -- e.g., 'interim-rule', 'formal-comments-that-were-received-in-response-to-the-nprm-regarding'
        # also ensure no duplicate agencies in each document's list by using set()
        
        agencies = document.get(self.field_keys[0], [])
        agency_names = document.get(self.field_keys[1], [])
        slugs = (agency_dict.get("slug", agency_dict.get("name", f"{agency_string}").lower().replace(" ","-")) for agency_dict, agency_string in zip(agencies, agency_names))
        return list(set(slug for slug in slugs if slug in self.schema.get("agencies")))

    def _extract_parents_subagencies(
            self, 
            document: dict, 
            slug_key: str = "agency_slugs", 
            return_format: str = None, 
            return_values_as_str: bool = True, 
            identify_ira: bool = True
        ):
        """Extract parent and subagency information from agency data and return in requested format based on API metadata.
        Supported return formats include "child_ids", "child_slugs", "description", "id", "name", "parent_id", "short_name", "slug", "url".

        Args:
            return_format (str, optional): Format of returned data (e.g., slug, numeric id, short name/acronym, name). Defaults to "slug".
            return_columns_as_str (bool, optional): Return values as a str; otherwise returns a list. Defaults to True.
        """
        if return_format is None:
            return_format = "slug"
        document_copy = document.copy()
        slugs = document_copy.get(slug_key)
        parents = (self._get_agency_info(slug, return_format) for slug in slugs if slug in self.schema.get("parents"))
        subagencies = (self._get_agency_info(slug, return_format) for slug in slugs if slug in self.schema.get("subagencies"))
        if identify_ira:
            document_copy["independent_reg_agency"] = self._identify_independent_reg_agencies(slugs)
        if return_values_as_str:
            document_copy.update({
                f"parent_{return_format}": self._return_values_as_str(parents), 
                f"subagency_{return_format}": self._return_values_as_str(subagencies), 
                })
        else:
            document_copy.update({
                f"parent_{return_format}": list(parents), 
                f"subagency_{return_format}": list(subagencies), 
                })
        return document_copy
    
    def _identify_independent_reg_agencies(
            self, 
            slugs: list[str],
            independent_agencies: list | tuple = INDEPENDENT_REG_AGENCIES, 
            return_as_bool = True
        ):
        """Identifies whether agency slugs include an independent regulatory agency, based on the definition in [44 U.S.C. 3502(5)](https://www.law.cornell.edu/uscode/text/44/3502).
        
        Args:
            new_column (str, optional): Name of new column containing indicator for independent regulatory agencies. Defaults to "independent_reg_agency".
            independent_agencies (list | tuple, optional): Schema identifying independent regulatory agencies. Defaults to INDEPENDENT_REG_AGENCIES (constant).
        """
        ira = any(True if agency in independent_agencies else False for agency in slugs)
        if return_as_bool:
            return ira
        else:
            return 1 if ira else 0
        
    def _create_agency_slugs_key(self, document: dict, value_key: str = "agency_slugs", values: list = None) -> dict:

        document_copy = document.copy()
        
        document_copy.update({
            value_key: values, 
            })
        
        return document_copy
    
    def process_data(self, return_format: str = None) -> list[dict]:
        """_summary_

        Args:
            return_format (str, optional): _description_. Defaults to None.

        Returns:
            list[dict]: _description_
        """        
        return [
            self._extract_parents_subagencies(
                self._create_agency_slugs_key(doc, values=self._extract_agency_slugs(doc)), 
                return_format=return_format
                ) 
            for doc in self.documents
            ]


if __name__ == "__main__":
    
    from pprint import pprint
    
    from agencies import AgencyMetadata
    
    agencies_metadata = AgencyMetadata()
    agencies_metadata.get_metadata()
    agencies_metadata.transform()
    agencies_metadata.get_schema()
    #print(dir(agencies_metadata))

    import requests
    url = r"https://www.federalregister.gov/api/v1/documents.json?fields[]=agencies&fields[]=agency_names&fields[]=document_number&fields[]=json_url&fields[]=type&per_page=1000&conditions[publication_date][is]=2024-02-05"
    res = requests.get(url).json()["results"]
    
    test_instance = AgencyData2(
        metadata=agencies_metadata.transformed_data, 
        schema=agencies_metadata.schema, 
        documents=res
        )
    #print(dir(test_instance))
    
    #print(parent_slugs)
    #print(subagency_slugs)
    #pprint(test_instance.metadata.get("action"))
    documents = test_instance.process_data(return_format="name")
    pprint(set((k for d in documents for k in d)))
