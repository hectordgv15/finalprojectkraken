import unittest
import pandas as pd

from crypto_analysis.model import CryptoAnalysisModel


# Test CryptoAnalysisModel class
class TestCryptoAnalysisModel(unittest.TestCase):
    def setUp(self):
        # Initialize class
        self.model = CryptoAnalysisModel()

        # Dummy input data
        self.input_data = {"pair": "BTCUSD", "interval": 1440, "since": 1696118400, "until": 1696377600}

        # Expected output data
        data = {
            "date": [
                pd.to_datetime(1698364800, unit="s"),
                pd.to_datetime(1698451200, unit="s"),
            ],
            "open": [34155.2, 33915.1],
            "high": [34239.7, 34463.7],
            "low": [33318.6, 33852.8],
            "close": [33915.1, 34092.1],
            "volume": [2681.16178873, 1222.22173256],
            "MA": [29102.17692307692, 29355.684615384613],
            "period_high": [35225.0, 35225.0],
            "period_low": [26820.0, 26820.1],
            "pctK": [84.41522903033906, 86.52095801258788],
            "pctD": [87.80646459962247, 86.14130211372418],
            "Buy_Signal": [0, 0],
            "Sell_Signal": [0, 0],
            "Overbought_Signal": [0, 0],
            "Oversold_Signal": [0, 0],
        }

        self.expected_output = pd.DataFrame(data, columns=data.keys())

    def test_get_conection(self):
        # Test connection attribute
        self.model.get_conection()
        self.assertTrue(self.model.connection is not None)

    def test_load_config(self):
        # Test configuration dictionary generation
        self.model.load_config()
        self.assertTrue(self.model.config is not None)
        self.assertTrue(isinstance(self.model.config, dict))

    def test_get_data(self):
        # Get data
        output_data = self.model.get_data(**self.input_data)

        # Set expected output (first 2 rows)
        expected_output_0 = [pd.to_datetime(1696204800, unit="s"), 27981.1, 28572.5, 27298.0, 27500.9, 5477.09708743]
        expected_output_1 = [pd.to_datetime(1696291200, unit="s"), 27500.9, 27658.2, 27189.0, 27428.2, 2269.82042802]

        # Check output not empty
        self.assertTrue(len(output_data) > 0)

        # Check output columns
        self.assertTrue(all(output_data.columns == ["date", "open", "high", "low", "close", "volume"]))

        # Check output values
        self.assertTrue(all(output_data.loc[0] == expected_output_0))
        self.assertTrue(all(output_data.loc[1] == expected_output_1))

        # Check data cache
        self.assertTrue(len(self.model.data_cache) > 0)
        self.assertTrue("raw" in self.model.data_cache[self.input_data["pair"]])

    def test_get_crypto_pairs(self):
        # Set default pairs
        default_pairs = ["ETHUSD", "BTCUSD", "USDTUSD", "XRPUSD", "USDCUSD", "SOLUSD", "ADAUSD", "DOGEUSD", "TRXUSD"]

        # Get Cryptocurrencies pairs
        pairs = self.model.get_crypto_pairs()

        # Check that the output contain at least default pairs
        self.assertTrue(set(default_pairs) <= set(pairs))

    def test_compute_indicators(self):
        # Get data with computed indicators
        _ = self.model.get_data(**self.input_data)
        output_data = self.model.compute_indicators(**self.input_data)

        # Check output not empty
        self.assertTrue(len(output_data) > 0)

        # Check output columns
        self.assertTrue(all(output_data.columns == self.expected_output.columns))

        # Check output values
        self.assertTrue(all(output_data.loc[0] == self.expected_output.loc[0]))
        self.assertTrue(all(output_data.loc[1] == self.expected_output.loc[1]))

        # Check indicators values
        self.assertTrue(all(output_data["pctK"] >= 0) and all(output_data["pctK"] <= 100))
        self.assertTrue(all(output_data["pctD"] >= 0) and all(output_data["pctD"] <= 100))

        # Check signal values
        self.assertTrue(set(output_data["Buy_Signal"].unique()) <= {0, 1})
        self.assertTrue(set(output_data["Sell_Signal"].unique()) <= {0, 1})
        self.assertTrue(set(output_data["Overbought_Signal"].unique()) <= {0, 1})
        self.assertTrue(set(output_data["Oversold_Signal"].unique()) <= {0, 1})

        # Check data cache
        self.assertTrue(len(self.model.data_cache) > 0)
        self.assertTrue("data" in self.model.data_cache[self.input_data["pair"]])

    def test_graph_pair(self):
        # Test graph generation
        fig = self.model.graph_pair(self.expected_output, "BTCUSD")
        self.assertTrue(fig is not None)


if __name__ == "__main__":
    unittest.main()
