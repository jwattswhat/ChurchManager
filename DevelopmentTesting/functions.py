import datetime


def pydate2wxdate(date):
    assert isinstance(date, (datetime.datetime, datetime.date))
    tt = date.timetuple()
    dmy = (tt[2], tt[1]-1, tt[0])
    return wx.DateTimeFromDMY(*dmy)


def wxdate2pydate(date):
    assert isinstance(date, wx.DateTime)
    if date.IsValid():
        ymd = map(int, date.FormatISODate().split('-'))
        return datetime.date(*ymd)
    else:
        return None


def SQLdate_to_string(SQLdate):
    dtobj = datetime.datetime.strptime(SQLdate, "%Y-%m-%d")
    st = dtobj.strftime("%Y-%m-%m")
    return st

# def mysql_field_type(field):
