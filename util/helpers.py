
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

def handle_player_full_names(df):
    """
    Generally skater names will be displayed as just their last names. This function will be
    called in the event that multiple skaters share a last name, and will adjust their last names
    to also show their first initials (e.g. Nylander -> W. Nylander and A. Nylander).

    If two players share the same name AND same first initial (screw you Elias Pettersson's), then
    add their position to their name too (e.g. E. Pettersson (F) and E. Pettersson (D)).

    :param DataFrame df: DataFrame with all player info for the team.
    """
    # Each player will consist of a tuple of (Full name, position)
    players = list(zip(df['name'], df['position']))
    last_names = [(player[0].split()[-1], player[1]) for player in players]

    # Find a list of all player last names which appear twice by maintaining a set of ones which
    # have been seen and checking any subsequent ones against that set.
    seen = set()
    dupes = [player[0] for player in last_names if player[0] in seen or seen.add(player[0])]
    final_names = []
    for player in players:
        name = player[0]
        last_name = name.split()[-1]
        if last_name in dupes:
            # If a last name appears in `dupes`, it means it was seen more than once, so add the
            # first initial to the display name
            initial = name.split()[0][0]
            display_name = f'{initial}. {last_name}'
            if display_name in final_names:
                # If that combination of first initial and last name has already been added to the
                # list of display names, then add their position as well.
                display_name = f"{display_name} ({player[1]})"
            final_names.append(display_name)
        else:
            final_names.append(last_name)
    print(final_names)
    return final_names
