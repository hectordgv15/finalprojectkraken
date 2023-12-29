# Import libraries
import pandas as pd
import streamlit as st
import os

from crypto_analysis.utils import select_box_date
from crypto_analysis.model import CryptoAnalysisModel
from crypto_analysis.exception import CryptoAnalysisException


class CryptoAnalysisApp:
    """
    Main application class for the crypto analysis dashboard.
    """

    def __init__(self):
        """
        Initialize the model, config, and other necessary components.
        """
        # Initialize model
        self.model = CryptoAnalysisModel()
        self.config = self.model.config

    def run(self):
        """
        Dashboard deployment. This is the main entry point for the application.
        Display the main user interface elements in the appropriate order.
        """
        # Set page layout configuration
        st.set_page_config(layout="wide")

        # Display all the components
        self.display_title()
        self.display_sidebar()
        self.display_additional_info()
        self.display_graph()

    def display_title(self):
        """
        Display the application title and subtitle.
        """
        # Title
        st.title(self.config["text"]["title"])

        # Subtitle
        st.subheader("🔔 " + self.config["text"]["subtitle"])

    def display_sidebar(self):
        """
        Display the sidebar element, which includes the asset selection dropdown and the data
        explorer expander.
        """
        try:
            # Display logo
            logo_path = self.config["logo"]["path"]
            if not os.path.exists(logo_path):
                logo_path = os.path.join("crypto_analysis", logo_path)
            st.sidebar.image(logo_path, caption=self.config["logo"]["caption"])

            # Display asset selection dropdown
            ticker_options = self.model.get_crypto_pairs()
            self.selected_asset = st.sidebar.selectbox(self.config["text"]["asset_selectbox"], ticker_options)

            # Get data and compute indicators for selected asset
            asset_data = self.model.get_data(pair=self.selected_asset)
            asset_data = self.model.compute_indicators(pair=self.selected_asset)

            # Display date selector
            start_date, end_date = select_box_date(asset_data)

            # Filter data by selected date range
            self.filtered_data = asset_data[
                asset_data["date"].between(pd.to_datetime(start_date), pd.to_datetime(end_date))
            ]

            # Display data explorer
            with st.expander("💹​ " + self.config["text"]["data_expander"]):
                showData = st.multiselect(
                    "Filter: ",
                    self.filtered_data.columns,
                    default=[
                        "date",
                        "open",
                        "high",
                        "close",
                        "volume",
                        "pctK",
                        "pctD",
                        "Buy_Signal",
                        "Sell_Signal",
                    ],
                )
                st.dataframe(self.filtered_data[showData], use_container_width=True)

        # Raise exception if there is a problem with the selected asset
        except Exception as e:
            st.warning(self.config["text"]["asset_warning"], icon="⚠️")
            raise CryptoAnalysisException(e, "DATA BUILD")

    def display_additional_info(self):
        """
        Display the additional information, which includes metrics for the average return, average
        price, overbought signals, and oversold signals.
        """
        try:
            # Calculate the number of buy and sell signals
            cat_buy = self.filtered_data["Buy_Signal"].sum()
            cat_sell = self.filtered_data["Sell_Signal"].sum()

            # Calculate the average return and average price
            avg_return = self.filtered_data["close"].pct_change().mean() * 100
            avg_price = self.filtered_data["close"].mean()

            # Display the metrics
            value1, value2, value3, value4 = st.columns(4, gap="medium")

            with value1:
                st.info("Average return", icon="🚨")
                st.metric(label="Daily", value=f"{avg_return:,.2f}%")

            with value2:
                st.info("Average price", icon="🚨")
                st.metric(label="Daily", value=f"{avg_price:,.2f}")

            with value3:
                st.info("Buy signals", icon="🚨")
                st.metric(label="Times", value=f"{cat_buy:,.0f}")

            with value4:
                st.info("Sell signals", icon="🚨")
                st.metric(label="Times", value=f"{cat_sell:,.0f}")

        except Exception as e:
            raise CryptoAnalysisException(e, "INDICATORS BUILD")

    def display_graph(self):
        """
        Display the interactive graph element.
        """
        try:
            fig = self.model.graph_pair(self.filtered_data, self.selected_asset)
            st.plotly_chart(fig)
        except Exception as e:
            raise CryptoAnalysisException(e, "GRAPH BUILD")
