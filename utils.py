import utime


def format_date(dt: int) -> str:
    """Converts a unix timestamp to a string like "1 Jan\""""

    dtup = utime.localtime(dt)
    formatted: str
    if dtup[1] == 1:
        formatted = "Jan"
    elif dtup[1] == 2:
        formatted = "Feb"
    elif dtup[1] == 3:
        formatted = "Mar"
    elif dtup[1] == 4:
        formatted = "Apr"
    elif dtup[1] == 5:
        formatted = "May"
    elif dtup[1] == 6:
        formatted = "Jun"
    elif dtup[1] == 7:
        formatted = "Jul"
    elif dtup[1] == 8:
        formatted = "Aug"
    elif dtup[1] == 9:
        formatted = "Sep"
    elif dtup[1] == 10:
        formatted = "Oct"
    elif dtup[1] == 11:
        formatted = "Nov"
    elif dtup[1] == 12:
        formatted = "Dec"
    else:
        formatted = "???"

    return f"{dtup[2]} {formatted}"
