# =========================================================================================================================
# Import libraries
# Data process
import pandas as pd
import numpy as np

# Krakenex library
import krakenex
from pykrakenapi import KrakenAPI

# Dates
import datetime

# Graphics
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

# =========================================================================================================================
# Parameters
ticker = 'SOLUSD' # Get information
interval = 1440 # Get information

st_window = 14 # Compute indicator
st_nmean = 3 # Compute indicator


# Initialize API
api = krakenex.API()
connection = KrakenAPI(api)

# =========================================================================================================================
# Extract information
daily_data = connection.get_ohlc_data(ticker, interval = interval, ascending = True)[0]
daily_data = daily_data.iloc[:, [1, 2, 3, 4, 6]].apply(pd.to_numeric, errors = 'coerce').reset_index()
daily_data = daily_data.rename(columns = {'dtime': 'date'})

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

# =========================================================================================================================
# Compute stochastic oscillator
daily_data['period_high'] = daily_data['high'].rolling(st_window).max()
daily_data['period_low'] = daily_data['low'].rolling(st_window).min()
daily_data['pctK'] = (daily_data['close'] - daily_data['period_low']) * 100 / (daily_data['period_high'] - daily_data['period_low'])
daily_data['pctD'] = daily_data['pctK'].rolling(st_nmean).mean()
daily_data = daily_data.dropna().reset_index(drop = True)

daily_data['buy_sell_signal'] = np.where(daily_data['pctK'] > daily_data['pctD'], 'Buy', 'Sell')

# Graph of indicator
fig = make_subplots(specs = [[{"secondary_y": True}]])

fig.add_trace(
    go.Scatter(x = daily_data['date'], y = daily_data['pctK'], name = "%K"),
    secondary_y = False,
)

fig.add_trace(
    go.Scatter(x = daily_data['date'], y = daily_data['pctD'], name = "%D"),
    secondary_y = False,
)

fig.add_trace(
    go.Scatter(x = daily_data['date'], y = daily_data['close'], name = "Close"),
    secondary_y = True,
)

fig.update_layout(
    title_text = 'Stochastic Oscillator: {}'.format(ticker)
)

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

fig.update_xaxes(title_text = "Date")

fig.update_yaxes(title_text = "Indicator (%K, %D)", secondary_y = False)
fig.update_yaxes(title_text = "Price", secondary_y = True)

fig.show()


