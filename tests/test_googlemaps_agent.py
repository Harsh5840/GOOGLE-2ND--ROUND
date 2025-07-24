import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import unittest
from unittest.mock import patch, MagicMock
from tools.maps import get_best_route

class TestGoogleMapsTool(unittest.TestCase):
    @patch('tools.maps.gmaps')
    def test_get_best_route_success(self, mock_gmaps):
        mock_gmaps.directions.return_value = [{
            'summary': 'Main St',
            'legs': [{
                'distance': {'text': '5 km'},
                'duration': {'text': '10 mins'},
                'duration_in_traffic': {'text': '12 mins'},
                'start_address': 'A',
                'end_address': 'B',
                'steps': [
                    {'html_instructions': 'Go straight', 'distance': {'text': '1 km'}, 'duration': {'text': '2 mins'}}
                ]
            }]
        }]
        result = get_best_route('A', 'B')
        self.assertIn('summary', result)
        self.assertEqual(result['summary'], 'Main St')

    @patch('tools.maps.gmaps')
    def test_get_best_route_no_key(self, mock_gmaps):
        with patch('tools.maps.GOOGLE_MAPS_API_KEY', None):
            result = get_best_route('A', 'B')
            self.assertIn('error', result)

    @patch('tools.maps.gmaps')
    def test_get_best_route_api_error(self, mock_gmaps):
        mock_gmaps.directions.side_effect = Exception('fail')
        result = get_best_route('A', 'B')
        self.assertIn('error', result)

if __name__ == '__main__':
    unittest.main() 