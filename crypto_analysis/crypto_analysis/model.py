import yaml
import requests
import krakenex
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from crypto_analysis.utils import process_response
from crypto_analysis.exception import CryptoAnalysisException

import os


class CryptoAnalysisModel:
    def __init__(self):
        self.get_conection()
        self.load_config()
        self.data_cache = {}

    def get_conection(self):
        self.connection = krakenex.API()

    def load_config(self, config_path="config.yml"):
        # Get config path
        if not os.path.exists(config_path):
            config_path = os.path.join("crypto_analysis", config_path)

        # Read and parse config file
        with open(config_path, "r") as file:
            config = yaml.load(file, Loader=yaml.FullLoader)

        self.config = config

    def get_data(self, pair="BTCUSD", interval=None, **kwargs):
        """
        This function allows us to obtain the historical asset data.
        The second argument refers to the time interval for the data
        in seconds; for example, to display daily data we need
        indicates how many seconds there are in a day.
        """
        # Time interval. If None, get from config
        if interval is None:
            interval = self.config["data"]["interval"]

        try:
            # Get data from cache
            data = self.data_cache.get(pair, {}).get("raw", "NO_DATA")

            # Obtain data if asset not found in cache
            if isinstance(data, str):
                # Set API request parameters
                params = {
                    "pair": pair,
                    "interval": interval,
                    **kwargs,
                }

                # Get response from API
                response = self.connection.query_public("OHLC", params)

                # Response error raise
                if response["error"]:
                    raise CryptoAnalysisException(response["error"][0], "API CALL")

                # Process response
                data = process_response(response)

                # Save data in cache memory
                self.data_cache[pair] = {"raw": data}

            return data

        except Exception as e:
            raise CryptoAnalysisException(e, "GET DATA")

    def get_crypto_pairs(self):
        """
        This method obtains a list of supported cryptocurrency pairs from the Kraken API.
        """
        # Get the list of cryptography pairs from the Kraken API
        url = "https://api.kraken.com/0/public/AssetPairs"
        response = requests.get(url)

        # Default and most common pairs
        default_pairs = ["ETHUSD", "BTCUSD", "USDTUSD", "XRPUSD", "USDCUSD", "SOLUSD", "ADAUSD", "DOGEUSD", "TRXUSD"]

        try:
            # Get pairs as a list
            pairs_data = response.json()
            pairs = list(pairs_data["result"].keys())

            # Show common pairs first
            pairs = default_pairs + pairs
            return pairs

        except:
            # Return default pairs if the request fails
            print("Warning: Getting default pairs")
            return default_pairs

    def compute_indicators(self, pair="BTCUSD", interval=None, **kwargs):
        """
        This function allows us to calculate the stochastic Oscillator.
        The second argument refers to the time interval for the data
        in seconds; for example, to display daily data we need
        indicates how many seconds there are in a day.
        """
        # Time interval. If None, get from config
        if interval is None:
            interval = self.config["data"]["interval"]

        # Get data from cache
        raw_data = self.data_cache.get(pair, {}).get("raw", "NO_DATA")

        # Obtain data if asset not found in cache
        if isinstance(raw_data, str):
            print(f"Warning. No existing raw data for {pair}")
            raw_data = self.get_data(kwargs, pair=pair, interval=interval)

        data = raw_data.copy()

        try:
            # Compute stochastic oscillator

            # Moving average
            data["MA"] = data["close"].rolling(window=self.config["data"]["window_size_ma"]).mean()

            # Period highest and lowest value
            data["period_high"] = data["high"].rolling(self.config["model"]["stochastic_window"]).max()
            data["period_low"] = data["low"].rolling(self.config["model"]["stochastic_window"]).min()

            # Compute %K and %D
            data["pctK"] = ((data["close"] - data["period_low"]) / (data["period_high"] - data["period_low"])) * 100
            data["pctD"] = data["pctK"].rolling(self.config["model"]["stochastic_nmean"]).mean()

            data = data.dropna().reset_index(drop=True)

            # Define buy and sell signals based on %K and %D crossover
            # %D line crosses below %K line with values below 20% -> But signal
            data["Buy_Signal"] = (
                (data["pctK"] > data["pctD"]) & (data["pctK"].shift(1) < data["pctD"].shift(1)) & (data["pctK"] < 20)
            ).astype(int)

            # %K line crosses below %D line with values above 80% -> Sell signal
            data["Sell_Signal"] = (
                (data["pctK"] < data["pctD"]) & (data["pctK"].shift(1) > data["pctD"].shift(1)) & (data["pctK"] > 80)
            ).astype(int)

            # Define overbought and oversold signals (Other methodology, not in use)
            data["Overbought_Signal"] = np.where((data["pctK"] > 80) & (data["pctK"].shift(1) < 80), 1, 0)
            data["Oversold_Signal"] = np.where((data["pctK"] < 20) & (data["pctK"].shift(1) > 20), 1, 0)

            # Save data in cache memory
            self.data_cache[pair]["data"] = data

            return data

        except Exception as e:
            raise CryptoAnalysisException(e, "COMPUTE INDICATORS")

    def graph_pair(self, data, pair):
        # Define multiple plots
        fig = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.1, row_heights=[2, 0.7, 0.5])

        # Asset behavior
        fig.add_trace(
            go.Candlestick(
                x=data["date"],
                open=data["open"],
                high=data["high"],
                low=data["low"],
                close=data["close"],
                name="Candlestick",
            ),
            row=1,
            col=1,
        )

        # Moving average
        fig.add_trace(
            go.Scatter(
                x=data["date"], y=data["MA"], mode="lines", name="MA", line=dict(color="black", dash="dashdot")
            ),
            row=1,
            col=1,
        )

        # Sthochastic Oscilator
        fig.add_trace(go.Scatter(x=data["date"], y=data["pctK"], name="%K", line=dict(color="#FF8300")), row=2, col=1)
        fig.add_trace(go.Scatter(x=data["date"], y=data["pctD"], name="%D", line=dict(color="green")), row=2, col=1)

        # Volume
        fig.add_trace(go.Bar(x=data["date"], y=data["volume"], name="Volume", marker_color="#875E5E"), row=3, col=1)

        # Plot oscilators thresholds, in 80% and 20%
        fig.add_hline(y=80, row=2, col=1, line=dict(color="red", dash="dot"))
        fig.add_hline(y=20, row=2, col=1, line=dict(color="green", dash="dot"))

        # Plot design

        # First plot (asset)
        fig.update_yaxes(title_text="Close price", row=1, col=1)
        fig.update_xaxes(title_text="", row=1, col=1)

        # Second plot (Stochastic)
        fig.update_yaxes(title_text="Stochastic", row=2, col=1)
        fig.update_xaxes(title_text="", row=2, col=1)

        # Third plot (Volume)
        fig.update_yaxes(title_text="Volume", row=3, col=1)
        fig.update_xaxes(title_text="", row=3, col=1)

        # Define graph layout, add range selector
        fig.update_layout(
            title_text=f" ☑️​ Technical analysis: {pair}",
            showlegend=True,
            height=self.config["visual"]["h_plot"],
            width=self.config["visual"]["w_plot"],
            xaxis=dict(
                rangeselector=dict(
                    buttons=list(
                        [
                            dict(count=7, label="1w", step="day", stepmode="backward"),
                            dict(count=1, label="1m", step="month", stepmode="backward"),
                            dict(count=3, label="3m", step="month", stepmode="backward"),
                            dict(count=6, label="6m", step="month", stepmode="backward"),
                            dict(count=1, label="YTD", step="year", stepmode="todate"),
                            dict(count=1, label="1y", step="year", stepmode="backward"),
                            dict(step="all"),
                        ]
                    )
                )
            ),
            xaxis_rangeslider_visible=False,
        )

        return fig
