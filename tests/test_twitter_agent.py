import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import unittest
from unittest.mock import patch, MagicMock
from tools.twitter import fetch_twitter_posts

class TestTwitterTool(unittest.TestCase):
    @patch('tools.twitter.tweepy.Client')
    def test_fetch_twitter_posts_success(self, mock_client):
        mock_instance = MagicMock()
        mock_client.return_value = mock_instance
        mock_instance.search_recent_tweets.return_value.data = [
            MagicMock(text='tweet1', id='1', created_at='2024-01-01', author_id='a')
        ]
        mock_instance.search_recent_tweets.return_value.includes = {'users': [{'id': 'a', 'username': 'user1'}]}
        result = fetch_twitter_posts('NYC', 'news', 1)
        self.assertIn('tweets', result)
        self.assertEqual(result['tweets'][0]['text'], 'tweet1')

    @patch('tools.twitter.tweepy.Client')
    def test_fetch_twitter_posts_no_token(self, mock_client):
        with patch('tools.twitter.BEARER_TOKEN', None):
            result = fetch_twitter_posts('NYC', 'news', 1)
            self.assertIn('error', result)

    @patch('tools.twitter.tweepy.Client')
    def test_fetch_twitter_posts_api_error(self, mock_client):
        mock_instance = MagicMock()
        mock_instance.search_recent_tweets.side_effect = Exception('fail')
        mock_client.return_value = mock_instance
        result = fetch_twitter_posts('NYC', 'news', 1)
        self.assertIn('error', result)

if __name__ == '__main__':
    unittest.main() 