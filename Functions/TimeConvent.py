import re
from disnake.ext import commands

time_regex = re.compile(r"(?:(\d{1,5})(h|s|m|d|w|mon|y))+?")
time_dict = {"h": 60 ** 2, "s": 1, "m": 60, "d": 60 ** 2 * 24, "w": 60 **
                                                                    2 * 24 * 7, "mon": 60 ** 2 * 24 * 30,
             "y": 60 ** 2 * 24 * 31 * 12,
             "ч": 60 ** 2, "с": 1, "м": 60, "д": 60 ** 2 * 24, "н": 60 **
                                                                    2 * 24 * 7, "мес": 60 ** 2 * 24 * 30,
             "л": 60 ** 2 * 24 * 31 * 12,
             "час": 60 ** 2, "сек": 1, "мин": 60, "дней": 60 ** 2 * 24, "недель": 60 **
                                                                                  2 * 24 * 7,
             "месяцев": 60 ** 2 * 24 * 30, "лет": 60 ** 2 * 24 * 31 * 12
             }

time_rus_key = {"h": "часа", "s": "секунд", "m": "минут", "d": "дней", "w": "недель", "mon": "месяцев", "y": "лет"}


def convert_to_russion(argument):
    args = argument.lower()
    matches = re.findall(time_regex, args)
    time = 0
    time_rus = ''
    longs = 0
    for key, value in matches:
        try:
            time += time_dict[value] * float(key)
            time_rus = time_rus_key[value]
            longs = key
        except KeyError:
            raise commands.BadArgument(
                f"{value} данный аргумент не верный! Правильный пример: s|m|h|d|w|mon|y "
            )
        except ValueError:
            raise commands.BadArgument(f"{key} это не цифра!")
    return round(time), str(time_rus), int(
        longs)  # time - время в секундах, time_rus - название на русском, longs - время в цифрах