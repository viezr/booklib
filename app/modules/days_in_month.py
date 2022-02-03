'''
Get number of days in month
'''
from datetime import date as dt


def days_in_month( month: [str, int], year: [str, int] = None) -> int:
    '''
    Return number of days in given month.
    '''
    days = {
        "jan":31, "feb":28, "mar":31, "apr":30, "may":31, "jun":30,
        "jul":31, "aug":31, "sep":30, "oct":31, "nov":30, "dec":31
    }
    year = _check_year(year)
    month = _check_month(month)
    if _leap_year(int(year)):
        days["feb"] = 29
    if month not in days:
        err = " ".join(["Month", month, "not found"])
        raise ValueError(err)
    else:
        return days[month]

def _check_year(year: [str, int]) -> str:
    '''
    Check year input
    '''
    if not year:
        year = dt.today().strftime("%Y")
    if isinstance(year, int):
        year = str(year)
    elif not isinstance(year, str):
        err = "Year value type should be string or integer"
        raise TypeError(err)
    if len(year) not in range(2, 5):
        err = f"Year length should have 2 or 4 simbols"
        raise ValueError(err)
    else:
        try:
            int(year)
        except:
            err = "Year value should have number"
            raise ValueError(err)
    if len(year) == 2:
        year = dt.today().strftime("%Y")[3:] + year
    return year

def _check_month(month: [str, int]) -> str:
    '''
    Check month input
    '''
    months = {
        1: "jan", 2: "feb", 3: "mar", 4: "apr", 5: "may", 6: "jun",
        7: "jul", 8: "aug", 9: "sep", 10: "oct", 11: "nov", 12: "dec"
    }
    try:
        month_int = int(month)
        if month_int in range(1,13):
            return months[month_int]
        else:
            err = "Month integer value out of range 1-12"
            raise ValueError(err)
    except:
        pass
    if not isinstance(month, str):
        err = "Month value type should be string"
        raise TypeError(err)
    if len(month) < 3:
        err = "Month length should have at least 3 simbols"
        raise ValueError(err)
    return month.lower()[0:3]

def _leap_year(year: int) -> bool:
    '''
    Check year is leap
    '''
    if year % 400 == 0:
        return True
    elif year % 100 == 0:
        return False
    elif year % 4 == 0:
        return True
    return False
