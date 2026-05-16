from flask import (
    Flask,
    current_app, 
    render_template, 
    send_from_directory,
    flash,
    redirect,
    url_for,
    request,
    session
)

from markdown import markdown
from functools import wraps
import os
import warnings
warnings.filterwarnings("ignore", category=ResourceWarning)

# Create the Flask application
app = Flask(__name__)
app.config['DOCUMENTS_FOLDER'] = 'documents'   # set default documents folder, can be overridden in tests
app.secret_key = 'secret'

# Decorator to require sign in for certain routes
def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if 'username' not in session:
            flash("You must be signed in to access this page.")
            return redirect(url_for('signin'))
        return f(*args, **kwargs)
    return wrapper

def get_data_path():
    if app.config.get('TESTING'):
        # When running tests, use a dedicated folder inside tests/
        return os.path.join(os.path.dirname(__file__), 'tests', 'data')
    else:
        # In production, use the default documents folder
        return app.config['DOCUMENTS_FOLDER']

# Define the route for the homepage
@app.route("/")
def index():
    
    # Get the path to the documents folder from the app configuration
    docs_folder = get_data_path()
    # Get a list of all documents in the folder
    try:
        files= os.listdir(docs_folder)
    except FileNotFoundError:
        files = []
    # Render the homepage template with the list of documents
    return render_template('index.html', documents=files)

# Create a new file
@app.route("/new")
@login_required
def new_file():
    # Render a form to create a new file
    return render_template('new.html')

@app.route("/create", methods=['POST'])
@login_required
def create_file():
    # Create a new empty file from the submitted form data
    filename = request.form.get('filename', '').strip()
    docs_folder = get_data_path()
    file_path = os.path.join(docs_folder, filename)

    #Validation
    if not filename:
        flash("A name is required.")
        return render_template('new.html'), 422 # Unprocessable Entity
    
    if os.path.exists(file_path):
        flash(f"File '{filename}' already exists.")
        return render_template('new.html'), 422
    
    #Create the new file
    with open(file_path, 'w') as f:
        f.write('') # empty content - user can edit later

    flash(f"File '{filename}' has been created.")
    return redirect(url_for('index'))


@app.route("/documents/<filename>")
def file_content(filename):
    # Check if the requested file exists in the documents folder
    docs_folder = get_data_path()
    file_path = os.path.join(docs_folder, filename)
    
    if os.path.isfile(file_path):
        # If the file exists, serve it
        # If the file is a markdown file, convert it to HTML before serving
        if filename.endswith('.md'):
            with open(file_path, 'r') as f:
                content = f.read()
                html_content = markdown(content)
                return render_template('markdown.html', content=html_content)
        # For other file types, serve them directly
        return send_from_directory(docs_folder, filename)
    else:
        # If the file does not exist, flash an error message and redirect to the homepage
        flash(f"File '{filename}' not found.")
        return redirect(url_for('index'))
    
    # Serve the requested document
    return send_from_directory(docs_folder, filename)

# Edit the file content
@app.route("/documents/<filename>/edit", methods=['GET', 'POST'])
@login_required
def edit_file(filename):
    # Check if the requested file exists in the documents folder
    docs_folder = get_data_path()
    file_path = os.path.join(docs_folder, filename)
    
    if os.path.isfile(file_path):
        if request.method == 'POST':
            # Save the edited content to the file
            new_content = request.form['content']
            with open(file_path, 'w') as f:
                f.write(new_content)
            flash(f"File '{filename}' has been updated.")
            return redirect(url_for('index'))
        else:
            # Read the current content of the file and render the edit form
            with open(file_path, 'r') as f:
                content = f.read()
            return render_template('edit.html', filename=filename, content=content)
    else:
        # If the file does not exist, flash an error message and redirect to the homepage
        flash(f"File '{filename}' not found.")
        return redirect(url_for('index'))
    
# Delete a file
@app.route("/documents/<filename>/delete", methods=['POST'])
@login_required
def delete_file(filename):
    # Check if the requested file exists in the documents folder
    docs_folder = get_data_path()
    file_path = os.path.join(docs_folder, filename)

    if os.path.isfile(file_path):
        os.remove(file_path)
        flash(f"File '{filename}' has been deleted.")
        return redirect(url_for('index'))
    else:
        flash(f"File '{filename}' not found.")
    return redirect(url_for('index'))

# Sign in route (placeholder, no actual authentication implemented)
@app.route("/signin", methods=['GET', 'POST'])
def signin():
    # If user is already signed in, redirect to the index page
    if 'username' in session:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        # Hardcoded credentials for demonstration purposes
        if username == 'admin' and password == 'password':
            session['username'] = username
            flash("You have successfully signed in.")
            return redirect(url_for('index'))
        else:
            flash("Invalid username or password.")
            return render_template('signin.html'), 401 # Unauthorized
        
    # Get request - render the sign in form
    return render_template('signin.html')

# Create signout route
@app.route("/signout", methods=['POST'])
def signout():
    # Remove username from session
    session.pop('username', None)
    flash("You have been signed out.")
    return redirect(url_for('index'))

# Run the app
if __name__ == "__main__":
    app.run(debug=True, port=5003)