"""
Module for creating a dashboard displaying certain plots and tables used to determine
if there are any interesting free agents to add to my fantasy baseball team.
"""
import os
import zipfile
import json
import asyncio
from datetime import datetime

import requests
import matplotlib
import matplotlib.figure
import matplotlib.pyplot as plt
import pandas as pd
import panel as pn

from plotting.fantasy.mlb_free_agents import main as fa_plot

matplotlib.use("agg")

pn.extension('tabulator')

## Constants #########################################################################
POSITIONS = ['C', '1B', '2B', '3B', 'SS', 'OF', 'SP', 'RP']
ACCENT = "teal"
## End Constants #####################################################################


## Globals ###########################################################################
df_dict = {pos: {
                "df": None,
                "freeze": 0
                } for pos in POSITIONS}
## End Globals ########################################################################


## Bound Functions ####################################################################
# These are functions which will be bound to widgets which will provide the inputs
# used as function parameters and provide ouputs that can be displayed in the dashboard
async def get_plot(pos: str, date_range: str) -> matplotlib.figure:
    """
    Bound function which takes the position and date_range from their respective widgets
    and created a MatplotLib plot that will be displayed in the panel.

    :param str pos: The player position for which to make the plot.
    :param str date_range: The date range being used (i.e. week, month, season)
    :return matplotlib.figure: The matplotlib figure which will be displayed.
    """
    fig = fa_plot(position=pos, dashboard=True, term=date_range.split(' ')[-1].lower())
    plt.close(fig)  # CLOSE THE FIGURE TO AVOID MEMORY LEAKS!
    return fig


async def get_freeze_rows(pos: str) -> list[int]:
    """
    Gets the indices of rows that should be frozen in the statistics table. Current
    desired behaviour is to freeze the rows for each player already on my team.

    :param str pos: The player positions we're checking for.
    :return list[int]: A list of integers corresponding to the row indices which should be frozen.
    """
    df = pd.read_csv(f'data/fantasy_data_{pos}.csv')
    num_freeze = len(df[df['on_team']].drop_duplicates(['Name']))
    del df
    return list(range(num_freeze))


async def get_df(pos: str, date_range: str) -> pd.DataFrame:
    """
    Given a desired position and date range from their widgets, returns a DataFrame
    containing statistics for that position and date range.

    :param str pos: The desired player position 
    :param str date_range: The desired date range
    :return pd.DataFrame: DataFrame containing statistics with the desired conditions applied.
    """
    df = pd.read_csv(f'data/fantasy_data_{pos}.csv')
    try:
        df = df[df['term'] == date_range.lower()]
    except TypeError as e:
        print(f"Failed getting df for {pos}")
        print(f"df_dict: {df_dict}")
        raise e

    # Delete columns we don't want to see displayed on the dashboard
    del df['on_team']
    del df['Team']
    del df['term']

    df['Name'] = df.apply(lambda row: f"{row['Name'][0]}. {' '.join(row['Name'].split(' ')[1:])}",
                          axis=1)

    # Make sure the number of freeze rows is updated properly before returning the df
    task = asyncio.create_task(get_freeze_rows(pos))
    await task

    return df
## End Bound Functions ################################################################

@pn.cache
def load_data() -> None:
    """
    Function to be run at the initialization of the dashboard.

    Downloads all of the relevant CSV data files from GitHub, where they are stored as build
    artifact for a build that runs daily and scrapes the relevant statistics,

    Expects GitHub PAT with proper permissions to be available as an environment variable under
    'GITHUB_PAT'.

    :raises ValueError: Raises a ValueError if an artifact with today's timestamp is not found.
    """

    url = "https://api.github.com/repos/hockey-stats/chart-plotting/actions/artifacts"
    payload = {}
    headers = {
        'Authorization': f'Bearer {os.environ["GITHUB_PAT"]}'
    }
    output_filename = 'data.zip'

    # Returns a list of every available artifact for the repo
    response = requests.request("GET", url, headers=headers, data=payload, timeout=10)
    response_body = json.loads(response.text)

    # Get today's date in YYYY-MM-DD format, to compare to the returned artifacts
    today = datetime.today().strftime('%Y-%m-%d')

    for artifact in response_body['artifacts']:
        if artifact['name'] == 'dashboard-fa-data':
            artifact_creation_date = artifact['created_at'].split('T')[0]
            if today == artifact_creation_date:
                download_url = artifact['archive_download_url']
                break
                # Breaks when we find an artifact with the correct name and today's date
    else:
        # Raise an error if no such artifact as found
        raise ValueError(f"Data for {today} not found, exiting....")

    # Downloads the artifact as a zip file...
    dl_response = requests.request("GET", download_url, headers=headers, data=payload, timeout=20)
    with open(output_filename, 'wb') as fo:
        fo.write(dl_response.content)

    # ... and unzips
    with zipfile.ZipFile(output_filename, 'r') as zip_ref:
        zip_ref.extractall('data')

    # The unzipped contents will be one DataFrame for each position
    for pos in POSITIONS:
        # Read the raw CSV into a DataFrame
        df = pd.read_csv(f'data/fantasy_data_{pos}.csv')

        # Determine the number of players on team, for rows to freeze
        t_df = df[df['on_team']]
        num_freeze = len(set(t_df['Name']))
        df_dict[pos]['df'] = df
        df_dict[pos]['freeze'] = list(range(0, num_freeze))

    print(f"Data loaded for {artifact_creation_date}")


## Main Script Body ###################################################################

# Load today's data
load_data()

# Initialize the select widget for choosing the player position
position_widget = pn.widgets.Select(
                      description="Select a position",
                      name="Position",
                      options=['C', '1B', '2B', '3B', 'SS', 'OF', 'SP', 'RP'],
                      width=65
                  )

# Initialize the radio button widget for choosing the date range
date_range_widget = pn.widgets.RadioButtonGroup(
                        description='Select a date range over which to display data.',
                        options = ['Week', 'Month', 'Season'],
                        value='Week',
                        button_style='outline',
                        button_type='primary',
                        orientation='vertical',
                        width=65,
                    )

# Binding functions to their appropriate widgets
figure = pn.bind(get_plot, pos=position_widget, date_range=date_range_widget)
rows_to_freeze = pn.bind(get_freeze_rows, pos=position_widget)
table = pn.bind(get_df, pos=position_widget, date_range=date_range_widget)

# Initialize the table widget which displays our statistics in a table
table_pane = pn.widgets.Tabulator(
                             table,
                             layout='fit_columns',
                             show_index=False,
                             frozen_rows=rows_to_freeze,
                             theme='simple',
                             stylesheets=[":host .tabulator {font-size: 8px;}"]
                         )

# Initialize the pane displaying our plot
plot = pn.pane.Matplotlib(
    figure, format="svg", dpi=144, fixed_aspect=True, height=350
)

# Add all of the above to a FastListTemplate and make it servable
pn.template.FastListTemplate(
    title="Fantasy Free Agents of Interest",
    sidebar=[position_widget, date_range_widget],
    sidebar_width=70,
    main=[pn.Row(table_pane, plot)],
    accent=ACCENT,
    main_layout=None
).servable()

## End Main Script Body ###############################################################
