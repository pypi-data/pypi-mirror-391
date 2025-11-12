import unittest
from unittest.mock import patch, call
from progenomes import download

class TestDownload(unittest.TestCase):

    def test_get_genome_url(self):
        # Test case 1: representative-genomes
        url = download._get_genome_url('representative-genomes', 'proteins')
        expected_url = 'https://progenomes.embl.de/data/repGenomes/progenomes3.proteins.representatives.fasta.bz2'
        self.assertEqual(url, expected_url)

        # Test case 2: aquatic
        url = download._get_genome_url('aquatic', 'contigs')
        expected_url = 'https://progenomes.embl.de/data/habitats/representatives.aquatic.contigs.fasta.gz'
        self.assertEqual(url, expected_url)

    @patch('urllib.request.urlretrieve')
    def test_download_genomes(self, mock_urlretrieve):
        components = ['proteins', 'contigs']
        download.download_genomes('representative-genomes', components)

        # Check that urlretrieve was called with the correct URLs
        expected_calls = [
            call('https://progenomes.embl.de/data/repGenomes/progenomes3.proteins.representatives.fasta.bz2', 'progenomes3.proteins.representatives.fasta.bz2'),
            call('https://progenomes.embl.de/data/repGenomes/progenomes3.contigs.representatives.fasta.bz2', 'progenomes3.contigs.representatives.fasta.bz2')
        ]
        mock_urlretrieve.assert_has_calls(expected_calls, any_order=True)

    def test_get_dataset_url(self):
        # Test case 1: habitats-per-isolate
        url = download._get_dataset_url('habitats-per-isolate')
        expected_url = 'https://progenomes.embl.de/data/proGenomes3_habitat_isolates.tab.bz2'
        self.assertEqual(url, expected_url)

        # Test case 2: highly-important-strains
        url = download._get_dataset_url('highly-important-strains')
        expected_url = 'https://progenomes.embl.de/data/highly_important_strains.tab.bz2'
        self.assertEqual(url, expected_url)

    @patch('urllib.request.urlretrieve')
    def test_download_dataset(self, mock_urlretrieve):
        download.download_dataset('habitats-per-isolate')
        mock_urlretrieve.assert_called_once_with(
            'https://progenomes.embl.de/data/proGenomes3_habitat_isolates.tab.bz2',
            'proGenomes3_habitat_isolates.tab.bz2'
        )

if __name__ == '__main__':
    unittest.main()
