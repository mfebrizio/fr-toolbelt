from datetime import date
import re


class DateFormatError(Exception):
    pass


class DateFormatter:
    
    def __init__(self, input_date: date | str) -> None:
        self.input_date = input_date
        self.formatted_date: date = self.__convert_to_datetime_date(input_date)
        self.year: int | None = self.formatted_date.year
        self.quarter_schema = {
            "Q1": ("01-01", "03-31"), 
            "Q2": ("04-01", "06-30"), 
            "Q3": ("07-01", "09-30"), 
            "Q4": ("10-01", "12-31"), 
            }
    
    def __extract_year(self, input_date: str | date):
        """Extract year from a string in a format similar to `datetime.datetime` or `datetime.date`.

        Args:
            alt_input_date (str | date): String of date.
        
        Returns:
            int: Year attribute of `datetime.date` object.
        """
        if isinstance(input_date, str):
            res = re.compile(r"\d{4}-\d{2}-\d{2}", re.I).match(input_date)
            if isinstance(res, re.Match):
                year = date.fromisoformat(res[0]).year
        elif isinstance(input_date, date):
            year = input_date.year
        else:
            year = None
        
        return year

    def __convert_to_datetime_date(self, input_date: date | str) -> date:
        """Converts `self.input_date` from `str` to `datetime.date`. Returns input if already in proper format.
        Input string should be in any valid ISO 8601 format (e.g., for Jan. 1, 2024 -> 2024-01-01, 20240101, 2024-W01-1).

        Raises:
            TypeError: Inappropriate argument type for input_date parameter.

        Returns:
            date: Date object.
        """    
        if isinstance(input_date, date):
            return input_date
        elif isinstance(input_date, str):
            return date.fromisoformat(input_date)
        else:
            raise TypeError(f"Inappropriate argument type {type(input_date)} for parameter 'input_date'.")

    def get_formatted_date(self) -> date:
        """Get `self.formatted_date` instance attribute.

        Returns:
            date: Formatted version of input date.
        """
        return self.formatted_date
    
    def get_year(self, alt_input_date: str | date = None) -> int:
        """Get `self.year` instance attribute

        Returns:
            int: Year of input date.
        """
        if alt_input_date is not None:
            return self.__extract_year(input_date=alt_input_date)
        else:
            return self.year
    
    def date_in_quarter(self, check_year: str, check_quarter: str, return_quarter_end: bool = True) -> date:
        """Checks if given date falls within a year's quarter. 
        Returns input date if True, otherwise returns first or last day of quarter.

        Args:
            input_date (date | str): Date to check.
            year (str): Year to check against.
            quarter (tuple): Quarter to check against.
            return_quarter_end (bool, optional): Return end date of quarter when input not in range. Defaults to True.

        Raises:
            TypeError: Inappropriate argument type for 'input_date'.

        Returns:
            datetime.date: Returns input_date when it falls within range; otherwise returns boundary date of quarter.
        """
        quarter_range = self.quarter_schema.get(f"{check_quarter}".upper())
        check_date = self.__convert_to_datetime_date(self.input_date)
        range_start = date.fromisoformat(f"{check_year}-{quarter_range[0]}")
        range_end = date.fromisoformat(f"{check_year}-{quarter_range[1]}")
        in_range = (check_date >= range_start) and (check_date <= range_end)
        #return in_range
        if in_range:
            return check_date
        elif (not in_range) and return_quarter_end:
            return range_end
        elif (not in_range) and (not return_quarter_end):
            return range_start
        else:
            raise DateFormatError

    def greater_than_date(self, comparison_date: date | str, inclusive: bool = False) -> bool:
        """Compare whether a formatted date occurs after a given comparison date.

        Args:
            comparison_date (date | str): A given date to compare with the formatted date.

        Returns:
            bool: True if formatted date occurs after comparison date.
        """    
        if inclusive:
            return self.formatted_date >= self.__convert_to_datetime_date(comparison_date)
        else:
            return self.formatted_date > self.__convert_to_datetime_date(comparison_date)
    
    def less_than_date(self, comparison_date: date | str, inclusive: bool = False) -> bool:
        """Compare whether a formatted date occurs after a given comparison date.

        Args:
            comparison_date (date | str): A given date to compare with the formatted date.

        Returns:
            bool: True if formatted date occurs before comparison date.
        """
        if inclusive:
            return self.formatted_date <= self.__convert_to_datetime_date(comparison_date)
        else:
            return self.formatted_date < self.__convert_to_datetime_date(comparison_date)
