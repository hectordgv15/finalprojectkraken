import unittest
import pandas as pd
from datetime import datetime, timedelta

from crypto_analysis.utils import select_box_date, process_response


class TestUtils(unittest.TestCase):
    def setUp(self):
        # Set raw API response data
        response_data = [
            [1641340800, "45", "47", "42", "43", "44", "40", 10],
            [1641427200, "43", "43", "42", "43", "43", "47", 20],
            [1641513600, "43", "43", "40", "41", "41", "57", 15],
        ]
        self.response = {"error": [], "result": {"BTCUSD": response_data, "last": 1641513600}}

        # Set date dataframe
        self.date_df = pd.DataFrame(
            [
                pd.to_datetime(1698364800, unit="s"),
                pd.to_datetime(1698451200, unit="s"),
                pd.to_datetime(1698537600, unit="s"),
                datetime.today() + timedelta(days=2),
            ],
            columns=["date"],
        )

    def test_process_response(self):
        # Set expected processed output
        output_data = [
            [pd.to_datetime(1641340800, unit="s"), 45, 47, 42, 43, 40],
            [pd.to_datetime(1641427200, unit="s"), 43, 43, 42, 43, 47],
            [pd.to_datetime(1641513600, unit="s"), 43, 43, 40, 41, 57],
        ]
        expected_output = pd.DataFrame(output_data, columns=["date", "open", "high", "low", "close", "volume"])

        # Get processed output
        output = process_response(self.response)

        # Check output columns
        self.assertTrue(all(output.columns == expected_output.columns))

        # Check output values
        self.assertTrue(all(output == expected_output))

    def test_select_box_date(self):
        # Set expected output
        expected_start_date = pd.to_datetime(1698364800, unit="s")
        expected_end_date = (
            datetime.today().strftime("%Y/%m/%d"),
            (datetime.today() - timedelta(days=1)).strftime("%Y/%m/%d"),
        )

        start_date, end_date = select_box_date(self.date_df)

        # Check start date
        self.assertTrue(start_date.strftime("%Y/%m/%d") == expected_start_date.strftime("%Y/%m/%d"))

        # Check start date
        self.assertTrue(end_date.strftime("%Y/%m/%d") in expected_end_date)


if __name__ == "__main__":
    unittest.main()
