from flask import (
    Flask,
    current_app, 
    render_template, 
    send_from_directory,
    flash,
    redirect,
    url_for
)

from markdown import markdown
import os

# Create the Flask application
app = Flask(__name__)
app.config['DOCUMENTS_FOLDER'] = 'documents'   # set default documents folder, can be overridden in tests
app.secret_key = 'secret'


# Define the route for the homepage
@app.route("/")
def index():
    
    # Get the path to the documents folder from the app configuration
    docs_folder = current_app.config['DOCUMENTS_FOLDER']
    # Get a list of all documents in the folder
    try:
        files= os.listdir(docs_folder)
    except FileNotFoundError:
        files = []
    # Render the homepage template with the list of documents
    return render_template('index.html', documents=files)

@app.route("/documents/<filename>")
def file_content(filename):
    # Check if the requested file exists in the documents folder
    docs_folder = current_app.config['DOCUMENTS_FOLDER']
    file_path = os.path.join(docs_folder, filename)
    
    if os.path.isfile(file_path):
        # If the file exists, serve it
        # If the file is a markdown file, convert it to HTML before serving
        if filename.endswith('.md'):
            with open(file_path, 'r') as f:
                content = f.read()
                html_content = markdown(content)
                return html_content, 200, {'Content-Type': 'text/html; charset=utf-8'}
        # For other file types, serve them directly
        return send_from_directory(docs_folder, filename)
    else:
        # If the file does not exist, flash an error message and redirect to the homepage
        flash(f"File '{filename}' not found.")
        return redirect(url_for('index'))
    
    # Serve the requested document
    return send_from_directory(docs_folder, filename)


# Run the app
if __name__ == "__main__":
    app.run(debug=True, port=5003)