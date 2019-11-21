"""
Average daily user counts
"""

# Imports
from datetime import datetime
import os
import pandas as pd

# Verify file path to trax data is correct
trafx_data_file_path = os.path.abspath(os.path.join(os.getcwd(), "..", "..", "data", "raw", "TRAFx_raw.csv"))

# Load data
trafx_df = pd.read_csv(trafx_data_file_path)

# Convert Day to datetime
trafx_df['Day'] = trafx_df['Day'].apply(lambda x: datetime.strptime(x, "%Y-%m-%d"))

# Drop all rows with null data
# trafx_df.dropna(inplace=True)

# Append season, month, and day of week on to main dataframe
trafx_df['month'] = trafx_df['Day'].apply(lambda x: x.strftime('%b'))
trafx_df['dayOfWeek'] = trafx_df['Day'].apply(lambda x: x.strftime('%A'))


def set_season(date_time):
    if date_time.month == 12:
        return "{}-{}".format(date_time.year, date_time.year + 1)
    elif date_time.month <= 4:
        return "{}-{}".format(date_time.year - 1, date_time.year)
    else:
        return 'None'


trafx_df['season'] = trafx_df['Day'].apply(lambda x: set_season(x))
trafx_df = trafx_df[trafx_df['season'] != 'None']

adu_df = pd.DataFrame(columns=['site', 'season', 'month', 'dayOfWeek', 'n', 'adu'])

# Get monthly averages
ms_adu_val = trafx_df.groupby(['season', 'month']).mean()
ms_adu_n = trafx_df.groupby(['season', 'month']).count()
for season, month in ms_adu_val.index.to_list():
    for site in ms_adu_val.columns:
        if ms_adu_n.loc[season, month][site] > 0:
            adu_df.loc[len(adu_df)] = [site, season, month, 'all', ms_adu_n.loc[season, month][site],
                                       ms_adu_val.loc[season, month][site]]

# Get daily averages
msd_adu_val = trafx_df.groupby(['season', 'month', 'dayOfWeek']).mean()
msd_adu_n = trafx_df.groupby(['season', 'month', 'dayOfWeek']).count()
for season, month, dow in msd_adu_val.index.to_list():
    for site in ms_adu_val.columns:
        if msd_adu_n.loc[season, month, dow][site] > 0:
            adu_df.loc[len(adu_df)] = [site, season, month, dow, msd_adu_n.loc[season, month, dow][site],
                                       msd_adu_val.loc[season, month, dow][site]]
