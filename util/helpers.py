
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


def handle_player_full_names(names):
    """
    Generally skater names will be displayed as just their last names. This function will be
    called in the event that multiple skaters share a last name, and will adjust their last names
    to also show their first initials (e.g. Nylander -> W. Nylander and A. Nylander).

    :param list names: List of full names.
    """
    last_names = [name.split()[-1] for name in names]
    seen = set()
    dupes = [name for name in last_names if name in seen or seen.add(name)]
    final_names = []
    for name in names:
        last_name = name.split()[-1]
        if last_name in dupes:
            initial = name.split()[0][0]
            display_name = f'{initial}. {last_name}'
            final_names.append(display_name)
        else:
            final_names.append(last_name)
    return final_names