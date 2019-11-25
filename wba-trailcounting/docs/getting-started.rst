Getting started  
===============  

# Python Environment  
* Python 3.7 - Use conda to create a conda environment  
* modules - There are some modules installed from conda and some that are only 
available via pip. See requirements.txt  

# Data management
1. [Optional] Run either Notebook 1.0 (in notebooks) or web_scrape_alta_snowfall.py
(in src/data). This will pull daily snowfall numbers from alta's snowfall history
webpage. It's possible the url, request headers, and tokens may have changed and need
updating. This will create alta_snowfall.csv in data/raw.

2. Run Notebook 2.0 or make_dataset_daily_users.py. This requires that the raw data
has been downloaded from the TRAFx website to data/raw and named TRAFx_raw.csv. The
raw csv should have columns of "Day" and then one for each <site_name>. This will 
create daily_user_averages.csv in data/processed.

These two csv form the bases for the scripts to generate figures etc. 
