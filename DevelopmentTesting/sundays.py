import datetime
 
 
def next_weekday(d, weekday):
    days_ahead = weekday - d.weekday()
    if days_ahead <= 0:
        days_ahead += 7
    return d + datetime.timedelta(days_ahead)
 

d = datetime.date(2022, 9, 1)
next_sunday = next_weekday(d, 6)
print(next_sunday)