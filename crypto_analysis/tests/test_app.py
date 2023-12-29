import unittest

from crypto_analysis.app import CryptoAnalysisApp


# Test CryptoAnalysisApp class. Integration-Testing.
class TestCryptoAnalysisApp(unittest.TestCase):
    def setUp(self):
        # Initialize class
        self.app = CryptoAnalysisApp()

    def test_init(self):
        # Check initialization attributes
        self.assertTrue(self.app.model is not None)
        self.assertTrue(self.app.config is not None)
        self.assertTrue(isinstance(self.app.config, dict))

    def test_display_title(self):
        # Display title method test
        self.app.display_title()
        self.assertTrue(True)

    def test_display_sidebar(self):
        # Display sidebar method and generated attributes test
        self.app.display_sidebar()
        self.assertTrue(self.app.filtered_data is not None)
        self.assertTrue(self.app.selected_asset is not None)

    def test_display_additional_info(self):
        # Display additional info method test
        self.app.display_sidebar()
        self.app.display_additional_info()
        self.assertTrue(True)

    def test_display_graph(self):
        # Display graph method test
        self.app.display_sidebar()
        self.app.display_graph()
        self.assertTrue(True)


if __name__ == "__main__":
    unittest.main()
