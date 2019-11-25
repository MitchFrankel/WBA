"""
This module provides functions for generating bokeh plots for daily user figures
"""

import numpy as np
from bokeh.models import ColumnDataSource, FactorRange, HoverTool, Range1d, Title, LabelSet
from bokeh.plotting import figure
from bokeh.transform import dodge


# GLobals
PLOT_COLORS = ('#0EBFE9', '#0BB5FF', '#009ACD', '#00688B', '#0D4F8B')  # Base colors - blues in increasing darkness
MONTHS = ("Dec", "Jan", "Feb", "Mar", "Apr")
ALL_DOW = ("All", "Saturday", "Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday")
COL_WIDTH = 0.8
COL_GAP = 0.05


def make_data_set(sites, season, day_of_week, adu_df):
    """
    Set the data based on site, day of week, and seasons selected. Then sort based on
    season then month
    """
    return adu_df.query("site in @sites and dayOfWeek == @day_of_week and season == @season").sort_values(['month'])


def init_figure():
    return figure(x_range=FactorRange(*MONTHS), y_range=(0, 100), plot_height=400,
                  plot_width=800, toolbar_location='right', tools="save", title="")


def style_plot(p):
    """
    Stylize the plot
    """
    # Title
    p.title.text_font_size = '12pt'
    p.title.text_font_style = 'bold'

    # x-axis modifications
    p.x_range.range_padding = 0.1
    p.xgrid.grid_line_color = None
    p.xaxis.major_tick_line_color = None  # turn off x-axis major ticks
    p.xaxis.minor_tick_line_color = None  # turn off x-axis minor ticks
    p.xaxis.major_label_orientation = 0
    p.xaxis.major_label_text_font_size = '12pt'
    p.xaxis.major_label_text_font_style = 'bold'
    p.xaxis.major_label_standoff = 10

    # y-axis modifications
    p.y_range.start = 0
    p.yaxis.minor_tick_line_color = None
    p.yaxis.major_label_text_font_size = '12pt'
    p.yaxis.major_label_text_font_style = 'bold'

    # legend
    p.legend.location = "top_left"
    p.legend.orientation = "horizontal"

    return p


def set_title_str(season, day_of_week):
    """
    Generate title string for plot
    """
    dow_str = 'Per Month' if day_of_week == 'All' else "Per Month For {}s".format(day_of_week.title())
    return "Season {} | Average Daily Trailhead Users {}".format(season, dow_str)


def set_col_width_offset(n_sites):
    """
    Determine column widths and offsets based on seasons [brute force cause I can't think at the moment]
    """
    width = COL_WIDTH / n_sites
    if n_sites == 1:
        offsets = [0]
    else:
        gap = COL_GAP / (n_sites-1)
        ixs = list(range(-(n_sites//2), n_sites//2 + 1))
        if n_sites % 2 == 0:
            ixs.remove(0)
            offsets = [(gap + width) * (i - np.sign(i)/2) for i in ixs]
        else:
            offsets = [(gap + width) * i for i in ixs]

    return width, offsets


def make_plot(src_df, p=None, show_sensor_n=False):
    """
    Generate the bokeh plot based on specific data
    """

    # If base figure does not exist, create now
    if p is None:
        p = init_figure()

    # Determine how many sites there are, then column width/offsets
    sites = sorted(src_df['site'].unique())
    n_sites = len(sites)
    width, offsets = set_col_width_offset(n_sites)

    # Add bar plot for each site
    for offset, site, color in zip(offsets, sites, PLOT_COLORS[0:len(offsets)]):
        temp_df = src_df.query("site == @site")
        adu = [0 if temp_df[temp_df['month'] == month].empty
               else temp_df[temp_df['month'] == month]['adu'].values[0]
               for month in MONTHS]

        p.vbar(x=dodge('x', offset, range=p.x_range), top='counts', width=width,
               source=ColumnDataSource(data=dict(x=MONTHS, counts=adu)),
               fill_alpha=0.9, hover_fill_alpha=1.0, legend_label=site, name=site, color=color)

        # Add n days of data labels
        n_days_data = ["" if temp_df[temp_df['month'] == month].empty
                       else "({})".format(temp_df[temp_df['month'] == month]['n'].values[0])
                       for month in MONTHS]

        if show_sensor_n:
            labels = LabelSet(x=dodge('x', offset, range=p.x_range), y='y', text='n', level='glyph', y_offset=0,
                              source=ColumnDataSource(data=dict(x=MONTHS, y=adu, n=n_days_data)),
                              render_mode='canvas', text_font_size="7pt", text_align='center', text_color='#000000')

            p.add_layout(labels)

    # Add hover tool
    p.add_tools(HoverTool(tooltips=[("Site", "$name"),
                                    ("Average Daily Users", "@counts{int}")]))

    # Stylize plot
    style_plot(p)

    # Add title and fix y_range
    title_str = set_title_str(src_df['season'].values[0], src_df['dayOfWeek'].values[0])
    p.add_layout(Title(text=title_str, text_font_size="13pt"), 'above')
    p.y_range = Range1d(0, src_df['adu'].max() * 1.3)
    if show_sensor_n:
        p.add_layout(Title(text="Note: (*) is number of days with sensor data",
                           text_font_size="10pt", text_font_style='normal'), 'below')

    return p
