
def total_toi_as_timestamp(toi):
    """
    Given the total TOI as a float representing the number of minutes played,
    return a string representing the timestamp in the form MM:SS.

    :param float toi: Total time on ice, in minutes.
    """

    minutes = int(toi)
    seconds = int(60 * (toi - minutes))
    minutes = str(minutes) if minutes >= 10 else '0' + str(minutes)
    seconds = str(seconds) if seconds >= 10 else '0' + str(seconds)
    timestamp = f"{minutes}:{seconds}"
    return timestamp