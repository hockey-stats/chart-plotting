"""
Some universal utility functions to be used by processing scripts.
"""

def convert_raw_to_ph(total_toi, flat_total):
    rate_value = round(flat_total * (60.0/ total_toi), 2)
    return rate_value