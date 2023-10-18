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
import plotly.io as pio
from plotly.subplots import make_subplots

# Streamlit
import streamlit as st



# =========================================================================================================================
# Parameters
ticker = ('BTCUSD', 'ETHUSD', 'USDTUSD', 'BNBUSD', 'XRPUSD', 'USDCUSD', 'SOLUSD', 'ADAUASD', 'DOGEUSD', 'TRXUSD') # Get information
interval = 1440 # Get information

st_window = 14 # Compute indicator
st_nmean = 3 # Compute indicator


# Initialize API
api = krakenex.API()
connection = KrakenAPI(api)

# =========================================================================================================================
# Function to extract the information
def get_information_asset(ticker = 'BTCUSD', interval = 1440):
    # Extract the information
    data = connection.get_ohlc_data(ticker, interval = interval, ascending = True)[0]
    data = data.iloc[:, [1, 2, 3, 4, 6]].apply(pd.to_numeric, errors = 'coerce').reset_index()
    data = data.rename(columns = {'dtime': 'date'})

    # Compute stochastic oscillator
    data['period_high'] = data['high'].rolling(st_window).max()
    data['period_low'] = data['low'].rolling(st_window).min()
    data['pctK'] = (data['close'] - data['period_low']) * 100 / (data['period_high'] - data['period_low'])
    data['pctD'] = data['pctK'].rolling(st_nmean).mean()
    data = data.dropna().reset_index(drop = True)
    
    # Define sell and buy signals
    data['buy_sell_signal'] = np.where(data['pctK'] > data['pctD'], 'Buy', 'Sell')
    
    return(data)

Init_data = get_information_asset()


# =========================================================================================================================
# Streamlit App
st.set_page_config(layout = "wide")
    
st.title("Kraken Project: Stochastic Oscillator for cryptocurrencies")
st.write("This is an interactive site where you can see the behavior of all cryptocurrencies")

st.sidebar.image("https://altcoinsbox.com/wp-content/uploads/2023/03/crypto.com-wallet-logo.png", caption = "")

# Select date and asset
start_date = st.sidebar.date_input('Start Date', min_value = Init_data['date'].min(), max_value = Init_data['date'].max())
end_date = st.sidebar.date_input('End Date', min_value = Init_data['date'].min(), max_value = Init_data['date'].max())

add_selectbox = st.sidebar.selectbox(
    "Which asset do you want to see?",
    ticker
)


# Filtered data
daily_data = get_information_asset(ticker = add_selectbox, interval = interval)
filtered_data = daily_data[(daily_data['date'] >= pd.to_datetime(start_date)) & (daily_data['date'] <= pd.to_datetime(end_date))]


# Initial Graph
fig_1 = px.line(filtered_data, x = 'date', y = 'close', title = 'Time series chart: {}'.format(add_selectbox))

fig_1.update_xaxes(
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
fig_1.update_yaxes(title_text = "Close Price")
fig_1.update_xaxes(title_text = "Date")


fig_1.update_layout(width = 1000, height = 600)


# Graph of indicator
fig_2 = make_subplots(specs = [[{"secondary_y": True}]])

fig_2.add_trace(
    go.Scatter(x = filtered_data['date'], y = filtered_data['pctK'], name = "%K"),
    secondary_y = False,
)

fig_2.add_trace(
    go.Scatter(x = filtered_data['date'], y = filtered_data['pctD'], name = "%D"),
    secondary_y = False,
)

fig_2.add_trace(
    go.Scatter(x = filtered_data['date'], y = filtered_data['close'], name = "Close"),
    secondary_y = True,
)

fig_2.update_layout(
    title_text = 'Stochastic Oscillator: {}'.format(add_selectbox)
)

fig_2.update_xaxes(
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

fig_2.update_xaxes(title_text = "Date")

fig_2.update_yaxes(title_text = "Indicator (%K, %D)", secondary_y = False)
fig_2.update_yaxes(title_text = "Close Price", secondary_y = True)
fig_2.update_layout(width = 1000, height = 600)

# =========================================================================================================================
# Show plots
st.plotly_chart(fig_1)
st.plotly_chart(fig_2)

