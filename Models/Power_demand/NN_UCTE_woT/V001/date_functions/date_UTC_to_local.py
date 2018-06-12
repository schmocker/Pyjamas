from pytz import timezone

def date_UTC_to_local(self, date_UTC):

    date_local = date_UTC.astimezone(timezone('UTC'))

    return date_local
