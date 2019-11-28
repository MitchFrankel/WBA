"""
This module provides functions for generating bokeh plots for daily user figures
"""

from datetime import datetime
import os
import pandas as pd
import numpy as np

file_path = os.path.abspath(os.path.join(os.getcwd(), "..", "..", "data", "raw", "TRAFx_raw.csv"))
trafx_df = pd.read_csv(file_path)
trafx_df['Day'] = trafx_df['Day'].apply(lambda x: datetime.strptime(x, '%Y-%m-%d'))
trafx_df.replace(np.nan, 0, inplace=True)

file_path = os.path.abspath(os.path.join(os.getcwd(), "..", "..", "data", "raw", "alta_snowfall.csv"))
alta_df = pd.read_csv(file_path)
alta_df['Report Date'] = alta_df['Report Date'].apply(lambda x: datetime.strptime(x, '%Y-%m-%d'))
alta_df['Day'] = alta_df['Report Date']


def make_data_set(trafx_df, alta_df, season, site):
    # Set start/end date
    start_date = datetime.strptime("{}-12-01".format(season.split("-")[0]), '%Y-%m-%d')
    end_date = datetime.strptime("{}-04-30".format(season.split("-")[1]), '%Y-%m-%d')

    # Only keep Day and site
    tmp_trafx_df = trafx_df[['Day', site]]

    # Loop through all possible dates and get data
    df = pd.DataFrame(columns=['date', 'users', 'new_snow', 'cum_snow', 'storm_total'])
    last_cum_snow = 0
    for day in pd.date_range(start_date, end_date):

        # trafx data
        users = 0 if tmp_trafx_df.query("Day == @day").empty else tmp_trafx_df.query("Day == @day")[site].values[0]

        # alta data
        if alta_df.query("Day == @day").empty:
            alta_data = [0, last_cum_snow, 0]
        else:
            alta_data = alta_df.query("Day == @day")[['24 Hr New Snow',
                                                      'Storm Total', 'Cumulative Season Snow']].values[0]
            last_cum_snow = alta_df.query("Day == @day")['Cumulative Season Snow'].values[0]

        df.loc[len(df)] = [day, users] + list(alta_data)

    return df


df = make_data_set(trafx_df, alta_df, '2018-2019', 'LCC Our Lady')
df.head(5)











