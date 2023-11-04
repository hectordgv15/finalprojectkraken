# =========================================================================================================================
# Import libraries
# Data process
import pandas as pd
import numpy as np

# Krakenex library
import krakenex
from pykrakenapi import KrakenAPI

# Dates
import time
import datetime
from datetime import datetime, timedelta

# Graphics
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px
import plotly.io as pio
from plotly.subplots import make_subplots

# Streamlit
import streamlit as st

# =========================================================================================================================
# Streamlit App initial config
st.set_page_config(layout = "wide")
    
st.title("STOCHASTIC OSCILLATOR FOR CRYPTOCURRENCIES")
st.subheader("🔔 This is an interactive site where you can see the behavior of all cryptocurrencies")


# Special effect    
with st.spinner('Wait for it...'):
    time.sleep(7)
    
    
# =========================================================================================================================
# Parameters and load data
# Data
ticker = ('BTCUSD', 'ETHUSD', 'USDTUSD', 'XRPUSD', 'USDCUSD', 'SOLUSD', 'ADAUASD', 'DOGEUSD', 'TRXUSD') # Get information
interval = 1440

# Model
stochastic_window = 14 # Compute indicator
stochastic_nmean = 3 # Compute indicator

window_size_ma = 26 # Compute MA

# graph
days_plot_dafault = 180
w_plot = 1000
h_plot = 600


# Initialize API
api = krakenex.API()
connection = KrakenAPI(api)


# Function to extract the information
def get_information_asset(ticker = 'BTCUSD', interval = 1440):
    
    '''
    This function allows us to calculate the stochastic Oscillator.
    The second argument refers to the time interval for the data 
    in seconds; for example, to display daily data we need
    indicates how many seconds there are in a day.
    
    '''
    
    try:
        # Extract the information
        data = connection.get_ohlc_data(ticker, interval = interval, ascending = True)[0]
        data = data.iloc[:, [1, 2, 3, 4, 6]].apply(pd.to_numeric, errors = 'coerce').reset_index()
        data = data.rename(columns = {'dtime': 'date'})

        # Compute stochastic oscillator
        data['MA26'] = data['close'].rolling(window = window_size_ma).mean()
        data['period_high'] = data['high'].rolling(stochastic_window).max()
        data['period_low'] = data['low'].rolling(stochastic_window).min()
        data['pctK'] = (data['close'] - data['period_low']) * 100 / (data['period_high'] - data['period_low'])
        data['pctD'] = data['pctK'].rolling(stochastic_nmean).mean()
        data = data.dropna().reset_index(drop = True)
        
        # Define sell and buy signals
        data['signal'] = np.where(data['pctK'] > data['pctD'], 'Buy', 'Sell')
        
        return(data)
    
    except:
        print("There is a problem with the function or its parameters")


# =========================================================================================================================
# Site bar
st.sidebar.image("../images/Logohg.png", caption = "Technological platform for financial services")


# Select date and asset
def select_box_date(inicial_data, days_plot):
    
    '''
    this function generates the box to select a specific range of dates.
     
    '''
    
    start_date = st.sidebar.date_input('Start date',
                                    (datetime.today() - timedelta(days = days_plot)), 
                                    min_value = inicial_data['date'].min(), 
                                    max_value = inicial_data['date'].max()
                                    )

    try:
        end_date = st.sidebar.date_input('End date',
                                        datetime.today(), 
                                        min_value = inicial_data['date'].min(), 
                                        max_value = inicial_data['date'].max()
                                        )
        
    # Sometimes the user make a query when the data is not available because the API have not shown the data yet.    
    except:
        end_date = st.sidebar.date_input('End date',
                                        datetime.today() - timedelta(days = 1), 
                                        min_value = inicial_data['date'].min(), 
                                        max_value = inicial_data['date'].max()
                                        )
    
    return(start_date, end_date)

add_selectbox = st.sidebar.selectbox(
                                    "Which asset do you want to see?", 
                                    ticker
                                    )


# Apply
# Initial data to set date range
Init_data = get_information_asset()

select_date = select_box_date(Init_data, days_plot_dafault)


# =========================================================================================================================
# Dataframe filtered
daily_data = get_information_asset(
                                  ticker = add_selectbox, 
                                  interval = interval
                                  )


filtered_data = daily_data[(daily_data['date'] >= pd.to_datetime(select_date[0])) & 
                           (daily_data['date'] <= pd.to_datetime(select_date[1]))]




with st.expander("💹​ Asset information"):
    
    showData = st.multiselect('Filter: ', 
                              filtered_data.columns, 
                              default = [
                                        "date", 
                                         "open", 
                                         "high", 
                                         "close", 
                                         "volume", 
                                         "pctK", 
                                         "pctD", 
                                         "signal"
                                         ]
                              )
    
    st.dataframe(filtered_data[showData], use_container_width = True)


# =========================================================================================================================
# Additional information in boxes
count_cat = filtered_data['signal'].value_counts()
cat_buy = count_cat['Buy']
cat_sell = count_cat['Sell']

avg_return = filtered_data['close'].pct_change().mean() * 100
avg_price = filtered_data['close'].mean()

value1, value2, value3, value4 = st.columns(4, gap = 'large')

with value1:
    st.info(
           'Average return', 
           icon = "🚨"
           )
    st.metric(
             label = "Daily", 
             value = f"{avg_return:,.2f}%"
             )
    
with value2:
    st.info(
           'Average price', 
           icon = "🚨"
           )
    st.metric(
             label = "Daily", 
             value = f"{avg_price:,.2f}"
             )

with value3:
    st.info(
           'Buy signals', 
           icon = "🚨"
           )
    st.metric(
             label = "Times", 
             value = f"{cat_buy:,.0f}"
             )
    
with value4:
    st.info(
           'Sell signals', 
           icon = "🚨"
           )
    st.metric(
             label = "Times", 
             value = f"{cat_sell:,.0f}"
             )


# =========================================================================================================================
# Define graph function
def time_series_chart(t1, t2):
    
    # Basic plot
    fig_1 = px.line(filtered_data, 
                    x = 'date', 
                    y = ['close', 'MA26'], 
                    title = f' ☑️​​ {add_selectbox}', 
                    color_discrete_map = {"close": "black", 
                                          "MA26": "green"}
                    )
    
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
    
    fig_1.update_yaxes(title_text = "Close price")
    fig_1.update_xaxes(title_text = "Date")
    fig_1.update_layout(width = t1, height = t2)
    
    st.plotly_chart(fig_1)
    
    
    # Graph of indicator
    fig_2 = make_subplots(specs = [[{"secondary_y": True}]])
    fig_2.add_trace(
        go.Scatter(x = filtered_data['date'], y = filtered_data['pctK'], name = "%K", line = dict(color = '#FF8300')),
        secondary_y = False,
    )
    fig_2.add_trace(
        go.Scatter(x = filtered_data['date'], y = filtered_data['pctD'], name = "%D", line = dict(color = 'green')),
        secondary_y = False,
    )
    fig_2.add_trace(
        go.Scatter(x = filtered_data['date'], y = filtered_data['close'], name = "Close", line = dict(color = 'black')),
        secondary_y = True,
    )
    fig_2.update_layout(
        title_text = '☑️​ ​Stochastic Oscillator: {}'.format(add_selectbox)
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
    fig_2.update_yaxes(title_text = "Close price", secondary_y = True)
    fig_2.update_layout(width = t1, height = t2)

    st.plotly_chart(fig_2)


# Apply
time_series_chart(w_plot, h_plot)