import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import unittest
from unittest.mock import patch, MagicMock
from agents.google_search_agent import google_search

class TestGoogleSearchAgent(unittest.TestCase):
    @patch('agents.google_search_agent.requests.get')
    def test_google_search_success(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.json.return_value = {
            'items': [
                {'title': 't1', 'snippet': 's1', 'link': 'l1'}
            ]
        }
        mock_get.return_value = mock_resp
        result = google_search('test')
        self.assertEqual(result[0]['title'], 't1')

    @patch('agents.google_search_agent.requests.get')
    def test_google_search_no_creds(self, mock_get):
        with patch('agents.google_search_agent.GOOGLE_SEARCH_API_KEY', None):
            result = google_search('test')
            self.assertEqual(result, [])

    @patch('agents.google_search_agent.requests.get')
    def test_google_search_api_error(self, mock_get):
        mock_get.side_effect = Exception('fail')
        result = google_search('test')
        self.assertEqual(result, [])

if __name__ == '__main__':
    unittest.main() 