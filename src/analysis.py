# =========================================================================================================================
# Import libraries
# Data process
import pandas as pd
import numpy as np

# Krakenex library
import krakenex
from pykrakenapi import KrakenAPI

import requests

# Dates
import datetime

# Graphics
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px

# =========================================================================================================================
# Parameters
ticker = 'BTCUSD'
intervalo = 1440

# Initialize API
api = krakenex.API()
connection = KrakenAPI(api)

# Extract information
daily_data = connection.get_ohlc_data(ticker, interval = intervalo, ascending = True)[0]
daily_data = daily_data.iloc[:, [1, 2, 3, 4, 6]].apply(pd.to_numeric, errors = 'coerce').reset_index()
daily_data = daily_data.rename(columns = {'dtime': 'date'})

# =========================================================================================================================
# Interactive Graph
fig = px.line(daily_data, x = 'date', y = 'close', title = 'Time series chart: {}'.format(ticker))

fig.update_xaxes(
    rangeslider_visible = True,
    rangeselector = dict(
        buttons = list([
            dict(count = 1, label = "1m", step = "month", stepmode = "backward"),
            dict(count = 6, label = "6m", step = "month", stepmode = "backward"),
            dict(count = 1, label = "YTD", step = "year", stepmode = "todate"),
            dict(count = 1, label = "1y", step = "year", stepmode = "backward"),
            dict(step = "all")
        ])
    )
)

fig.show()


