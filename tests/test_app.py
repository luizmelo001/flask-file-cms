import unittest
import sys
import os
from app import app

# Allow importing app from parent directory
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class CMSTest(unittest.TestCase):
    def setUp(self):
        # Set up a test client for the Flask application
        app.config['TESTING'] = True
        self.client = app.test_client()

    def test_index(self):
        # Test the index route
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, "text/html; charset=utf-8")

        data = response.get_data(as_text=True)
        self.assertIn("about.md", data)
        self.assertIn("changes.txt", data)
        self.assertIn("history.txt", data)

    def test_file_content(self):
        # Test the file content route for an existing file
        response= self.client.get('/documents/history.txt')
        self.assertEqual(response.status_code, 200)
        self.assertIn("text/plain; charset=utf-8", response.content_type)
        self.assertIn("Python 0.9.0 (initial release) is released.", response.get_data(as_text=True)) # is a in b?

    def test_file_content_markdown(self):
        # Test the file content route for a markdown file
        response = self.client.get('/documents/about.md')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, "text/html; charset=utf-8")
        self.assertIn("<h1>Python is...</h1>", response.get_data(as_text=True))

    def test_file_not_found(self):
        # Test the file content route for a non-existing file
        response = self.client.get('/documents/nonexistent.txt')
        self.assertEqual(response.status_code, 302)  # Redirect to index
        
        # Follow the redirect and check for the flash message
        follow_response = self.client.get(response.headers['Location'])
        self.assertEqual(follow_response.status_code, 200)
        self.assertIn("nonexistent.txt", follow_response.get_data(as_text=True))

         # Check for flash message (HTML escaped, so don't rely on exact quotes)
        html = follow_response.get_data(as_text=True)
        self.assertIn("nonexistent.txt", html)
        self.assertIn("not found", html)

         # Assert that a page reload removes the message
        index_response = self.client.get("/")
        self.assertEqual(index_response.status_code, 200)
        self.assertNotIn("nonexistent.txt", index_response.get_data(as_text=True))
        self.assertNotIn("not found", index_response.get_data(as_text=True))
            

if __name__ == '__main__':
    unittest.main()