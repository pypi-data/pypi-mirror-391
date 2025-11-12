import unittest
from unittest.mock import patch, MagicMock
from progenomes import view

class TestView(unittest.TestCase):

    def test_get_url(self):
        # Test with a valid item
        url, filetype = view.get_url('habitats-per-isolate')
        self.assertEqual(url, 'https://progenomes.embl.de/data/proGenomes3_habitat_isolates.tab.bz2')
        self.assertEqual(filetype, 'tab.bz2')

        # Test with another valid item
        url, filetype = view.get_url('highly-important-strains')
        self.assertEqual(url, 'https://progenomes.embl.de/data/highly_important_strains.tab.bz2')
        self.assertEqual(filetype, 'tab.bz2')

        # Test with an invalid item
        with self.assertRaises(ValueError):
            view.get_url('invalid-item')

    @patch('polars.from_pandas')
    @patch('pandas.read_table')
    def test_view_tab_bz2(self, mock_read_table, mock_from_pandas):
        # Mock the return value of get_url
        with patch('progenomes.view.get_url', return_value=('some_url.tab.bz2', 'tab.bz2')):
            view.view('any_target')
            mock_read_table.assert_called_once_with('some_url.tab.bz2')
            mock_from_pandas.assert_called_once()

    @patch('polars.from_pandas')
    @patch('pandas.read_csv')
    def test_view_tsv_bz2(self, mock_read_csv, mock_from_pandas):
        # Mock the return value of get_url
        with patch('progenomes.view.get_url', return_value=('some_url.tsv.bz2', 'tsv.bz2')):
            view.view('any_target')
            mock_read_csv.assert_called_once_with('some_url.tsv.bz2', sep='\t', index_col=None)
            mock_from_pandas.assert_called_once()

    @patch('polars.read_csv')
    def test_view_other(self, mock_read_csv):
        # Mock the return value of get_url
        with patch('progenomes.view.get_url', return_value=('some_url.csv', 'csv')):
            view.view('any_target')
            mock_read_csv.assert_called_once_with('some_url.csv', separator='\t')


if __name__ == '__main__':
    unittest.main()
