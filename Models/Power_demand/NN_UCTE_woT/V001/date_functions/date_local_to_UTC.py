from pytz import timezone

def date_local_to_UTC(self, date_local):

    date_UTC = date_local.astimezone(timezone('Europe/Brussels'))

    return date_UTC
