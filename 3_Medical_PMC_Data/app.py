import os
import sqlite3
from flask import Flask, render_template, g

app = Flask(__name__)
DATABASE = 'counter.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

def init_db():
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        cursor.execute('CREATE TABLE IF NOT EXISTS visit_count (id INTEGER PRIMARY KEY, count INTEGER)')
        cursor.execute('INSERT OR IGNORE INTO visit_count (id, count) VALUES (1, 0)')
        db.commit()

def get_and_increment_count():
    db = get_db()
    cursor = db.cursor()
    cursor.execute('UPDATE visit_count SET count = count + 1 WHERE id = 1')
    db.commit()
    cursor.execute('SELECT count FROM visit_count WHERE id = 1')
    return cursor.fetchone()[0]

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.route('/')
def dashboard():
    visitor_count = get_and_increment_count()
    return render_template('dashboard_final.html', count=visitor_count)

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000)
