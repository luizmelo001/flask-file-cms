import unittest
import shutil
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
        # Set up a temporary data path for testing
        self.data_path = os.path.join(os.path.dirname(__file__), 'data')
        os.makedirs(self.data_path, exist_ok=True)

    def tearDown(self):
        # Clean up the temporary data path after tests
        shutil.rmtree(self.data_path, ignore_errors=True)

    def create_document(self, filename, content=""):
        # Helper method to create a document in the test data path
        file_path = os.path.join(self.data_path, filename)
        with open(file_path, 'w') as f:
            f.write(content)
      

    def test_index(self):
        # Create some test documents
        self.create_document('about.md', "# About Python")
        self.create_document('changes.txt', "Python 3.10 introduces pattern matching.")
        
        # Test the index route
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, "text/html; charset=utf-8")

        data = response.get_data(as_text=True)
        self.assertIn("about.md", data)
        self.assertIn("changes.txt", data)
    

    def test_file_content(self):
        # Create a test document
        self.create_document('history.txt', "Python 0.9.0 (initial release) is released.")

        # Test the file content route for an existing file
        response= self.client.get('/documents/history.txt')
        self.assertEqual(response.status_code, 200)
        self.assertIn("text/plain; charset=utf-8", response.content_type)
        self.assertIn("Python 0.9.0 (initial release) is released.", response.get_data(as_text=True)) # is a in b?

    def test_file_content_markdown(self):
        # Create a test markdown document
        self.create_document('about.md', "# Python is...")

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

    def test_edit_file(self):
        # Create a test document
        self.create_document('history.txt', 'original content')
        # Test the edit file route for an existing file
        response = self.client.get('/documents/history.txt/edit')
        self.assertEqual(response.status_code, 200)
        self.assertIn("<textarea", response.get_data(as_text=True))
        self.assertIn("original content", response.get_data(as_text=True))

        # POST new content
        new_content = "Updated history content."
        response = self.client.post('/documents/history.txt/edit',
                                    data={'content': new_content},
                                    follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'has been updated', response.data)

        #Verify the file content was updated
        with open(os.path.join(self.data_path, 'history.txt'), 'r') as f:
            content = f.read()
            self.assertEqual(content, new_content)

    def test_new_file_form(self):
        # Test the new file form route
        response = self.client.get('/new')
        self.assertEqual(response.status_code, 200)
        self.assertIn("<input", response.get_data(as_text=True))
        self.assertIn('type="submit"', response.get_data(as_text=True))

    def test_create_new_file(self):
        #Test the new file creation route
        response = self.client.post('/create', data={'filename': 'newfile.txt'}, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'has been created', response.data)

        # Verify the new file was created
        file_path = os.path.join(self.data_path, 'newfile.txt')
        self.assertTrue(os.path.isfile(file_path))
        with open(file_path, 'r') as f:
            content = f.read()
            self.assertEqual(content, '')  # New file should be empty   

    def test_delete_file(self):
        #Create a test document
        self.create_document('todelete.txt', 'content to delete')

        #Test the delete file route
        response = self.client.post('/documents/todelete.txt/delete', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'has been deleted', response.data)

    #Test sign in route
    def test_signin(self):
        response = self.client.post('/signin', data={'username': 'admin', 'password': 'password'}, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'You have successfully signed in.', response.data)

    def test_signin_invalid(self):
        response = self.client.post('/signin', data={'username': 'wrong', 'password': 'credentials'}, follow_redirects=True)
        self.assertEqual(response.status_code, 401)
        self.assertIn(b'Invalid username or password.', response.data)

    # Test sign out route
    def test_signout(self):
        response = self.client.post('/signout', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'You have been signed out.', response.data)


if __name__ == '__main__':
    unittest.main()