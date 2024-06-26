from datetime import date
from fr_toolbelt.utils import DateFormatter


def test__convert_to_datetime_date(
        success = ("2024-01-01", "20240101", "2024-W01-1", date(2024, 1, 1))
    ):
    
    for attempt in success:
        fdate = DateFormatter(attempt)
        result = fdate._DateFormatter__convert_to_datetime_date(attempt)
        assert isinstance(result, date)


def test_get_year_self(
        input_success: dict = {"string": "2023-01-01", "year": 2023}, 
        input_fail: str = "01/01/2023"
    ):
    
    fdate = DateFormatter(input_success.get("string"))
    year = fdate.get_year()
    assert isinstance(year, int)
    assert year == input_success.get("year")
    
    try:
        DateFormatter(input_fail).get_year()
    except ValueError as e:
        assert e.__class__ == ValueError


def test_get_year_alt(
        input_success: dict = {
            1: {"string": "2023-01-01", "year": 2023}, 
            2: {"string": "2024-01-01", "year": 2024}
            }
    ):
    
    fdate = DateFormatter(input_success.get(1).get("string"))
    year = fdate.get_year(input_success.get(2).get("string"))
    assert isinstance(year, int)
    assert year == input_success.get(2).get("year")


def test_get_formatted_date(
        success = ("2024-01-01", "20240101", "2024-W01-1", date(2024, 1, 1))
    ):
    for attempt in success:
        result = DateFormatter(attempt).get_formatted_date()
        assert isinstance(result, date)


def test_date_in_quarter():
    
    attempt1, attempt2, year, quarter = date(2023, 1, 1), date(2023, 4, 1), "2023", "Q1"
    
    fdate1 = DateFormatter(attempt1)
    result = fdate1.date_in_quarter(year, quarter)
    assert attempt1 == result
    
    fdate2 = DateFormatter(attempt2)
    result = fdate2.date_in_quarter(year, quarter)
    assert attempt2 != result
    assert f"{result}" == f"{year}-{fdate2.quarter_schema.get(quarter)[1]}", "should return end of Q1"
    
    result = fdate2.date_in_quarter(year, quarter, return_quarter_end=False)
    assert attempt2 != result
    assert f"{result}" == f"{year}-{fdate2.quarter_schema.get(quarter)[0]}", "should return beginning of Q1"


def test_gt_date_exclusive(inputs = {
        "earlier": date(2023, 1, 1), 
        "later": date(2023, 4, 1)}
    ):
    fdate = DateFormatter(inputs.get("later"))
    res = fdate.greater_than_date(inputs.get("earlier"))
    assert res, "later > earlier"
    res2 = fdate.greater_than_date(inputs.get("later"))
    assert not res2, "later !> later (exclusive)"
    
    fdate = DateFormatter(inputs.get("earlier"))
    res = fdate.greater_than_date(inputs.get("later"))
    assert not res, "earlier !> later"
    res2 = fdate.greater_than_date(inputs.get("earlier"))
    assert not res2, "earlier !> earlier (exclusive)"


def test_gt_date_inclusive(inputs = {
        "earlier": date(2023, 1, 1), 
        "later": date(2023, 4, 1)
        }
    ):
    fdate = DateFormatter(inputs.get("later"))
    res = fdate.greater_than_date(inputs.get("later"), inclusive=True)
    assert res, "later == later (inclusive)"
    
    fdate = DateFormatter(inputs.get("earlier"))
    res = fdate.greater_than_date(inputs.get("earlier"), inclusive=True)
    assert res, "earlier == earlier (inclusive)"


def test_lt_date_exclusive(inputs = {
        "earlier": date(2023, 1, 1), 
        "later": date(2023, 4, 1)
        }
    ):
    fdate = DateFormatter(inputs.get("later"))
    res = fdate.less_than_date(inputs.get("earlier"))
    assert not res, "later !< earlier"
    res2 = fdate.less_than_date(inputs.get("later"))
    assert not res2, "later !< later (exclusive)"
    
    fdate = DateFormatter(inputs.get("earlier"))
    res = fdate.less_than_date(inputs.get("later"))
    assert res, "earlier < later"
    res2 = fdate.less_than_date(inputs.get("earlier"))
    assert not res2, "earlier !< earlier (exclusive)"


def test_lt_date_inclusive(inputs = {
        "earlier": date(2023, 1, 1), 
        "later": date(2023, 4, 1)
        }
    ):
    fdate = DateFormatter(inputs.get("later"))
    res = fdate.less_than_date(inputs.get("later"), inclusive=True)
    assert res, "later == later (inclusive)"
    
    fdate = DateFormatter(inputs.get("earlier"))
    res = fdate.less_than_date(inputs.get("earlier"), inclusive=True)
    assert res, "earlier == earlier (inclusive)"
