import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import unittest
from unittest.mock import patch, MagicMock
from tools.google_search import google_search

class TestGoogleSearchTool(unittest.TestCase):
    @patch('tools.google_search.requests.get')
    def test_google_search_success(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.json.return_value = {
            'items': [
                {'title': 't1', 'snippet': 's1', 'link': 'l1'}
            ]
        }
        mock_get.return_value = mock_resp
        result = google_search('test')
        self.assertIn('results', result)
        self.assertEqual(result['results'][0]['title'], 't1')

    @patch('tools.google_search.requests.get')
    def test_google_search_no_creds(self, mock_get):
        with patch('tools.google_search.GOOGLE_SEARCH_API_KEY', None):
            result = google_search('test')
            self.assertEqual(result, {'results': []})

    @patch('tools.google_search.requests.get')
    def test_google_search_api_error(self, mock_get):
        mock_get.side_effect = Exception('fail')
        result = google_search('test')
        self.assertEqual(result, {'results': []})

if __name__ == '__main__':
    unittest.main() 
