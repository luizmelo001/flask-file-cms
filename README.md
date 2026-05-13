# Flask Document CMS

A lightweight, file‑based CMS built with Flask.  
Serves plain text (`.txt`) and Markdown (`.md`) files from a local folder – no database required.


## Features

- 📄 Lists all documents from a `documents/` directory  
- 📝 Serves `.txt` files as plain text  
- 🎨 Renders `.md` files as HTML using Markdown  
- 🔔 Flash message on missing file + redirect to homepage  
- 🧪 Unit tests included  


## Project Structure

cms/
├── app.py # Main Flask application
├── documents/ # Folder with .txt and .md files
│ ├── about.md
│ ├── changes.txt
│ └── history.txt
├── templates/
│ └── index.html # File listing template
├── tests/
│ └── test_app.py # Unit tests
└── README.md


## Using the cms

Place any .txt or .md file into the documents/ folder.
The homepage lists all files automatically.
Click on a .txt file – you’ll see plain text.
Click on a .md file – you’ll see rendered HTML (headings, bold, etc.).
Request a non‑existent file → you’re redirected to the homepage with a flash message.