import unittest
from unittest.mock import patch, MagicMock
from agents.reddit_agent import fetch_reddit_posts, RedditAgent

class TestRedditAgent(unittest.TestCase):
    @patch('agents.reddit_agent.praw.Reddit')
    def test_fetch_reddit_posts_success(self, mock_reddit):
        mock_instance = MagicMock()
        mock_reddit.return_value = mock_instance
        subreddit = MagicMock()
        post = MagicMock(title='post1', id='1', author='author1', created_utc=123, url='url1')
        subreddit.hot.return_value = [post]
        mock_instance.subreddit.return_value = subreddit
        result = fetch_reddit_posts('news', 1)
        self.assertIn('posts', result)
        self.assertEqual(result['posts'][0]['title'], 'post1')

    @patch('agents.reddit_agent.praw.Reddit')
    def test_fetch_reddit_posts_no_creds(self, mock_reddit):
        with patch('agents.reddit_agent.REDDIT_CLIENT_ID', None):
            result = fetch_reddit_posts('news', 1)
            self.assertIn('error', result)

    @patch('agents.reddit_agent.praw.Reddit')
    def test_fetch_reddit_posts_api_error(self, mock_reddit):
        mock_reddit.side_effect = Exception('fail')
        result = fetch_reddit_posts('news', 1)
        self.assertIn('error', result)

if __name__ == '__main__':
    unittest.main() 