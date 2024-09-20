import os
import pytz


def set_default_timezone():
    time_zone = 'America/Sao_Paulo'
    os.environ['TZ'] = time_zone
    pytz.timezone(time_zone)
