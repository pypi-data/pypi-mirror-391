import unittest
from unittest.mock import patch
import sys
import os
import http.server
import socketserver
import threading
import time
from progenomes.cli import progenomes
from io import StringIO

PORT = 8000
BASE_URL = f"http://localhost:{PORT}"
FIXTURES_DIR = os.path.join(os.path.dirname(__file__), '..', 'fixtures')

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=FIXTURES_DIR, **kwargs)

class TestCliIntegration(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.httpd = socketserver.TCPServer(("", PORT), Handler)
        cls.server_thread = threading.Thread(target=cls.httpd.serve_forever)
        cls.server_thread.daemon = True
        cls.server_thread.start()
        time.sleep(1) # Give the server a moment to start

    @classmethod
    def tearDownClass(cls):
        cls.httpd.shutdown()
        cls.httpd.server_close()
        cls.server_thread.join()

    def tearDown(self):
        # Clean up downloaded files
        if os.path.exists('proGenomes3_habitat_isolates.tab.bz2'):
            os.remove('proGenomes3_habitat_isolates.tab.bz2')

    @patch('progenomes.download.DATASET_INITIAL_URL', BASE_URL)
    def test_download_dataset_integration(self):
        sys.argv = ['progenomes', 'download', 'datasets', 'habitats-per-isolate']
        progenomes.main()
        self.assertTrue(os.path.exists('proGenomes3_habitat_isolates.tab.bz2'))
        # Further checks could be added here to verify file content

    @patch('progenomes.view.INITIAL_URL', BASE_URL)
    def test_view_integration(self):
        # This test will fetch the file from the local server
        sys.argv = ['progenomes', 'view', 'habitats-per-isolate']
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            progenomes.main()
            output = mock_stdout.getvalue()
            self.assertIn('col1', output)
            self.assertIn('val1', output)

if __name__ == '__main__':
    unittest.main()
