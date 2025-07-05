import sqlite3
from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = 'your_secret_key_here' # Replace with a strong, random key

DATABASE = 'database.db'

def init_db():
    """Initializes the database with a 'data' table if it doesn't exist."""
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                message TEXT
            )
        ''')
        conn.commit()

def get_db():
    """Connects to the database."""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row # This allows accessing columns by name
    return conn

@app.route('/')
def index():
    """Renders the main page with data input and search forms."""
    return render_template('index.html')

@app.route('/add', methods=['POST'])
def add_data():
    """Adds new data to the database."""
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']

        if not name or not email:
            flash('Name and Email are required fields!', 'error')
            return redirect(url_for('index'))

        try:
            with get_db() as conn:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO data (name, email, message) VALUES (?, ?, ?)",
                               (name, email, message))
                conn.commit()
            flash('Data added successfully!', 'success')
        except sqlite3.Error as e:
            flash(f'Error adding data: {e}', 'error')
        return redirect(url_for('index'))

@app.route('/search', methods=['GET', 'POST'])
def search_data():
    """Searches and displays existing data based on query."""
    query = request.args.get('query', '') # For GET requests
    if request.method == 'POST':
        query = request.form.get('query', '') # For POST requests (if you add a form)

    data = []
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            if query:
                # Basic search by name or email (case-insensitive)
                cursor.execute("SELECT * FROM data WHERE name LIKE ? OR email LIKE ?",
                               (f'%{query}%', f'%{query}%'))
            else:
                cursor.execute("SELECT * FROM data") # Display all if no query
            data = cursor.fetchall()
    except sqlite3.Error as e:
        flash(f'Error searching data: {e}', 'error')

    return render_template('results.html', data=data, query=query)

@app.route('/delete/<int:id>', methods=['POST'])
def delete_data(id):
    """Deletes a record from the database."""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM data WHERE id = ?", (id,))
            conn.commit()
        flash('Record deleted successfully!', 'success')
    except sqlite3.Error as e:
        flash(f'Error deleting record: {e}', 'error')
    return redirect(url_for('search_data')) # Redirect back to search results

if __name__ == '__main__':
    init_db() # Initialize the database when the app starts
    app.run(debug=True) # Run the Flask app in debug mode
